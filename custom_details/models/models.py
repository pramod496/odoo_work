# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from odoo import api, fields, models, _


class VendorCodeCustomer(models.Model):
	_inherit = "res.partner"
	vendor_code = fields.Char('Vendor Code')
	vendor_id = fields.Many2one('crm.lead' , string="Type")
	product_details = fields.Many2many('product.template', string="Product Details")

class VendorCrmProduct(models.Model):
	_inherit = "crm.lead"
	lead_id = fields.One2many('res.partner', 'vendor_id', 'Others')
	# vendor_id = fields.One2many('res.Partner', string="Type")

class VendorCrmLead(models.Model):
	_inherit = "crm.lead"
	fax_number = fields.Char('Fax')
	depatmnt = fields.Char('Department')
	vendor_region=fields.Char('Region')
	save_date=fields.Date('Save Date')

class MrpBOM(models.Model):
	_inherit = "mrp.bom"

class SaleOrder(models.Model):
	_inherit = "sale.order"

class PurchaseOrder(models.Model):
	_inherit = "purchase.order"

class AccountInvoice(models.Model):
	_inherit = "account.move"

class StockPicking(models.Model):
	_inherit = "stock.picking"

class MrpProduction(models.Model):
	_inherit = "mrp.production"

# class WorkOrderQuotation(models.Model):
# 	_inherit = "work.order.quotation"
