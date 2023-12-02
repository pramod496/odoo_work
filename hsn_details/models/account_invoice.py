from odoo import api, fields, models, _
from odoo.exceptions import UserError
import math
from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from json import dumps
from odoo.tools import float_compare, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from contextlib import contextmanager
from itertools import zip_longest
from hashlib import sha256

import ast
import json
import re
import warnings


class AccountInvoice(models.Model):
    _inherit = "account.move"

    hsn_line_ids = fields.One2many("hsn.line", 'invoice_id', string='HSN LInes')
    # executes_hsn_table = fields.char("executes hsn", compute="compute_hsn", store=True)
    tax_total = fields.Monetary("Total Tax")
    total_cgst_amount = fields.Float("Total CGST Amount")
    total_sgst_amount = fields.Float("Total SGST Amount")
    total_igst_amount = fields.Float("Total IGST Amount")

    def compute_amount_rounded(self):
        self.amount_untaxed_rounded = round(self.amount_untaxed)
        self.amount_tax_rounded = round(self.amount_tax)

    def action_invoice_open(self):
        for lines in self.invoice_line_ids:
            taxes = lines.tax_ids
        for rec in self.invoice_line_ids:
            if rec.tax_ids != taxes:
                raise UserError(_("You can not use different taxes in a single invoice..!!"))
        return super(AccountInvoice, self).action_invoice_open()

    # @api.onchange('invoice_line_ids')
    # def compute_highest_tax(self):
    #     tax_amt, tax = 0, []
    #     sub_price =0.00
    #     for rec in self.invoice_line_ids:
    #         tax_amt_new, tax_id_new = 0, []
    #         print('highest tax')
    #         for re in rec.tax_ids:
    #             sub_price += re.amount
    #             tax_id_new.append(re.id)
    #         # if tax_amt_new > tax_amt:
    #         #     tax_amt = tax_amt_new
    #         #     tax = tax_id_new
    #     # print("$#$#$#####", tax)
    #     self.freight_tax_ids = [(6, 0, tax)]
    #     self.packing_tax_ids = [(6, 0, tax)]
    #     self.loading_tax_ids = [(6, 0, tax)]
    #     self.testing_tax_ids = [(6, 0, tax)]
    #     raise UserError('hi')

    @api.onchange('invoice_line_ids')
    @api.constrains('amount_total')
    def compute_highest_tax(self):
        tax_amt, tax = 0, []
        for rec in self.invoice_line_ids:
            tax_amt_new, tax_id_new = 0, []
            # print('highest tax')
            for re in rec.tax_ids:
                tax_amt_new += re.amount
                tax_id_new.append(re.id)
            if tax_amt_new > tax_amt:
                tax_amt = tax_amt_new
                tax = tax_id_new
        # print("$#$#$#####", tax)
        self.freight_tax_ids = [(6, 0, tax)]
        self.packing_tax_ids = [(6, 0, tax)]
        self.loading_tax_ids = [(6, 0, tax)]
        self.testing_tax_ids = [(6, 0, tax)]
        if self.invoice_line_ids:
            for i in self.invoice_line_ids:
                if i.price_unit != 0:
                    self.compute_hsn()

    def compute_hsn(self):
        sale = self.env['sale.order'].search([('client_order_ref', '=', self.ref)], limit=1)
        self.sale_id = sale.id
        hsn_list = []
        for rec in self.invoice_line_ids:
            hsn_list.append(rec.hsn_code)
        hsn_list = list(set(hsn_list))
        self.write({
            'hsn_line_ids': [(5, 0, 0)]
        })
        tax_type = 'state'

        # taxes = self.invoice_line_ids.search([], limit=1).invoice_line_tax_ids
        for lines in self.invoice_line_ids:
            taxes = lines.tax_ids
        for tax in taxes:
            if tax.name.upper().find('IGST') != -1:
                tax_type = 'integrated'
                break
        print(tax_type, '@@@@@@@@@@@@@@@@@@@@@')

        inv_list = []
        # print("@@@@@@@@@@@@@@", taxes, tax_type)
        if tax_type == 'state':
            for hsn in hsn_list:
                vals = {}
                # line_ids = self.invoice_line_ids.search([('hsn_code', '=', hsn), ('move_id', '=', self.id)])
                line_ids = self.invoice_line_ids.filtered(lambda line: line.hsn_code == hsn)
                # print(line_ids, len(line_ids))

                hsn_total = 0.00
                for rec in line_ids:
                    hsn_total += rec.price_subtotal

                # print(hsn_total,'hsn total')
                bb_total = 0.00
                # all_line_ids = self.invoice_line_ids.search([('invoice_id', '=', self.id)])
                for rec in self.invoice_line_ids:
                    bb_total += rec.price_subtotal

                extra_charges = 0
                if self.freight_tax_ids:
                    extra_charges += self.freight_value
                if self.packing_tax_ids:
                    extra_charges += self.packing_value
                if self.loading_tax_ids:
                    extra_charges += self.loading_value
                if self.testing_tax_ids:
                    extra_charges += self.testing_value

                percentage = (100 / self.amount_untaxed) * hsn_total
                taxable_amount = (hsn_total * extra_charges / bb_total) + hsn_total

                # print("#######################", percentage, taxable_amount)

                if len(taxes) != 0:

                    for tax in taxes:
                        if tax.name.upper().find('IGST') == -1:

                            if tax.name.upper().find('TCS') == -1:
                                tax_rate = tax.amount
                                print(tax_rate, '&*&^%$$%^')
                                tax_amt = round((taxable_amount * tax_rate) / 100, 2)

                                vals = {
                                    'invoice_id': self.id,
                                    'hsn_code': hsn,
                                    'taxable_value': taxable_amount,
                                    'cgst_rate': tax_rate,
                                    'cgst_amt': tax_amt,
                                    'sgst_rate': tax_rate,
                                    'sgst_amt': tax_amt,
                                    'total_tax_amount': tax_amt * 2,
                                    # 'total_tax_amount_rounded': round(val_d.get('tax_amount') + val_d.get('extra_tax')),
                                }
                    inv_list.append((0, 0, vals))

                # for tax in taxes:
                #     if tax.name.upper().find('IGST') == -1 and tax.name.upper().find('SGST') == -1 and tax.name.upper().find('CGST') == -1:
                #
                #         if tax.name.upper().find('TCS') == -1 :
                #             tax_rate = tax.amount
                #             print(tax_rate, '&*&^%$$%^')
                #             tax_amt = round((taxable_amount * tax_rate) / 100, 2)

        if tax_type == "integrated":
            for hsn in hsn_list:
                vals = {}
                line_ids = self.invoice_line_ids.filtered(lambda line: line.hsn_code == hsn)
                # print(line_ids, len(line_ids))
                bb_total = 0.00

                hsn_total = 0.00
                for rec in line_ids:
                    hsn_total += rec.price_subtotal
                for rec in self.invoice_line_ids:
                    bb_total += rec.price_subtotal
                extra_charges = 0
                if self.freight_tax_ids:
                    extra_charges += self.freight_value
                if self.packing_tax_ids:
                    extra_charges += self.packing_value
                if self.loading_tax_ids:
                    extra_charges += self.loading_value
                if self.testing_tax_ids:
                    extra_charges += self.testing_value

                # try:
                percentage = (100 / self.amount_untaxed) * hsn_total
                taxable_amount = (hsn_total * extra_charges / bb_total) + hsn_total
                for tax in taxes:
                    print(tax.amount)
                    print(tax.name, '$$$$')
                    if tax.name.upper().find('TCS') == -1:
                        # continue

                        tax_rate = tax.amount
                        tax_amt = (taxable_amount * tax_rate) / 100

                vals = {
                    'invoice_id': self.id,
                    'hsn_code': hsn,
                    'taxable_value': taxable_amount,
                    'igst_rate': tax_rate,
                    'igst_amt': tax_amt,
                    'total_tax_amount': tax_amt,
                }

                inv_list.append((0, 0, vals))

        else:
            if len(taxes) == 0:
                for hsn in hsn_list:
                    vals = {}
                    line_ids = self.invoice_line_ids.filtered(lambda line: line.hsn_code == hsn)
                    # print(line_ids, len(line_ids))
                    bb_total = 0.00

                    hsn_total = 0.00
                    for rec in line_ids:
                        hsn_total += rec.price_subtotal
                    for rec in self.invoice_line_ids:
                        bb_total += rec.price_subtotal
                    extra_charges = 0
                    if self.freight_tax_ids:
                        extra_charges += self.freight_value
                    if self.packing_tax_ids:
                        extra_charges += self.packing_value
                    if self.loading_tax_ids:
                        extra_charges += self.loading_value
                    if self.testing_tax_ids:
                        extra_charges += self.testing_value

                    # try:
                    percentage = (100 / self.amount_untaxed) * hsn_total
                    taxable_amount = (hsn_total * extra_charges / bb_total) + hsn_total
                    vals = {
                        'invoice_id': self.id,
                        'hsn_code': hsn,
                        'taxable_value': taxable_amount,
                        # 'total_tax_amount_rounded': round(val_d.get('tax_amount') + val_d.get('extra_tax')),
                    }
                    inv_list.append((0, 0, vals))

        self.write({'hsn_line_ids': inv_list})
        self.compute_tax_totals()


    def compute_tax_totals(self):
        if self.hsn_line_ids:
            total_cgst, total_sgst, total_igst = 0, 0, 0
            for rec in self.hsn_line_ids:
                # total += rec.total_tax_amount
                total_cgst += rec.cgst_amt
                total_sgst += rec.sgst_amt
                total_igst += rec.igst_amt
                # total_igst += rec.igst_amt

            # self.tax_total = total
            self.total_cgst_amount = total_cgst
            self.total_sgst_amount = total_sgst
            self.total_igst_amount = total_igst

        else:
            # self.tax_total = 0.00
            self.total_cgst_amount = 0.00
            self.total_sgst_amount = 0.00
            self.total_igst_amount = 0.00
        self.compute_total_hsn_tax()

    @api.onchange('total_cgst_amount', 'total_sgst_amount', 'total_igst_amount')
    def compute_total_hsn_tax(self):
        self.tax_total = self.total_cgst_amount + self.total_sgst_amount + self.total_igst_amount
        self.amount_total = self.amount_untaxed + self.tax_total + self.tcs_amount
        self.amount_tax = self.tax_total


class AccountInvoiceLine(models.Model):
    _inherit = "account.move.line"

    subtotal_cus = fields.Float("Subtotal", compute="update_subtotal")

    def update_subtotal(self):
        for rec in self:
            if rec.price_subtotal:
                rec.subtotal_cus = self.round_down(rec.price_subtotal)
            else:
                rec.subtotal_cus = 0.00

    def round_down(self, value):
        return math.floor(value * 100)/100.0
