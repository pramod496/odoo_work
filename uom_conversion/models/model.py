from odoo import models, fields, api, _
from odoo.tools import float_round
from odoo.exceptions import UserError


class product_template(models.Model):

    _inherit = "product.template"

    consumed_in_lengths = fields.Boolean('Consumed in Lengths', default=True)
    kgs_mtr = fields.Float('kgs/mtr')
    density  = fields.Float('Density (Kg/Cubic Mtr)')
    thickness  = fields.Float('Thickness (MM)')
    same_uom_consumed = fields.Boolean('Same UOM Consumed', default=False)


class Mrp_Bom(models.Model):
    _inherit = 'mrp.bom.line'

    length = fields.Float('Length (Mtr)')
    width = fields.Float('Width (Mtr)')
    thickness = fields.Float('Thickness (MM)', store=True)
    consumed_in_lengths = fields.Boolean('Consumed in Lengths', default=False)
    same_uom_consumed = fields.Boolean('Same UOM Consumed' , default=False)


    @api.onchange('product_id')
    def _onchange_thickness(self):
        if self.product_id.consumed_in_lengths == False:
            self.consumed_in_lengths = False
        if self.product_id.thickness:
            self.thickness = self.product_id.thickness
        if self.product_id.same_uom_consumed ==True:
            self.same_uom_consumed = True
        else:
            self.same_uom_consumed = False



    @api.onchange('length','width','thickness')
    def _onchange_product_id(self):
    	if self.product_id.consumed_in_lengths:
	    	self.consumed_in_lengths = True
    		self.product_qty = self.product_id.kgs_mtr*self.length
    	if self.length and self.width:
        	self.product_qty = (self.product_id.density*self.length*self.width*self.thickness)/1000


class StockRequestLines(models.Model):
    _inherit = 'stock.request.line'

    length = fields.Float('Length (Mtr)')
    width = fields.Float('Width (Mtr)')
    thickness = fields.Float('Thickness (MM)')


class ManufacturingOrder(models.Model):
    _inherit = 'stock.move'

    length = fields.Float('Length (Mtr)')
    width = fields.Float('Width (Mtr)')
    thickness = fields.Float('Thickness (MM)')

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    @api.model
    def create(self, vals_list):
        res = super(MrpBom, self).create(vals_list)
        res.write({            
               'bom_line_ids': [(1, bom_line.id, dict(thickness=bom_line.product_id.product_tmpl_id.thickness)) for bom_line in res.bom_line_ids]
           })
        return res


    # def explode(self, product, quantity, picking_type=False):
    #     """
    #         Explodes the BoM and creates two lists with all the information you need: bom_done and line_done
    #         Quantity describes the number of times you need the BoM: so the quantity divided by the number created by the BoM
    #         and converted into its UoM
    #     """
    #     from collections import defaultdict
    #
    #     graph = defaultdict(list)
    #     V = set()
    #
    #     def check_cycle(v, visited, recStack, graph):
    #         visited[v] = True
    #         recStack[v] = True
    #         for neighbour in graph[v]:
    #             if visited[neighbour] == False:
    #                 if check_cycle(neighbour, visited, recStack, graph) == True:
    #                     return True
    #             elif recStack[neighbour] == True:
    #                 return True
    #         recStack[v] = False
    #         return False
    #
    #     boms_done = [(self, {'qty': quantity, 'product': product, 'original_qty': quantity, 'parent_line': False})]
    #     lines_done = []
    #     V |= set([product.product_tmpl_id.id])
    #
    #     bom_lines = [(bom_line, product, quantity, False) for bom_line in self.bom_line_ids]
    #     for bom_line in self.bom_line_ids:
    #         V |= set([bom_line.product_id.product_tmpl_id.id])
    #         graph[product.product_tmpl_id.id].append(bom_line.product_id.product_tmpl_id.id)
    #     while bom_lines:
    #         current_line, current_product, current_qty, parent_line = bom_lines[0]
    #         bom_lines = bom_lines[1:]
    #
    #         if current_line._skip_bom_line(current_product):
    #             continue
    #
    #         line_quantity = current_qty * current_line.product_qty
    #         bom = self._bom_find(products=current_line.product_id, picking_type=picking_type or self.picking_type_id, company_id=self.company_id.id)
    #         # print('bom1', bom, bom.get(current_line.product_id))
    #         if bom:
    #             bom = bom.get(current_line.product_id)
    #         # print(bom)
    #         # print(bom.type)
    #         print(boms_done, lines_done)
    #         if bom and bom.type == 'phantom':
    #             converted_line_quantity = current_line.product_uom_id._compute_quantity(line_quantity / bom.product_qty, bom.product_uom_id)
    #             bom_lines = [(line, current_line.product_id, converted_line_quantity, current_line) for line in bom.bom_line_ids] + bom_lines
    #             for bom_line in bom.bom_line_ids:
    #                 graph[current_line.product_id.product_tmpl_id.id].append(bom_line.product_id.product_tmpl_id.id)
    #                 if bom_line.product_id.product_tmpl_id.id in V and check_cycle(bom_line.product_id.product_tmpl_id.id, {key: False for  key in V}, {key: False for  key in V}, graph):
    #                     raise UserError(_('Recursion error!  A product with a Bill of Material should not have itself in its BoM or child BoMs!'))
    #                 V |= set([bom_line.product_id.product_tmpl_id.id])
    #             boms_done.append((bom, {'qty': converted_line_quantity, 'length' : bom_line.length,'width' : bom_line.width,
    #         'thickness' : bom_line.thickness,'product': current_product, 'original_qty': quantity, 'parent_line': current_line}))
    #         elif bom and bom.type != 'normal':
    #             # We round up here because the user expects that if he has to consume a little more, the whole UOM unit
    #             # should be consumed.
    #             rounding = current_line.product_uom_id.rounding
    #             line_quantity = float_round(line_quantity, precision_rounding=rounding, rounding_method='UP')
    #             lines_done.append((current_line, {'qty': line_quantity, 'length' : current_line.length,'width' : current_line.width,
    #         'thickness' : current_line.thickness,'product': current_product, 'original_qty': quantity, 'parent_line': parent_line}))
    #     print(boms_done, lines_done)
    #     # raise ValueError('Nilsu')
    #     return boms_done, lines_done

class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    def _generate_raw_move(self, bom_line, line_data):
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
        alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
        if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
            return self.env['stock.move']
        if bom_line.product_id.type not in ['product', 'consu']:
            return self.env['stock.move']
        if self.bom_id.operation_ids:
            routing = self.bom_id.operation_ids
        else:
            routing = self.bom_id.operation_ids
        if routing and routing.location_id:
            source_location = routing.location_id
        else:
            source_location = self.location_src_id
        original_quantity = (self.product_qty - self.qty_produced) or 1.0
        data = {
            'sequence': bom_line.sequence,
            'name': self.name,
            'date': self.date_planned_start,
            'date_expected': self.date_planned_start,
            'bom_line_id': bom_line.id,
            'picking_type_id': self.picking_type_id.id,
            'product_id': bom_line.product_id.id,
            'length' : bom_line.length,
            'width' : bom_line.width,
            'thickness' : bom_line.thickness,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': self.product_id.property_stock_production.id,
            'raw_material_production_id': self.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': self.procurement_group_id.id,
            'propagate': self.propagate,
            'unit_factor': quantity / original_quantity,
        }
        return self.env['stock.move'].create(data)

    
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        pickingtype = False
        picking = self.env['stock.picking']
        if self.type_seq:
            if self.type_seq == 'subcontract' or self.subcontract_prod:
                if self.vendor:
                    for el in self.vendor:
                        location = el.property_stock_supplier.id
                        break
                # pickingtype = self.env['stock.picking.type'].search([('subcontract', '=', True),
                #                                                               ('code', '=', 'mrp_operation')
                #                     , ('default_location_src_id', '=',location),
                #                      ('default_location_dest_id', '=',location)],
                #                                                              limit=1)
                # self.name = self.env['ir.sequence'].next_by_code('mrp.production.subcontract') or _('New')
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
                # self.name = self.env['ir.sequence'].next_by_code('mrp.production.shop.floor') or _('New')
            else:
                picking_type_id = self.picking_type_id or self._get_default_picking_type()
                # picking_type_id = self.env['stock.picking.type'].browse(picking_type_id)
                # if picking_type_id:
                #     self.name = picking_type_id.sequence_id.next_by_id()
                # else:
                #     self.name = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
        if self.type_seq=='normal':
            pickingtype = self.env['stock.picking.type'].search([('code', '=', 'internal'),
                                                                 ('mrp_confirm', '=', True),
                                                                 ('default_location_src_id', 'in', self.env['stock.location'].search([('finished_product','=',True)]).ids),
                                                                 (
                                                                 'default_location_dest_id', 'in', self.env['stock.location'].search([('logistics','=',True)]).ids)],
                                                                limit=1)
            pick_lines = []
            pick_lines.append((0, 0, {
                'name': 'Test Location',
                'product_id': self.product_id.id,
                'product_uom_qty': self.product_qty,
                # 'reserved_availability':line.product_qty,
                # 'quantity_done':line.product_qty,
                'product_uom': self.product_id.uom_id.id,
            }))
        if self.type_seq != 'normal':
            pass

        if not self.type_seq == 'subcontract':
            stock_request_location = self.env['stock.location'].search([('wip_location', '=', True)], limit=1)
            stock_lines = []
            company_user = self.env.user.company_id
            warehouse = self.env['stock.warehouse'].search([('company_id', '=', company_user.id)], limit=1)

            if warehouse:
                location_id = warehouse.lot_stock_id.id
            request_id = self.env['stock.request']
            for pick_line in self.move_raw_ids:
                stock_lines.append((0, 0, {
                    'name': 'Test Location',
                    'product_id': pick_line.product_id.id,
                    'location_id': location_id,
                    'location_dest_id': stock_request_location.id,
                    'product_uom_qty': pick_line.product_uom_qty,
                    'product_uom': pick_line.product_uom.id,
                    'length' :pick_line.length,
                    'width' :pick_line.width,
                    'thickness' :pick_line.thickness,
                    'date':pick_line.date,
                    'name':pick_line.product_id.name,
                    'pending_qty':pick_line.product_uom_qty,
                    # 'stock_move_id':pick_line.id

                }))
            request_id1 = request_id.create({'location_id': location_id,
                                    'location_dest_id': stock_request_location.id,
                                    'stock_line': stock_lines,
                                    'origin': self.id,
                                    'issued_date':self.date_planned_start,
                                    'state':'draft',
                                    'iwo_ref':self.internal_work_order_id.id if self.internal_work_order_id else False,
                                    'requested_by':self.env.user.id,

                                    })
        if self and not self.procurement_group_id:
            self.procurement_group_id = self.env["procurement.group"].create({'name': self.name}).id
        # self._generate_moves()
        self.state = 'confirmed'
        return res
