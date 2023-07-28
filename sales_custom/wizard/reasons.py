from odoo import fields, models


class RasonDetails(models.TransientModel):
    _name = 'reason.details'
    _rec_name = 'reason'

    reason = fields.Char('Enter Reason for rejected')

    def set_reason(self):
        order = self.env['sale.order'].browse([(self.env.context['active_id'])])
        order.reason = self.reason