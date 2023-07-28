# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import datetime
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class HelpdeskCreateTimesheet(models.TransientModel):
    _name = 'helpdesk.create.timesheet'
    _description = "Create Timesheet from ticket"

    # _sql_constraints = [('time_positive', 'CHECK(time_spent > 0)', "The timesheet's time must be positive" )]

    time_spent = fields.Float('Time')
    description = fields.Char('Description')
    ticket_id = fields.Many2one(
        'helpdesk.tickets', "Ticket", required=True,
        default=lambda self: self.env.context.get('active_id', None),
    )


    def action_generate_timesheet(self):
        print("\n\n\n\n\naction_generate_timesheet==========\n\n\n\n")
        values = {
            'account_ticket_id': self.ticket_id.id,
            'account_date': fields.Datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
            'account_name': self.description,
            'user_id': self.env.uid,
            'account_unit_amount': self.time_spent,

        }
        print("\n\n\n\n\naction_generate_timesheet==========values\n\n\n\n", values)
        timesheet = self.env['calculate.line'].create(values)
        print("\n\n\n\n\naction_generate_timesheet==========timesheet\n\n\n\n", timesheet)
        self.ticket_id.write({
            'timer_start': False,
            'timer_pause': False
        })
        self.ticket_id.account_timesheet_ids = [(4, timesheet.id, None)]
        return timesheet
