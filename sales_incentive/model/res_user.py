from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    is_eligible = fields.Boolean('Is Eligible')