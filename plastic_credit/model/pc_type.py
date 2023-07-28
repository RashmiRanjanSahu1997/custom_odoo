from odoo import fields, models, api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class PlasticCreditType(models.Model):
    _name = 'pc.type'
    _description = 'Pc Type'
    
    name = fields.Char('Name')
    is_active = fields.Boolean('Is Active')
    db_id = fields.Integer('DataBase ID')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
    ]

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        cur.execute('''select name from plastic_credit_type''')
        db_name = cur.fetchall()
        d_name = []
        for rec in db_name:
            d_name.append(rec[0])
        res = super(PlasticCreditType,self).create(vals)     
        if res.name not in d_name:   
            cur.execute("""insert into plastic_credit_type(name,is_active,type_id) VALUES (%s,%s,%s)""",(res.name,res.is_active,res.id))
            cur.execute('''select id from plastic_credit_type where type_id={}'''.format(res.id))
            ids= cur.fetchall()
            res.db_id = ids[0][0]
        else:
            cur.execute('''UPDATE plastic_credit_type set type_id=%s WHERE name=%s''',(res.id,res.name))
        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'name' in vals.keys():
            rec = [vals['name'],self.id]
            query = """Update plastic_credit_type set name = %s where type_id = %s"""
            cur.execute(query,rec)
        conn.commit()
        cur.close()
        res = super(PlasticCreditType,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM plastic_credit_type WHERE type_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(PlasticCreditType, self).unlink()
        return res

    def sync_now(self):
        try:

            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select type_id,name from plastic_credit_type''')
            all_data= cur.fetchall()
            db_id=[]
            db_name = []
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    cur.execute("""insert into plastic_credit_type(name,is_active,type_id) VALUES (%s,%s,%s)""",(rec.name,rec.is_active,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,name from plastic_credit_type where type_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE plastic_credit_type set name={} WHERE type_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))

