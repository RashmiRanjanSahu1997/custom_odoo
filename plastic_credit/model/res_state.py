from odoo import models,fields,api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class ResState(models.Model):

    _inherit = 'res.country.state'

    db_id = fields.Integer('DB ID')

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        res = super(ResState,self).create(vals)
        query = """insert into state(state_id,name,
                    country_id) 
                    VALUES (%s,%s,%s)"""
        cur.execute(query,(res.id,res.name,res.country_id.id))
        cur.execute('''select id from state where state_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()
        return res


    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'name' in vals.keys():
            cur.execute("""Update state set name = %s where state_id = %s""",(vals['name'],self.id))
        res = super(ResState,self).write(vals)
        conn.commit()
        cur.close()
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM state WHERE id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(ResState, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select state_id,name from state''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    query = """insert into state(state_id,name,
                        country_id) 
                        VALUES (%s,%s,%s)"""
                    cur.execute(query,(rec.id,rec.name,rec.country_id.id))
                elif rec.id in db_id:
                    cur.execute('''select id,name from state where state_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE state set name={} WHERE state_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close() 
        except Exception as e:
            raise ValidationError(_(str(e)))