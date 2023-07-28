# -*- coding: utf-8 -*-
from odoo import models, fields, api


class PaymentsInterest(models.Model):
    _name = 'payment.interest'
    _description = "Interest's payments"


    name = fields.Char(string="Name", required=False, )
