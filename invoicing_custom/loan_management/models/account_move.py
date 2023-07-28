

from odoo import fields, models


class AccountMove(models.Model):
    _inherit = "account.move"

    loan_line_id = fields.Many2one(
        "account.loan.line",
        readonly=True,
        ondelete="restrict",
    )

    loan_id = fields.Many2one(
        "account.loan",
        readonly=True,
        store=True,
        ondelete="restrict",
    )

    def action_post(self):
        res = super().action_post()
        for record in self:
            loan_line_id = record.loan_line_id
            if loan_line_id:
                if not record.loan_line_id:
                    record.loan_line_id = loan_line_id
                record.loan_id = loan_line_id.loan_id
                record.loan_line_id.check_move_amount()
                record.loan_line_id.loan_id.compute_posted_lines()
                if record.loan_line_id.sequence == record.loan_id.periods:
                    record.loan_id.close()
        return res

class AccountPaymentss(models.Model):
    _inherit = "account.payment"

    loan_id = fields.Many2one('account.loan', store=True,)


    def _create_payments(self):
        print("\n\n\n _create_payments---------------------------",self._context)
        self.ensure_one()
        batches = self._get_batches()
        edit_mode = self.can_edit_wizard and (len(batches[0]['lines']) == 1 or self.group_payment)
        to_process = []

        move_id = self.env['account.move'].sudo().browse(self._context.get('active_id'))
        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard()
            print("\n\n\n\n\n\n\n\n\n payment_vals =========",payment_vals)
            payment_vals['loan_id'] = move_id.loan_id.id if move_id and move_id.loan_id else False
            to_process.append({
                'create_vals': payment_vals,
                'to_reconcile': batches[0]['lines'],
                'batch': batches[0],
            })
        else:
            # Don't group payments: Create one batch per move.
            if not self.group_payment:
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        new_batches.append({
                            **batch_result,
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        self._post_payments(to_process, edit_mode=edit_mode)
        self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments

# class AccountPaymentssTransaction(models.Model):
#     _inherit = "payment.transaction"
#
#     loan_id = fields.Many2one('account.loan', store=True,)

