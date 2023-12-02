from odoo import models, fields, api
import pdb

from collections import namedtuple
import json
import time
from datetime import date

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter
from odoo.addons import decimal_precision as dp
from datetime import datetime, timedelta


class StockPickingInherited(models.Model):
    _inherit = "stock.picking"

    suppliers_invoice_date = fields.Date(string="Suppliers Invoice Date")
    suppliers_test_certificate = fields.Selection([('Required','Required'),('Not Required','Not Required')])
    suppliers_test_certificate_date = fields.Date(string="Suppliers Test Certificate Date")
    test_certificate = fields.Char(string="Test Certificate No")
    test_certificate_date = fields.Date(string="Test Certificate No Date")
    details_of_rejection = fields.Text('Details of Rejection')
    approved_by = fields.Many2one('res.users', string="Approved by",index=True, default=lambda self: self.env.user)
    po_date = fields.Date(string='PO Date')
    kind_attn = fields.Many2one('res.partner',string="Kind Attention")

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
                             'po_quantity': line.product_qty,
                             'date_deadline': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             'picking_type_id': self.picking_type_id.id, 
                             'state': 'draft', 
                             'product_id': line.product_id.id,
                             'location_dest_id': self.location_dest_id.id, 
                             'name': line.product_id.name,
                             'po_ref': purchase.id,
                             'price_unit': line.price_unit,
                             'discount' : line.discount,
                             'price_subtotal': line.price_subtotal,
                             'price_total': line.price_total,
                             'taxes_id': [(6,0,tax_lines)]}))
            values.update(move_ids_without_package=move_lines)
        return {'value':values}



class QualityCheckInherits(models.Model):
    _inherit = "quality.check"

    qty_accepted_under_dev = fields.Float('Quantity Accepted Under Deviation',copy=False)
    qty_accepted_under_dev_val = fields.Float('Qty Under Deviation Val',compute="_get_qty_accepted_under_dev_val")

    @api.depends('qty_accepted_under_dev')
    def _get_qty_accepted_under_dev_val(self):
        for record in self:
            qty=0
            record.qty_accepted_under_dev_val = False
            if record.qty_accepted_under_dev:
                if record.picking_id:
                    quality = self.env['quality.check'].search([('picking_id','=',record.picking_id.id), ('product_id', '=', record.product_id.id)])
                    # quality_1 = self.env['quality.check'].search(
                    #     [('picking_id', '=', record.picking_id.id), ('product_id', '=', record.product_id.id)],limit=1)

                    for el in quality:
                        qty=qty+int(el.qty_accepted_under_dev)
                    for move_id in record.picking_id.move_ids_without_package:
                        if move_id.product_id==record.product_id:
                            move_id.write({'qty_accepted_under_dev':qty})
            # else:
            #    record.qty_accepted_under_dev_val = False
        return True

    
    @api.onchange('qty_accepted_under_dev')
    def _onchange_qty_accepted_under_dev(self):
        for record in self:
            qty = 0
            if record.qty_accepted_under_dev > (record.inspected_qty):
                raise UserError(_('Please check that the Rejected Quantity is greater than Inspected Quantity'
                                  ))
            else:
                record.sudo().update({'qty_accepted_under_dev': record.qty_accepted_under_dev,
                                      'qty_accepted_under_dev_val':record.qty_accepted_under_dev_val
                                      })


class StockMove(models.Model):
    _inherit = "stock.move"

    qty_accepted_under_dev = fields.Float('Quantity Accepted Under Deviation',copy=False)

    po_quantity = fields.Float(string="PO Qty")


