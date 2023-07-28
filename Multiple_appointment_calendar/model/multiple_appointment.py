from odoo import fields , models
class Multipleappointmentcalendar(models.Model):
    _name = 'multiple.appointment'
    _description = 'multipleappointment calendar'

    name = fields.Char(string='name')
    date = fields.Date(string='date')
    age = fields.Boolean(string='18years above')
    color = fields.Integer(string='color')
    active = fields.Boolean(string='active', default=True)
