# -*- coding: utf-8 -*-
# from odoo import http


# class LoanManagement(http.Controller):
#     @http.route('/loan__management/loan__management', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loan__management/loan__management/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('loan__management.listing', {
#             'root': '/loan__management/loan__management',
#             'objects': http.request.env['loan__management.loan__management'].search([]),
#         })

#     @http.route('/loan__management/loan__management/objects/<model("loan__management.loan__management"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loan__management.object', {
#             'object': obj
#         })
