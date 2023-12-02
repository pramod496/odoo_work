import datetime
from datetime import datetime
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import Warning
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp
import pdb
from odoo.exceptions import ValidationError, RedirectWarning, except_orm, UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class MrpProduction(models.Model):
    """ Manufacturing Orders """
    _inherit = 'mrp.production'

    
    def _stock_request_count(self):
        for order in self:
            stock_request_count = self.env['stock.request'].search([('origin', '=', order.id)])
            order.stock_request_order_count = len(stock_request_count)



    stock_request_order_count = fields.Integer(string='# of Stock Request Orders', compute='_stock_request_count')
    stock_request_state = fields.Selection(
            [('draft', 'Draft'),
             ('waiting_issue', 'Waiting for Issue'),
             ('done', 'Issue Approved')], string='Stock Request Status', readonly=True, copy=False, default='draft')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('production_started', 'Production Started'),
        ('to_close', 'To Close'),
        ('pause', 'Pause'),
        ('planned', 'Planned'),
        ('progress', 'In Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', track_visibility='onchange')

    production_status = fields.Boolean('Production Status', default=False)

    def action_start_production(self):
        return self.write({'state': 'production_started', 'production_status': True})

    def dummy(self):

        # moves_raw = self.move_raw_ids.filtered(
        #     lambda move: move.state not in ('done', 'cancel'))
        # if wo == self.workorder_ids[-1]:
        #     moves_raw |= self.move_raw_ids.filtered(lambda move: not move.operation_id)
        # moves_finished = self.move_finished_ids.filtered(
        #     lambda move: move.operation_id == operation)  # TODO: code does nothing, unless maybe by_products?
        # moves_raw.mapped('move_line_ids').write({'workorder_id': wo.id})
        # (moves_finished + moves_raw).write({'workorder_id': wo.id})
        self.write({'state': 'confirmed'})
        self.button_plan()
        # self.workorder_ids += self.env['mrp.workorder'].create({
        self.workorder_ids = [(0, 0, {
            'name': 'Manufacturing',
            'workcenter_id': 1,
            'product_id': self.product_id.id,
            'product_uom_id': self.product_id.uom_id.id,

        })]
        return 

    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        self.write({'production_status': False})
        return res
            
class StockRequest(models.Model):
    _name = 'stock.request'
    _order = 'id desc'

    
    def update_quantity_all(self):
        for el in self:
            for line in el.stock_line:
                line.issued_qty = line.pending_qty
                # line.state = 'draft'
                # print(line, line.state)
                # return
                line.update_quantity()
                line.state = 'done'
                el.state = 'done'


    # @api.depends('stock_line.pending_qty')
    # def compute_state(self):
    #     qty = 0
    #     pdb.set_trace()
    #     for el in stock_line:
    #         if el.pending_qty==0:
    #             el.state = 'partial'




    # 
    # def action_assign(self):
    #     for production in self:
    #         move_to_assign = production.stock_line.filtered(lambda x: x.state in ('confirmed', 'waiting', 'assigned'))
    #         # move_to_assign._action_assign()
    #         if self.origin.availability == 'assigned':
    #             self.issued_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #             self.state = 'done'
    #             self.origin.write({'stock_request_state': 'done'})
    #     return True





    name = fields.Char('Name')
    stock_line  = fields.One2many('stock.request.line','stock_id',string='Issue lines',readonly=True, states={'waiting_issue': [('readonly', False)]})
    request_date = fields.Datetime(string='Request Date', required=True, default=fields.Datetime.now)
    origin = fields.Many2one('mrp.production', string='Source Document', copy=False)
    issued_date = fields.Datetime(string='Approve Date',)
    requested_by = fields.Many2one('res.users', string='Requested by')
    description = fields.Text(string='Additional Information')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    location_id = fields.Many2one('stock.location', 'Source Location',auto_join=True, index=True, required=True)
    location_dest_id = fields.Many2one('stock.location', 'Destination Location',auto_join=True, index=True, required=True)
    state = fields.Selection(
                    [('draft', 'Draft'),
                     ('waiting_issue','Waiting for Issue'),
                     ('done', 'Done')],string='State',   compute='_compute_order_state',readonly=True, index=True, copy=False, default='draft',store=True, track_visibility='onchange')
    # field_state=fields.Char('Fields', compute='_compute_order_state')
    bool = fields.Boolean(default=False)
    iwo_ref = fields.Many2one('work.order.quotation','Internal WO Ref')
    # state= fields.Selection(related='stock_move_id.state', store=True)

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('stock.request') or '/'
        return super(StockRequest, self).create(vals)

    
    def mrp_stock_request_confirm(self):
        for indent in self:
            indent_id = self.env['stock.request']
            indent.write({'state': 'waiting_issue'})
            indent.origin.write({'stock_request_state': 'waiting_issue'})
            indent.bool=True

    
    @api.depends('stock_line.state')
    def _compute_order_state(self):
        """
        Update the state of lunch.order based on its orderlines. Here is the logic:
        - if at least one order line is cancelled, the order is set as cancelled
        - if no line is cancelled but at least one line is not confirmed, the order is set as new
        - if all lines are confirmed, the order is set as confirmed
        
        """
        if not self.stock_line:
            self.state = 'draft'
        else:
            isConfirmed = True
            for orderline in self.stock_line:
                if orderline.state == 'done':
                    continue
                else:
                    isConfirmed = False

            if isConfirmed:
                self.state = 'done'
            else:
                self.state = 'waiting_issue'
        return
        # if not self.stock_line:
        #
        #     self.state = 'draft'
        #     # self.state = 'new'
        # else:
        #     isConfirmed = True
        #     if self.bool==False:
        #         self.state = 'draft'
        #         return
        #     if self.bool==True:
        #         self.state='waiting_issue'
        #         return
        #     else:
        #         for orderline in self.stock_line:
        #             if orderline.state == 'partial'  or orderline.state=='draft':
        #                 return
        #         self.state = 'done'

class StockPickingTypeInherit(models.Model):
    _inherit = 'stock.picking.type'

    stock_request = fields.Boolean(default=False,string='Stock Request')

class StockRequestLines(models.Model):
    _name = 'stock.request.line'

    
    def update_quantity(self):
        if self.issued_qty:

            if self.product_uom_qty < (self.issued_qty + self.qty_issue):
                raise ValidationError(_('Issue Quanitty is exceeding than Initial Demand Quantity'))

        if self.issued_qty > 0:
            if self.product_id.qty_available >= self.issued_qty:

                self.stock_update_line = [(0, 0, {
                    'date': fields.Datetime.now(),
                    'quantity': self.issued_qty,
                })]
                if self.stock_update_line:
                    for el in self.stock_update_line:
                        if not el.date:
                            el.unlink()
                        elif el.quantity <= 0:
                            el.unlink()
                        else:
                            pass
                qty =0

                pickingtype = self.env['stock.picking.type'].search([('code', '=', 'internal'),
                                                                     ('stock_request', '=', True),
                                                                     ('default_location_src_id', '=',self.location_id.id),
                                                                     (
                                                                         'default_location_dest_id', 'in',
                                                                         self.env['stock.location'].search(
                                                                             [('wip_location', '=', True)]).ids)],
                                                                    limit=1)
                picking = self.env['stock.picking']
                pick_lines = []
                pick_lines.append((0, 0, {
                    'name': 'Test Location',
                    'product_id': self.product_id.id,
                    'product_uom_qty': self.issued_qty,
                    # 'reserved_availability':line.product_qty,
                    # 'quantity_done':line.product_qty,
                    'product_uom': self.product_id.uom_id.id,
                    # 'quantity_done':self.issued_qty,
                    # 'qty_done':self.issued_qty,
                    'location_id':self.location_id.id,
                    'location_dest_id':self.location_dest_id.id,
                }))
                picking1 = picking.create({'location_id': pickingtype.default_location_src_id.id,
                                           'location_dest_id': pickingtype.default_location_dest_id.id,
                                           'picking_type_code': 'incoming',
                                           'move_lines': pick_lines,
                                           'move_type': 'direct',
                                           'origin': self.stock_id.name,
                                           'ref_name': '',
                                           'picking_type_id': pickingtype.id,
                                           })


                picking1.action_confirm()
                picking1.action_assign()
                # print(picking1.state)
                picking1.action_set_quantities_to_reservation()
                # print(picking1.state)
                picking1.button_validate()
                # print(picking1.state)


                # picking1.button_validate_custom()

                # move = self.env['stock.move']
                #
                # move_id = move.create({
                #     'name':'New',
                #     'location_id':self.location_id.id,
                #     'location_dest_id':self.location_dest_id.id,
                #     'product_id':self.product_id.id,
                #     'product_uom_qty':self.issued_qty,
                #     'product_uom':self.product_uom.id
                # })
                # move_id._action_confirm()
                # move_id._action_done()
                qty1=0
                for el in self.stock_update_line:
                    qty =qty+el.quantity
                    qty1 = qty1 + el.quantity

                self.pending_qty= self.product_uom_qty - qty
                self.qty_issue = qty1

                self.write({'issued_qty': 0.00})
                for el in self:
                    if el.pending_qty ==0:
                        el.state='done'
                    else:
                        el.state='partial'
            else:
                raise ValidationError(_('There is no stock available for the given product'))

        # raise ValidationError("wait")

    @api.depends('product_id')
    def _get_quantity(self):
        stock_on_hand={}
        for rec in self:
            stock = self.env['stock.quant'].search([
                ('location_id', '=', rec.location_id.id),
                ('product_id', '=', rec.product_id.id)
            ])
            stock_on_hand[rec.product_id.id] = sum(stock.mapped('available_quantity'))
        for el in self:
            if not el.product_id:
                return {}
            if el.product_id:
                el.qty_available = stock_on_hand[el.product_id.id]




    stock_id = fields.Many2one('stock.request')
    product_id = fields.Many2one('product.product','Product')
    name = fields.Char('Description')
    qty_available = fields.Float(string='Quantity Available', compute=_get_quantity)
    product_uom_qty = fields.Float('Initial Demand',digits=dp.get_precision('Product Unit of Measure'),default=0.0)
    issued_qty = fields.Float('Issued Qty')
    # qty_issue = fields.Float('Issued Qty',compute='issue_qy')
    qty_issue = fields.Float('Issued Qty')
    product_uom = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    pending_qty = fields.Float('Pending Qty')
    available_qty = fields.Float('Available Qty')
    location_id = fields.Many2one('stock.location', 'Source Location',auto_join=True, index=True, required=True)
    location_dest_id = fields.Many2one('stock.location', 'Destination Location',auto_join=True, index=True, required=True)
    date = fields.Datetime('Date', default=fields.Datetime.now, index=True)
    stock_update_line = fields.One2many('stock.request.update', 'stock_request_line', string='Stock Line Update')
    # stock_move_id = fields.Many2one('stock.move','Stock Move Ref')
    # state= fields.Selection(related='stock_move_id.state', store=True)
    state = fields.Selection(
        [('draft', 'Draft'),
         ('partial', 'Partially Available'),
         ('done', 'Done')], string='State', readonly=True, default='draft', track_visibility='onchange')
    stock_req_name= fields.Char(related='stock_id.name', store=True)
    stock_req_date = fields.Datetime(related='stock_id.request_date', store=True)

class StockLocationInherite(models.Model):
    _inherit = 'stock.location'

    wip_location = fields.Boolean('Is a WIP Location?')

class StockRequestUpdate(models.Model):
    _name='stock.request.update'

    date = fields.Datetime('Date', readonly=True)
    remarks = fields.Char('Remarks')
    quantity = fields.Float('Quantity', readonly=True)
    stock_request_line = fields.Many2one('stock.request.line', string='Stock Request line')

class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'



    
    def button_validate_custom(self):
        self.ensure_one()
        if not self.move_lines and not self.move_line_ids:
            raise UserError(_('Please add some items to move.'))

        # If no lots when needed, raise error
        picking_type = self.picking_type_id
        precision_digits = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        no_quantities_done = all(float_is_zero(move_line.qty_done, precision_digits=precision_digits) for move_line in self.move_line_ids)
        no_reserved_quantities = all(float_is_zero(move_line.product_qty, precision_rounding=move_line.product_uom_id.rounding) for move_line in self.move_line_ids)
        if no_reserved_quantities and no_quantities_done:
            raise UserError(_('You cannot validate a transfer if no quantites are reserved nor done. To force the transfer, switch in edit more and encode the done quantities.'))

        if picking_type.use_create_lots or picking_type.use_existing_lots:
            lines_to_check = self.move_line_ids
            if not no_quantities_done:
                lines_to_check = lines_to_check.filtered(
                    lambda line: float_compare(line.qty_done, 0,
                                               precision_rounding=line.product_uom_id.rounding)
                )

            for line in lines_to_check:
                product = line.product_id
                if product and product.tracking != 'none':
                    if not line.lot_name and not line.lot_id:
                        raise UserError(_('You need to supply a Lot/Serial number for product %s.') % product.display_name)

        if no_quantities_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.immediate.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        if self._get_overprocessed_stock_moves() and not self._context.get('skip_immediate'):
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({'pick_ids': [(4, self.id)]})
            return {
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.overprocessed.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }

        # Check backorder should check for other barcodes
        if self._check_backorder():
            return self.action_generate_backorder_wizard()
        self.action_set_quantities_to_reservation()
        self.action_done()
        self.button_validate()
        return


class StockMoveLineInherited(models.Model):
    _inherit = 'stock.move.line'

    main_product = fields.Many2one(related='production_id.product_id', store=True)
    partner_id = fields.Many2one(related='production_id.partner_id',store=True)
    mrp_name = fields.Char(related='production_id.name',store=True)

    
class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.immediate.production.line"


    
    def do_produce(self):
        # Nothing to do for lots since values are created using default data (stock.move.lots)
        quantity = self.product_qty
        if float_compare(quantity, 0, precision_rounding=self.product_uom_id.rounding) <= 0:
            raise UserError(_("The production order for '%s' has no quantity specified.") % self.product_id.display_name)
        for move in self.production_id.move_finished_ids:
            if move.product_id.tracking == 'none' and move.state not in ('done', 'cancel'):
                rounding = move.product_uom.rounding
                if move.product_id.id == self.production_id.product_id.id:
                    move.quantity_done += float_round(quantity, precision_rounding=rounding)
                elif move.unit_factor:
                    # byproducts handling
                    move.quantity_done += float_round(quantity * move.unit_factor, precision_rounding=rounding)
        self.check_finished_move_lots()
        if self.production_id.state in ['confirmed','production_started']:
            self.production_id.write({
                'state': 'progress',
                'date_start': datetime.now(),
            })
        return {'type': 'ir.actions.act_window_close'}