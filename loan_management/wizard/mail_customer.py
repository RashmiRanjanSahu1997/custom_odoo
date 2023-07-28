from odoo import models, fields,api


class SendMail(models.TransientModel):
    _name = 'mail.customer'

    name = fields.Many2many('res.partner',string='Recipients')
    sub = fields.Char('Subject')
    body = fields.Html()
    attachment_ids = fields.Many2many('ir.attachment','Attachment')


    def send_mail(self):
        temp_id = self.env.ref('loan_management.send_loan_mail_template')
        temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)

