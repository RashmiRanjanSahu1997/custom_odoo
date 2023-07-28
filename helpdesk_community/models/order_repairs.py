# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models, _


class HelpdeskOrderRepair(models.Model):
    _name = "helpdesk.order.repair"
    _description = "Odoo Advanced Helpdesk Support In Repairing"
    _rec_name = 'name'


    name = fields.Char(string="Present Team")
    type = fields.Char(string="Types")

    status_id = fields.Selection([
        ('quotation', 'QUOTATION'),
        ('ready', 'Ready to Repair'),
        ('confirme', 'CONFIRM'),
        ('under_repaired', 'UNDER REPAIR'),
        ('repaired', 'REPAIRED'),
    ], 'Status', store=True, default='quotation', required=True, tracking=True)


    def confirm_repair(self):
        for rec in self:
            rec.status_id = 'confirme'

    def start_repair(self):
        pass

    def cancel_repair(self):
        pass

    def send_quotation_order(self):
        for rec in self:
            rec.status_id = 'under_repaired'

    def print_quotation_order(self):
        for rec in self:
            rec.status_id = 'repaired'

    def cancel_repair(self):
        for rec in self:
            rec.status_id = 'quotation'