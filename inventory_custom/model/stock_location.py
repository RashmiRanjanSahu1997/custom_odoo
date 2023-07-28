from odoo import fields, models


class StockLocation(models.Model):
    _inherit = 'stock.location'

    stock_capacity = fields.Integer('Maximum Stock Capacity')

    