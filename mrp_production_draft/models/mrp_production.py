# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2009-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: fasluca(<https://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError
from psycopg2 import IntegrityError
from odoo.addons import decimal_precision as dp
import pdb


# from odoo.addons.mrp.models.mrp_production import MrpProduction as mp


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     return 9/0

    #
    type_seq = fields.Selection([
        ('normal', 'Normal'), ('shop_floor', 'Shop Floor'), ('subcontract', 'Sub Contract')],
        string='Type', compute="get_type_seq", required=True, )

    def get_type_seq(self):
        for el in self:
            if el.bom_id.operation_ids.subcontract:
                el.type_seq = 'subcontract'
                el.subcontract = True
            elif el.bom_id.operation_ids.shoop_floor:
                el.type_seq = 'shop_floor'
            else:
                el.type_seq = 'normal'

    @api.depends('picking_type_id')
    def get_location(self):
        for el in self:
            el.location_src_id = el.picking_type_id.default_location_src_id.id
            el.location_dest_id = el.picking_type_id.default_location_dest_id.id

    # @api.onchange('product_id', 'picking_type_id', 'company_id')
    # def _onchange_product_id(self):
    #     """ Finds UoM of changed product. """
    #     if not self.product_id:
    #         self.bom_id = False
    #     else:
    #         bom = self.env['mrp.bom']._bom_find(products=self.product_id, picking_type=self.picking_type_id,
    #                                             company_id=self.company_id.id)
    #         if bom:
    #             bom = bom[self.product_id]
    #         if bom.bom_type == 'normal':
    #             self.bom_id = bom.id
    #             if self.product_qty == 0:
    #                 self.product_qty = self.bom_id.product_qty
    #             self.product_uom_id = self.bom_id.product_uom_id.id
    #         else:
    #             self.bom_id = False
    #             self.product_uom_id = self.product_id.uom_id.id
    #         return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}

    @api.onchange('bom_id')
    def _onchange_bom_id(self):
        if self.product_qty ==0:
            self.product_qty = self.bom_id.product_qty
        self.product_uom_id = self.bom_id.product_uom_id.id

    
    @api.depends('bom_id.operation_ids', 'bom_id.operation_ids')
    def _compute_routing(self):
        for production in self:
            if production.bom_id.operation_ids:
                production.operation_ids = production.bom_id.operation_ids.id
            else:
                production.operation_ids = False

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('pause','Pause'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange')
    location_src_id = fields.Many2one(
        'stock.location', 'Raw Materials Location',
        compute='get_location',        readonly=True, required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',compute='get_location',
        # default=_get_default_location_dest_id,
        readonly=True, required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will stock the finished products.")
    product_qty = fields.Float(
        'Quantity To Produce',
         digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, required=True, track_visibility='onchange',
        states={'confirmed': [('readonly', False)]})
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=True, states={'confirmed': [('readonly', False)]},
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")


    
    def write(self, vals):
        # try:
        #     res = super(MrpProduction, self).write(vals)
        # except IntegrityError:
        #     raise ValidationError(_("Reference must be unique per Company for confirmed orders!"))
        res = super(MrpProduction, self).write(vals)
        if 'date_planned_start' in vals:
            moves = (self.mapped('move_raw_ids') + self.mapped('move_finished_ids')).filtered(
                lambda r: r.state not in ['done', 'cancel'])
            moves.write({
                'date': vals['date_planned_start'],
            })
        if res:
            return res

    
    def unlink(self):
        if any(production.state not in ['draft', 'cancel'] for production in self):
            raise UserError(_('Cannot delete a manufacturing order not in draft or cancel state'))
        return super(MrpProduction, self).unlink()

    
    def action_confirm(self):
        if not self:
            return
        print('action', self.bom_id.bom_line_ids, self.bom_id)
        pickingtype = False
        picking = self.env['stock.picking']
        if self.type_seq:
            if self.type_seq == 'subcontract' or self.subcontract_prod:
                if self.vendor:
                    for el in self.vendor:
                        location = el.property_stock_supplier.id
                        break
            elif self.type_seq == 'shop_floor':

                stock_type_id = self.env['stock.picking.type'].search([
                    ('code', '=', 'mrp_operation'),
                    ('warehouse_id.company_id', 'in',
                     [self.env.context.get('company_id', self.env.user.company_id.id), False])],
                    limit=1)

                wip_loc = self.env['stock.location'].search([('wip_location', '=', True)], limit=1)
                pickingtype = self.env['stock.picking.type'].search([('shoop_floor','=',True),
                                                                              ('code', '=', 'mrp_operation')
                                        ,('default_location_src_id','=',wip_loc.id)],limit=1)
                self.location_dest_id =  self.picking_type_id.default_location_dest_id.id
            else:
                picking_type_id = self.picking_type_id or self._get_default_picking_type()
            self.procurement_group_id = self.env["procurement.group"].create({'name': self.name}).id
        # self.state = 'confirmed'
        self.workorder_ids = [(0, 0, {
            'name': 'Manufacturing',
            'workcenter_id': 1,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,

        })]
        print(self, self.product_id, self.move_finished_ids)
        if not self.move_finished_ids:
            location_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
            location_dest_id = self.location_dest_id.id
            self.move_finished_ids += self.env['stock.move'].create({
                                            'name': self.product_id.name,
                                            'product_id': self.product_id.id,
                                            'product_uom_qty': self.product_qty,
                                            'origin': self.name,
                                            # 'reserved_availability':line.product_qty,
                                            # 'quantity_done':line.product_qty,
                                            'product_uom': self.product_id.uom_id.id,
                                            # 'picking_id': picking1.id,
                                            'location_id': location_id,
                                            'location_dest_id': location_dest_id,
                                            })
        print('cut', self.bom_id.bom_line_ids, self.bom_id)
        res = super(MrpProduction, self).action_confirm()
        return res

    def button_mark_done(self):
        # for order in self:
        #     if order.type_seq == 'normal':
        #         pickingtype = self.env['stock.picking.type'].search([('code', '=', 'internal'),
        #                                                          ('mrp_confirm', '=', True),
        #                                                          ('default_location_src_id', 'in', self.env['stock.location'].search([('finished_product','=',True)]).ids),
        #                                                          (
        #                                                          'default_location_dest_id', 'in', self.env['stock.location'].search([('logistics','=',True)]).ids)],
        #                                                         limit=1)
        #         pick_lines = []
        #         pick_lines.append((0, 0, {
        #             'name': 'Test Location',
        #             'product_id': self.product_id.id,
        #             'product_uom_qty': self.product_qty,
        #             # 'reserved_availability':line.product_qty,
        #             # 'quantity_done':line.product_qty,
        #             'product_uom': self.product_id.uom_id.id,
        #         }))
        #         picking1 = self.env['stock.picking'].create({'location_id': pickingtype.default_location_src_id.id,
        #                                    'location_dest_id': pickingtype.default_location_dest_id.id,
        #                                    'picking_type_code': 'incoming',
        #                                    # 'move_lines': pick_lines,
        #                                    'move_type': 'direct',
        #                                    'origin': self.name,
        #                                    'ref_name': self.internal_work_order_id.name if self.internal_work_order_id else False,
        #                                    'picking_type_id': pickingtype.id,
        #                                    'so_id': self.so_ref.id if self.so_ref else False,
        #                                    })
        #         if picking1:
        #             location = self.env['stock.location'].search([('finished_product','=',True),('location_id','=', False)])
        #             location_dest = self.env['stock.location'].search([('logistics','=',True)])
        #             move = self.env['stock.move'].create({
        #                 'name': 'Test Location',
        #                 'product_id': self.product_id.id,
        #                 'product_uom_qty': self.product_qty,
        #                 # 'reserved_availability':line.product_qty,
        #                 # 'quantity_done':line.product_qty,
        #                 'product_uom': self.product_id.uom_id.id,
        #                 'picking_id': picking1.id,
        #                 'location_id':location.id,
        #                 'location_dest_id':location_dest.id,
        #                 })
        #
        #             if move:
        #                 lots = self.env['stock.production.lot'].search([('so_id','=', picking1.so_id.id),('product_id','=', self.product_id.id)])
        #                 if lots:
        #                     for lot in lots:
        #
        #                         location = self.env['stock.location'].search([('finished_product','=',True),('location_id','=', False)])
        #                         location_dest = self.env['stock.location'].search([('logistics','=',True)])
        #
        #                         moveline = self.env['stock.move.line'].create({
        #                             'picking_id': picking1.id,
        #                             'move_id': move.id,
        #                             'product_id': move.product_id.id,
        #                             'product_uom_id': move.product_id.uom_id.id,
        #                             'qty_done':1,
        #                             'location_id':location.id,
        #                             'location_dest_id':location_dest.id,
        #                             'lot_id': lot.id,
        #                             })
        # if self.state == 'done':
        #     if self.so_ref != False:
        #         if self.so_ref.picking_ids:
        #             for pick in self.so_ref.picking_ids:
        #                 pick.action_assign()
                        
        res = super(MrpProduction, self).button_mark_done()
        self.bom_id.write({'select_bom': False})
        return res

class StockPickingTypeInherit(models.Model):
    _inherit = 'stock.picking.type'


    subcontract = fields.Boolean(default=False,string='Subcontract')
    shoop_floor = fields.Boolean(default=False,string='Shop Floor')
    mrp_confirm = fields.Boolean(default=False,string='Logistics')


class StocklocationInherit(models.Model):
    _inherit = 'stock.location'

    shoop_floor = fields.Boolean(default=False, string='Is Shop Floor Location')
    finished_product = fields.Boolean(default=False, string='Is Finished Product Location')
    logistics = fields.Boolean(default=False, string='Is Logistics Location')




class stockpickingInherit(models.Model):
    _inherit = "stock.picking"
    
    so_id = fields.Many2one('sale.order', string="Sale Order Ref")

    
    def button_validate(self):
        if self.origin:
            mrp = self.env['mrp.production'].search([('name','=', self.origin)])
            if mrp:
                if mrp.state == 'done':
                    if mrp.so_ref != False:
                        if mrp.so_ref.picking_ids:
                            for pick in mrp.so_ref.picking_ids:
                                pick.action_assign()
        return super(stockpickingInherit, self).button_validate()
