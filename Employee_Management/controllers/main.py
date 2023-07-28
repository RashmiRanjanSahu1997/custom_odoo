from odoo import http, _
from odoo.http import request


class SalesDetails(http.Controller):

    @http.route('/sales/customer/<int:c_id>', methods = ['GET'], 
                        type='http', auth='public', csrf=False)
    def order_details(self,c_id,**kwargs):
        order_id = request.env['sale.order'].sudo().search([('id','=',c_id)])
        values = {
            'Sl No':order_id.name,
            'customer':order_id.partner_id.name,
            'Total Price':order_id.tax_totals_json
            }
        
        return str(values)