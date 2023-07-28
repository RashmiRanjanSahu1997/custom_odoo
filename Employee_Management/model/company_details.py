from odoo import fields , models, api
from odoo.exceptions import ValidationError


class CompanyDetails(models.Model):
    _name = 'company.details'
    _description = 'this is using for company details'

    name = fields.Char(string='Name', required=True)
    location = fields.Char(string='Address', default='Ahmedabad')
    no_of_employees = fields.Integer(string='No of Employees', compute='_compute_get_total_nos')
    emp_ids = fields.One2many('employee.details', 'company_id', string='Employee')
    hr_ids = fields.One2many('hr.details', 'company_id', string='HR Details')
    department_ids = fields.One2many('department.details', 'company_id', 'Department')
    priority = fields.Selection([('0', 'Low'), ('1', 'Medium'),
                                 ('2', 'High'), ('3', 'Very High')])
    type = fields.Selection([('public limited', 'Public Limited'),
                             ('private limited', 'Private Limited'),
                             ('one Person limited', 'One Person Limited')], string='Company Type')

    _sql_constraints = [('name_uniq', 'UNIQUE(name)','Only one same name allowed')]

    def get_employee(self):
        return {
            'name': 'Company Details',
            'res_model': 'employee.details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'target': 'fullscreen',
            'domain': [('company_id', '=', self.id)]
        }

    @api.depends('emp_ids.name')
    def _compute_get_total_nos(self):
        for rec in self:
            rec.no_of_employees = len(rec.emp_ids)

    def search_button(self):
        emp = self.env['company.details'].search([])
        count_emp = self.env['company.details'].search_count([('type','=','one Person limited')])
        for company in self.env['company.details'].browse([26, 25, 24, 23, 22, 21,3,4,6,87,677,77]):
            if company.exists():
                print('yes exists',company)
            else:
                print('Not Exists',company)

    @api.constrains('name')
    def _check_description(self):
        for record in self:
            if record.name != self.name:
                raise ValidationError("Fields name must be different")






