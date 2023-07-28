from odoo import models, fields


class CreateCompany(models.TransientModel):
    _name = 'company'

    name = fields.Char('Name')
    address = fields.Text('Address')
    type = fields.Selection([('public limited', 'Public Limited'),
            ('private limited', 'Private Limited'),
            ('one person limited', 'One Person Limited')])
    emp_ids = fields.Many2many('employee.details',  string='Employee')


    def CreateCompany(self):
        self.env['company.details'].create({
            "name": self.name,'location':self.address,'type':self.type,'emp_ids':self.emp_ids

        })
