from odoo import fields, models


class DesignationDetails(models.Model):
    _name = 'designation.details'
    _description = 'This is using for Designation details'

    name = fields.Char(string='Designation')
    emp_ids = fields.One2many('employee.details', 'designation_id', string='Employee')
