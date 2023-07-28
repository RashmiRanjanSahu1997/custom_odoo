from odoo import fields, models,api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class Materials(models.Model):
    _name = 'plastic.materials'
    _description = 'Plastic Materials'
    
    name = fields.Char('Name')
    db_id = fields.Integer('DataBase ID')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
    ]

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur=conn.cursor() 
        res = super(Materials,self).create(vals)
        cur.execute("""insert into materials(name,added_by,material_id) VALUES (%s,%s,%s)""",(res.name,res.create_uid.id,res.id))
        cur.execute('''select id from materials where material_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'name' in vals.keys():
            rec = [vals['name'],self.id]
            query = """Update materials set name = %s where material_id = %s"""
            cur.execute(query,rec)
        conn.commit()
        cur.close()
        res = super(Materials,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM materials WHERE material_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(Materials, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select material_id,name from materials''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    cur.execute("""insert into materials(name,added_by,material_id) VALUES (%s,%s,%s)""",(rec.name,rec.create_uid.id,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,name from materials where material_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE materials set name={} WHERE material_id={}'''.format(str(rec.name),rec.id))
            conn.commit()
            cur.close() 
        except Exception as e:
            raise ValidationError(_(str(e)))
