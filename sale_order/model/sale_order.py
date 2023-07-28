from odoo import models, fields,_
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    city = fields.Char()

    def action_confirm(self):
        if self.partner_id.credit_limit >= self.amount_total:
            res = super(SaleOrder,self).action_confirm()
            return res
        else:
            raise ValidationError(_("your order limit exceed"))


            

    



