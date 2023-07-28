from odoo import models, fields, api
import random


class DepartmentDetails(models.Model):
    _name = 'department.details'
    _description = 'This is using for Department details'

    name = fields.Char(string='Name', required=True)
    head_name = fields.Many2one('employee.details', required=True, string='Head Name')
    company_id = fields.Many2one('company.details', string='Company Name')
    type = fields.Char('Company Type', compute='_compute_company_type')
    random_no = fields.Integer('OTP')

    @api.depends('company_id.type')
    def _compute_company_type(self):
        for rec in self:
            rec.type = rec.company_id.type

    def random_no_field(self):
        self.random_no = random.randint(100000, 999999)