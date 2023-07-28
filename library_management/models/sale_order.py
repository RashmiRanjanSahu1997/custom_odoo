from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"

    create_date = fields.Date("Create Date", default=fields.Date.context_today)
    
    