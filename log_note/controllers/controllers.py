# -*- coding: utf-8 -*-
from odoo import http

# class LogNote(http.Controller):
#     @http.route('/log_note/log_note/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/log_note/log_note/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('log_note.listing', {
#             'root': '/log_note/log_note',
#             'objects': http.request.env['log_note.log_note'].search([]),
#         })

#     @http.route('/log_note/log_note/objects/<model("log_note.log_note"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('log_note.object', {
#             'object': obj
#         })