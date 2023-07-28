from odoo import models,fields,api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class ResCountry(models.Model):

    _inherit = 'res.country'

    db_id = fields.Integer('DB ID')

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()     
        res = super(ResCountry,self).create(vals)
        cur.execute("""insert into country
                (name,phone_code,country_code,country_id) VALUES (%s,%s,%s,%s)""",
                (res.name,res.phone_code,res.code,res.id))
        cur.execute('''select id from country where country_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()   
        return res

    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'name' in vals.keys():
            cur.execute("""Update country set name = %s where id = %s""",(vals['name'],self.id))
        res = super(ResCountry,self).write(vals)
        conn.commit()
        cur.close()
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM country WHERE id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(ResCountry, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select country_id,name from country''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    cur.execute("""insert into country
                    (name,phone_code,country_code,country_id) VALUES (%s,%s,%s,%s)""",
                    (rec.name,rec.phone_code,rec.code,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,name from country where country_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE country set name={} WHERE country_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))



            