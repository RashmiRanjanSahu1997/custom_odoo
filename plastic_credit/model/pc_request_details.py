from odoo import models,fields,api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class RequestDetails(models.Model):
    _name = 'request.details'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'Request Details'

    name = fields.Many2one('res.users','Name')
    request_details = fields.Char('Request Details')
    action_by = fields.Many2one('res.users','Action By')
    pc_received = fields.Boolean('Is Pc received')
    def state(self):
        s=self.env['request.status'].search([('name','=','Draft')])
        return s.id
    status = fields.Many2one('request.status','Status',default=state)
    code = fields.Char('Request Code',required=True,
                          readonly=True, default=lambda self: _('New'))
    activity_ids = fields.Many2one('mail.activity','activity_ids')
    db_id = fields.Integer('DataBase ID')

    _sql_constraints = [
        ('request_details_uniq', 'unique (request_details)', "Name already exists !"),
    ]

    @api.model
    def create(self,vals):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur = conn.cursor()
            if vals.get('invite_code', _('New')) == _('New'):
                vals['code'] = self.env['ir.sequence'].next_by_code(
                'request.details') or _('New')     
            res = super(RequestDetails,self).create(vals)
            cur.execute("""insert into plastic_credit_request_details
                    (requester,pc_request_details,status,action_by,is_pc_received,request_details_id) VALUES (%s,%s,%s,%s,%s,%s)""",
                    (res.name.id,res.request_details,res.status.id,res.create_uid.id,res.pc_received,res.id))
            cur.execute('''select id from plastic_credit_request_details where request_details_id={}'''.format(res.id))
            ids= cur.fetchall()
            res.db_id = ids[0][0]
            manager = self.env['res.groups'].search([('name','=','Manager')])
            manager_id=[]
            manag_id = manager.users
            for rec in manager.users:
                manager_id.append(rec.partner_id.id)
            context=dict(self.env.context)
            context.update({'ids':res.id,'name':res.name.name})
            self.env.context = context
            print(manager_id)         
            temp_id = self.env.ref('plastic_credit.approve_plastic_request_mail_template')
            temp_id.with_context(self.env.context).send_mail(self.id, force_send=True,email_values={
                        'recipient_ids': [(6,0, manager_id)]})
            # except:
            # cur.execute("""DELETE FROM plastic_credit_request_details WHERE request_details_id={}""".format(res.id))
            conn.commit()
            cur.close()
            return res
        except Exception as e:
            raise ValidationError(_(str(e)))

    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'request_details' in vals.keys():
            rec = [vals['request_details'],self.id]
            query = """Update plastic_credit_request_details set pc_request_details = %s where request_details_id = %s"""
            cur.execute(query,rec)
        elif 'status' in vals.keys():
            s=self.env['request.status'].browse(vals['status'])
            if self.status.name=='Done':
                raise ValidationError(_("you can't change status once done"))
            elif s.name=='Done':
                self.write({'action_by':self.create_uid.id})
                obj = self.env['request.status'].search([('name','=','Draft')])
                self.env['request.details.history'].create({'requester':self.name.id,'name':self.request_details,'pc_received':self.pc_received,'status':obj.id,'state_id':self.name.partner_id.state_id.id,'country':self.name.partner_id.country_id.id,'street':self.name.partner_id.street,'city':self.name.partner_id.city,'zip':self.name.partner_id.zip})
                temp_id = self.env.ref('plastic_credit.done_plastic_request_mail_template')
                temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
            elif s.name == 'Cancelled':
                temp_id = self.env.ref('plastic_credit.cancel_plastic_request_mail_template')
                temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
        conn.commit()
        cur.close()
        res = super(RequestDetails,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM plastic_credit_request_details WHERE request_details_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(RequestDetails, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select request_details_id,pc_request_details from plastic_credit_request_details''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.request_details not in db_name:
                    cur.execute("""insert into plastic_credit_request_details
                    (requester,pc_request_details,status,action_by,is_pc_received,request_details_id) VALUES (%s,%s,%s,%s,%s,%s)""",
                    (rec.name.id,rec.request_details,rec.status.id,rec.create_uid.id,rec.pc_received,rec.id))
                elif rec.id not in db_id:
                    cur.execute('''select id,pc_request_details from plastic_credit_request_details where request_details_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.request_details != ids[0][1]:
                        cur.execute('''UPDATE plastic_credit_request_details_history set pc_request_details={} WHERE request_details_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))

    def preview_sale_order(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url': self.get_portal_url(),
        }

    def get_portal_url(self):
        portal_link = "%s/?db=%s" % (self.env['ir.config_parameter'].sudo().get_param('web.base.url'), self.env.cr.dbname)
        return portal_link

    def preview_req_history(self):
        try:
            return {
                'name': _('Request History'),
                'view_mode': 'tree,form',
                'res_model': 'request.details.history',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('name', '=', self.request_details)],
            }
        except:
            raise ValidationError(_('No record found'))
        
