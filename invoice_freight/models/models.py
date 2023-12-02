# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import email_re, email_split, email_escape_char, float_is_zero, float_compare, pycompat, date_utils

class AccountInvoiceInherit(models.Model):
    _inherit = 'account.move'

    freight_type = fields.Selection([('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Untaxed'), ('none', 'None')])
    freight_value = fields.Float(string='Value', store=True,)
    packing_value = fields.Float(string='Value', store=True,)
    testing_value = fields.Float(string='Value', store=True,)
    loading_value = fields.Float(string='Value', store=True,)
    packing_amount = fields.Float(string='Untaxed Packing Amount', store=True, compute='_compute_amount',)
    testing_amount = fields.Float(string='Untaxed Testing Amount', store=True, compute='_compute_amount',)
    loading_amount = fields.Float(string='Untaxed Loading Amount', store=True, compute='_compute_amount',)
    freight_amount  = fields.Float(
        string='Untaxed Freight Amount', store = True,compute='_compute_amount',
    )
    freight_total = fields.Float(
        string='Freight Total',store = True,compute='_compute_amount',
    )
    packing_total = fields.Float(
        string='Packing Total',store = True,compute='_compute_amount',
    )
    testing_total = fields.Float(
        string='Testing Total', store=True, compute='_compute_amount',
    )
    loading_total = fields.Float(
        string='Loading Total', store=True, compute='_compute_amount',
    )
    freight_tax = fields.Float(
        string='Freight Tax Total',store = True,compute='_compute_amount',
    )
    packing_tax = fields.Float(
        string='Packing Tax Total',store = True,compute='_compute_amount',
    )
    testing_tax = fields.Float(
        string='Testing Tax Total', store=True, compute='_compute_amount',
    )
    loading_tax = fields.Float(
        string='Loading Tax Total', store=True, compute='_compute_amount',
    )
    freight_tax_ids = fields.Many2many(
        'account.tax', 'freight_account_move_tax_rel',
        string='Taxes for Freight',store = True,
    )
    packing_tax_ids = fields.Many2many(
        'account.tax', 'packing_account_move_tax_rel',
        string='Taxes for Packing',store = True,
    )
    testing_tax_ids = fields.Many2many('account.tax', 'testing_account_move_tax_rel', string='Taxes for Testing')
    loading_tax_ids = fields.Many2many('account.tax', 'loading_account_move_tax_rel', string='Taxes for Loading')
    tcs = fields.Many2one('tcs.tcs', string="TCS")
    tcs_value = fields.Float("TCS Amount")
    tcs_amount = fields.Float("TCS Amount", store=True, compute='_compute_amount')

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.tax_ids.amount',
                 'currency_id', 'company_id', 'invoice_date', 'move_type', 'freight_type', 'freight_value',
                 'freight_tax_ids', 'packing_value', 'packing_tax_ids', 'loading_value', 'loading_tax_ids',
                 'testing_value', 'testing_tax_ids', 'tcs_value')
    def _compute_amount(self):
        # print('sssin tax')
        super(AccountInvoiceInherit, self)._compute_amount()
        for rec in self:
            round_curr = rec.currency_id.round
            # for tax_line in rec.tax_line_ids:
            #     tax_line.amount_total = round(tax_line.amount_total)
                # print("$%$%$%$%$%$%$", tax_line.amount_total)
            rec.amount_untaxed = sum(line.price_subtotal for line in rec.invoice_line_ids)
            rec.amount_tax = sum(round_curr(line.amount) for line in rec.invoice_line_ids.tax_ids)
            tax_cal = rec.amount_tax / 100 * rec.amount_untaxed

            rec.amount_untaxed = sum(line.price_subtotal for line in rec.invoice_line_ids)
            rec.freight_amount = rec.freight_value
            rec.packing_amount = rec.packing_value
            rec.loading_amount = rec.loading_value
            rec.testing_amount = rec.testing_value
            rec.tcs_amount = rec.tcs_value
            # round_curr = self.currency_id.round

            rec.amount_tax = sum(round_curr(line.amount) for line in rec.invoice_line_ids.tax_ids)


            for i in rec.freight_tax_ids:
                rec.freight_tax += i.amount*rec.freight_amount/100
            for i in rec.packing_tax_ids:
                rec.packing_tax += i.amount*rec.packing_amount/100
            for i in rec.testing_tax_ids:
                rec.testing_tax += i.amount*rec.testing_amount/100
            for i in rec.loading_tax_ids:
                rec.loading_tax += i.amount*rec.loading_amount/100

            # print(self.amount_tax,"SDASDASD")
            rec.amount_tax += rec.packing_tax + rec.freight_tax + rec.loading_tax + rec.testing_tax
            # rec.amount_tax = round(rec.amount_tax)
            # print(round(self.amount_tax), "SDA#####")
            rec.freight_total = rec.freight_tax + rec.freight_amount
            rec.packing_total = rec.packing_tax + rec.packing_amount
            rec.loading_total = rec.loading_tax + rec.loading_amount
            rec.testing_total = rec.testing_tax + rec.testing_amount

            rec.amount_total = rec.amount_untaxed + rec.amount_tax + rec.freight_amount + rec.packing_amount + rec.testing_amount + rec.loading_amount

            rec.rounded_total = round(rec.amount_untaxed + rec.freight_amount + rec.packing_amount + rec.testing_amount + rec.loading_amount + rec.tcs_amount + rec.tax_total)
            # rec.rounded_total = round(rec.amount_untaxed + rec.amount_tax + rec.freight_amount + rec.packing_amount + rec.testing_amount + rec.loading_amount + rec.tcs_amount)
            # print(rec.rounded_total,rec.amount_untaxed,rec.amount_tax,rec.freight_amount,rec.packing_amount,rec.tcs_amount,'frieght')
            rec.amount_total = tax_cal + rec.amount_untaxed + rec.freight_amount + rec.packing_amount + rec.testing_amount + rec.loading_amount + rec.tcs_amount
            # removed by soyeb bcz it was overriding real roundoff# rec.round_off_value = rec.rounded_total - (rec.amount_untaxed + rec.amount_tax + rec.freight_amount + rec.packing_amount + rec.testing_amount + rec.loading_amount + rec.tcs_amount)
            # print(rec.round_off_value,'soyebbbbbbbbbbbbbb',rec.rounded_total,rec.amount_untaxed,rec.amount_tax,rec.freight_amount,rec.packing_amount,rec.testing_amount,rec.loading_amount,rec.tcs_amount)
            amount_total_company_signed = rec.amount_total
            amount_untaxed_signed = rec.amount_untaxed
            if rec.currency_id and rec.company_id and rec.currency_id != rec.company_id.currency_id:
                currency_id = rec.currency_id
                amount_total_company_signed = currency_id._convert(rec.amount_total, rec.company_id.currency_id, rec.company_id, rec.invoice_date or fields.Date.today())
                amount_untaxed_signed = currency_id._convert(rec.amount_untaxed, rec.company_id.currency_id, rec.company_id, rec.invoice_date or fields.Date.today())
            sign = rec.move_type in ['in_refund', 'out_refund'] and -1 or 1
            rec.amount_total_in_currency_signed = amount_total_company_signed * sign
            rec.amount_total_signed = rec.amount_total * sign
            rec.amount_untaxed_signed = amount_untaxed_signed * sign

    # @api.onchange('invoice_line_ids')
    # def _onchange_invoice_line_ids(self):
    #     taxes_grouped = self.get_taxes_values()
    #     tax_lines = self.tax_line_ids.filtered('manual')
    #     for tax in taxes_grouped.values():
    #         # print("@#@#@@@@@@@", tax)
    #         tax['amount'] = round(tax['amount'])
    #         # print("@#@#@@@@@@@", tax)
    #         tax_lines += tax_lines.new(tax)
    #     self.tax_line_ids = tax_lines
    #     return


    
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = line.currency_id or line.company_id.currency_id
                    residual += from_currency._convert(line.amount_residual, self.currency_id, line.company_id, line.date or fields.Date.today())
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        # print(residual,"XDDDDD")
        # print(self.packing_total, self.freight_total,"XEEEEEEE")
        residual += self.packing_total + self.freight_total
        # print(residual)
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False

class SaleOrderInherit(models.Model):
    _inherit = "sale.order"

    freight_type = fields.Selection([('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Untaxed'), ('none', 'None')])
    freight_value = fields.Float(string='Value',store = True,)
    packing_value = fields.Float(string='Value',store = True,)
    packing_amount = fields.Float(string='Untaxed Packing Amount',store = True,compute='_amount_all',)
    freight_amount  = fields.Float(
        string='Untaxed Freight Amount',store = True,compute='_amount_all',
    )
    freight_total = fields.Float(
        string='Freight Total',store = True,compute='_amount_all',
    )
    packing_total = fields.Float(
        string='Packing Total',store = True,compute='_amount_all',
    )
    freight_tax = fields.Float(
        string='Freight Tax Total',store = True,compute='_amount_all',
    )
    packing_tax = fields.Float(
        string='Packing Tax Total',store = True,compute='_amount_all',
    )
    freight_tax_ids = fields.Many2many(
        'account.tax', 'freight_sale_tax_rel',
        string='Taxes for Freight',store = True,
    )
    packing_tax_ids = fields.Many2many(
        'account.tax', 'packing_sale_tax_rel',
        string='Taxes for Packing',store = True,
    )


    @api.depends('order_line.price_total', 'freight_value','packing_value','freight_tax_ids','packing_tax_ids')
    def _amount_all(self):

        self.freight_amount = self.freight_value
        self.packing_amount = self.packing_value
        for i in self.freight_tax_ids:
            self.freight_tax += i.amount*self.freight_amount/100
        for i in self.packing_tax_ids:
            self.packing_tax += i.amount*self.packing_amount/100
        self.freight_total = self.freight_tax + self.freight_amount
        self.packing_total = self.packing_tax + self.packing_amount
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            amount_tax+= self.freight_tax + self.packing_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'packing_amount': self.packing_amount,
                'packing_tax': self.packing_tax,
                'packing_tax': self.packing_total,
                'freight_amount': self.freight_amount,
                'freight_tax': self.freight_tax,
                'freight_tax': self.freight_total,
                'amount_total': amount_untaxed + amount_tax + self.freight_amount + self.packing_amount,
            })
