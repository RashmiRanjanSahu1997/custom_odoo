from odoo import http, _
from odoo.http import request
import psycopg2



class PlasticCredit(http.Controller):

    #api for user import in database 
    @http.route(['/create/db/user'], type='http',methods=['POST'], auth='public', csrf=False)
    def main_menu_user(self, **kw):
        user = request.env['res.users'].sudo().search([('active','=',True)])
        total= []
        conn = self.connection()
        cur=conn.cursor()
        for rec in user:
            users=[]
            users.append(rec.name)
            users.append(rec.login)
            users.append(rec.id)
            users.append(rec.password)
            users.append(rec.partner_id.city)
            users.append(rec.partner_id.zip)
            users.append(rec.partner_id.mobile)
            users.append(rec.partner_id.id)
            users.append(12)
            users.append(5)
            if rec.partner_id.activity_type_id.id:
                users.append(rec.partner_id.activity_type_id.id)
            else:
                users.append(0)
            users.append(rec.create_date)
            users.append(rec.write_date)
            total.append(tuple(users))
        for rec in total:
            postgres_insert_query = """insert into public.user(user_name,email,user_id,password,city,zip_code,mobile_no,company_id,country_id,state_id,user_type_id,created_on,updated_on) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
            cur.execute(postgres_insert_query, rec)
        print('user Documents  inserted success')
        conn.commit()
        cur.close()

    #api for company import in database
    @http.route(['/create/db/comp'], type='http',methods=['POST'], auth='public', csrf=False)
    def main_menu_comp(self, **kw):
        conn=self.connection()
        cur = conn.cursor()
        company = request.env['res.company'].sudo().search([])
        comp = []
        for rec in company:
            c=[]
            c.append(rec.id)
            c.append(rec.name)
            c.append(rec.create_date)
            c.append(rec.write_date)
            comp.append(tuple(c))
        for rec in comp:
            pg  = """insert into user_company(company_id,company_name,created_on,updated_on) VALUES (%s,%s,%s,%s)"""
            cur.execute(pg,rec)
        conn.commit()
        cur.close()

    #api for attachment import in database 
    @http.route(['/create/db/attach'], type='http',methods=['POST'], auth='public', csrf=False)
    def main_menu_attach(self, **kw):
        conn=self.connection()
        cur = conn.cursor()
        documents = request.env['ir.attachment'].sudo().search([])
        doc=[]
        for rec in documents:
            d=[]
            d.append(rec.id)
            d.append((rec.name))
            d.append(rec.type)
            d.append(rec.create_date)
            d.append(rec.write_date)
            doc.append(tuple(d))
        for rec in doc:
            pg = """insert into document_details(document_id,document_name,document_type,created_on,updated_on) VALUES (%s,%s,%s,%s,%s)"""
            cur.execute(pg,rec)
        conn.commit()
        cur.close()

    def connection(self):
        conn =psycopg2.connect(
        host="localhost",
        database="plastic_credit",
        user="odoo14",
        password="odoo14")
        return conn