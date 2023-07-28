from odoo.exceptions import ValidationError
import psycopg2
from odoo import api, fields, models, tools, _
import sys


class DatabaseConnection(models.Model):
    _name = 'data.connection'
    _description = 'Main Data Connection Check' 

    name = fields.Char('Link/URL')
    database_name = fields.Char('Database Name')
    user = fields.Char('User')
    password = fields.Char('Password')
    is_active = fields.Boolean('Active')
    is_connect = fields.Boolean('Is Connected',default=False)
    table = fields.Selection([('settings','Settings'),
    ('user_invitaton','User Invitation'),('user_invitation_status','User Invitation Status'),
    ('user_wallet','User Wallet'),('materials','Materials'),
    ('plastic_credit_request_details','Plastic Credit Request Details'),
    ('plastic_credit_request_details_status','Plastic credit Request Details status'),
    ('plastic_credit_type','Plastic Credit Type'),
    ('plastic_credit_request_details_history','Plastic  Credit Request Details History'),
    ('user','User'),('user_company','User Company'),('country','Country'),
    ('state','State'),('document_details','Document Details')])
    match_id =fields.Many2many('match.data','data_id',string='Matched Data')
    unmatch_id  = fields.Many2many('unmatch.data',string='Unmatched Data')

    def set_unmatched_data(self):
        conn = self.connection()
        cur = conn.cursor()
        for rec in self.unmatch_id:
            if self.table =='settings':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE settings set key=%s WHERE setting_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj=self.env['user.setting'].browse(rec.odoo_id)
                            obj.write({'key':rec.name})
                    else:
                        cur.execute('''UPDATE settings set setting_id=%s WHERE key=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from settings where setting_id={}'''.format(rec.db_id))
                    else:
                        self.env['user.setting'].create({'key':rec.name})
                elif rec.odoo_name:
                    obj=self.env['user.setting'].browse(rec.odoo_id)
                    if rec.convert_type == True:
                        cur.execute("""insert into settings
                            (key,value,description,data_type,setting_id) VALUES (%s,%s,%s,%s,%s)""",(obj.key,obj.value,obj.description,obj.data_type,obj.id))
                    else:
                        obj.unlink()     

            elif self.table=='materials':           
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE materials set name=%s WHERE material_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            record = self.env['plastic.materials'].browse(rec.odoo_id)
                            record.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE materials set material_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from materials where material_id={}'''.format(rec.db_id))
                    else:
                        self.env['plastic.materials'].create({'name':rec.name})
                elif rec.odoo_name:
                    obj=self.env['plastic.materials'].browse(rec.odoo_id)
                    if rec.convert_type == True:
                        cur.execute("""insert into materials(name,added_by,material_id) VALUES (%s,%s,%s)""",(obj.name,obj.create_uid.id,obj.id))
                    else:
                        obj.unlink()
    
            elif self.table=='user_invitaton':                  
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE user_invitaton set email=%s WHERE user_invitation_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj= self.env['user.invitation'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE user_invitaton set user_invitation_id=%s WHERE email=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from user_invitaton where user_invitation_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select email,expiration_days,status from user_invitaton where user_invitation_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['user.invitation'].create({'name':data[0][0],'email':data[0][0],'expire_days':data[0][1],'status':data[0][2]})
                elif rec.odoo_name:
                    obj= self.env['user.invitation'].browse(rec.odoo_id)
                    if rec.convert_type  == False:
                        obj.unlink()
                    else:
                        cur.execute("""insert into user_invitaton(email,invite_code,invited_by,expiration_days,status,updated_by,user_invitation_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                                (obj.name,obj.invite_code,obj.create_uid.id,obj.expire_days,obj.status.id,obj.create_uid.id,obj.id))
                        
            elif self.table=='user_company':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE user_company set company_name=%s WHERE company_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj= self.env['res.company'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE user_company set company_id=%s WHERE company_name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name: 
                    if rec.convert_type==True:
                        cur.execute('''delete from user_company where company_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name from user_company where company_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['res.company'].create({'name':data[0][0]})
                elif rec.odoo_name:
                    if rec.convert_type == True:
                        cur.execute("""insert into user_company(company_id,company_name) VALUES (%s,%s)""",(rec.odoo_id,rec.odoo_name))
                    else:
                        self.env['res.company'].browse(rec.odoo_id).unlink()

            elif self.table=='user':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE public.user set user_name=%s WHERE user_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['res.users'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE public.user set user_id=%s WHERE user_name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from public.user where user_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select user_name,email from public.user where user_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['res.users'].create({'name':data[0][0],'login':data[0][1]})
                elif  rec.odoo_name:
                    if rec.convert_type ==True:
                        obj = self.env['res.users'].browse(rec.odoo_id)
                        c=[obj.name,obj.login,obj.id,obj.partner_id.zip or 0,obj.company_id.id or 0,obj.country_id.id or 0]
                        query = """insert into public.user(user_name,
                        email,user_id,zip_code,company_id,country_id) 
                        VALUES (%s,%s,%s,%s,%s,%s)"""
                        cur.execute(query,c)
                    else:
                        self.env['res.users'].browse(rec.odoo_id).unlink()

            elif self.table=='user_invitation_status':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE user_invitation_status set name=%s WHERE invitation_status_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['invitation.status'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE user_invitation_status set invitation_status_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from user_invitation_status where invitation_status_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name from user_invitation_status where invitation_status_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['invitation.status'].create({'name':data[0][0]})
                elif rec.odoo_name:
                    if rec.convert_type == True:
                        cur.execute("""insert into user_invitation_status(name,invitation_status_id) VALUES (%s,%s)""",
                            (rec.odoo_name,rec.odoo_id))
                    else:
                        self.env['invitation.status'].browse(rec.odoo_id).unlink()
                
            elif self.table=='plastic_credit_request_details_status':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE plastic_credit_request_status set name=%s WHERE request_status_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['request.status'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE plastic_credit_request_status set request_status_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from plastic_credit_request_status where request_status_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name from plastic_credit_request_status where request_status_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['request.status'].create({'name':data[0][0]})
                elif rec.odoo_name:
                    if rec.convert_type==True:
                        obj = self.env['request.status'].browse(rec.odoo_id)
                        cur.execute("""insert into plastic_credit_request_status(name,request_status_id) VALUES (%s,%s)""",(rec.odoo_name,rec.odoo_id))
                    else:
                        self.env['request.status'].browse(rec.odoo_id).unlink()
                        
            elif self.table=='country':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE country set name=%s WHERE country_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['res.country'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE country set country_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type==True:
                        cur.execute('''delete from country where country_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name from country where country_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['res.country'].create({'name':data[0][0]})
                elif rec.odoo_name:
                    obj = self.env['res.country'].browse(rec.odoo_id)
                    if rec.convert_type == True:
                        cur.execute("""insert into country
                        (name,phone_code,country_code,country_id) VALUES (%s,%s,%s,%s)""",
                        (obj.name,obj.phone_code,obj.code,obj.id))
                    else:
                        obj.unlink()
                
            elif self.table=='state':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type == True:
                            cur.execute('''UPDATE state set name=%s WHERE state_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj=self.env['res.country.state'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE state set state_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from state where state_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name from state where state_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['res.country.state'].create({'name':data[0][0]})
                elif rec.odoo_name:
                    obj=self.env['res.country.state'].browse(rec.odoo_id)
                    if rec.convert_type== True:
                        query = """insert into state(state_id,name,
                            country_id) 
                            VALUES (%s,%s,%s)"""
                        cur.execute(query,(obj.id,obj.name,obj.country_id.id))
                    else:
                        self.env['res.country.state'].browse(rec.odoo_id).unlink()

            elif self.table=='plastic_credit_type':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type== True:
                            cur.execute('''UPDATE plastic_credit_type set name=%s WHERE type_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['pc.type'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE plastic_credit_type set type_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from plastic_credit_type where type_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name from plastic_credit_type where type_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['pc.type'].create({'name':data[0][0]})                
                elif rec.odoo_name:
                    obj = self.env['pc.type'].browse(rec.odoo_id)
                    if rec.convert_type == True:
                        cur.execute("""insert into plastic_credit_type(name,is_active,type_id) VALUES (%s,%s,%s)""",(obj.name,obj.is_active,obj.id))
                    else:
                        obj.unlink()

            elif self.table=='plastic_credit_request_details':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type== True:
                            cur.execute('''UPDATE plastic_credit_request_details set pc_request_details=%s WHERE request_details_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['request.details'].browse(rec.odoo_id)
                            obj.write({'request_details':rec.name})
                    else:
                        cur.execute('''UPDATE plastic_credit_request_details set request_details_id=%s WHERE pc_request_details=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from plastic_credit_request_details where request_details_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select pc_request_details,action_by,status,requester from plastic_credit_request_details where request_details_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['request.details'].create({'request_details':data[0][0],'action_by':data[0][1],'status':data[0][2],'name':data[0][3] or 0})
                elif rec.odoo_name:
                    obj = self.env['request.details'].browse(rec.odoo_id)
                    if rec.convert_type == True:               
                        cur.execute("""insert into plastic_credit_request_details
                        (pc_request_details,status,action_by,is_pc_received,request_details_id,requester) VALUES (%s,%s,%s,%s,%s,%s)""",
                        (obj.request_details,obj.status.id,obj.create_uid.id,obj.pc_received,obj.id,obj.name.id or 0))
                    else:
                        obj.unlink()
            elif self.table == 'plastic_credit_request_details_history':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type== True:
                            cur.execute('''UPDATE plastic_credit_request_details_history set name=%s WHERE pcr_history_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['request.details.history'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE plastic_credit_request_details_history set pcr_history_id=%s WHERE name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from plastic_credit_request_details_history where pcr_history_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select name,status,category,region,requester from plastic_credit_request_details_history where pcr_history_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['request.details.history'].create({'name':data[0][0],'status':data[0][1],'category_id':data[0][2],'region':data[0][3],'requester':data[0][4]})
                elif rec.odoo_name:
                    obj = self.env['request.details.history'].browse(rec.odoo_id)
                    if rec.convert_type == True:               
                        cur.execute("""insert into plastic_credit_request_details_history
                        (name,status,action_by,category,region,pcr_history_id,requester) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (obj.name,obj.status.id,obj.create_uid.id,obj.pc_received,obj.category.id,obj.region.id,obj.id,obj.requester.id))
                    else:
                        obj.unlink()

            elif self.table=='user_wallet':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type:
                            cur.execute('''UPDATE user_wallet set wallet_address=%s WHERE wallet_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj= self.env['user.wallet'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE user_wallet set wallet_id=%s WHERE wallet_address=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from user_wallet where wallet_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select wallet_address,private_key,wallet_password from user_wallet where wallet_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['user.wallet'].create({'name':data[0][0],'private_key':data[0][1],'wallet_password':data[0][2]})
                elif rec.odoo_name:
                    obj= self.env['user.wallet'].browse(rec.odoo_id)
                    if rec.convert_type == True:
                        cur.execute("""insert into user_wallet
                        (user_id,wallet_address,private_key,wallet_password,wallet_balance,uncleared_balance,wallet_id) VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                        (obj.create_uid.id,obj.name,obj.private_key,obj.wallet_password,obj.wallet_balance,obj.uncleared_balance,obj.id))
                    else:
                        obj.unlink()
        
            elif self.table=='document_details':
                if rec.name and rec.odoo_name:
                    if rec.db_id == rec.odoo_id:
                        if rec.convert_type==True:
                            cur.execute('''UPDATE document_details set document_name=%s WHERE document_id=%s''',(rec.odoo_name,rec.odoo_id))
                        else:
                            obj = self.env['ir.attachment'].browse(rec.odoo_id)
                            obj.write({'name':rec.name})
                    else:
                        cur.execute('''UPDATE document_details set document_id=%s WHERE document_name=%s''',(rec.odoo_id,rec.odoo_name))
                elif rec.name:
                    if rec.convert_type == True:
                        cur.execute('''delete from document_details where document_id={}'''.format(rec.db_id))
                    else:
                        cur.execute('''select document_name,document_type from document_details where document_id={}'''.format(rec.db_id))
                        data = cur.fetchall()
                        self.env['ir.attachment'].create({'name':data[0][0],'type':data[0][1]})
                elif rec.odoo_name:
                    obj = self.env['ir.attachment'].browse(rec.odoo_id)
                    if rec.convert_type == True:
                        query="""insert into document_details(document_id,document_name,document_type) VALUES (%s,%s,%s)"""
                        cur.execute(query,(obj.id,obj.name,obj.type))
                    else:
                        obj.unlink()
        self.compare_tables()
        conn.commit()
        cur.close()

    @api.model
    def create(self,vals):
        s=self.env['data.connection'].search([])
        l=[]
        for rec in s:
            if rec.is_active:
                l.append(rec.id)
        if vals['is_active']==True:
            if len(l)>1:
                raise ValidationError(_("one database already active"))  
        res = super(DatabaseConnection,self).create(vals)
        return res
    
    def write(self,vals):
        s=self.env['data.connection'].search([])
        l=[]
        for rec in s:
            if rec.is_active:
                l.append(rec.id)
        if 'is_active' in vals:
            if vals['is_active'] ==True:
                if len(l)>=1:
                    raise ValidationError(_("one database already active")) 
        res = super(DatabaseConnection,self).write(vals)
        return res

    def is_connected(self):
        try:
            conn=psycopg2.connect(
            host=self.name,
            database=self.database_name,
            user=self.user,
            password=self.password)
            self.is_connect =True
            if conn:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                    'title': ('Connection Test Successfully'),
                    'message': ('Connected'),
                    'sticky': False,
                    },
                }
        except Exception as e:
            self.write({'is_connect':False})
            return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _(str(e)),
                'type': 'danger',
                'sticky': False,
            },
        }
            
    def reload(self):
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def connection(self):
        try:
            data=self.env['data.connection'].search([('is_active','=',True)])
            if data:
                conn=psycopg2.connect(host=data.name,
                database=data.database_name,user=data.user,
                password=data.password)
                return conn
            else:
                raise ValidationError(_('Sorry not active Database'))
        except:
            datas = self.env['data.connection'].search([])
            if datas:
                raise ValidationError(_('Sorry not active Database'))
            else:
                s=self.env['data.connection'].create({'name':'localhost',
                'database_name':'plastic_credit','user':'odoo14',
                'password':'odoo14','is_active':True})

                conn=psycopg2.connect(host=s.name,
                    database=s.database_name,user=s.user,
                    password=s.password)
                return conn

        
    def compare_tables(self):
        conn = self.connection()
        cur = conn.cursor()
        self.env['match.data'].search([]).unlink()
        self.env['unmatch.data'].search([]).unlink()
        try:
            if self.table=='plastic_credit_type':
                cur.execute("""select name,type_id from plastic_credit_type""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['pc.type'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from plastic_credit_type where type_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from plastic_credit_type where type_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select type_id from plastic_credit_type where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()      
            
            elif self.table=='plastic_credit_request_details_status':    
                cur.execute("""select name,request_status_id from plastic_credit_request_status""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['request.status'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from plastic_credit_request_status where request_status_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from plastic_credit_request_status where request_status_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select request_status_id from plastic_credit_request_status where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()   
                
            elif self.table=='plastic_credit_request_details':    
                cur.execute("""select pc_request_details,request_details_id from plastic_credit_request_details""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['request.details'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.request_details)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select pc_request_details from plastic_credit_request_details where request_details_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select pc_request_details from plastic_credit_request_details where request_details_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.request_details==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.request_details,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.request_details})
                    else:
                        if rec.request_details in d_name:
                            cur.execute('''select request_details_id from plastic_credit_request_details where pc_request_details=%s''',(rec.request_details,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.request_details,'name':rec.request_details,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.request_details})
                self.create_unmatch()

            elif self.table=='plastic_credit_request_details_history':    
                cur.execute("""select name,pcr_history_id from plastic_credit_request_details_history""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['request.details.history'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from plastic_credit_request_details_history where pcr_history_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from plastic_credit_request_details_history where pcr_history_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select pcr_history_id from plastic_credit_request_details_history where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='user_invitaton':    
                cur.execute("""select email,user_invitation_id from user_invitaton""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['user.invitation'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select email from user_invitaton where user_invitation_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select email from user_invitaton where user_invitation_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select user_invitation_id from user_invitaton where email=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='user_invitation_status':    
                cur.execute("""select name,invitation_status_id from user_invitation_status""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['invitation.status'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from user_invitation_status where invitation_status_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from user_invitation_status where invitation_status_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select invitation_status_id from user_invitation_status where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.key})
                self.create_unmatch()

            elif self.table=='user_wallet':    
                cur.execute("""select wallet_address,wallet_id from user_wallet""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['user.wallet'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select wallet_address from user_wallet where wallet_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select wallet_address from user_wallet where wallet_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select wallet_id from user_wallet where wallet_address=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='settings':    
                cur.execute("""select key,setting_id from settings""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0]) 
                data_odoo = self.env['user.setting'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.key)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select key from settings where setting_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select key from settings where setting_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.key==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.key,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.key})
                    else:
                        if rec.key in d_name:
                            cur.execute('''select setting_id from settings where key=%s''',(rec.key,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.key,'name':rec.key,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.key})
                self.create_unmatch()

            elif self.table=='user':    
                cur.execute("""select user_name,user_id from public.user""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['res.users'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select user_name from public.user where user_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select user_name from public.user where user_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select user_id from public.user where user_name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='user_company':    
                cur.execute("""select company_name,company_id from user_company""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['res.company'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select company_name from user_company where company_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select company_name from user_company where company_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select company_id from user_company where company_name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='country':    
                cur.execute("""select name,country_id from country""")
                data = cur.fetchall()
                l=[]
                d_name = []
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['res.country'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from country where country_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from country where country_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select country_id from country where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()
            
            elif self.table=='state':    
                cur.execute("""select name,state_id from state""")
                data = cur.fetchall()
                l=[]
                for rec in data:
                    l.append(rec[1])
                    # n.append(rec[0])
                data_odoo = self.env['res.country.state'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from state where state_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from state where state_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select state_id from state where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='document_details':    
                cur.execute("""select document_name,document_id from document_details""")
                data = cur.fetchall()
                l=[]
                d_name=[]
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['ir.attachment'].search([])
                od_id=[]
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select document_name from document_details where document_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select document_name from document_details where document_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select document_id from document_details where document_name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

            elif self.table=='materials':    
                cur.execute("""select name,material_id from materials""")
                data = cur.fetchall()
                l=[]
                d_name=[]
                for rec in data:
                    l.append(rec[1])
                    d_name.append(rec[0])
                data_odoo = self.env['plastic.materials'].search([])
                od_id = []
                od_name = []
                for rec in data_odoo:
                    od_id.append(rec.id)
                    od_name.append(rec.name)
                for record in l:
                    if record not in od_id:
                        cur.execute('''select name from materials where material_id={}'''.format(record))
                        name = cur.fetchall()
                        if name[0][0] not in od_name:
                            self.env['unmatch.data'].create({'db_id':record,'name':name[0][0]})
                for rec in data_odoo:
                    if rec.id in l:
                        cur.execute('''select name from materials where material_id={}'''.format(rec.id))
                        name = cur.fetchall()
                        if rec.name==name[0][0]:
                            self.env['match.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_name':rec.name,'odoo_id':rec.id})
                        else:
                            self.env['unmatch.data'].create({'name':name[0][0],'db_id':rec.id,'odoo_id':rec.id,'odoo_name':rec.name})
                    else:
                        if rec.name in d_name:
                            cur.execute('''select material_id from materials where name=%s''',(rec.name,))
                            data_id = cur.fetchall()
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name,'name':rec.name,'db_id':data_id[0][0]})
                        else:
                            self.env['unmatch.data'].create({'odoo_id':rec.id,'odoo_name':rec.name})
                self.create_unmatch()

        except Exception as e:
            raise ValidationError(_(str(e)))
            
    def create_unmatch(self):
        s=self.env['match.data'].search([])
        ids=[]
        for rec in s:
            ids.append(rec.id)    
        self.write({'match_id':[(6,0,ids)]})
        s=self.env['unmatch.data'].search([])
        ids=[]
        for rec in s:
            ids.append(rec.id)     
        self.write({'unmatch_id':[(6,0,ids)]})



