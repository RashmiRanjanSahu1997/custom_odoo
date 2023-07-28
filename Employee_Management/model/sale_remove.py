from odoo import fields, models, api
import datetime
from odoo.exceptions import ValidationError


class SaleRemove(models.Model):
    _inherit = 'sale.order'

    def write(self, vals):
        if self.state in ('sent', 'sale'):
            for rec in vals:
                vals[rec] = self[rec]
        res = super(SaleRemove, self).write(vals)
        return res

    @api.model
    def sales_confirm(self):
        record = self.env['sale.order'].search([('state','in',['draft', 'sent'])])
        today_date = datetime.datetime.now().date()
        for rec in record:
            order_date =rec.date_order.date()
            if (today_date-order_date).days >=1:
                rec.action_confirm()

    @api.constrains('name')
    def _check_description(self):
        order_id = self.env['sale.order'].search([
            ('partner_id','=',self.partner_id.name),
            ('date_order','<=', (datetime.date.today()).strftime('%Y-%m-%d')),
            ('date_order','>=',(datetime.date.today()).strftime('%Y-%m-%d'))])
        if len(order_id) > 1:
            raise ValidationError("Only one customer allowed in  single day")
        # today_date =datetime.datetime.now().date()
        # for rec in order_id:
        #     order_date =rec.date_order.date()
        #     if today_date == order_date:








        # for rec in self:
        #     order_date =dateutil.parser.parse(str(rec.date_order)).date()
        #     if rec.partner_id == self.partner_id:
        #         if today_date == order_date:
        #             raise ValidationError("Only one customer allowed in  single day")

                
