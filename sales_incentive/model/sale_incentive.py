from itertools import product
from odoo import fields, models


class SaleIncentive(models.Model):
    _name = 'sale.incentive'

    name = fields.Many2one('res.users','Name')
    product = fields.Many2one('product.product','Product')
    total_price = fields.Integer('Total Price')
    incentive = fields.Integer('Incentive')
    date_order = fields.Datetime('Order Date')
    # total_incentive = fields.Integer('Total Price', compute ='total_incentive_price')

    # def total_incentive_price(self):
    #     total = 0
    #     for rec in self:
    #         total = total+rec.incentive
    #     rec.total_incentive = total

