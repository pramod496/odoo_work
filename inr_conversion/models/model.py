from odoo import models, fields, api
from odoo.tools import float_round
from odoo.exceptions import UserError


class sale_order(models.Model):

    _inherit = "sale.order"

    price_in_inr = fields.Float('Price in INR', required=True, default='1.0')
    total_in_inr = fields.Float('Total in INR', compute='amount_in_inr')

    # @api.depends('amount_total')
    def amount_in_inr(self):
        for record in self :
            if record.pricelist_id.currency_id:
                record.total_in_inr = record.price_in_inr * record.amount_total


class purchase_order(models.Model):

    _inherit = "purchase.order"

    cost_in_inr = fields.Float('Cost in INR', required=True, default='1.0')
    total_in_inr = fields.Float('Total in INR', compute='amount_in_inr')

    # @api.depends('amount_total')
    def amount_in_inr(self):
        for record in self :
            if record.currency_id:
                record.total_in_inr = record.cost_in_inr * record.amount_total
