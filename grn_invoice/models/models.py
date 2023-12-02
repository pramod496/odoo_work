# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import namedtuple
import json
import time

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
import datetime
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
import pdb


class Picking(models.Model):
    _inherit = "stock.picking"

    destination_warehouse = fields.Many2one('stock.warehouse', string="Destination Warehouse")
    account_ids = fields.Many2one('account.move', string="Accounting")
    is_invoiced = fields.Boolean('Boolean', default=False,)

    
    def refund_inv(self):
        # res = super(StockInv, self)._onchange_vendor_bill()


        vals_item = {}
        vals_line_item = {}
        if self.is_invoiced ==False:
            active_ids = self._context.get('active_ids', [])

            inv_obj = self.env['account.move']
            invl_obj = self.env['account.move.line']
            # invref_obj = self.env['account.move.refund']
            

            list = []
            # if self.type in ('in_invoice', 'in_refund')
            tax_lines = []
            for pick_line in self.move_ids_without_package:
                
                #if pick_line.taxes_id:
                    #for tax in pick_line.taxes_id:
                        #tax_lines.append(tax.id)
                
                list.append((0, 0, {
                    'product_id': pick_line.product_id.id,
                    'name': pick_line.product_id.name,
                    # 'invoice_date': pick_line.date_deadline,
                    'quantity': pick_line.quantity_done,
                    'product_uom_id': pick_line.product_uom.id,
                    'price_unit': pick_line.price_unit,
                    'discount' : pick_line.discount,
                    'account_id': self.partner_id.property_account_payable_id.id,
                    'tax_ids': [(6, 0, pick_line.taxes_id.ids)],
                    'po_name':pick_line.po_ref.id,
                    'price_subtotal':pick_line.price_subtotal,


                }))
                # self.write({'extract_word_ids': data})

            self.account_ids = inv_obj.create({
                'type': 'in_invoice',
                'partner_id': self.partner_id.id,
                'state': 'draft',
                # 'number': 'New',
                'invoice_line_ids': list,
                'invoice_date': fields.Date.today(),
                'origin': self.name,
                'account_receipt': True,
                #'product':self.product.id,
                # 'vendor_bill_purchase_id' : picking_id.name,
                # 'filter_refund': 'refund',

            })
            # print(self.account_ids,self.account_ids.invoice_line_ids,'account ids')

            # self.account_ids = inv_obj.create({'invoice_line_ids':list})
            # self.account_ids.create({'invoice_line_ids':list})
            self.account_ids.write({'invoice_line_ids':list})

            # for line in self.account_ids.invoice_line_ids:
            #     if line.po_name.order_line:
            #         for el in line.po_name.order_line:
            #             if el.product_id == line.product_id:
            #                 line.quantity = el.product_qty
            #                 line.price_unit = el.price_unit

            # raise UserError('wait here')
            self.is_invoiced=True

    
    def action_view_account(self):
        # print ('ssssssssssssssssssssssssssssssssssssssssssss')

        # action = self.env.ref('account.view_move_form').read()[0]
        action = self.env.ref('sale_to_mrp.account_inherited_form_view').read()[0]

        account_ids = self.mapped('account_ids')
        if len(account_ids) > 1:
            action['domain'] = [('id', 'in', account_ids.ids)]
        elif account_ids:
            # action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['views'] = [(self.env.ref('sale_to_mrp.account_inherited_form_view').id, 'form')]
            action['res_id'] = account_ids.id

        # view_id = self.env.ref('account.view_move_form')
        view_id = self.env.ref('sale_to_mrp.account_inherited_form_view')
        # print('hr')
        # raise UserError('wait soyeb')

        return {
            'name': _('New Quotation'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            'view_id': view_id.id,
            'views': [(view_id.id, 'form')],
            'res_id': account_ids.id
        }


# class StockInv(models.TransientModel):
# 	_inherit = 'stock.backorder.confirmation'
#
#
# 		print (picking_id.partner_id.name,pick_line.name,'mmmmmmmmmmmmmmmmmmmmmmmmmmm')

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    account_receipt = fields.Boolean(default=False,
                                     help="Set active to false to hide the Account Tag without removing it.")
    product = fields.Many2one('product.product','Product')
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        readonly=True,
        states={'draft': [('readonly', False)]})
    
    picking_type_code = fields.Selection([
        ('incoming', 'Vendors'),
        ('outgoing', 'Customers'),
        ('internal', 'Internal')], related='picking_type_id.code',
        readonly=True,store=True)

    #
    # def action_invoice_open(self):
    #     res = super(AccountInvoiceInherit, self).action_invoice_open()
        

class AccountInvoiceLineInherited21(models.Model):
    _inherit = 'account.move.line'

    po_name = fields.Many2one('purchase.order', string='PO Ref#', default=False)


class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'


    
    def _process(self, cancel_backorder=False):
        if cancel_backorder:
            for pick_id in self.pick_ids:
                moves_to_log = {}
                for move in pick_id.move_lines:
                    if float_compare(move.product_uom_qty, move.quantity_done, move.product_uom.rounding) > 0:
                        moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
                pick_id._log_less_quantities_than_expected(moves_to_log)
        self.pick_ids.action_done()

        # res = super(StockInv, self)._onchange_vendor_bill()

        vals_item = {}
        vals_line_item = {}
        if cancel_backorder:
            for pick_id in self.pick_ids:
                backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', pick_id.id)])
                active_ids = backorder_pick._context.get('active_ids', [])
                print (active_ids)

                inv_obj = self.env['account.move']
                invl_obj = self.env['account.move.line']
                # invref_obj = self.env['account.move.refund']

                list = []
                # if self.type in ('in_invoice', 'in_refund')
                tax_lines = []
                account_id_id=False
                journal_id_id =False
                if backorder_pick.picking_type_id.code =='incoming':
                    for pick_line in backorder_pick.move_ids_without_package:
                        # if pick_line.taxes_id:
                        # for tax in pick_line.taxes_id:
                        # tax_lines.append(tax.id)
                        account_id_id=self.env['account.account'].search([('name','=', 'Purchase Expense')])
                        journal_id_id = self.env['account.journal'].search([('name', '=', 'Vendor Bills')])

                        list.append((0, 0, {
                            'product_id': pick_line.product_id.id,
                            'name': pick_line.product_id.name,
                            'invoice_date': pick_line.date_expected,
                            'quantity': pick_line.product_uom_qty,
                            'uom_id': pick_line.product_uom.id,
                            'price_unit': pick_line.price_unit,
                            'account_id':account_id_id.id,
                            # 'account_id': backorder_pick.partner_id.property_account_payable_id.id,
                            'invoice_line_tax_ids': [(6, 0, pick_line.taxes_id.ids)],

                        }))

                    backorder_pick.account_ids = inv_obj.create({
                        'type': 'in_refund',
                        'partner_id': backorder_pick.partner_id.id,
                        'state': 'draft',
                        # 'number': 'New',
                        'invoice_line_ids': list,
                        'invoice_date': fields.Date.today(),
                        'origin': backorder_pick.backorder_id.name,
                        'account_receipt': True,
                        'journal_id':journal_id_id.id,
                        # 'product':self.product.id,
                        # 'vendor_bill_purchase_id' : picking_id.name,
                        # 'filter_refund': 'refund',

                    })

                backorder_pick.action_cancel()
                pick_id.message_post(body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))

        
        