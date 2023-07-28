from odoo import fields, models, api
from datetime import datetime


class FieldAdd(models.Model):
    _inherit = 'sale.order'

    delivery_date = fields.Date(string="Delhivery Date")


    # def action_confirm(self):
    #     res = super(FieldAdd,self).action_confirm()
    #     print(self.picking_ids)
    #     self.picking_ids.move_ids_without_package.quantity_done =4
    #     return res
   
# compute='_get_delhivery_date'
    # @api.depends('picking_ids')
    # def _get_delhivery_date(self):
    #     # print('================get_delhivery_date')
    #     for rec in self:
    #         # print('============================record',rec)
    #         # if rec.order_line.product_uom_qty == rec.order_line.qty_delivered:
    #         if rec.picking_ids:
            

    #             for picking_dates in rec.picking_ids:
    #                 # if picking_dates.date:
    #                 rec.delivery_date=picking_dates.date
    #         else:

    #             rec.delivery_date =''


    # def action_confirm(self):
    #     if self.delivery_date:
    #         self.delivery_date = self._get_delhivery_date()
    #     res = super(FieldAdd,self).action_confirm()

    #     return res



