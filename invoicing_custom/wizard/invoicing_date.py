# from typing_extensions import Required
from odoo import models, fields


class InvoicingDate(models.TransientModel):
    _name = 'invoicing.date'

    start_date = fields.Date('Start Date', required=True)
    end_date = fields.Date('End Date', required = True)


    def get_pdf_report(self):
        s=self.env['account.move'].search([('invoice_date','>', self.start_date),
                                                ('invoice_date','<',self.end_date)])
        data = {
            
        }
        name = []
        date = []
        price = []
        for rec in s:
            name.append(rec.partner_id.name)
            date.append(rec.invoice_date)
            price.append(rec.amount_total_signed)
        
        data['name']=name
        data['date']=date
        data['price'] = price


        print(data,'=================================')
        return self.env.ref('invoicing_custom.save_invoice_pdf_report').report_action(s,data=data)
    