from odoo import fields, models, api


class ProjectDetails(models.Model):
    _name = 'project.details'
    _description = 'this is using for project details'

    name = fields.Char(string='project', required=True)
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', copy=False)
    budget = fields.Integer(string='Budget', copy=False)
    emp_id = fields.Many2many('employee.details', 'employee_project_rel',
                              'employee_id', 'project_id', required=True, string='Employees')
    company_id = fields.Many2one('company.details', string='Company')
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Low'),
        ('2', 'High'),
        ('3', 'Very High')], string="Priority")
    state = fields.Selection([
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('delivered', 'Delivered')], default='processing')
    total_employees = fields.Integer('Total Employees', compute='_total_employees')

    def set_completed(self):
        self.state = 'completed'

    def set_delivered(self):
        self.state = 'delivered'

    @api.depends('emp_id.name')
    def _total_employees(self):
        for rec in self:
            rec.total_employees = len(rec.emp_id)

    def empty(self):
        pass

    def copy(self, default=None):
        res = super(ProjectDetails, self).copy(default=default)
        return res

    @api.model
    def create(self, vals):
        if not vals.get('company_id'):
            com_id = self.env['company.details'].search([('name', '=', 'tecblic')], limit=1)
            vals.update({'company_id': com_id.id})
        res = super(ProjectDetails, self).create(vals)
        return res


    
