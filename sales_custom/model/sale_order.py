from odoo import fields,models,api,_


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    states = fields.Selection(selection=[('draft', 'Draft'),
                                        ('sfa', 'Submit For Approval'),
                                        ('approved', 'Approved'),
                                        ('rejected', 'Rejected')], string='Status', default='draft')
    reason = fields.Char('Reason')

    def sub_approval(self):
        setting_price =int(self.env['ir.config_parameter'].sudo().get_param('sale_amount', False))
        setting_user = int(self.env['ir.config_parameter'].sudo().get_param('sales_manager', False))
        user = self.env['res.users'].browse([(setting_user)])
        context = dict(self.env.context)
        context.update({'email': user.login})
        self.env.context = context
        if int(self.amount_total)>= setting_price:
            temp_id = self.env.ref('sales_custom.approve_sales_mail_template')
            temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
            self.states='sfa'
        else:
            self.states = 'approved'
            temp_id = self.env.ref('sales_custom.sales_submit_mail_template')
            temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)

    @api.model
    def create(self, vals):
        setting_price =int(self.env['ir.config_parameter'].sudo().
                                            get_param('sale_amount', False))
        product = super(SaleOrder,self).create(vals)
        if product.amount_total <= setting_price:
            product.states ='approved'
            temp_id = self.env.ref('sales_custom.sales_submit_mail_template')
            temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
        return product

    def set_rejection(self):
        self.states ='rejected'
        temp_id = self.env.ref('sales_custom.reject_sale_mail_template')
        temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
        return {
            'name': _('Reason for Rejection'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'reason.details',
            'target': 'new',
        }
    
    def set_approved(self):
        self.states ='approved'
        temp_id = self.env.ref('sales_custom.sales_submit_mail_template')
        temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
    
    def write(self, vals):
        setting_price =float(self.env['ir.config_parameter'].sudo().get_param('sale_amount', False))
        res = super(SaleOrder,self).write(vals)
        if vals.get('order_line'):
            if self.amount_total>=setting_price:
                self.states = 'draft'
            else:
                self.states = 'approved'
                temp_id = self.env.ref('sales_custom.sales_submit_mail_template')
                temp_id.with_context(self.env.context).send_mail(self.id, force_send=True)
        return res

    