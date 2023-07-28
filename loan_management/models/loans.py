# -*- coding: utf-8 -*-
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class LoanManagement(models.Model):
    _name = 'loan.management'
    _description = 'Loan Management'
    _rec_name = 'customer'

    customer = fields.Many2one(comodel_name="res.partner", string="Customer", required=True, )
    loan_amount = fields.Float(string="Loan Amount", related='products.price', required=True, )
    is_land_contract = fields.Boolean(string="Is Land Contract")
    down_payment = fields.Float(string="Down Payment", required=True, )
    rate = fields.Integer(string="rate", required=True, )
    reference_no = fields.Char(string='Order Reference', required=True,
                               readonly=True, default=lambda self: _('New'))

    products = fields.Many2one(comodel_name="loan.product", string="Product", required=False, )
    rate_per_month = fields.Char(string="Rate Per Month", required=False, )
    round_on_end = fields.Boolean(string="Round On End")
    starting_date = fields.Date(string="Starting Date", required=True, )
    installment_due_date = fields.Date(string="Installment Due Date", required=False, )
    closing_date = fields.Integer(string="Closing Date", required=False, )
    no_of_installment = fields.Integer(string="No Of Installment", required=True, )
    time_between_two_installments = fields.Float(string="Time Between Two Installments(in month)", required=False, )
    upcoming_invoice_amount = fields.Float(string="Upcoming Invoice", required=False, )
    total_amount_date = fields.Float(string="Total Amount Date", )
    days_due = fields.Float(string="Days Due", )

    loan_lines_ids = fields.One2many('loans.lines', 'loans_id', string="Loan Lines", required=False, )
    property_insurances = fields.Many2one(comodel_name="account.tax", string="Property Insurance", required=False, )
    property_tax = fields.Many2one(comodel_name="account.tax", string="Property Tax", required=False, )

    status = fields.Selection(selection=
                              [('draft', 'DRAFT'), ('validated', 'VALIDATED'), ('cancelled', 'CANCELLED'),
                               ('closed', 'CLOSED')])

    vendor_bill_count = fields.Integer("Vendor Bill Count", compute='_compute_vendor_bill_count')
    payment_count = fields.Integer("Payment Count")

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'loan.number') or _('New')
            res = super(LoanManagement, self).create(vals)
        return res

    def _get_company_currency(self):
        for partner in self:
            if partner.company_id:
                partner.currency_id = partner.sudo().company_id.currency_id
            else:
                partner.currency_id = self.env.company.currency_id

    def _compute_payments_count(self):
        print("_compute_payments_count====================", self)

    # @api.depends('line_ids')
    def _compute_vendor_bill_count(self):
        purchase_types = self.env['account.move'].get_purchase_types()
        domain = [
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', 'in', purchase_types),
            ('analytic_account_id', 'in', self.ids)
        ]
        groups = self.env['account.move.line']._read_group(domain, ['move_id:count_distinct'], ['analytic_account_id'])
        moves_count_mapping = dict((g['analytic_account_id'][0], g['move_id']) for g in groups)
        for account in self:
            account.vendor_bill_count = moves_count_mapping.get(account.id, 0)

    def extra_payments(self):
        pass

    def Postpone_installments(self):
        print("Postpone_installments")
        return {
            'effect': {
                'fadeout': 'slow',
                'message': "Postpone sucessfull",
                'type': 'rainbow_man',
            }
        }

    def button_draf(self):
        for rec in self:
            print("---------------------------------", rec.state)

    def cancel_loan(self):
        for rec in self:
            rec.status = 'cancelled'

    def close_loan(self):
        for rec in self:
            rec.status = 'draft'

    def method_validation(self):
        for rec in self:
            rec.status = 'validated'

    def amount_si(self):
        if self.customer:
            sr_no = 1
            vals = self.loan_amount
            inst = self.no_of_installment / 12
            insts = self.no_of_installment
            rat = self.rate / 100
            date_start = datetime.strptime(str(self.starting_date), '%Y-%m-%d')
            pen_py = 1 + rat * inst
            pen = vals * pen_py
            si = pen / insts
            intrestes = vals * 1 / 100
            pend = si - intrestes
            values = []
            for rec in range(self.no_of_installment):
                val = vals
                pending_principal = round(val - pend, 2)
                vals = pending_principal
                date_start = date_start + relativedelta(months=1)
                values.append({
                    'seq': sr_no, 'days_due': date_start, 'pending_principal': vals, 'loan_payment': si,
                    'principal': pend,
                    'interests': intrestes,
                })
                sr_no += 1
                print("list.....................", [(0, 0, item) for item in values])
            self.loan_lines_ids = [(0, 0, item) for item in values]
        return True

    def action_view_vendor_bill(self):
        self.ensure_one()
        result = {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "domain": [('move_type', 'in', self.env['account.move'].get_purchase_types())],
            "context": {"create": False},
            "name": "Vendor Bills",
            'view_mode': 'tree,form',
        }
        return result

    def action_view_payments(self):
        result = {
            "type": "ir.actions.act_window",
            "res_model": "payment.interest",
            # "domain": [('move_type', 'in', self.env['account.move'].get_purchase_types())],
            "context": {"create": False},
            "name": "payments",
            'view_mode': 'tree,form',
        }
        return result

    def _compute_journal_items(self):
        for rec in self:
            #
            print("_compute_invoice_count", rec)

    journal_count = fields.Integer("Journal Count")
    journal_ids = fields.Integer("sale_id")

    def method_journal_items(self):
        return {
            "name": "Journal Items",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.journal",
            # "domain": [("sale_id", "=", self.id)],
        }

    journal_count = fields.Integer("Journal Count")
    journal_ids = fields.Integer("sale_id")

    def method_journal_items(self):
        purchase_types = self.env['account.move'].get_purchase_types()
        print("purchase_types====================================================", purchase_types)
        domain = [
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', 'in', purchase_types),
            ('analytic_account_id', 'in', self.ids)
        ]
        print("domain====================================================", domain)
        groups = self.env['account.move.line']._read_group(domain, ['move_id:loan_amount'], ['analytic_account_id'])
        print("groups====================================================", groups)
        moves_count_mapping = dict((g['analytic_account_id'][0], g['move_id']) for g in groups)
        print("moves_count_mapping====================================================", moves_count_mapping)
        for account in self:
            account.journal_count = moves_count_mapping.get(account.id, 0)
            print("account    self====================================================", account, self)
            print("account.journal_count====================================================", account.journal_count)

        return {
            "name": "Journal Items",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.journal",
            # "domain": [("sale_id", "=", self.id)],
        }

    def _compute_invoice_count(self):
        for rec in self:
            #
            print("_compute_invoice_count", rec)

    invoice_count = fields.Integer("Invoice Count")
    invoice_ids = fields.Integer("sale_id")

    def method_invoice(self):
        return {
            "name": "Invoice",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.move",
            # "domain": [("sale_id", "=", self.id)],
        }

    def _compute_insurances(self):
        for rec in self:
            #
            print("_compute_invoice_count", rec)

    insurances_count = fields.Integer("Invoice Count")
    insurances_ids = fields.Integer("sale_id")

    def method_insurances(self):
        return {
            "name": "Insurances",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.tax",
            # "domain": [("sale_id", "=", self.id)],
        }

    def _compute_tax_items(self):
        for rec in self:
            #
            print("_compute_invoice_count", rec)

    tax_count = fields.Integer("Invoice Count")
    tax_ids = fields.Integer("sale_id")

    def method_tax_items(self):
        return {
            "name": "Tax Items",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.tax",
            # "domain": [("sale_id", "=", self.id)],
        }

    def _compute_payment_transaction(self):
        for rec in self:
            #
            print("_compute_invoice_count", rec)

    payment_transaction_count = fields.Integer("Invoice Count")
    payment_transaction_ids = fields.Integer("sale_id")

    def method_payment_transaction(self):
        return {
            "name": "Payment Transaction",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "payment.transaction",
            # "domain": [("sale_id", "=", self.id)],
        }

    def _compute_payment(self):
        for rec in self:
            print("_compute_invoice_count", rec)

    payment_count = fields.Integer("Invoice Count")
    payment_ids = fields.Integer("sale_id")

    def method_payment(self):
        return {
            "name": "Payment",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.payment",
            # "domain": [("sale_id", "=", self.id)],
        }

    def update_price_product(self):
        purchase_ids = self.ids
        context = {}
        print("*********************************************************************call wizard fucntion")
        purchase_ids = self.env.context.get('active_ids', [])
        print("*********************************************************************purchase_ids", purchase_ids)
        context = dict(self._context)
        print("*********************************************************************context", context)
        return {

            'type': 'ir.actions.act_window',

            'view_type': 'list',

            'view_mode': 'list',

            'res_model': 'account.move',

            'target': 'new',

            'context': context
        }


class LoanManagementLines(models.Model):
    _name = 'loans.lines'
    _description = 'Loans Lines'

    seq = fields.Integer(string="Sequence", store=True)
    days_due = fields.Date(string="Days Due", store=True)
    pending_principal = fields.Float(string="Pending Principal", store=True)
    loan_payment = fields.Float(string="Loan Payment", store=True)
    principal = fields.Float(string="Principal", store=True)
    interests = fields.Float(string="Interests", store=True)
    total_amount = fields.Float(string="Total Amount", store=True)
    amount_due = fields.Float(string="Amount Due", store=True)
    paid_on = fields.Float(string="Paid On", store=True)
    loans_id = fields.Many2one(comodel_name="loan.management", string="loans_id", required=False, store=True)


class LoanPaymentBrower(models.Model):
    _name = 'payment.borrower'
