# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import date
from odoo import api, fields, models, _


class HelpdeskTicketsTags(models.Model):
    _name = "tickets.tags"
    _description = "Helpdesk Support Tickets tags"
    _rec_name = 'name'


    name = fields.Char(string="Tags Name")
    color = fields.Integer(string="Color")