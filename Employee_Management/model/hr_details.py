from odoo import fields , models , api

class HrDetails(models.Model):
    _name = 'hr.details'
    _description = 'Hr details'

    name = fields.Char(string='Name', required=True)
    mob_no = fields.Char(string='Hr Contact No', required=True)
    address = fields.Char(string='Hr Address')
    company_id = fields.Many2one('company.details', required=True, string='Company Name')
    image = fields.Image(string='Hr Image')

    @api.onchange('company_id')
    def _onchange_company_id(self):
        print("Onchange Called >>")

