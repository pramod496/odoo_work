# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import UserError
import itertools
from operator import itemgetter
from odoo.exceptions import ValidationError,UserError
import pdb
class ServicePurchaseOrder(models.Model):
    _name = 'service.purchase.order'


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    # To create a purchase order while clicking on produce button:
    
    def action_confirm(self):
        if self.type_seq == 'subcontract' and self.subcontract_prod == False:
            raise UserError(_('Please check the subcontract box. '))
        if self.type_seq == 'subcontract' and not self.product_id.parent_id:
            raise UserError(_('Please add parent product to %s.') % self.product_id.name)
        res = super(MrpProduction, self).action_confirm()
        vals_item = {}
        vals_line_item = {}
        po_obj = self.env['purchase.order']
        pol_obj = self.env['purchase.order.line']
        if self:
            if self.internal_work_order_id:
                reference = self.internal_work_order_id.name

        if self.subcontract_prod and not self.purchase_ids:
            vals_item = {
                'partner_id': self.vendor.ids[0],
                'state': 'draft',
                'mrp_id': self.id,
                'origin': self.name,
                'bool_mo': True,
                'name' : 'New',
                'ref_name': self.internal_work_order_id.name if self.internal_work_order_id else False,
            }
            po_id = po_obj.create(vals_item)

            #service_id  = self.env['product.template'].search([('parent_id','=',self.product_id.product_tmpl_id.id)])
            vals_line_item = {
                'product_id': self.product_id.id,
                'name': self.product_id.name,
                'date_planned': self.date_planned_start,
                'product_qty': self.product_qty,
                'product_uom': self.product_id.uom_id.id,
                'price_unit': 0.0,
                'taxes_id': [(6, 0, self.product_id.supplier_taxes_id.ids)],
                'order_id': po_id.id,
            }
            pol_obj.create(vals_line_item)
        # picking = self.picking_subcontract()
        return res

    
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        if self.purchase_ids:
            for po in self.purchase_ids:
                for mo in self.finished_move_line_ids:
                    for po_line in po.order_line:
                        if not po_line.qty_received == mo.qty_done and not self.env.user.has_group('mrp.group_mrp_manager'):
                            raise UserError(_('Quantity to produce and Produced Qty Should be same for validation by user.'))
        return res

    
    def action_purchase_view(self):
        action = self.env.ref('purchase.purchase_rfq')
        result = action.read()[0]
        result['domain'] = "[('id', 'in', " + str(self.purchase_ids.ids) + ")]"
        return result

    @api.onchange('vendor')
    def onchange_picking_type(self):
        if self.subcontract_prod:
            if self.vendor:
                for el in self.vendor:
                    self.location_src_id = el.property_stock_supplier.id
                    self.location_dest_id = el.property_stock_supplier.id
                    break


    
    def picking_subcontract(self):
        purchase_id = self.env['purchase.order'].search([('origin','=',self.name)],limit=1)
        # if purchase_id.state == 'purchase':
        self.sub_bool=True
        if self.subcontract_prod:
            if self.vendor:
                pickingtype = self.env['stock.picking.type'].search([('code', '=', 'mrp_operation'),('subcontract','=', True)], limit=1)
                picking = self.env['stock.picking']
                # mo_id = self.env['mrp.production'].search([('name', '=', self.name)], limit=1)

                pick_lines = []
                reference =''
                if self:
                    if self.internal_work_order_id:
                        reference = self.internal_work_order_id.name
                for line in self.move_raw_ids:
                    pick_lines.append((0, 0, {
                        'name': 'Test Location',
                        'product_id': line.product_id.id,
                        'product_uom_qty': line.product_qty,
                        # 'reserved_availability':line.product_qty,
                        # 'quantity_done':line.product_qty,
                        'product_uom': line.product_id.uom_id.id,
                    }))

                stock_type_id = self.env['stock.picking.type'].search([
                    ('code', '=', 'mrp_operation'),
                    ('warehouse_id.company_id', 'in',
                     [self.env.context.get('company_id', self.env.user.company_id.id), False])],
                    limit=1)
                if self.vendor:
                    for el in self.vendor:
                        location = el.property_stock_supplier.id
                        break
                picking= picking.create({
                    'location_id':pickingtype.default_location_src_id.id ,
                                           'location_dest_id': location,
                                           'partner_id': self.vendor.ids[0],
                                           'picking_type_code': 'outgoing',
                                           'move_lines': pick_lines,
                                           'move_type': 'direct',
                                           'origin':  self.name,
                                           'subcontract':True,
                                           'ref_name':self.internal_work_order_id.name if self.internal_work_order_id else False,
                                           'picking_type_id': pickingtype.id,
                                           })
                self.pick_ids = picking.id
        # self._picking_count()
        # else:
        #     raise ValidationError(_('Please confirm the PO for the Job Order '))


    
    def action_delivery_view(self):
        view = self.env.ref('stock.view_picking_form').id

        return {
            'name': _('New'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'tree',
            'views': [(view, 'form')],
            'res_model': 'stock.picking',
            'view_id': view,
            'target': 'current',
            'res_id':self.pick_ids.id
        }


    @api.onchange('product_id')
    def onchange_product_name(self):
        if self.product_id.parent_id.id:

            self.parent_id=self.product_id.parent_id.id

    @api.depends('purchase_ids')
    def _purchase_count(self):
        for order in self:
            order.purchase_count = len(order.purchase_ids)


    def _picking_count(self):
        for order in self:
            plist = []
            # print (order.pick_ids)
            # order.picking_count = len(order.pick_ids)            
            if order.subcontract_prod:
            	domain = [('origin','=', self.name),('picking_type_code','=','mrp_operation')]
            else:
            	domain = [('origin','=', self.name),('picking_type_code','=','outgoing')]
            pickings = self.env['stock.picking'].search(domain)
            for pick in pickings:
                plist.append(pick.id)
            order.picking_count = len(plist)


    purchase_count = fields.Integer(compute='_purchase_count', string='# Purchases')
    purchase_ids = fields.One2many('purchase.order', 'mrp_id', string='Pickings')
    # pick_ids = fields.One2many('stock.picking', 'mrp_id', string='Pickings')
    vendor = fields.Many2many('res.partner', string="Suggested Vendors")
    subcontract_prod = fields.Boolean(string="Subcontract")
    sub_bool = fields.Boolean(default=False)
    pick_ids = fields.Many2one('stock.picking')
    # picking_count = fields.Integer(string="Picking", compute='_picking_count')
    parent_id = fields.Many2one(related='product_id.parent_id', string='Parent product')
    ref_name = fields.Char(string='Internal Work Order')

    @api.model
    def create(self, vals):
        if vals.get('bom_id'):
            bom = self.env['mrp.bom'].search([('id','=', vals.get('bom_id'))])
            if bom.operation_ids.subcontract == True:
                pickingtype = self.env['stock.picking.type'].search([('code', '=', 'mrp_operation'),('subcontract','=', True)], limit=1)
                vals['picking_type_id'] = pickingtype.id
                vals['location_src_id'] = pickingtype.default_location_src_id.id
                vals['location_dest_id'] = pickingtype.default_location_dest_id.id
            if bom.operation_ids.shoop_floor == True:
                pickingtype = self.env['stock.picking.type'].search([('code', '=', 'mrp_operation'),('shoop_floor','=', True)], limit=1)
                vals['picking_type_id'] = pickingtype.id
                vals['location_src_id'] = pickingtype.default_location_src_id.id
                vals['location_dest_id'] = pickingtype.default_location_dest_id.id
        res = super(MrpProduction, self).create(vals)
        return res

    # @api.model
    # def create(self, vals):
    #
    #     res = super(MrpProduction, self).create(vals)

    #     for el in res.picking_ids:
    #         el.partner_id = res.vendor
    #     return res
    #
    # 
    # def write(self, vals):
    #     for el in self.picking_ids:
    #         el.partner_id = self.vendor
    #     res = super(MrpProduction, self).write(vals)
    #     return res


class Location(models.Model):
    _inherit = "stock.location"

    def should_bypass_reservation(self):
        res = super(Location, self).should_bypass_reservation()
        action = self.usage in ('customer', 'inventory', 'production') or self.scrap_location
        return action


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    mrp_id = fields.Many2one('mrp.production', string="Manufacturing Order")
    ref_name = fields.Char(string='Internal Work Order')
    bool_mo = fields.Boolean(default=False)

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            if 'bool_mo' in values:
                if values['bool_mo']:
                    values['name'] = self.env['ir.sequence'].next_by_code('service.purchase.order') or _('New')
                    values['po_type'] = 'spo'
                else:
                    values['name'] = self.env['ir.sequence'].next_by_code('purchase.order') or '/'
                    values['po_type'] = 'po'

        res = super(PurchaseOrder, self).create(values)
        return res




class Picking(models.Model):
    _inherit = 'stock.picking'

    subcontract = fields.Boolean(string="Subcontract")
    bom_material_ids = fields.One2many('bom.materials', 'picking_id', string="BoM Products")
    flag = fields.Boolean(string="Flag", default=False)
    ref_name = fields.Char(string='Internal Work Order')
    mrp_id = fields.Many2one('mrp.production', string="Manufacturing Order")



    
    def button_validate(self):
        self.mrp_validation()
        # if self.picking_type_code in ('outgoing', 'internal'):
        #     for ml in self.move_lines:
        #         sq = self.env['stock.quant'].search([('product_id', '=', ml.product_id.id), ('location_id', '=', self.location_id.id)])
        #         if not sq:
        #             raise UserError(_('There is no stock available for the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) in the stock location. Kindly add the required stock.'))
        #         else:
        #             for i in sq:
        #                 if ml.quantity_done > i.quantity:
        #                     raise UserError(_('You cannot validate this stock operation because the stock level of the product ( ' + (ml.product_id.default_code or '') + ' ' + (ml.product_id.name) + ' ) would become negative on the stock location and negative stock is not allowed for this product.'))
        res = super(Picking, self).button_validate()
        return res

    
    def mrp_validation(self):
        if self.purchase_id.mrp_id.product_id:
            for line in self.move_lines:
                if line.product_id == self.purchase_id.mrp_id.product_id:
                    total_qty = 0
                    if self.purchase_id.mrp_id.finished_move_line_ids:
                        for mrp in self.purchase_id.mrp_id.finished_move_line_ids:
                            if mrp.done_move:
                                total_qty += mrp.qty_done
                        if not line.purchase_line_id.qty_received:
                            if line.quantity_done > total_qty:
                                raise UserError(_('Quantity should not be greater than the Processed Mrp Qty. (or) There is no or less Processed Qty in Stock Move.'))
                        else:
                            curr_qty_done = line.purchase_line_id.qty_received + line.quantity_done
                            if curr_qty_done > total_qty:
                                raise UserError(_('Quantity should not be greater than the processed Mrp Qty .Few of the quantities may be Received'))
                        if self.purchase_id.mrp_id.product_qty == total_qty:
                            self.purchase_id.mrp_id.button_mark_done()
                    else:
                        raise UserError(_('Kindly Process the respective MRP / Work Order for Qty.'))
        return True

    
    def get_bom_materials(self):
        list_prod = []
        if not self.bom_material_ids:
            raise UserError(_('Atleast One item is must in BoM Products to update.'))
        if self.bom_material_ids:
            for line in self.bom_material_ids:
                if line.produce_qty <= 0:
                    raise UserError(_('BoM Quantity should not be Zero to Update.'))
            for bom_id in self.bom_material_ids:
                bom_br = self.env['mrp.bom'].browse(bom_id.product_id.id)
                for bom_line_id in bom_br.bom_line_ids:
                    create_vals = {}
                    create_vals = {
                        'name': bom_line_id.product_id.name,
                        'product_id': bom_line_id.product_id.id,
                        'product_uom': bom_line_id.product_uom_id.id,
                        'product_uom_qty': bom_id.produce_qty * bom_line_id.product_qty,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'picking_id': self.id,
                    }
                    list_prod.append(create_vals)
        list_prod.sort(key=itemgetter('product_id'))
        move_temp = []
        for key, items in itertools.groupby(list_prod, key=itemgetter('product_id', 'name', 'product_uom', 'location_id', 'location_dest_id')):
            move_temp.append({
                'product_id': key[0],
                'name': key[1],
                'product_uom': key[2],
                'location_id': key[3],
                'location_dest_id': key[4],
                'product_uom_qty': sum([item["product_uom_qty"] for item in items])
            })
        for new_line in move_temp:
            move_id = self.env['stock.move'].create(new_line)
            move_id.update({'picking_id': self.id})
        self.flag = True
        return True


class BomMaterials(models.Model):
    _name = 'bom.materials'

    picking_id = fields.Many2one('stock.picking', string="Picking")
    product_id = fields.Many2one('mrp.bom', string="BoM Product")
    produce_qty = fields.Float(string="Quantity")
