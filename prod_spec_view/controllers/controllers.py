# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json

class ProdSpecView(http.Controller):
	@http.route('/prod_spec_view/get_data/', type='json', auth='user')
	def index(self, id, model, **kw):
		sale_id = id
		sale_order = ""
		if model == "work.order.quotation":
			work_order = request.env['work.order.quotation'].sudo().search([('id', '=', id)])
			if len(work_order) > 1 or len(work_order) == 0:
				return {'status': False, 'desc': "Error in retrieving Work Order"}
			else:
				sale_id = work_order.sale_id.id
				if not sale_id:
					return {'status':False, 'desc':"Error in retrieving Sale Order"}
				order = request.env['sale.order'].sudo().search([('id','=',sale_id)])
				for i in order:
					sale_order = request.env['sale.order'].sudo().search([('name','=',i.origin)])
		elif model == "sale.order":		
			sale_order = request.env['sale.order'].sudo().search([('id','=',sale_id)])
			if "/OA" in sale_order.name:
				sale_order = request.env['sale.order'].sudo().search([('name','=',sale_order.origin)])
			if len(sale_order) > 1 or len(sale_order) == 0:
				return {'status':False, 'desc':"Error in retrieving Sale Order"}
		else:
			return {'status':False, 'desc':"Not Compatible"}
		counter = -1
		res = {}
		res['sale_order_lines'] = []
		for i in sale_order:
			if i.origin:
				o_sale_order = request.env['sale.order'].sudo().search([('name','=',i.origin)])
				if len(o_sale_order) == 1:
					for j in o_sale_order.order_line:
						res['sale_order_lines'].append({'product_name':j.product_id.name,})
						counter+=1
						spec_lines = request.env['product.specification.line'].sudo().search([('order_line_id', '=', j.id)])
						res['sale_order_lines'][counter]['specs'] = []
						specs = {}
						for l in spec_lines:
							res['sale_order_lines'][counter]['specs'].append({'product_specification1':l.product_specification1,'product_specification2':l.product_specification2,'product_specification3':l.product_specification3,'product_specification4':l.product_specification4,'product_specification5':l.product_specification5,'product_specification6':l.product_specification6,})
					# print({'status':True,'res':res})
					return {'status':True,'res':res}
				else:
					return {'status':False, 'desc':"Error in retrieving Sale Order"}
			for j in i.order_line:
				# print("coming2")
				res['sale_order_lines'].append({'product_name':j.product_id.name,})
				counter+=1
				spec_lines = request.env['product.specification.line'].sudo().search([('order_line_id', '=', j.id)])
				res['sale_order_lines'][counter]['specs'] = []
				specs = {}
				for l in spec_lines:
					res['sale_order_lines'][counter]['specs'].append({'product_specification1': l.product_specification1,'product_specification2':l.product_specification2,'product_specification3':l.product_specification3,'product_specification4':l.product_specification4,'product_specification5':l.product_specification5,'product_specification6':l.product_specification6,})
			# print({'status': True, 'res': res})
			return {'status': True, 'res': res}