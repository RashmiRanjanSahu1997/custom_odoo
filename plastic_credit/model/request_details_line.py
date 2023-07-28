from odoo import fields,models,api


class RequestDetailsLine(models.Model):
    _name = 'request.details.line'
    _description = 'Request Details Line'

    name = fields.Many2one('product.product','Name')
    quantity = fields.Float('Quantity')
    desc = fields.Char('Description')
    history_id = fields.Many2one('request.details.history')
    # unit_price = fields.Monetary('Unit Price')
    uom = fields.Many2one('uom.uom',string='UOM')

    @api.onchange('name')
    def desc_onchange(self):
        for rec in self:
            rec.desc = rec.name.name
            rec.uom = rec.name.uom_id.id