from odoo import fields,models,api,_
import psycopg2
from odoo.exceptions import ValidationError
from . import database


class RequestStatus(models.Model):
    _name = 'request.status'
    _order = 'order'
    _description = 'Request Status'

    name = fields.Char('Name')
    order = fields.Integer('Order Sequence')
    is_closed = fields.Boolean('Is Closed')
    db_id = fields.Integer('DataBase ID')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Name already exists !"),
    ]
    
    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        cur.execute('''select name from plastic_credit_request_status''')
        db_name = cur.fetchall()
        d_name = []
        for rec in db_name:
            d_name.append(rec[0])
        res = super(RequestStatus,self).create(vals)
        if res.name not in d_name:

            
            cur.execute("""insert into plastic_credit_request_status(name,request_status_id) VALUES (%s,%s)""",(res.name,res.id))
            cur.execute('''select id from plastic_credit_request_status where request_status_id={}'''.format(res.id))
            ids= cur.fetchall()
            res.db_id = ids[0][0]
        else:
            
            cur.execute('''UPDATE plastic_credit_request_status set request_status_id=%s WHERE name=%s''',(res.id,res.name))

        conn.commit()
        cur.close()   
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'name' in vals.keys():
            rec = [vals['name'],self.id]
            query = """Update plastic_credit_request_status set name = %s where request_status_id = %s"""
            cur.execute(query,rec)
        conn.commit()
        cur.close()
        res = super(RequestStatus, self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM plastic_credit_request_status WHERE request_status_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(RequestStatus, self).unlink()
        return res

    def sync_now(self):
        try:
            conn =database.DatabaseConnection.connection(self)
            cur=conn.cursor()
            cur.execute('''select request_status_id,name from plastic_credit_request_status''')
            all_data= cur.fetchall()
            db_id=[]
            db_name=[]
            for rec in all_data:
                db_id.append(rec[0])
                db_name.append(rec[1])
            for rec in self:
                if rec.id not in db_id and rec.name not in db_name:
                    cur.execute("""insert into plastic_credit_request_status(name,request_status_id) VALUES (%s,%s)""",(rec.name,rec.id))
                elif rec.id in db_id:
                    cur.execute('''select id,name from plastic_credit_request_status where request_status_id={}'''.format(rec.id))
                    ids= cur.fetchall()
                    rec.db_id = ids[0][0]
                    if rec.name != ids[0][1]:
                        cur.execute('''UPDATE plastic_credit_request_status set name={} WHERE request_status_id={}'''.format(rec.name,rec.id))
            conn.commit()
            cur.close()
        except Exception as e:
            raise ValidationError(_(str(e)))

