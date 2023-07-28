from odoo import fields, models


class SendMail(models.TransientModel):
    _name = 'send.mail'

    def send_employee_mail(self):
        self.ensure_one()
        template_id = self._find_mail_template()
        # lang = self.env.context.get('lang')
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        # ctx = {
        #     'default_model': 'employee.details',
        #     'default_res_id': self.ids[0],
        #     'default_use_template': bool(template_id),
        #     'default_template_id': template_id,
        #     'default_composition_mode': 'comment',
        #     'mark_so_as_sent': True,
        #     'custom_layout': "mail.mail_notification_paynow",
        #     'proforma': self.env.context.get('proforma', False),
        #     'force_email': True,
        #     # 'model_description': self.with_context(lang=lang).type_name,
        # }
        # return {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'form',
        #     'res_model': 'mail.compose.message',
        #     'views': [(False, 'form')],
        #     'view_id': False,
        #     'target': 'new',
        #     'context': ctx,
        # }

