from odoo import fields, models, api


class HrManagement(models.Model):
    _inherit = 'hr.employee'

    basic_pay = fields.Integer(string='Basic Pay')
    epf = fields.Integer('EPF')
    total_salary = fields.Integer('TOTAL SALARY', compute='compute_total_salary')
    com_mob = fields.Char(string='Mob No', related='address_id.phone')

    @api.depends('epf', 'basic_pay')
    def compute_total_salary(self):
        self.total_salary = self.epf + self.basic_pay

