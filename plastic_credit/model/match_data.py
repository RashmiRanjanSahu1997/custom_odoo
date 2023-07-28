from odoo import fields, models


class MatchedData(models.TransientModel):
    _name = 'match.data'
    _description= 'Matching Data'

    name= fields.Char('Name')
    db_id = fields.Integer('DB id')
    odoo_name= fields.Char('Odoo Name')
    odoo_id = fields.Integer('Odoo ID')
    data_id = fields.Many2one('data.connection')
    