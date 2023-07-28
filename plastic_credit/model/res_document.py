from odoo import models,fields,api,_
import psycopg2
import config
from odoo.exceptions import ValidationError
from . import database


class ResAttachment(models.Model):

    _inherit = 'ir.attachment'

    db_id = fields.Integer('DB ID')

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        res = super(ResAttachment,self).create(vals)
        query = """insert into document_details(document_id,document_name,
                    document_type) 
                    VALUES (%s,%s,%s)"""
        cur.execute(query,(res.id,res.name,res.type))
        cur.execute('''select id from document_details where document_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close()
        return res


    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if vals:
            if 'datas' in vals.keys():
               res = super(ResAttachment,self).write(vals)
            elif 'name' in vals.keys():
                cur.execute("""Update document_details set document_name = %s where document_id = %s""",(vals['name'],self.id))
        res = super(ResAttachment,self).write(vals)
        conn.commit()
        cur.close()
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM document_details WHERE document_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(ResAttachment, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select document_id,document_name from document_details''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    query="""insert into document_details(document_id,document_name,document_type) VALUES (%s,%s,%s)"""
                    cur.execute(query,(rec.id,rec.name,rec.type))
                elif rec.id in db_id:
                    cur.execute('''select id,document_name from document_details where document_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE document_details set document_name={} WHERE document_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()    
        except Exception as e:
            raise ValidationError(_(str(e)))