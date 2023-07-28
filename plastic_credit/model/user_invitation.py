from odoo import fields, models, api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database
import re


class UserInvitation(models.Model):
    _name  = 'user.invitation'
    _inherit = ['mail.thread','mail.activity.mixin']
    _description = 'User Invitation'

    name = fields.Char('Name')
    email = fields.Char('Email')
    invite_code = fields.Char('Invite Code', required=True,
                          readonly=True, default=lambda self: _('New'))
    expire_days = fields.Integer('Expiration Days', default=7)
    def state(self):
        s=self.env['invitation.status'].search([('name','=','Draft')])
        return s
    status = fields.Many2one('invitation.status','Status',default=state)
    user_type  = fields.Selection([('individual','Individual'),('company','Company')])
    db_id = fields.Integer('DataBase ID')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !")]
        
    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        s=self.env['user.invitation'].search([])
        list=[]
        for rec in s:
            list.append(rec.email)
        if vals['email'] in list:
            raise ValidationError(_("Email already exists"))     
        else:
            if vals.get('invite_code', _('New')) == _('New'):
                vals['invite_code'] = self.env['ir.sequence'].next_by_code(
                'user.invitation') or _('New')
        match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', vals['email'])
        if match == None:
            raise ValidationError(_('Not a valid E-mail ID'))
        res = super(UserInvitation,self).create(vals)
        if res.user_type == 'company':
            cur.execute("""insert into user_invitaton(email,invite_code,invited_by,expiration_days,status,updated_by,user_invitation_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (res.name,res.invite_code,res.create_uid.id,res.expire_days,res.status.id,res.create_uid.id,res.id))
            comp_id = self.env['res.company'].create({'name':res.name})
            if res.status.name == 'Done':
                yc=self.env['res.company'].search([('name','=','YourCompany')])
                ids = [comp_id.id,yc.id]
                user_id = self.env['res.users'].create({'name':res.name,'login':res.email})
                user_id.write({'company_ids':[(6, 0, ids)],'company_id':comp_id.id})
                user_id.partner_id.write({'company_type':'company'})
        else:
            cur.execute("""insert into user_invitaton(email,invite_code,invited_by,expiration_days,status,updated_by,user_invitation_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (res.name,res.invite_code,res.create_uid.id,res.expire_days,res.status.id,res.create_uid.id,res.id))
        cur.execute('''select id from user_invitaton where user_invitation_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        yc=self.env['res.company'].search([('name','=','YourCompany')])
        comp_user = self.env['res.company'].search([('name','=',self.name)])
        if 'name' in vals.keys():
            rec = [vals['name'],self.id]
            query = """Update user_invitaton set email = %s where user_invitation_id = %s"""
            cur.execute(query,rec)
        elif 'status' in vals.keys():
            s=self.env['invitation.status'].browse(vals['status'])
            if self.status.name=='done' or self.status.name=='Done':
                raise ValidationError(_("you can't change status once done"))
            elif s.name=='done' or s.name=='Done':
                users= self.env['res.users'].create({'name':self.name,'login':self.email})
                if self.user_type == 'company':
                    comp_ids=self.env['res.company'].search([('name','=',self.name)])
                    ids = [comp_ids.id or 0,yc.id]
                    users.partner_id.write({'company_type':'company'})
                    users.write({'company_ids':[(6, 0, ids)],'company_id':comp_ids.id or yc.id})
        elif 'user_type'in vals:
            if vals['user_type']=='company':
                comp_id=self.env['res.company'].create({'name':self.name})
                user=self.env['res.users'].search([('name','=',self.name)])
                ids = [comp_id.id,yc.id]
                if self.status.name == 'Done':
                    user.write({'company_ids':[(6, 0, ids)],'company_id':comp_id.id})
                    user.partner_id.write({'company_type':'company'})   
        conn.commit()
        cur.close()
        res = super(UserInvitation,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM user_invitaton WHERE user_invitation_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(UserInvitation, self).unlink()
        return res

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

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select user_invitation_id,email from user_invitaton''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name  not in db_name:
                    cur.execute("""insert into user_invitaton(email,invite_code,invited_by,expiration_days,status,updated_by,user_invitation_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (rec.name,rec.invite_code,rec.create_uid.id,rec.expire_days,rec.status.id,rec.create_uid.id,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,email from user_invitaton where user_invitation_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE user_invitaton set email={} WHERE user_invitation_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()

        except Exception as e:
            raise ValidationError(_(str(e)))


