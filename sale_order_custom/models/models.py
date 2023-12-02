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


class SaleOrderLineInherited(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('material_line_ids.sale_price')
    def _compute_estimation_amount(self):
        """
        Compute the amounts of the Bom line.
        """
        qty = 0
        for rec in self:
            for line in rec.material_line_ids:
                qty = qty + line.sale_price
            self.update({
                'total_est_price': qty,

            })


    schedule_ids = fields.One2many(
        'sale.order.line.schedule',
        'sale_order_line_id',
        string='Scheduled Dates',
    )
    material_line_ids = fields.One2many('sale.order.line.materials', 'material_id', string='Material Lines',
                    copy=False,)
    total_est_price = fields.Monetary(compute='_compute_estimation_amount', string='Total Estimated Price', store=True, default=0.0)

class SaleOrderSchedule(models.Model):
    _name = "sale.order.line.schedule"

    sale_order_line_id = fields.Many2one(
        'sale.order.line',
        string='Sale Order Line ID',
    )

    planned_date = fields.Datetime(
        string='Planned Date',
    )

    planned_quantity = fields.Float(
        string='Planned Quantity',
    )
    # uom_id = fields.Many2one(
    #     'uom.uom',
    #     string='Unit of Measure',default = lambda self: self.sale_order_line_id.product_uom
    # )

class sale_order_line_materials(models.Model):

    _name = "sale.order.line.materials"

    
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {}
        if self.product_id:
            self.hsn_code = self.product_id.default_code
            self.sale_price = self.product_id.standard_price




    material_id = fields.Many2one('sale.order.line', string='sale Order Reference')
    product_id = fields.Many2one('product.product', string='Product')
    hsn_code = fields.Char('Code')
    sale_price = fields.Float('Cost Price')


class SaleOrderCustom(models.Model):
    _inherit = 'sale.order'

    invoice_status_custom = fields.Selection([
        ('invoiced', 'Invoiced'),
        ('half_invoice', 'Partially Invoiced'),
        ('not', 'Yet to Invoice')
    ], string='SO Invoice Status', compute='_get_inv_status',store=True, readonly=True)



    @api.depends('order_line.invoice_status_line')
    def _get_inv_status(self):
        for res in self:
            if res.invoice_count:
                not_state = res.order_line.filtered(lambda x: x.invoice_status_line in ('not'))
                half_state = res.order_line.filtered(lambda x: x.invoice_status_line in ('half_invoice'))
                full_state = res.order_line.filtered(lambda x: x.invoice_status_line in ('invoiced'))
                if half_state:
                    res.invoice_status_custom = 'half_invoice'
                elif not full_state:
                    res.invoice_status_custom = 'not'
                elif not_state and full_state:
                    res.invoice_status_custom = 'half_invoice'
                else:
                    res.invoice_status_custom = 'invoiced'
            if not res.invoice_count:
                res.invoice_status_custom = 'not'

    def update_all_sale_orders(self):
        order_id = self.search([])
        for res in order_id:
            if res.invoice_count:
                not_state = res.order_line.filtered(lambda x: x.invoice_status_line in ('not'))
                half_state = res.order_line.filtered(lambda x: x.invoice_status_line in ('half_invoice'))
                full_state = res.order_line.filtered(lambda x: x.invoice_status_line in ('invoiced'))
                if half_state:
                    res.invoice_status_custom = 'half_invoice'
                elif not full_state:
                    res.invoice_status_custom = 'not'
                elif not_state and full_state:
                    res.invoice_status_custom = 'half_invoice'
                else:
                    res.invoice_status_custom = 'invoiced'
            if not res.invoice_count:
                res.invoice_status_custom = 'not'


class SaleOrderCustom(models.Model):
    _inherit = 'sale.order.line'


    invoice_status_line = fields.Selection([
        ('invoiced', 'Invoiced'),
        ('half_invoice', 'Partially Invoiced'),
        ('not', 'Yet to Invoice')
    ], string='Invoice Status', compute='_get_invoice_status', readonly=True, store=True)

    @api.depends('invoice_status_line', 'product_uom_qty', 'qty_invoiced')
    def _get_invoice_status(self):
        for rec in self:
            if rec.qty_invoiced == 0.0 :
                rec.invoice_status_line = 'not'
            elif rec.qty_invoiced > 0.0 :
                if rec.product_uom_qty <= rec.qty_invoiced:
                    rec.invoice_status_line = 'invoiced'
                if rec.qty_invoiced < rec.product_uom_qty:
                    rec.invoice_status_line = 'half_invoice'





    # def _get_invoice_status(self):
    #     for res in self:
    #         if not res.invoice_count:
    #             res.invoice_status_custom = 'not'
    #         inv_rec = self.env['account.move'].search([('origin', '=', res.name)])
    #         for rec in inv_rec:
    #             if rec.state == 'open':
    #                 if rec.residual > 0 and rec.residual < rec.amount_total:
    #                     res.invoice_status_custom = 'half invoice'
    #             if rec.state == 'paid':
    #                 res.invoice_status_custom = 'invoiced'
    #             if rec.state == 'draft' or rec.residual == rec.amount_total:
    #                 res.invoice_status_custom = 'not'





    



            
            

            

            
            

            
