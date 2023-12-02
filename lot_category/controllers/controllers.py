# -*- coding: utf-8 -*-
from odoo import http

# class LotCategory(http.Controller):
#     @http.route('/lot_category/lot_category/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lot_category/lot_category/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lot_category.listing', {
#             'root': '/lot_category/lot_category',
#             'objects': http.request.env['lot_category.lot_category'].search([]),
#         })

#     @http.route('/lot_category/lot_category/objects/<model("lot_category.lot_category"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lot_category.object', {
#             'object': obj
#         })