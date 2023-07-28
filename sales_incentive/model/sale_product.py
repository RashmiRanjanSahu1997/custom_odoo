from odoo import fields, models


class SaleProduct(models.Model):
    _inherit  = 'product.product'

    incentive = fields.Integer('Incentive')
    