from odoo import fields, models


class GetReports(models.TransientModel):

    _name = 'product.reports'

    name = fields.Many2many('mrp.bom.line',string="Product")
    # bom = fields.Char(string="BOM")
    # quantities = fields.Integer('Quantities')
    # price = fields.Integer('Price')

    # @api.model
    # def default_get(self,fields):
        
    #     active = self.env.context.get('active_id')
    #     product = self.env["mrp.bom"].browse(active)
    #     self.name = [(6, 0, [16, 17])]
    #     for rec in product.bom_line_ids:
    #         new=self.env["mrp.bom.line"].browse(rec.id).product_id
    #         self.name=[(6, 0, [new.name])]
    #     values = super(GetReports,self).default_get(fields)
        # res = super(GetReports,self).default_get(fields)
        

       
        # return values
        # bom = self.env['mrp.bom'].browse(bom_id)
        # active_id = bom.product_uom_id
        # print('active id',bom)
         # print('==============',res)
        # active_id  = self.env.context.get('id')
        # print('active id',active_id')
            





