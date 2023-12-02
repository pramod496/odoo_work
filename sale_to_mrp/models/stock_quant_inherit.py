import base64
from datetime import datetime, timedelta

from odoo import api, models, fields, _
from odoo.tests.common import Form
from odoo.exceptions import UserError
import csv
import pdb


# class document_file(models.ModelModel):
#     _inherit = 'ir.attachment'


class VendorCodeCustomer(models.Model):
    _inherit = "res.partner"

    vendor_id = fields.Many2one('crm.lead', string="Type")
    state_code_res = fields.Char(string='State code')
    alternative_num = fields.Char(String='Alternative Phone Number')
    alternative_email = fields.Char(String='Alternative Email')
    alternative_num1 = fields.Char(String='Alternative Mobile Number')




class StockQuantInherit(models.Model):
    _inherit = 'stock.quant'




    @api.depends('quantity', 'standard_price')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            value = line.quantity * line.standard_price
            line.update({
                'total_value': value,
            })

    standard_price = fields.Float(string='Cost',related='product_id.standard_price',track_visibility='always',store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id)
    total_value = fields.Monetary(compute='_compute_amount', currency_field='currency_id', string='Value', readonly=True,track_visibility='always',store=True)

class StateCode(models.Model):
    _inherit = 'res.company'

    state_code_new = fields.Char(string='State code')
    alternative_num = fields.Char(String='Alternative Phone Number')
    alternative_num1 = fields.Char(String='Alternative Mobile Number')
    alternative_email = fields.Char(String='Alternative Email')