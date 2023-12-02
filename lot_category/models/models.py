# -*- coding: utf-8 -*-

from odoo import models, fields, api

# class lot_category(models.Model):
#     _name = 'lot_category.lot_category'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100

class IrSequence(models.Model):
	_inherit = 'ir.sequence'

	category_id = fields.Many2one('product.category', string="Category", copy=False)

class ProductionLotCategory(models.Model):
	_inherit = 'stock.production.lot'

	name = fields.Char('Lot/Serial Number', required=True, help="Unique Lot/Serial Number")


class ProductCategory(models.Model):
	_inherit = "product.category"

	@api.model
	def create(self, vals):
		res = super(ProductCategory, self).create(vals)
		yr = str(fields.Datetime.now().year)
		nextyr = str(fields.Datetime.now().year + 1)
		code_str = 'stock.lot.serial.' +vals.get('name').lower()
		new_code = code_str.replace(" ", ".")
		if vals.get('name'):
			self.env['ir.sequence'].create({
				'name': vals.get('name')+' '+ 'Sequence',
				'code': new_code,
				'prefix': vals.get('name')+yr[2:]+nextyr[2:],
				'implementation': 'standard',
				'active': True,
				'number_next': 1,
				'number_increment':1,
				'padding': 4,
				'company_id': False,
				'category_id': res.id,
				})
		return res

	def _category_sequence_create(self):
		categories = self.search([])
		if categories:
			for category in categories:
				sequence_exist = self.env['ir.sequence'].search([('category_id','=', category.id)])
				if not sequence_exist:
					yr = str(fields.Datetime.now().year)
					nextyr = str(fields.Datetime.now().year + 1)
					code_str = 'stock.lot.serial.' +category.name.lower()
					new_code = code_str.replace(" ", ".")
					category_seq = self.env['ir.sequence'].create({
						'name': category.name+' '+ 'Sequence',
						'code': new_code,
						'prefix': category.name+yr[2:]+nextyr[2:],
						'implementation': 'standard',
						'active': True,
						'number_next': 1,
						'number_increment':1,
						'padding': 5,
						'company_id': False,
						'category_id': category.id,
						})



