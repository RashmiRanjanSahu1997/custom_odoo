
from enum import Flag
from odoo import fields, models, api
from odoo.exceptions import AccessError


class ExportExcel(models.Model):
    _name = 'export.excel'
    
    name = fields.Char('Action Name')
    model_id = fields.Many2one('ir.model', string="Applies to")
    is_company_detail = fields.Boolean(string="Print Company Details")
    is_print_sum = fields.Boolean(string="Print Sum")
    sub_model_id = fields.Many2one('ir.model', string="Sub Model")
    is_group_by =  fields.Boolean('Group By')
    is_active = fields.Boolean('Active')
    field_ids = fields.Many2many(
        'ir.model.fields',
        string="Field",
        domain="[('model_id', '=', model_id)]"
    )
    is_send_report = fields.Boolean(compute='_compute_is_send_report')

    sheet_name = fields.Char('Excel Sheet Name',default='Account Move Line')
    header_text = fields.Char('Header Text',default='Account Move Line xls Report')
    bg_color = fields.Char('Sum Background Color',default='#eaebed')
    font_color = fields.Char('Total Font Color',default='black')

    #Company Style
    ctext_style = fields.Char('Company Text style',default='calibri')
    ct_size = fields.Integer('Text Size',default=10)
    ct_color = fields.Char('Text Color',default='black')
    ct_bg_color = fields.Char('Background Color',default='white')
    ct_bold = fields.Boolean('Bold',)
    ct_italic = fields.Boolean('Italic')
    ct_underline = fields.Boolean('Underline')
    ct_text_align = fields.Selection([('left','Left'),('right','Right'),
                            ('center','Center'),('top','Top')],default='left')
    ct_border = fields.Boolean('Border')
    ct_border_color = fields.Char('Border Color')

    #Header Style
    htext_style = fields.Char('Company Text style',default='calibri')
    ht_size = fields.Integer('Text Size',default=15)
    ht_color = fields.Char('Text Color',default='black')
    ht_bg_color = fields.Char('Background Color',default='white')
    ht_bold = fields.Boolean('Bold',default=True)
    ht_italic = fields.Boolean('Italic')
    ht_underline = fields.Boolean('Underline')
    ht_text_align = fields.Selection([('left','Left'),('right','Right'),
                            ('center','Center'),('top','Top')],default='center')
    ht_border = fields.Boolean('Border')
    ht_border_color = fields.Char('Border Color')

    #Group Style
    gtext_style = fields.Char('Company Text style',default='calibri')
    gt_size = fields.Integer('Text Size',default=10)
    gt_color = fields.Char('Text Color',default='black')
    gt_bg_color = fields.Char('Background Color',default='yellow')
    gt_sub_color = fields.Char('Subgroup Background Group',default='#c6c6c6')
    gt_bold = fields.Boolean('Bold',default=True)
    gt_italic = fields.Boolean('Italic')
    gt_underline = fields.Boolean('Underline')
    gt_text_align = fields.Selection([('left','Left'),('right','Right'),
                    ('center','Center'),('top','Top')],default='left')
    gt_border = fields.Boolean('Border')
    gt_border_color = fields.Char('Border Color')

    _sql_constraints = [
        ('model_id_uniq', 'unique (model_id)','Already Exist this model')
    ]

    def create_server_action(self):
        server_action = self.env["ir.actions.server"].search([('name','=',self.name)])
        if not server_action:
            server_action=self.env["ir.actions.server"].create({
                'model_id': self.model_id.id,
                'state': 'code',
                'name': self.name,
                'code': "action = env['excel.report'].get_export_excel_wizard()"
                })
        server_action.create_action()

    def unlink_server_action(self): 
        unlink_actions = self.env['ir.actions.server'].search([('name','=',self.name)])
        unlink_actions.unlink_action()

    def _compute_is_send_report(self):
        for rec in self:
            server_action = self.env['ir.actions.server'].search([('name','=',rec.name),
                                                                    ('binding_model_id', '!=', False)])
            rec.is_send_report = server_action and True or False
