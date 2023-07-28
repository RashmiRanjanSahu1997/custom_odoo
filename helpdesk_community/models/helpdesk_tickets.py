# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date
import base64

from odoo import api, fields, models, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT


class HelpTickets(models.Model):
    _name = "helpdesk.tickets"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Odoo Available Helpdesk Support Tickets"
    _rec_name = 'helpdesk_teams_id'

    # def _default_name(self):
    #     return self.get_value()

    name = fields.Char(string="Name")
    helpdesk_teams_id = fields.Many2one('helpdesk.support.team', string="Helpdesk Team", tracking=True)
    age = fields.Integer(string="Age")
    type_r = fields.Char(related='helpdesk_teams_id.type', store=True, readonly=False)
    description = fields.Text('About Team', translate=True)
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('kids', 'Childern')], string="Gender")

    tags_ids = fields.Many2many(
        'tickets.tags', string='Tags')

    company_id = fields.Many2one('res.company', string='User', default=lambda self: self.env.company.id)
    customer_id = fields.Many2one('res.partner', string='Customer')
    # partner_name = fields.Char(related='partner_id.name')
    customer_email = fields.Char(string="Email")
    customer_phone = fields.Char(string="Phone Number")
    customer_task_ids = fields.One2many('project.task', 'custom_tickets_id', string='Tasks')

    user_id = fields.Many2one(
        'res.users', string='Assigned to',
        readonly=False, tracking=True)

    active = fields.Boolean(string="Active",
                            default=True)  # sare recodes active hai unarchive kar diya matlab k vo recode sab se hide or inactive ho jae ga

    tics_priority = [
        ('0', 'All'),
        ('1', 'Low priority'),
        ('2', 'High priority'),
        ('3', 'Urgent'),
    ]
    prioritys = fields.Selection(tics_priority, string='Priority', default='0')

    state_id = fields.Selection([
        ('new', 'New'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], 'Status', store=True, default='new', required=True, tracking=True)

    def start(self):
        pass

    def return_order(self):
        pass

    def coupon(self):
        pass

    def plan_intervention(self):
        pass

    custom_tickets = fields.Integer(string="Ticket Count", compute='_compute_ticket_count')

    @api.depends('customer_id')
    def _compute_ticket_count(self):
        # print("test>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>self", self)
        for ticket in self:
            custom_tickets = self.env['helpdesk.tickets'].search_count([('customer_id', '=', self.customer_id.id)])
            # print("custom_tickets==========================", custom_tickets)
            ticket.custom_tickets = custom_tickets

    def tickets_form_view(self):
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'helpdesk.tickets',
            'domain': [('customer_id', '=', self.customer_id.id)]
        }
        return action

    # print("test.............................")

    project_id = fields.Many2one("project.project", string="Project")
    project_task_id = fields.Many2one(
        "project.task", string="Task", store=True, readonly=False,
        domain="[('id', 'in', _related_task_ids)]", tracking=True,
    )

    _related_project_task_ids = fields.Many2many('project.task')
    account_timesheet_ids = fields.One2many('calculate.line', 'account_ticket_id', 'Timesheets')
    is_closed_ticket = fields.Boolean(string="Is Closed", readonly=True)
    time_spent = fields.Float(string="Spent Time")

    timer_start = fields.Datetime("Timer Start")
    timer_pause = fields.Datetime("Timer Last Pause")
    is_timer_running = fields.Boolean(compute="_compute_is_timer_running")
    res_model = fields.Char(required=True)
    res_id = fields.Integer(required=True)

    task_id = fields.Many2one('project.task', string="Task", help="Task from which quotation have been created")
    project_id = fields.Many2one("project.project", string="Project")
    total_hours_spent = fields.Float(compute='_compute_total_hours_spent', default=0)

    display_timesheet_timer = fields.Boolean("Display Timesheet Time", compute='_compute_display_timesheet_timer')
    use_helpdesk_timesheet = fields.Boolean('Timesheet activated on Team',
                                            readonly=True)
    timesheet_timer = fields.Boolean()
    display_timer_start_secondary = fields.Boolean()
    display_timer_start_primary = fields.Boolean()
    display_timer = fields.Boolean()
    encode_uom_in_days = fields.Boolean(compute='_compute_encode_uom_in_days')
    display_timer_stop = fields.Datetime(string="display timer stop", required=False)
    display_timer_pause = fields.Datetime(string="display timer pause", required=False)
    display_timer_resume = fields.Datetime(string="display timer resume", required=False)

    def _compute_encode_uom_in_days(self):
        self.encode_uom_in_days = self.env.company.timesheet_encode_uom_id == self.env.ref('uom.product_uom_day')

    _sql_constraints = [(
        'unique_timer', 'UNIQUE(res_model, res_id, user_id)',
        'Only one timer occurrence by model, record and user')]

    @api.depends('display_timesheet_timer', 'timer_start', 'timer_pause', 'total_hours_spent')
    def _compute_display_timer_buttons(self):
        for ticket in self:
            if not ticket.display_timesheet_timer:
                ticket.update({
                    'display_timer_start_primary': False,
                    'display_timer_start_secondary': False,
                    'display_timer_stop': False,
                    'display_timer_pause': False,
                    'display_timer_resume': False,
                })
            else:
                super(HelpTickets, ticket)._compute_display_timer_buttons()
                ticket.display_timer_start_secondary = ticket.display_timer_start_primary
                if not ticket.timer_start:
                    ticket.update({
                        'display_timer_stop': False,
                        'display_timer_pause': False,
                        'display_timer_resume': False,
                    })
                    if not ticket.total_hours_spent:
                        ticket.display_timer_start_secondary = False
                    else:
                        ticket.display_timer_start_primary = False

    @api.depends('use_helpdesk_timesheet', 'timesheet_timer', 'account_timesheet_ids', 'encode_uom_in_days')
    def _compute_display_timesheet_timer(self):
        for ticket in self:
            ticket.display_timesheet_timer = ticket.use_helpdesk_timesheet and ticket.timesheet_timer and not ticket.encode_uom_in_days

    @api.depends('account_timesheet_ids')
    def _compute_total_hours_spent(self):
        for tic in self:
            tic.total_hours_spent = round(sum(tic.account_timesheet_ids.mapped('account_unit_amount')), 2)

    @api.depends('timer_start', 'timer_pause')
    def _compute_is_timer_running(self):
        for record in self:
            record.is_timer_running = record.timer_start and not record.timer_pause

    def helpdesk_start_action(self):
        print("\n\n\n\n\n\n\naction_timer_start=========== ", self)
        if not self.timer_start:
            print("\n\n\n\n\n\n\ntimer_start=========== ", self.timer_start)
            self.write({'timer_start': fields.Datetime.now()})

    def helpdesk_stop_action(self):
        print("\n\n\n\n\n\n\naction_timer_stop=========== ", self)
        if not self.timer_start:
            return False
        minutes_spent = self._get_minutes_spent()
        self.write({'timer_start': False, 'timer_pause': False})
        return self._action_open_new_timesheet(minutes_spent * 60 / 3600)

    def _get_minutes_spent(self):
        print("\n\n\n\n\n\n\n_get_minutes_spent===========minute function start======", self)
        start_time = self.timer_start
        stop_time = fields.Datetime.now()
        if self.timer_pause:
            start_time += (stop_time - self.timer_pause)
        return (stop_time - start_time).total_seconds() / 60

    def helpdesk_pause_action(self):
        self.write({'timer_pause': fields.Datetime.now()})

    def helpdesk_resume_action(self):
        print("\n\n\n\n\n\n\nhelpdesk_resume_action=================", self)
        if self.timer_start and self.timer_pause:
            new_start = self.timer_start + (fields.Datetime.now() - self.timer_pause)
            self.write({'timer_start': new_start, 'timer_pause': False})

    @api.model
    def get_server_time(self):
        return fields.Datetime.now()

    def _action_open_new_timesheet(self, time_spent):
        print("time_spent ===============================", time_spent)
        action = {
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'helpdesk.create.timesheet',
            'target': 'new',
            'context': {
                **self.env.context,
                'active_id': self.id,
                'active_model': self._name,
                'default_time_spent': time_spent,
            },
        }
        return action


class CustomProjectTask(models.Model):
    _inherit = 'project.task'

    custom_tickets_id = fields.Many2one('helpdesk.tickets', string='Ticket')


class AccountCalculateLine(models.Model):
    _name = 'calculate.line'

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    account_ticket_id = fields.Many2one('helpdesk.tickets', 'Helpdesk Ticket')
    user_id = fields.Many2one('res.users', string='Employee', default=_default_user)
    account_name = fields.Char(string="Description")
    account_date = fields.Datetime(string="Date")
    account_unit_amount = fields.Float(string="Duration(Hr)")
