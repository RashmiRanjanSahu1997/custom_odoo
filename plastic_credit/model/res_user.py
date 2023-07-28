from odoo import models, fields, api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class ResUser(models.Model):
    _inherit = 'res.users'

    db_id = fields.Integer('DB ID')

    @api.model
    def create(self, vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        res = super(ResUser,self).create(vals)
        c=[res.name,res.login,res.id,res.partner_id.zip or 0,res.partner_id.id or 0,5]
        query = """insert into public.user(user_name,
            email,user_id,zip_code,company_id,country_id) 
            VALUES (%s,%s,%s,%s,%s,%s)"""
        cur.execute(query,c)
        cur.execute('''select id from public.user where user_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        res.partner_id.email = res.login
        
        conn.commit()
        cur.close()
        return res

    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'company_ids' in vals.keys():
            pass
        elif 'login' in vals.keys()  and 'name' in vals.keys():
            cur.execute("""Update public.user set user_name = %s,email=%s where user_id = %s""",(vals['name'],vals['login'],self.id))  
        elif 'login' in vals.keys():
            cur.execute("""Update public.user set email = %s where user_id = %s""",(vals['login'],self.id))
        elif 'name' in vals.keys():
            cur.execute("""Update public.user set user_name= %s where user_id = %s""",(vals['name'],self.id))
        conn.commit()
        cur.close()
        res = super(ResUser,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur=conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM public.user WHERE user_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(ResUser, self).unlink()
        return res

    def sync_now(self):
        # try:
        conn =database.DatabaseConnection.connection(self)
        cur=conn.cursor()
        cur.execute('''select user_id,user_name from public.user''')
        all_data= cur.fetchall()
        db_id=[]
        db_name=[]
        for rec in all_data:
            db_id.append(rec[0])
            db_name.append(rec[1])
        for rec in self:
            if rec.id not in db_id and rec.name not in db_name:
                c=[rec.name,rec.login,rec.id,rec.partner_id.zip or 0,rec.company_id or 0,rec.country_id or 0]
                query = """insert into public.user(user_name,
                email,user_id,zip_code,company_id,country_id) 
                VALUES (%s,%s,%s,%s,%s,%s)"""
                cur.execute(query,c)
            elif rec.id in db_id:
                cur.execute('''select id,user_name from public.user where user_id={}'''.format(rec.id))
                ids= cur.fetchall()
                rec.db_id = ids[0][0]
                if rec.name != ids[0][1]:
                    cur.execute('''UPDATE public.user set user_name={} WHERE user_id={}'''.format(rec.name,rec.id))
        conn.commit()
        cur.close()
        # except Exception as e:
        #     raise ValidationError(_(str(e)))




        
        

        