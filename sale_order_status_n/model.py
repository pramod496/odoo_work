# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import  models, fields, api
import pdb


class SaleOrderStatus(models.Model):
	_inherit = 'sale.order'
	
	demo_line = fields.One2many('status.sale.order1', 'demo_id', string='Sale Order Status')
	attach_file_ids = fields.Many2many('ir.attachment', 'so_attach_rel', 'sale', 'attach', string="Attach Files")

	
	def write(self, values):
		# pdb.set_trace()
		status_id=None
		# print(values.get('demo_line'))
		if values.get('demo_line'):
			for i in values.get('demo_line'):
				if i[2] == False or i[0] == 0:
					continue
				if i[2].get('status') and i[2].get('description'):
					status_id = self.demo_line.filtered(lambda line: line.id == i[1] and line.demo_id.id == self.id)
				elif i[2].get('status'):
					# print(i[1], self.id)
					status_id = self.demo_line.filtered(lambda line: line.id == i[1] and line.demo_id.id == self.id)			
				if status_id:
					mail_details = {'subject': "Sale order status update",
					 'body': "Dear "+status_id.demo_id.partner_id.name +",<br/>Your order status of "+ status_id.description.name+" has been changed from "+status_id.status + " to "+i[2].get('status'),
					 'partner_ids': [(status_id.demo_id.partner_id.id)]
					 }
					mail = self.env['mail.thread']
					mail.message_post(type="notification", subtype="mt_comment", **mail_details)
		result = super(SaleOrderStatus, self).write(values)
		return result




	


class StatusMaster(models.Model):		
	_name = "status.master"
	_description = "Status Master"

	name = fields.Char(string='Name')


class StatusSaleOrder1(models.Model):
	_name = 'status.sale.order1'
	_description = 'Status sale order' 

	name =fields.Char(string='Name')    
	demo_id = fields.Many2one('sale.order', string='Order Reference')  
	status = fields.Selection([('inprogress','Inprogress'), ( 'completed','Completed')],string='Status')
	description = fields.Many2one('status.master', string='Description')    
	remark = fields.Char(string='Remark')



