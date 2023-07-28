from odoo import models, fields, api,_
import psycopg2
import config
from odoo.exceptions import ValidationError
from . import database


class ResCompany(models.Model):
    _inherit = 'res.company'

    db_id = fields.Integer('DB ID')

    @api.model
    def create(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()     
        comp=[]
        comp.append(vals['name'])
        res = super(ResCompany,self).create(vals)
        cur.execute("""insert into user_company(company_id,company_name) VALUES (%s,%s)""",(res.id,res.name))
        cur.execute('''select id from user_company where company_id={}'''.format(res.id))
        ids= cur.fetchall()
        res.db_id = ids[0][0]
        conn.commit()
        cur.close() 
        return res
        
    def write(self,vals):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        if 'resource_calendar_id' in vals.keys():
            pass
        elif 'name' in vals.keys():
            rec = [vals['name'],self.id]
            query = """Update user_company set company_name = %s where company_id = %s"""
            cur.execute(query,rec)    
        conn.commit()
        cur.close()
        res = super(ResCompany,self).write(vals)
        return res

    def unlink(self):
        conn =database.DatabaseConnection.connection(self)
        cur = conn.cursor()
        for rec in self:
            cur.execute("""DELETE FROM user_company WHERE company_id={}""".format(rec.id))
        conn.commit()
        cur.close()
        res = super(ResCompany, self).unlink()
        return res

    def sync_now(self):
        conn =database.DatabaseConnection.connection(self)
        cur=conn.cursor()
        cur.execute('''select company_id,company_name from user_company''')
        all_data= cur.fetchall()
        db_id=[]
        db_name=[]
        for rec in all_data:
            db_id.append(rec[0])
            db_name.append(rec[1])
        for rec in self:
            if rec.id not in db_id and rec.name not in db_name:
                cur.execute("""insert into user_company(company_id,company_name) VALUES (%s,%s)""",(rec.id,rec.name))
            elif rec.id in db_id:
                cur.execute('''select id,company_name from user_company where company_id={}'''.format(rec.id))
                ids= cur.fetchall()
                rec.db_id = ids[0][0]
                if rec.name != ids[0][1]:
                    cur.execute('''UPDATE user_company set company_name={} WHERE company_id={}'''.format(rec.name,rec.id))
        conn.commit()
        cur.close()

    def delete_company(self):
        datac= self.data_connection()
        cur = datac.cursor()
        for rec in self:
            cur.execute('''delete from ir_property where company_id = {}'''.format(rec.id))
            datac.commit()       
            arc=self.env['stock.rule'].sudo().search([('company_id','=',rec.id),'|',('active','=',False),('active','=',True)])
            arc.unlink()
            st_pick=self.env['stock.picking.type'].sudo().search([('company_id','=',rec.id),'|',('active','=',False),('active','=',True)])
            st_pick.unlink()
            st_war=self.env['stock.warehouse'].sudo().search([('company_id','=',rec.id)])
            st_war.unlink()
            rec.unlink()
        cur.close()
        # for rec in self:
        #     cur.execute('''delete from ir_property where company_id = {}'''.format(rec.id))
        #     datac.commit()
            # cur.execute('''delete from stock_rule where company_id = {}'''.format(rec.id))
            # datac.commit()        
            # cur.execute('''delete from stock_picking_type where company_id = {}'''.format(rec.id))
            # datac.commit() 
            # cur.execute('''delete from stock_warehouse where company_id = {}'''.format(rec.id))
            # datac.commit()          
            # cur.execute('''delete from res_company where id = {}'''.format(rec.id))
            # datac.commit()
        # cur.close

    def data_connection(self):
        data_conn=psycopg2.connect(host='localhost',
                database='plastic_test03',user='odoo14',
                password='odoo14')
        return data_conn
    