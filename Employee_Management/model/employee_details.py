from odoo import fields, models, api
from datetime import datetime
from odoo.exceptions import ValidationError

class EmployeeDetails(models.Model):
    _name = 'employee.details'
    _description = 'this is employee details'

    name = fields.Char(string='Name', required=True)
    mob = fields.Char(string='Mob No', required=True)
    city = fields.Char(string='City')
    dob = fields.Date(string='Date Of Birth', copy=False)
    gender = fields.Selection(selection=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')],
        string='Gender')
    designation_id = fields.Many2one('designation.details', string='Designation', copy=False)
    is_active = fields.Boolean(string='Now Working', default=True)
    cv = fields.Binary(string='Resume')
    introduction = fields.Text(string='Write about Yourself')
    salary = fields.Integer(string='Salary')
    company_id = fields.Many2one('company.details', string='Company')
    experience = fields.Integer('Experience', required=True)
    image = fields.Image('Image')
    state = fields.Selection(selection=[('learning', 'Learning'),
                                        ('fresher', 'Fresher'),
                                        ('experienced', 'Experienced')], default='learning')
    email = fields.Char('Email')
    age = fields.Char('Age')
    epf = fields.Integer('EPF+ESI')
    ctc_salary = fields.Integer('CTC', compute='_compute_total_salary')
    company_address = fields.Char('Company Address', compute='_compute_company_address', store=True)
    emp_manager = fields.Many2one("res.users", "manager")

    def set_fresher(self):
        self.state = 'fresher'
        return {
            'effect': {
                'type': 'rainbow_man',
                'fadeout': 'slow',
                'message': 'Joined'
            }
        }

    def set_experienced(self):
        self.state = 'experienced'

    def move_designation(self):
        return {
            'name': 'Designation',
            'res_model': 'designation.details',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'target': 'current',
            'domain': [('emp_ids', '=', self.id)]
        }

    @api.onchange('dob')
    def _get_age_employee(self):
        age = self.dob
        if self.dob:
            self.age = str(datetime.today().year-int(datetime.strftime(self.dob, "%Y")))
        else:
            pass

    @api.depends('salary', 'epf')
    def _compute_total_salary(self):
        '''
        for record in self:
            ctc = 0
            ctc=ctc+record.epf+record.salary
            record.ctc_salary=ctc
        '''
        self.ctc_salary = self.salary+self.epf

    @api.depends('company_id.location')
    def _compute_company_address(self):
        for record in self:
            record.company_address = record.company_id.location

    @api.model
    def create(self, vals):
        res = super(EmployeeDetails, self).create(vals)
        if not res.age:
            res.age = 20
        return res

    def copy(self,default=None):
        res = super(EmployeeDetails, self).copy(default=default)
        return res

    def unlink(self):
        if self.state == 'experienced':
            raise ValidationError('Sorry,its not possible to delete')
        res = super(EmployeeDetails, self).unlink()
        return res

    def send_employee_email(self):
        temp_id = self.env.ref('Employee_Management.mail_template_confirm_employee').id
        template = self.env['mail.template'].browse(temp_id)
        template.send_mail(self.id, force_send=True)