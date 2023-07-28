from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def action_confirm(self):
        res = super(SaleOrder,self).action_confirm()
        if self.user_id.is_eligible:

            for rec in self.order_line:
            
                if rec.product_id.incentive:
                
                    price = (rec.price_subtotal*rec.product_id.incentive)//100
                    self.env['sale.incentive'].create({'name':self.create_uid.id,'product':rec.product_id.id,'total_price':rec.price_subtotal,'incentive':price})
        return res