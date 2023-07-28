from odoo import models, fields, _


class ProductVariant(models.Model):
    _inherit = 'product.product'

    def set_product_discount(self):
        ctx = {'active_ids':self.env.context['active_ids'],
            'active_model':self.env.context['active_model']}
        return {
            'name'      : _('Hi just set Discount'),
            'type'      : 'ir.actions.act_window',
            'res_model' : 'product.discount',
            # 'view_id'   : 'sale_products.product_discount_action',
            'view_type' : 'form',
            'view_mode' : 'form',
            'target'    : 'new',
            'context': self.env.context
        }