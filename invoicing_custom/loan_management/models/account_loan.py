

import logging
import math
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

_logger = logging.getLogger(__name__)
try:
    import numpy_financial
except (ImportError, IOError) as err:
    _logger.debug(err)


class AccountLoan(models.Model):
    _name = "account.loan"
    _description = "Loan"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    def _default_company(self):
        return self.env.company

    name = fields.Char(
        copy=False,
        required=True,
        readonly=True,
        default="/",
        states={"draft": [("readonly", False)]},
    )
    partner_id = fields.Many2one(
        "res.partner",
        required=True,
        string="Lender",
        help="Company or individual that lends the money at an interest rate.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=_default_company,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Invoices",
        compute='_get_invoiced',
        copy=False)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("posted", "Posted"),
            ("cancelled", "Cancelled"),
            ("closed", "Closed"),
        ],
        required=True,
        copy=False,
        default="draft",
    )
    line_ids = fields.One2many(
        "account.loan.line",
        readonly=True,
        inverse_name="loan_id",
        copy=False,
    )
    # date = fields.Date(
    #     required=True,
    #     readonly=True,
    #     help="Date when the payment will be accounted",
    # )
    periods = fields.Integer(
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Number of periods that the loan will last",
    )
    method_period = fields.Integer(
        string="Period Length",
        default=1,
        help="State here the time between 2 depreciations, in months",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    start_date = fields.Date(
        help="Start of the moves",
        readonly=True,
        states={"draft": [("readonly", False)]},
        copy=False,
    )
    rate = fields.Float(
        required=True,
        default=0.0,
        digits=(8, 6),
        help="Currently applied rate",
        tracking=True,
    )
    rate_period = fields.Float(
        compute="_compute_rate_period",
        digits=(8, 6),
        help="Real rate that will be applied on each period",
    )
    rate_type = fields.Selection(
        [("napr", "Compunde Interest"), ("ear", "Simple Interest"), ("real", "Real rate")],
        required=True,
        help="Method of computation of the applied rate",
        default="napr",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    loan_type = fields.Selection(
        [
            ("fixed-annuity", "Fixed Annuity"),
            ("fixed-annuity-begin", "Fixed Annuity Begin"),
            ("fixed-principal", "Fixed Principal"),
            ("interest", "Only interest"),
        ],
        required=True,
        help="Method of computation of the period annuity",
        readonly=True,
        states={"draft": [("readonly", False)]},
        default="fixed-annuity",
    )
    fixed_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_fixed_amount",
    )
    fixed_loan_amount = fields.Monetary(
        currency_field="currency_id",
        readonly=True,
        copy=False,
        default=0,
    )
    fixed_periods = fields.Integer(
        readonly=True,
        copy=False,
        default=0,
    )
    loan_amount = fields.Monetary(
        currency_field="currency_id",
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    residual_amount = fields.Monetary(
        currency_field="currency_id",
        default=0.0,
        required=True,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="Residual amount of the lease that must be payed on the end in "
             "order to acquire the asset",
    )
    round_on_end = fields.Boolean(
        default=False,
        help="When checked, the differences will be applied on the last period"
             ", if it is unchecked, the annuity will be recalculated on each "
             "period.",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    payment_on_first_period = fields.Boolean(
        default=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
        help="When checked, the first payment will be on start date",
    )
    currency_id = fields.Many2one(
        "res.currency",
        compute="_compute_currency",
        readonly=True,
    )
    journal_type = fields.Char(compute="_compute_journal_type")
    journal_id = fields.Many2one(
        "account.journal",
        domain="[('company_id', '=', company_id),('type', '=', journal_type)]",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    short_term_loan_account_id = fields.Many2one(
        "account.account",
        domain="[('company_id', '=', company_id)]",
        string="Short term account",
        help="Account that will contain the pending amount on short term",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    long_term_loan_account_id = fields.Many2one(
        "account.account",
        string="Long term account",
        help="Account that will contain the pending amount on Long term",
        domain="[('company_id', '=', company_id)]",
        readonly=False,
        states={"draft": [("readonly", False)]},
    )
    interest_expenses_account_id = fields.Many2one(
        "account.account",
        domain="[('company_id', '=', company_id)]",
        string="Interests account",
        help="Account where the interests will be assigned to",
        required=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    is_leasing = fields.Boolean(
        default=False,
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    leased_asset_account_id = fields.Many2one(
        "account.account",
        domain="[('company_id', '=', company_id)]",
        readonly=True,
        states={"draft": [("readonly", False)]},
    )
    product_id = fields.Many2one(
        "product.product",
        string="Loan product",
        help="Product where the amount of the loan will be assigned when the "
             "invoice is created",
    )
    interests_product_id = fields.Many2one(
        "product.product",
        string="Interest product",
        help="Product where the amount of interests will be assigned when the "
             "invoice is created",
    )
    pending_principal_amount = fields.Monetary(
        currency_field="currency_id",
        compute="_compute_total_amounts",
    )
    payment_amount = fields.Monetary(
        currency_field="currency_id",
        string="Total payed amount",
        compute="_compute_total_amounts",
    )
    interests_amount = fields.Monetary(
        currency_field="currency_id",
        string="Total interests payed",
        compute="_compute_total_amounts",
    )
    post_invoice = fields.Boolean(
        default=True, help="Invoices will be posted automatically"
    )
    property_insurances = fields.Many2one(comodel_name="product.product", string="Property Insurance", required=False, )
    property_tax = fields.Many2one(comodel_name="product.product", string="Property Tax", required=False, )

    move_ids = fields.One2many('account.move', 'loan_id', string="Move Ids")
    invoice_count = fields.Integer("Invoice Count", compute="_compute_invoice_count")
    payment_count = fields.Integer("Payment Count", compute="_compute_payment_count")
    journal_count = fields.Integer("Journals", compute="_compute_journal_count")

    def _compute_payment_count(self):
        for rec in self:
            rec.payment_count = self.env['account.payment'].sudo().search_count([('loan_id', '=', rec.id)])

    def _compute_invoice_count(self):
        for rec in self:
            rec.invoice_count = len(rec.move_ids.ids)

    def _compute_journal_count(self):
        for rec in self:
            rec.journal_count = self.env['account.move'].sudo().search_count([('loan_id', '=', rec.id)])

    _sql_constraints = [
        ("name_uniq", "unique(name, company_id)", "Loan name must be unique"),
    ]

    def method_invoice(self):
        return {
            "name": "Invoice",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.move",
            "domain": [("id", "in", self.move_ids.ids)],
        }

    def method_payment(self):
        return {
            "name": "Payment",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            "res_model": "account.payment",
            "domain": [("id", "in", self.env['account.payment'].sudo().search([('loan_id', '=', self.id)]).ids)],
        }

    # payment_transaction_count = fields.Integer("Transaction Count", compute="_compute_payment_transaction")
    # def _compute_payment_transaction(self):
    #     for rec in self:
    #         print("_compute_invoice_count", rec)
    #
    # def method_payment_transaction(self):
    #     return {
    #         "name": "Payment Transaction",
    #         "type": "ir.actions.act_window",
    #         "view_mode": "tree,form",
    #         "res_model": "payment.transaction",
    #         "domain": [("id", "in", self.env['account.payment'].sudo().search([('loan_id', '=', self.id)]).ids)],
    #     }

    def _compute_payment(self):
        for rec in self:
            print("_compute_invoice_count", rec)

    principal_count = fields.Integer("Principal Count", compute="_compute_payment_principal")
    payment_ids = fields.Integer("sale_id")

    def method_payment_principal(self):
        # view_id = self.sudo().get_formview_id(access_uid=access_uid)

        return {
            "name": "Principal",
            "type": "ir.actions.act_window",
            "view_mode": "tree,form",
            # 'views': [(view_id, 'form')],
            "res_model": "account.loan.line",
            "domain": [("loan_id", "=", self.id)],
        }

    @api.depends("line_ids", "currency_id", "loan_amount")
    def _compute_total_amounts(self):
        print("_compute_total_amounts================account.loan(2,)", self)
        for record in self:
            print("_compute_total_amounts record================account.loan(2,)", record)
            lines = record.line_ids.filtered(lambda r: r.move_ids)
            print("_compute_total_amounts lines================account.loan.line(63, 64, 53, 54, 55, 56)", lines)
            record.payment_amount = sum(lines.mapped("payment_amount")) or 0.0
            record.interests_amount = sum(lines.mapped("interests_amount")) or 0.0
            record.pending_principal_amount = (
                    record.loan_amount - record.payment_amount + record.interests_amount
            )
            print("_compute_total_amounts pending_principal_amount================8782.880000000001",
                  record.pending_principal_amount)

    @api.depends("rate_period", "fixed_loan_amount", "fixed_periods", "currency_id")
    def _compute_fixed_amount(self):
        print("_compute_fixed_amount==self================", self)
        """
        Computes the fixed amount in order to be used if round_on_end is
        checked. On fix-annuity interests are included and on fixed-principal
        and interests it isn't.
        :return:
        """
        for record in self:
            print("\n\n_compute_fixed_amount==record================", record)
            if record.loan_type == "fixed-annuity":
                print("_compute_fixed_amount==record.loan_type == fixed-annuity================ "
                      "after compute_rate then _compute_total_amounts")
                record.fixed_amount = -record.currency_id.round(
                    numpy_financial.pmt(
                        record.loan_rate() / 100,
                        record.fixed_periods,
                        record.fixed_loan_amount,
                        -record.residual_amount,
                    )
                )
                print("_compute_fixed_amount==record.loan_type == fixed-annuity================", record.fixed_amount)
            elif record.loan_type == "fixed-annuity-begin":
                record.fixed_amount = -record.currency_id.round(
                    numpy_financial.pmt(
                        record.loan_rate() / 100,
                        record.fixed_periods,
                        record.fixed_loan_amount,
                        -record.residual_amount,
                        when="begin",
                    )
                )
            elif record.loan_type == "fixed-principal":
                record.fixed_amount = record.currency_id.round(
                    (record.fixed_loan_amount - record.residual_amount)
                    / record.fixed_periods
                )
            else:
                record.fixed_amount = 0.0

    @api.model
    def compute_rate(self, rate, rate_type, method_period):
        """
        Returns the real rate
        :param rate: Rate
        :param rate_type: Computation rate
        :param method_period: Number of months between payments
        :return:
        """
        print("\n\ncompute_rate == self================", self)
        if rate_type == "napr":
            return rate / 12 * method_period
        if rate_type == "ear":
            return math.pow(1 + rate, method_period / 12) - 1
        return rate

    @api.depends("rate", "method_period", "rate_type")
    def _compute_rate_period(self):
        for record in self:
            print("\n\n_compute_rate_period==================", self)
            record.rate_period = record.loan_rate()
            print("_compute_rate_period==record.rate_period================", record.rate_period)

    def loan_rate(self):
        print("\n\nloan_rate==================", self)
        return self.compute_rate(self.rate, self.rate_type, self.method_period)

    @api.depends("journal_id", "company_id")
    def _compute_currency(self):
        print("\n\n_compute_currency==================", self)
        for rec in self:
            print("\n_compute_currency======rec============", rec)
            rec.currency_id = rec.journal_id.currency_id or rec.company_id.currency_id
            print("\n_compute_currency=====rec.currency_id=============", rec.currency_id)

    @api.depends("is_leasing")
    def _compute_journal_type(self):
        print("\n\n_compute_journal_type=====self=============", self)
        for record in self:
            print("_compute_journal_type=====record========", record)
            if record.is_leasing:
                record.journal_type = "purchase"
            else:
                record.journal_type = "general"

    @api.onchange("is_leasing")
    def _onchange_is_leasing(self):
        print("\n\n_onchange_is_leasing=====self=============", self)
        self.journal_id = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company_id.id),
                ("type", "=", "purchase" if self.is_leasing else "general"),
            ],
            limit=1,
        )
        print("\n_onchange_is_leasing===== self.journal_id=============", self.journal_id)
        self.residual_amount = 0.0

    @api.onchange("company_id")
    def _onchange_company(self):
        print("\n\n_onchange_company=====self=============", self)
        self._onchange_is_leasing()
        self.interest_expenses_account_id = (
            self.short_term_loan_account_id
        ) = self.long_term_loan_account_id = False

    def get_default_name(self, vals):
        return self.env["ir.sequence"].next_by_code("account.loan")

    @api.model
    def create(self, vals):
        if vals.get("name"):
            vals["name"] = self.get_default_name(vals)
        return super().create(vals)

    def post(self):
        print("\n\npost===== post============= ", self)
        self.ensure_one()
        if not self.start_date:
            self.start_date = fields.Date.today()
        self.compute_draft_lines()
        self.write({"state": "posted"})

    def close(self):
        self.write({"state": "closed"})

    def compute_lines(self):
        self.ensure_one()
        if self.state == "draft":
            return self.compute_draft_lines()
        return self.compute_posted_lines()

    def compute_posted_lines(self):
        """
        Recompute the amounts of not finished lines. Useful if rate is changed
        """
        amount = self.loan_amount
        for line in self.line_ids.sorted("sequence"):
            if line.move_ids:
                amount = line.final_pending_principal_amount
            else:
                line.rate = self.rate_period
                line.pending_principal_amount = amount
                line.check_amount()
                amount -= line.payment_amount - line.interests_amount
        if self.long_term_loan_account_id:
            self.check_long_term_principal_amount()

    def check_long_term_principal_amount(self):
        """
        Recomputes the long term pending principal of unfinished lines.
        """
        lines = self.line_ids.filtered(lambda r: not r.move_ids)
        print("\n\ncheck_long_term_principal_amount===== lines=============", lines)
        amount = 0
        if not lines:
            return
        final_sequence = min(lines.mapped("sequence"))
        print("\n\nfinal_sequence===== final_sequence=============", final_sequence)
        for line in lines.sorted("sequence", reverse=True):
            date = line.date + relativedelta(months=12)
            if self.state == "draft" or line.sequence != final_sequence:
                line.long_term_pending_principal_amount = sum(
                    self.line_ids.filtered(lambda r: r.date >= date).mapped(
                        "principal_amount"
                    )
                )
            line.long_term_principal_amount = (
                    line.long_term_pending_principal_amount - amount
            )
            amount = line.long_term_pending_principal_amount

    def new_line_vals(self, sequence, date, amount):
        return {
            "loan_id": self.id,
            "sequence": sequence,
            "date": date,
            "pending_principal_amount": amount,
            "rate": self.rate_period,
        }

    def compute_draft_lines(self):
        self.ensure_one()
        self.fixed_periods = self.periods
        self.fixed_loan_amount = self.loan_amount
        self.line_ids.unlink()
        amount = self.loan_amount
        if self.start_date:
            date = self.start_date
        else:
            date = datetime.today().date()
        delta = relativedelta(months=self.method_period)
        if not self.payment_on_first_period:
            date += delta
        for i in range(1, self.periods + 1):
            line = self.env["account.loan.line"].create(
                self.new_line_vals(i, date, amount)
            )
            line.check_amount()
            date += delta
            amount -= line.payment_amount - line.interests_amount
        if self.long_term_loan_account_id:
            self.check_long_term_principal_amount()

    def view_account_moves(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_line_form")
        result = action.read()[0]
        result["domain"] = [("loan_id", "=", self.id)]
        return result

    def view_account_invoices(self):
        self.ensure_one()
        action = self.env.ref("account.action_move_out_invoice_type")
        result = action.read()[0]
        result["domain"] = [("check_amount", "=", self.id), ("move_type", "=", "in_invoice")]
        return result

    @api.model
    def generate_loan_entries(self, date):
        """
        Generate the moves of unfinished loans before date
        :param date:
        :return:
        """
        res = []
        for record in self.search(
                [("state", "=", "posted"), ("is_leasing", "=", False)]
        ):
            lines = record.line_ids.filtered(
                lambda r: r.date <= date and not r.move_ids
            )
            res += lines.generate_move()
        return res

    @api.model
    def generate_leasing_entries(self, date):
        res = []
        for record in self.search(
                [("state", "=", "posted"), ("is_leasing", "=", True)]
        ):
            res += record.line_ids.filtered(
                lambda r: r.date <= date and not r.move_ids
            ).generate_invoice()
        return res

    def update_price_product(self):
        move_list = []
        for rec in self.line_ids:
            print("\n\n\n\n\n\n\n\n rec==================",rec)
            move_id = self.env["account.move"].create({
                "move_type": "out_invoice",
                "partner_id": rec.loan_id.partner_id.id,
                'invoice_date': '2020-01-10',
                'loan_id': rec.loan_id.id,
                'state': 'draft',
                'invoice_line_ids': [(0, 0, {
                                        "product_id": self.env['product.product'].sudo().search([('name', '=', 'principal')], limit=1).id,
                                        'price_unit': 500.0}),
                                     (0, 0, {
                                         'product_id': self.env['product.product'].sudo().search([('name', '=', 'Insurance')], limit=1).id,
                                         'price_unit': 150.0 }),
                                     (0, 0, {
                                         'product_id': self.env['product.product'].sudo().search([('name', '=', 'Tax')], limit=1).id,
                                         'price_unit': 200.0})
                                     ],
            })
            print(".....inv/..............", move_id)
            move_list.append(move_id)
        print("\n\n\n move_list.............", move_list)

    def extra_payments(self):
        pass

    def Postpone_installments(self):
        pass
