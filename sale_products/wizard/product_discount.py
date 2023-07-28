from odoo import models, fields, _
from odoo.exceptions import ValidationError 


class ProductDiscount(models.TransientModel):
    _name = 'product.discount'

    discount = fields.Integer('Set Discount Percentage')
    discount_type = fields.Selection([('sale','Sale'), ('cost','Cost')])

    def set_discount(self):
        print(self)
        print(self.env.context)
        model=self.env.context['active_model']
        for rec in self.env.context['active_ids']:
            product_id = self.env[model].search([('id','=',rec)])
            if self.discount_type=='sale':
                sale_price = ((product_id.lst_price)*(self.discount))//100
                product_id.write({'lst_price':(product_id.lst_price-sale_price)})
            elif self.discount_type=='cost':
                cost_price = ((product_id.standard_price)*(self.discount))//100
                product_id.write({'standard_price':(product_id.standard_price-cost_price)})
            else:
                raise ValidationError(_("Please select Discount type"))

