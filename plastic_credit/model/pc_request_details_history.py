from traitlets import default
from . import database
from odoo import models,fields,api,_
import psycopg2
from odoo.exceptions import ValidationError
import base64

class RequestDetailsHistory(models.Model):
    _name = 'request.details.history'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Request Details History'
    
    requester = fields.Many2one('res.users','Requester')
    name = fields.Char('Request Details')
    quantity_type = fields.Selection([('kg','Kilogram'),
                                    ('l','Litre'),
                                    ('cm','Centimeter')])
    code = fields.Char('Request Code',required=True,
                          readonly=True, default=lambda self: _('New'))
    def category(self):
        s=self.env['request.status'].search([('id','=',9)])
        return s
    category_id = fields.Many2one('product.category','Category',default=category)
    def regions(self):
        s=self.env['res.country'].search([('id','=',104)])
        return s
    region = fields.Many2one('res.country','Region',default=regions)
    pc_type = fields.Many2one('pc.type','PC Type')
    def default_status(self):
        s=self.env['request.status'].search([('name','=','Draft')])
        return s
    status = fields.Many2one('request.status','Status',default=default_status)
    pc_received = fields.Boolean('Is Pc received')
    is_deleted = fields.Boolean('Is Deleted')
    remark = fields.Char('Remarks')
    pcr_id = fields.Integer('PCR ID')
    db_id = fields.Integer('DataBase ID')
    request_line = fields.One2many('request.details.line','history_id','Order Details')
    state_id = fields.Many2one('res.country.state','State', store=True, readonly=True,)
    country = fields.Many2one('res.country','Country')
    city = fields.Char('City')
    zip = fields.Char('Code')
    street = fields.Char('Street')
    total  = fields.Float('Total Quantity')
    reason = fields.Char('Reason for Cancellation')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !")
    ]

    @api.onchange('requester')
    def add_address(self):
        obj = self.env['res.users'].browse(self.requester.id)
        self.state_id = obj.partner_id.state_id.id
        self.country = obj.partner_id.country_id.id
        self.city = obj.partner_id.city
        self.zip = obj.partner_id.zip
        self.street = obj.partner_id.street

    @api.onchange('request_line')
    def onchange_total(self):
        for rec in self:
            t=0
            for record in rec.request_line:
                t=t+record.quantity
            rec.total=t
            
    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if vals.get('invite_code', _('New')) == _('New'):
            vals['code'] = self.env['ir.sequence'].next_by_code(
            'request.details') or _('New')      
        res = super(RequestDetailsHistory,self).create(vals)
        cur.execute("""insert into plastic_credit_request_details_history
                (requester,name,user_id,quantity_type,category,region,pc_type,status,action_by,pc_received,is_deleted,status_remark,pcr_history_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                (res.requester.id,res.name,res.create_uid.id,res.quantity_type,res.category_id.id or 0,res.region.id or 0,res.pc_type.id or 0 ,res.status.id or 0,res.create_uid.id,res.pc_received,res.is_deleted,res.remark,res.id))
        cur.execute('''select id from plastic_credit_request_details_history where pcr_history_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        manager = self.env['res.groups'].search([('name','=','Manager')])
        manager_id=[]
        manag_id = manager.users
        for rec in manager.users:
            manager_id.append(rec.partner_id.id)
        context=dict(self.env.context)
        context.update({'ids':res.id})
        self.env.context = context
        temp_id = self.env.ref('plastic_credit.approve_plastic_request_history_mail_template')
        temp_id.with_context(self.env.context).send_mail(self.id, force_send=True,email_values={
                        'recipient_ids': [(6,0, manager_id)]})
        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'quantity' in vals.keys():
            rec = [vals['quantity'],self.id]
            query = """Update plastic_credit_request_details_history set quantity = %s where pcr_history_id = %s"""
            cur.execute(query,rec)
        if 'status' in vals.keys():
            status_id = self.env['request.status'].browse(vals['status'])
            if self.status.name=='Done':
                raise ValidationError(_('''You can't Change status Once it  is Done'''))
            if status_id.name =='Cancelled':
                if self.reason == False:
                    raise ValidationError(_('Please Enter reason details'))
                else:
                    temp_id = self.env.ref('plastic_credit.cancel_plastic_history_request_mail_template')
                    temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
            if status_id.name == 'InProgress':
                temp_id = self.env.ref('plastic_credit.inprocess_plastic_request_history_mail_template')
                temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)

            elif status_id.name == 'Done':
                report = self.env.ref('plastic_credit.request_history_pdf_report')._render_qweb_pdf(self.id)
                attachment=self.env['ir.attachment'].create({
                'name': 'customer_history',
                'type': 'binary',
                'datas': base64.b64encode(report[0]),
                'res_model': 'request.details.history',
                'res_id': self.id,
                'mimetype': 'application/x-pdf'
                })
                temp_id = self.env.ref('plastic_credit.done_plastic_request_history_mail_template')
                temp_id.with_context(self.env.context).send_mail(self.id, force_send=True,email_values={
                        'attachment_ids': [(4,attachment.id)]})          
        conn.commit()
        cur.close()
        res = super(RequestDetailsHistory,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM plastic_credit_request_details_history WHERE pcr_history_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(RequestDetailsHistory, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select pcr_history_id,name from plastic_credit_request_details_history''')
            all_data= cur.fetchall()
            db_id=[]
            db_name = []
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    cur.execute("""insert into plastic_credit_request_details_history
                    (requester,name,user_id,quantity_type,category,region,pc_type,status,action_by,pc_received,is_deleted,status_remark,pcr_history_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                    (rec.requester.id,rec.name,rec.create_uid.id,rec.quantity_type,rec.category_id.id or 0,rec.region.id or 0,rec.pc_type.id or 0,rec.status.id or 0,rec.create_uid.id or 0,rec.pc_received,rec.is_deleted,rec.remark,rec.id))
                elif rec.id in db_id: 
                    cur.execute('''select id,name from plastic_credit_request_details_history where pcr_history_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE plastic_credit_request_details_history set name={} WHERE pcr_history_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))


    
