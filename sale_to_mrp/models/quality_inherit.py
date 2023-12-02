# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import namedtuple
import json
import time
from datetime import date
import pdb

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta


class QualityCheck(models.Model):
    _inherit = "quality.check"

    check_deviation = fields.Boolean(default=False,string='Accept with Deviation')

    def do_measure(self):
        self.ensure_one()
        if self.check_deviation:
            return self.do_pass()
        else:
            if self.measure < self.point_id.tolerance_min or self.measure > self.point_id.tolerance_max:
                return {
                    'name': _('Quality Check Failed'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'quality.check',
                    'view_mode': 'form',
                    'view_id': self.env.ref('quality_control.quality_check_view_form_failure').id,
                    'target': 'new',
                    'res_id': self.id,
                    'context': self.env.context,
                }
            else:
                return self.do_pass()


class QualityPointInherit(models.Model):
    _name = "quality.parameter"

    name = fields.Char(string='name')
    category_id = fields.Many2one('product.category', 'Category', index=True, ondelete='cascade')


class ProductCategory(models.Model):
    _inherit = "product.category"

    parameter_ids = fields.One2many('quality.parameter', 'category_id', 'Parameter')

    def create_control_points(self):
        pickingtype = False
        products = self.env['product.template'].search([('categ_id','=',self.id)])
        for product in products:
            subcontract = False
            shopfloor = False
            for bom in product.bom_ids:
                if bom.operation_ids:
                    subcontract = bom.operation_ids.subcontract
                    shopfloor = bom.operation_ids.shoop_floor
                
            buy = False
            mrp = False
            mto = False
            if product.route_ids:
                for route in product.route_ids:
                    if route.name == 'Buy':
                        buy = True
                    if route.name == 'Manufacture':
                        mrp = True
                    if route.name == 'Make To Order':
                        mto = True
                        
            if buy == True:
                pickingtype = self.env['stock.picking.type'].search([('name','=', 'Receipts')])
            if mrp == True and mto == True:
                pickingtype = self.env['stock.picking.type'].search([('code','=', 'internal'),('mrp_confirm','=',True)])
            if mrp == True and mto == False:
                # pickingtype = self.env['stock.picking.type'].search([('name','=', 'Manufacturing')])
                if subcontract:
                    pickingtype = self.env['stock.picking.type'].search([('code','=', 'mrp_operation'),('subcontract','=',True)])
                elif shopfloor:
                    pickingtype = self.env['stock.picking.type'].search([('code','=', 'mrp_operation'),('shoop_floor','=',True)])
                else:
                    pickingtype = self.env['stock.picking.type'].search([('code','=', 'mrp_operation'),('shoop_floor','=',False),('subcontract','=',False)])                

            for parameter in self.parameter_ids:
                available_parameter = self.env['quality.point'].search([('title','=',parameter.name),('product_tmpl_id','=',product.id)])
                if not available_parameter:
                    # if pickingtype[0].code != 'mrp_operation':
                    self.env['quality.point'].create({'title':parameter.name,
                        'product_ids': [product.product_variant_id.id],
                        'product_tmpl_id': product.id,
                        'picking_type_ids': [pickingtype.id] if pickingtype else False})
        return True


class QualityPointInherit(models.Model):
    _inherit = "quality.point"

    title = fields.Char('Parameter')
    product_tmpl_id = fields.Many2one(
        'product.template', 'Product',required=True,
        domain="[('type', 'in', ['consu', 'product']),('is_quality','=',True)]")

class ProductTemplateInherit(models.Model):
    _inherit = "product.template"

    is_quality = fields.Boolean(default=True)

class QualityCheckInherit(models.Model):
    _inherit = "quality.check"


    @api.depends('point_id')
    def get_title(self):
        for el in self:
            el.title = 0
            if el.point_id:
                el.title = el.point_id.title

    @api.depends('picking_id')
    def get_grn_qty(self):
        for record in self:
            record.grn_qty = 0.0
            if record.picking_id:
                if record.picking_id.move_ids_without_package:
                    for move in record.picking_id.move_ids_without_package:
                        if move.product_id.id == record.product_id.id:
                            record.grn_qty = move.product_uom_qty
            # else:
            #     record.picking_id = False
            #     print('ssssssss', record.picking_id)

    # @api.depends('rejected_qty')
    # def _get_rejected_qty_val(self):
    #     for record in self:
    #         qty=0
    #         if record.rejected_qty:
    #             if record.picking_id:
    #                 quality = self.env['quality.check'].search([('picking_id','=',record.picking_id.id), ('product_id', '=', record.product_id.id)])
    #                 # quality_1 = self.env['quality.check'].search(
    #                 #     [('picking_id', '=', record.picking_id.id), ('product_id', '=', record.product_id.id)],limit=1)
    #
    #                 for el in quality:
    #                     qty=qty+int(el.rejected_qty)
    #                 for move_id in record.picking_id.move_ids_without_package:
    #                     if move_id.product_id==record.product_id:
    #                         move_id.write({'rejected_qty':qty})
    #
    #     return True

    
    @api.onchange('inspected_qty')
    def _onchange_inspected_qty(self):
        for record in self:
            quality = None
            if record.inspected_qty > record.grn_qty:
                return {
                    'warning': {
                        'title': "Inspected Quantity",
                        'message': _("Please check that the Inspected Quantity is greater than GRN Quantity"),
                    }
                }
            quality = self.env['quality.check'].search([('picking_id', '=', record.picking_id.id), ('product_id', '=', record.product_id.id)])
            if quality:
                for el in quality:
                    el.write({'inspected_qty': record.inspected_qty})
    
    @api.onchange('rejected_qty')
    def _onchange_rejected_qty(self):
        for record in self:
            qty = 0
            if record.rejected_qty > (record.inspected_qty):
                raise UserError(_('Please check that the Rejected Quantity is greater than Inspected Quantity'
                                  ))
            else:
                record.sudo().update({'rejected_qty': record.rejected_qty,
                                      'rejected_qty_val':record.rejected_qty_val
                                      })




    @api.model
    def _get_work_order(self):
        for el in self:
            el.iwo_id = False
            if el.picking_id_iwo:
                wo = self.env['work.order.quotation'].search([('name','=',el.picking_id_iwo)])
                if wo:
                    for x in wo:
                        el.iwo_id = x.id
            # else:
            #     el.picking_id_iwo = 0

    point_id = fields.Many2one('quality.point', 'Control Point')
    title = fields.Char('Parameter', compute='get_title')
    inspected_qty = fields.Float('Inspected Quantity', digits=dp.get_precision('Quality Tests'))
    # inspected_qty_val =fields.Char('Inspected Qty')
    
    grn_qty = fields.Float(
        'GRN Quantity',
        digits=dp.get_precision('Product Unit of Measure'),
        default=0.0,compute='get_grn_qty')
    rejected_qty=fields.Float('Rejected Quantity',copy=False)
    rejected_qty_val = fields.Integer('Rejected Qty Val',compute="_get_rejected_qty_val", store=True)
    mo_qty = fields.Float(related='production_id.product_qty', string='IWO Qty')
    picking_id_iwo = fields.Char(related='production_id.origin', string='IWO Reference')
    iwo_id = fields.Many2one('work.order.quotation',compute=_get_work_order)

    @api.depends('rejected_qty')
    def _get_rejected_qty_val(self):
        for record in self:
            qty = 0
            if record.rejected_qty:
                if record.picking_id:
                    quality = self.env['quality.check'].search(
                        [('picking_id', '=', record.picking_id.id), ('product_id', '=', record.product_id.id)])
                    # quality_1 = self.env['quality.check'].search(
                    #     [('picking_id', '=', record.picking_id.id), ('product_id', '=', record.product_id.id)],limit=1)

                    for el in quality:
                        # print(el.rejected_qty,'rejected quantity')
                        qty = qty + int(el.rejected_qty)
                    for move_id in record.picking_id.move_ids_without_package:
                        if move_id.product_id == record.product_id:
                            move_id.write({'rejected_qty': qty})
            else:
                record.rejected_qty = 0.0
        return True

class StockMove(models.Model):
    _inherit = "stock.move"

    po_ref = fields.Many2one('purchase.order',string='PO Ref#',default=False)
    price_unit = fields.Float(string='Unit Price', digits=dp.get_precision('Product Price'))
    discount = fields.Float(string='Discount (%)', digits=dp.get_precision('Discount'))
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])

    price_subtotal = fields.Float(compute='_compute_amount', string='Subtotal', store=True)
    price_total = fields.Float(compute='_compute_amount', string='Total', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Tax', store=True)
    currency_id = fields.Many2one(related='picking_id.currency_id', store=True, string='Currency', readonly=True)
    mo_id = fields.Many2one(related='picking_id.mo_id', string="Manufacturing Order Ref")
    sale_id = fields.Many2one(related='picking_id.sale_id', string="Sale Order Ref" ,copy=False)
    rejected_qty = fields.Float('Rejected Quantity',copy=False)


    @api.depends('product_uom_qty','quantity_done', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            vals = line._prepare_compute_all_values()
            if vals.get('quantity_done') > 0.0:
                taxes = line.taxes_id.compute_all(
                    vals['price_unit'],
                    vals['currency_id'],
                    vals['quantity_done'],
                    vals['product'],
                    vals['partner'])
            else:
                taxes = line.taxes_id.compute_all(
                    vals['price_unit'],
                    vals['currency_id'],
                    vals['product_uom_qty'],
                    vals['product'],
                    vals['partner'])
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })



    def _prepare_compute_all_values(self):
        # Hook method to returns the different argument values for the
        # compute_all method, due to the fact that discounts mechanism
        # is not implemented yet on the purchase orders.
        # This method should disappear as soon as this feature is
        # also introduced like in the sales module.
        self.ensure_one()
        return {
            'price_unit': self.price_unit,
            'currency_id': self.picking_id.currency_id,
            'quantity_done': self.quantity_done,
            'product_uom_qty': self.product_uom_qty,
            'product': self.product_id,
            'partner': self.picking_id.partner_id,
        }


    @api.model
    def create(self, vals):
        # print('cr',vals)
        # return 9/0
        # TDE CLEANME: PO update
        if vals.get('picking_type_id'):
            pickingtype = self.env['stock.picking.type'].search([('id','=', vals.get('picking_type_id'))])
            if pickingtype.name == 'Delivery Orders':
                vals['location_id'] = pickingtype.default_location_src_id.id        
        return super(StockMove, self).create(vals)


class stockpickingInherit(models.Model):
    _inherit = "stock.picking"

    @api.depends('move_ids_without_package.price_total')
    def _amount_all(self):
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.move_ids_without_package:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    dc_type = fields.Selection([('service', 'Service'),
        ('normal', 'Normal'),
        ('returnable', 'Returnable'),
        ('nonreturnable', 'Non Returnable')],string="Type")
    ref_name = fields.Char(string='Internal Work Order')
    po_id = fields.Many2many('purchase.order', string="Purchase Order")
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,
        default=lambda self: self.env.user.company_id.currency_id.id)

    amount_untaxed = fields.Float(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Float(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Float(string='Total', store=True, readonly=True, compute='_amount_all')
    mo_id = fields.Many2one('mrp.production', string="Manufacturing Order Ref")

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        res=[]
        if self.partner_id:
            poids = self.env['purchase.order'].search([('partner_id','=',self.partner_id.id),('state','=','purchase')])
            for po in poids:
                for line in po.order_line:
                    if line.not_applicable == False:
                        res.append(po.id)
            res = set(res)
        return {'domain':{'po_id':[('id', 'in', list(res))]}}

    @api.onchange('po_id')
    def onchange_po_id(self):
        move_lines = []
        values = {}
        product_uom_qty = 0
        if self.po_id:
            for purchase in self.po_id:
                if purchase.order_line:
                    for line in purchase.order_line:
                        if line.qty_received != 0:
                            product_uom_qty = line.product_uom_qty - line.qty_received
                        else:
                            product_uom_qty = line.product_uom_qty
                        tax_lines = []
                        if line.taxes_id:
                            for tax in line.taxes_id:
                                tax_lines.append(tax.id)

                        if line.not_applicable != True:
                            move_lines.append((0,0,{'location_id': self.location_id.id,
                             'product_uom_qty': product_uom_qty, 
                             'product_uom': line.product_uom.id, 
                             'date_expected': datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                             'picking_type_id': self.picking_type_id.id, 
                             'state': 'draft', 
                             'product_id': line.product_id.id,
                             'location_dest_id': self.location_dest_id.id, 
                             'name': line.product_id.name,
                             'po_ref': purchase.id,
                             'price_unit': line.price_unit,
                             'price_subtotal': line.price_subtotal,
                             'price_total': line.price_total,
                             'taxes_id': [(6,0,tax_lines)]}))
            values.update(move_ids_without_package=move_lines)
        return {'value':values}

    @api.model
    def create(self, vals):
        # TDE CLEANME: PO update

        if vals.get('picking_type_id'):
            pickingtype = self.env['stock.picking.type'].search([('id','=', vals.get('picking_type_id'))])
            if pickingtype.name == 'Delivery Orders':
                vals['location_id'] = pickingtype.default_location_src_id.id

        res = super(stockpickingInherit, self).create(vals)
        if vals.get('move_ids_without_package'):
            for lines in vals.get('move_ids_without_package'):
                if lines[2] != False:
                    if lines[2].get('quantity_done') > 0 and lines[2].get('po_ref'):
                        po = self.env['purchase.order'].search([('id','=', lines[2].get('po_ref'))])
                        if po.order_line:
                            for po_line in po.order_line:
                                if po_line.product_id.id == lines[2].get('product_id'):
                                    po_line.write({'qty_received':po_line.qty_received + lines[2].get('quantity_done')})
                                    if po_line.qty_received == po_line.product_uom_qty:
                                        po_line.write({'not_applicable': True})


        return res


    
    # def button_validate(self):
    #     self.ensure_one()
    #     print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
    #     if self.origin:
    #         mrp = self.env['mrp.production'].search([('name','=', self.origin)])
    #         if mrp:
    #             if mrp.state == 'done':
    #                 if mrp.so_ref != False:
    #                     if mrp.so_ref.picking_ids:
    #                         for so_do in mrp.so_ref.picking_ids:
    #                             so_do.action_assign()
    #     print("1111111111111111111111111111111111")
    #     if self.move_ids_without_package:
    #         for move in self.move_ids_without_package:
    #             if move.po_ref:
    #                 if move.po_ref.order_line:
    #                     for line in move.po_ref.order_line:
    #                         if line.product_id.id == move.product_id.id:
    #                             if not line.qty_received:
    #                                 line.write({'qty_received': line.qty_received + move.quantity_done})
    #                             if  move.picking_id.backorder_id:
    #                                 line.write({'qty_received': line.qty_received + move.quantity_done})
    #                         if line.qty_received == line.product_uom_qty:
    #                             line.write({'not_applicable': True})
    #     print("22222222222222222222222222222222222222222222")
    #     if self.subcontract:
    #         pickingtype = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
    #         picking = self.env['stock.picking']
    #         mo_id = self.env['mrp.production'].search([('name', '=', self.origin)], limit=1)
    #         reference=''
    #         if mo_id:
    #             if mo_id.internal_work_order_id:
    #                 reference = mo_id.internal_work_order_id.name
    #
    #         # pdb.set_trace()
    #         pick_lines = []
    #         pick_lines.append((0, 0, {
    #             'name': 'Test Location',
    #             'product_id': mo_id.product_id.id,
    #             'product_uom_qty': mo_id.product_qty,
    #             # 'reserved_availability':line.product_qty,
    #             # 'quantity_done':line.product_qty,
    #             'product_uom': mo_id.product_id.uom_id.id,
    #         }))
    #         picking1 = picking.create({'location_id': self.location_dest_id.id,
    #                                    'location_dest_id': self.location_id.id,
    #                                    'partner_id': self.partner_id.id,
    #                                    'picking_type_code': 'incoming',
    #                                    'move_lines': pick_lines,
    #                                    'move_type': 'direct',
    #                                    'origin': self.name + ',' + mo_id.name,
    #                                    'ref_name':reference,
    #                                    'picking_type_id': pickingtype.id,
    #                                    'sale_id': mo_id.internal_work_order_id.sale_id.id if mo_id.internal_work_order_id.sale_id else False,
    #                                    })
    #     print("3333333333333333333333333333333333")
    #     if self.move_ids_without_package:
    #         qc_ids = self.env['quality.check'].search([('picking_id','=',self.id)])
    #         for el in qc_ids:
    #             for line in self.move_ids_without_package:
    #                 if el.product_id == line.product_id:
    #                     if el.quality_state == 'pass':
    #                         pass
    #                     else:
    #                         raise UserError(
    #                             _('Please make sure " %s " as passed all Test ') % line.product_id.name)
    #
    #     print("444444444444444444444444444444444444444")
    #     if not self.move_lines and not self.move_line_ids:
    #         raise UserError(_('Please add some items to move.'))
    #
    #     # If no lots when needed, raise error
    #     picking_type = self.picking_type_id
    #     print(picking_type,"PPPPPPPPPPPPPPPPPPPPP")
    #     precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
    #     no_quantities_done = all(
    #         float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
    #     no_reserved_quantities = all(
    #         float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in
    #         self.move_line_ids)
    #     print(no_quantities_done,no_reserved_quantities,":::::::::::::::qqqqqqqqqqqqqq")
    #     if no_reserved_quantities and no_quantities_done:
    #         raise UserError(_(
    #             'You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))
    #     print("picking---------------------------------------------")
    #     if picking_type.use_create_lots or picking_type.use_existing_lots:
    #         lines_to_check = self.move_line_ids
    #         if not no_quantities_done:
    #             lines_to_check = lines_to_check.filtered(
    #                 lambda line: float_compare(line.qty_done, 0,
    #                                            precision_rounding=line.product_uom_id.rounding)
    #             )
    #
    #         for line in lines_to_check:
    #             product = line.product_id
    #             if product and product.tracking != 'none':
    #                 if not line.lot_name and not line.lot_id:
    #                     raise UserError(
    #                         _('You need to supply a Lot/Serial number for product %s.') % product.display_name)
    #     print(no_quantities_done,"ddddddddddddddddddddddddddddddddddd")
    #     if no_quantities_done:
    #         print('@!!!!@@!#@#@')
    #         view = self.env.ref('mrp.view_mrp_production_backorder_form')
    #         wiz = self.env['mrp.production.backorder'].create({'show_backorder_lines': self.id})
    #         return {
    #             'name': _('Immediate Transfer?'),
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'mrp.production.backorder',
    #             'views': [(view.id, 'form')],
    #             'view_id': view.id,
    #             'target': 'new',
    #             'res_id': wiz.id,
    #             'context': self.env.context,
    #         }
    #     print("yyyyyyyyyyyyyy::::::::::::::::::::::::::::::::::::::::::::::::::::")
    #     if self.action_put_in_pack() and not self._context.get('skip_backorder'):
    #         print("skip-----------------------------------")
    #         view = self.env.ref('mrp.view_mrp_production_backorder_form')
    #         wiz = self.env['mrp.production.backorder'].create({'show_backorder_lines': self.id})
    #         return {
    #             'type': 'ir.actions.act_window',
    #             'view_type': 'form',
    #             'view_mode': 'form',
    #             'res_model': 'mrp.production.backorder',
    #             'views': [(view.id, 'form')],
    #             'view_id': view.id,
    #             'target': 'new',
    #             'res_id': wiz.id,
    #             'context': self.env.context,
    #         }
    #
    #     if self.po_id:
    #         for po in self.po_id:
    #             po.write({'rev_bool': True})
    #
    #
    #
    #
    #     # Check backorder should check for other barcodes
    #     if self._check_backorder():
    #         return self.action_generate_backorder_wizard()
    #     self.action_done()
    #     return



class MrpWorkOrderInherit(models.Model):
    _inherit = "mrp.workorder"

    check_deviation = fields.Boolean(default=False, string='Accept with Deviation')

    def do_measure(self):
        self.ensure_one()
        point_id = self.current_quality_check_id.point_id
        if self.check_deviation:
            return self.do_pass()
        else:
            if self.measure < point_id.tolerance_min or self.measure > point_id.tolerance_max:
                return self.do_fail()
            else:
                return self.do_pass()


class StockImmediateTransfer(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        res = super(StockImmediateTransfer, self).process()
        if self.pick_ids:
            for pick in self.pick_ids:
                if pick.origin:
                    mrp = self.env['mrp.production'].search([('name','=', pick.origin)])
                    if mrp:
                        if mrp.state == 'done':
                            if mrp.so_ref != False:
                                if mrp.so_ref.picking_ids:
                                    for pick in mrp.so_ref.picking_ids:
                                        pick.action_assign()
        return res


# class StockInventoryAdjustment(models.TransientModel):
#     _inherit = 'stock.immediate.transfer'
#     _description = 'Inventory Adjustment Reference / Reason'
#
#
#     picking_id = fields.Many2one('stock.picking', 'Transfer', required=True)
    # quant_ids = fields.Many2many('stock.quant')
    # inventory_adjustment_name = fields.Char(default=_default_inventory_adjustment_name)
    # show_info = fields.Boolean('Show warning')
