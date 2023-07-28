from odoo import fields, models,api
from odoo.exceptions import AccessError


class GetProduct(models.Model):
    _inherit = 'product.template'
    
    def get_report_wizard(self):
        l=[]
        for bom in self.bom_ids.bom_line_ids:
            l.append(bom.id)

        return {
            'name': 'Product Details',
            'res_model': 'product.reports',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self,
                'default_name': [(6, 0, l)],
            },
        }

    