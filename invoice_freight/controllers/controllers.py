# -*- coding: utf-8 -*-
from odoo import http

# class InvoiceFreight(http.Controller):
#     @http.route('/invoice_freight/invoice_freight/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_freight/invoice_freight/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_freight.listing', {
#             'root': '/invoice_freight/invoice_freight',
#             'objects': http.request.env['invoice_freight.invoice_freight'].search([]),
#         })

#     @http.route('/invoice_freight/invoice_freight/objects/<model("invoice_freight.invoice_freight"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_freight.object', {
#             'object': obj
#         })