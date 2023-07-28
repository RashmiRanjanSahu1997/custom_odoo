from odoo import fields, models, api
from datetime import datetime


class DelhiveryDate(models.Model):
    _inherit = 'stock.picking'


    def button_validate(self):
        active_id=self.env.context.get('active_id')
        record = self.env['sale.order'].browse(active_id)
        record.delivery_date = datetime.today()
        res = super(DelhiveryDate,self).button_validate()
        if self.sale_id:
            self.sale_id.delivery_date=datetime.today()
        return res





