from datetime import datetime, timedelta
from functools import partial
from itertools import groupby

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import formatLang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare

from odoo.addons import decimal_precision as dp

from werkzeug.urls import url_encode
import pdb


class StudentRecord(models.Model):
    _inherit = 'sale.order'
#
#     
#     def _action_confirm(self):
#         if self.partner_id:
#             body = (_("Dear %s ,\
# <p>Your sale order has been confirmed %s.</p>") % (self.partner_id.name, self.partner_id.name))
#             subject = "Re:confirmation of sale order %s" % (self.partner_id.name)
#             self.message_post(body=body, subject=subject, partner_ids=[self.partner_id.id])


class WorkOrder(models.Model):
    _inherit = 'mrp.production'

    bool_pause = fields.Boolean(default=False)
    revision_no = fields.Text(string='Revision Number ')
    partner_id = fields.Many2one('res.partner', string="Customer")

    @api.model
    def create(self, values):
        if values.get('origin'):
            order = self.env['sale.order'].search([('name','=', values.get('origin'))])
            if order:
                values['partner_id'] = order.partner_id.id
        production = super(WorkOrder, self).create(values)
        return production



    
    def action_confirm(self):
        # self.onchange_product_id()
        return super(WorkOrder, self).action_confirm()
            # if not self.bool_pause:
            #     production._generate_moves()


    
    def action_assign(self):
        self.bool_pause = False

        res=super(WorkOrder, self).action_assign()

        return res

    
    def pause_button(self):
        self.ensure_one()
        self.bool_pause = True
        for el in self.move_raw_ids:

            el.write({'state': 'draft'})
        return self.write({'state': 'draft'})

    
    @api.depends('move_line_ids.product_qty')
    def _compute_reserved_availability(self):
        result = {data['move_id'][0]: data['product_qty'] for data in
            self.env['stock.move.line'].read_group([('move_id', 'in', self.ids)], ['move_id','product_qty'], ['move_id'])}
        for rec in self:
            rec.reserved_availability = rec.product_id.uom_id._compute_quantity(result.get(rec.id, 0.0), rec.product_uom, rounding_method='HALF-UP')


    
    def action_cancel(self):
        """ Cancels production order, unfinished stock moves and set procurement
        orders in exception """
        if any(workorder.state == 'progress' for workorder in self.mapped('workorder_ids')):
            raise UserError(_('You can not cancel production order, a work order is still in progress.'))
        documents = {}
        for production in self:
            for move_raw_id in production.move_raw_ids.filtered(lambda m: m.state not in ('done', 'cancel')):
                iterate_key = self._get_document_iterate_key(move_raw_id)
                if iterate_key:
                    document = self.env['stock.picking']._log_activity_get_documents(
                        {move_raw_id: (move_raw_id.product_uom_qty, 0)}, iterate_key, 'UP')
                    for key, value in document.items():
                        if documents.get(key):
                            documents[key] += [value]
                        else:
                            documents[key] = [value]
            production.workorder_ids.filtered(lambda x: x.state != 'cancel').action_cancel()
            finish_moves = production.move_finished_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            raw_moves = production.move_raw_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            (finish_moves | raw_moves)._action_cancel()
            picking_ids = production.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
            picking_ids.action_cancel()
        self.write({'state': 'cancel', 'is_locked': True})

        if documents:
            filtered_documents = {}
            for (parent, responsible), rendering_context in documents.items():
                if not parent or parent._name == 'stock.picking' and parent.state == 'cancel' or parent == self:
                    continue
                filtered_documents[(parent, responsible)] = rendering_context
            self._log_manufacture_exception(filtered_documents, cancel=True)
        return super(WorkOrder, self).action_cancel()

    
    # def button_mark_done(self):
    #     self.ensure_one()
    #     for wo in self.workorder_ids:
    #         if wo.time_ids.filtered(lambda x: (not x.date_end) and (x.loss_type in ('productive', 'performance'))):
    #             raise UserError(_('Work order %s is still running') % wo.name)
    #     self._check_production_lines()
    #     self._post_inventory()
    #     moves_to_cancel = (self.move_raw_ids | self.move_finished_ids).filtered(
    #         lambda x: x.state not in ('done', 'cancel'))
    #     moves_to_cancel._action_cancel()
    #     self.write({'state': 'done', 'date_finished': fields.Datetime.now()})
    #     return super(WorkOrder, self).button_mark_done()




class WorkOrderMail(models.Model):
    _inherit = 'mrp.workorder'

    partner_id = fields.Many2one(related='production_id.partner_id', string='Customer')

#     
#     def record_production(self):
#         if self.production_id.partner_id:
#             body = (_("Dear %s ,\
# <p>Your work order has been confirmed %s.</p>") % (
#             self.production_id.partner_id.name, self.production_id.partner_id.name))
#             subject = "Re:confirmation of work order %s" % (self.production_id.partner_id.name)
#             self.message_post(body=body, subject=subject, partner_ids=[self.production_id.partner_id.id])

#         res=super(WorkOrderMail, self).record_production()
#         return res




class StockMoveInherit(models.Model):
    _inherit = 'stock.move'

    
    @api.depends('move_line_ids.product_qty')
    def _compute_reserved_availability(self):
        for el in self:
            if el.raw_material_production_id.bool_pause:
                for rec in el:
                    rec.reserved_availability = 0.00
            else:

                result = {data['move_id'][0]: data['product_qty'] for data in
                          self.env['stock.move.line'].read_group([('move_id', 'in', self.ids)], ['move_id', 'product_qty'],
                                                                 ['move_id'])}
                for rec in self:
                    rec.reserved_availability = rec.product_id.uom_id._compute_quantity(result.get(rec.id, 0.0),
                                                                                    rec.product_uom,
                                                                                rounding_method='HALF-UP')
    @api.depends('raw_material_production_id')
    def _get_bool_track(self):

        for el in self:
            self.bool_track = False

            lists =[]
            if el.raw_material_production_id.bom_id:
                for rec in  el.raw_material_production_id.bom_id.bom_line_ids:
                    lists.append(rec.product_id.id)
                if el.product_id.id not in lists:
                    el.bool_track =True
                else:
                    el.bool_track = False




    reserved_availability = fields.Float(
        'Quantity Reserved', compute='_compute_reserved_availability',
        digits=dp.get_precision('Product Unit of Measure'),
        readonly=True, help='Quantity that has already been reserved for this move')

    bool_track = fields.Boolean(default=False,compute=_get_bool_track)
    revision_no = fields.Text(string='Revision Number ')

