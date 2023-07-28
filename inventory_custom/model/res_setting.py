from odoo import fields, models


class ResSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    stock_limit = fields.Integer('Stock Limit', config_parameter="stock_limit")

