# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import date

from odoo import api, fields, models, _


class HelpdeskSolution(models.Model):
    _name = "helpdesk.support.team"
    _description = "Odoo Advanced Helpdesk Support"
    _order = 'sequence, name'
    _rec_name = 'name'

    age = fields.Integer(string="Age")
    name = fields.Char(string="Helpdesk Team", required=True, translate=True)
    type = fields.Char(string="Types")
    description = fields.Text('About Team', translate=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.company)
    sequence = fields.Integer("Sequence", default=10)
    color = fields.Integer('Color Index', default=1)
    member_ids = fields.Many2many('res.users', string='Team Members')
    visibility_member_ids = fields.Many2many('res.users', 'helpdesk_visibility_team', string='Team Visibility',
                                             help="Team to whom this team will be visible. Keep empty for everyone to see this team.")
    assign_method = fields.Selection([
        ('manual', 'Manually'),
        ('randomly', 'Random'),
        ('balanced', 'Balanced')], string='Assignment Method', default='manual',
        store=True, readonly=False, required=True,
        help='Automatic assignment method for new tickets:\n'
             '\tManually: manual\n'
             '\tRandomly: randomly but everyone gets the same amount\n'
             '\tBalanced: to the person with the least amount of open tickets')


    def _default_domain_member_ids(self):
        # return [('groups_id', 'in', self.env.ref('helpdesk_community.group_helpdesk_user').id)]
        return True



