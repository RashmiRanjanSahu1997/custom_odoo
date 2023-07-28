from odoo import models,fields


class ResConfigSettings(models.TransientModel):
   _inherit = 'res.config.settings'

   sale_amount = fields.Integer('Amount', config_parameter="sale_amount")
   sales_manager = fields.Many2one('res.users','Manager', 
                                    config_parameter="sales_manager")
    


