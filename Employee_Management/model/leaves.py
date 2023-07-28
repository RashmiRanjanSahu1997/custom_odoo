from odoo import fields, models, api
import random
from datetime import datetime
from odoo.exceptions import ValidationError


class Leaves(models.Model):
    _name = 'leaves.details'
    _description = 'This is using for Leaves details'
    _rec_name = "reason"

    emp_id = fields.Many2one('employee.details', string='Name', required=True)
    from_date = fields.Date(string='From Date')
    end_date = fields.Date(string='End date')
    days = fields.Integer(string='No of Days', compute = '_remaining_days')
    reason = fields.Text(string='Reason', required=True)
    state = fields.Selection(selection=[('applied', 'Applied'),
                                        ('verified', 'Verified'),
                                        ('granted', 'Granted'),
                                        ('cancelled', 'Cancelled')], default='applied')
    total_leaves = fields.Integer(string='Total Leaves', default=15)
    otp = fields.Integer('Verify')
    verify1 = fields.Integer('OTP')

    def get_otp_verify(self):
        verify = random.randint(100000, 9999999)
        self.verify1 = verify

    def set_verified(self):
        if self.verify1 == self.otp:
            self.state = 'verified'
        else:
            self.state = 'cancelled'

    def set_granted(self):
        self.state = 'granted'
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Granted',
                'type': 'rainbow_man'
            }
        }

    def set_cancelled(self):
        self.state = 'cancelled'

    @api.onchange('from_date')
    def get_lastdate(self):
        self.end_date = False

    def _remaining_days(self):
        for rec in self:
            start=int(datetime.strftime(rec.from_date, "%d"))
            end = int(datetime.strftime(rec.end_date, "%d"))
            day = abs(start-end)
            if day>=15:
                raise ValidationError('Sorry you cannot take leave more than 15')
            else:
                rec.days = int(day)

    @api.model
    def count_details(self):
        if self.state == 'applied':
            self.state = 'cancelled'
        
