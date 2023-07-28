from odoo import fields, models,api


class UnmatchedData(models.TransientModel):
    _name = 'unmatch.data'
    _description = 'Unmatch Data'

    name = fields.Char('Name')
    db_id = fields.Integer('DB id')
    odoo_name = fields.Char('Odoo Name')
    odoo_id = fields.Integer('Odoo ID')
    data_id = fields.Many2one('data.connection')
    convert_type=fields.Boolean('Convert Type', default=True)