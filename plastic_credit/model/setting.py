from odoo import fields, models,api,_
import psycopg2
from odoo.exceptions import UserError, ValidationError
from . import database


class UserSetting(models.Model):
    _name = 'user.setting'
    _description ='User Setting'

    key = fields.Char('Key')
    value = fields.Char('Value')
    description = fields.Char('Description')
    data_type = fields.Char('Data Type')
    db_id = fields.Integer('DataBase ID')
    
    _sql_constraints = [
        ('name_uniq', 'unique (key)', "Name already exists !"),
    ]

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()     
        res = super(UserSetting, self).create(vals)
        cur.execute("""insert into settings
                (key,value,description,data_type,setting_id) VALUES (%s,%s,%s,%s,%s)""",
                (res.key,res.value,res.description,res.data_type,res.id))

        cur.execute('''select id from settings where setting_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'key' in vals.keys() and 'value' in vals.keys():
            rec = [vals['key'],vals['value'],self.id]
            query = """Update settings set key = %s,value=%s where setting_id = %s"""
            cur.execute(query,rec)
        conn.commit()
        cur.close()
        res = super(UserSetting, self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM settings WHERE setting_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(UserSetting, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select setting_id,key from settings''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.key not in db_name:
                    cur.execute("""insert into settings
                    (key,value,description,data_type,setting_id) VALUES (%s,%s,%s,%s,%s)""",
                    (rec.key,rec.value,rec.description,rec.data_type,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,key from settings where setting_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.key != ids[0][1]:
                        cur.execute('''UPDATE settings set key=%s WHERE setting_id=%s''',(rec.key,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))
            
       