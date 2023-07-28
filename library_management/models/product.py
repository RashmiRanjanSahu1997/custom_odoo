from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    abc = fields.Char("abc")