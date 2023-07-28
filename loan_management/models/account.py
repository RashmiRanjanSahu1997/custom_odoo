# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _


class AccountPayment(models.Model):
    _inherit = 'account.move'

    @api.model
    def _default_user(self):
        return self.env.context.get('user_id', self.env.user.id)

    def _default_team_ids(self):
        team_id = self.env.context.get('default_team_id')
        if team_id:
            return [(4, team_id, 0)]

    xyz = fields.Char(string="Customer name", required=False, )
    salesperson = fields.Many2one('res.users', required=False, default=_default_user)
    salesteams = fields.Many2many('res.users', string="Salesteam", required=False, default=_default_team_ids)
    salesteam = fields.Char(string="Salesteam", required=False)
    is_installment = fields.Boolean(string="Is Installment?",  )
    is_downpayment = fields.Boolean(string="Is Downpayment?",  )

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('posted', 'Paid'),
        ('cancel', 'Cancelled'),
    ], string='Status', required=True, readonly=True, copy=False, tracking=True,
        default='draft')


# loan_management.access_account_loan,access_account_loan,loan_management.model_account_loan,loan_management.group_account_user,1,0,0,0
# loan_management.access_account_loan_manager,access_account_loan,loan_management.model_account_loan,loan_management.group_account_manager,1,1,1,1
# loan_management.access_account_loan_line,access_account_loan_line,loan_management.model_account_loan_line,loan_management.group_account_user,1,0,0,0
# loan_management.access_account_loan_line_manager,access_account_loan_line,loan_management.model_account_loan_line,loan_management.group_account_manager,1,1,1,1
# loan_management.access_account_loan_generate_wizard,access_account_loan_generate_wizard,loan_management.model_account_loan_generate_wizard,loan_management.group_account_user,1,0,0,0
# loan_management.access_account_loan_pay_amount,access_account_loan_pay_amount,loan_management.model_account_loan_pay_amount,loan_management.group_account_user,1,0,0,0
# loan_management.access_account_loan_post,access_account_loan_post,loan_management.model_account_loan_post,loan_management.group_account_user,1,0,0,0
# loan_management.access_account_loan_post_manager,access_account_loan_post_manager,loan_management.model_account_loan_post,loan_management.group_account_manager,1,1,1,1










