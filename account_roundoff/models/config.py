# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Treesa Maria Jude(<https://www.cybrosys.com>)
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
#    If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################


from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo import fields, models, api, _


class RoundOffSetting(models.TransientModel):
   # _inherit = 'account.config.settings'
    _inherit = 'res.config.settings'
    round_off = fields.Boolean(string='Allow rounding of invoice amount', help="Allow rounding of invoice amount")
    round_off_account = fields.Many2one('account.account', string='Round Off Account')

   #added by soyeb for error fix
    account_fiscal_country_id = fields.Many2one(
        string="Fiscal Country",
        comodel_name='res.country',
        compute='compute_account_tax_fiscal_country',
        store=True,
        readonly=False,
        help="The country to use the tax reports from for this company")

   #round_off = fields.Boolean(string='Allow rounding of invoice amount', help="Allow rounding of invoice amount")
    #round_off_account = fields.Many2one('account.account', string='Round Off Account')

    @api.model
    def get_values(self):
        res = super(RoundOffSetting, self).get_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        res.update(
            round_off_account=int(ICPSudo.get_param('foss_roundoff.round_off_account')),
        )
        return res

    
    def set_values(self):
        super(RoundOffSetting, self).set_values()
        ICPSudo = self.env['ir.config_parameter'].sudo()
        ICPSudo.set_param("foss_roundoff.round_off_account", self.round_off_account.id)



class AccountRoundOff(models.Model):
    _inherit = 'account.move'

    # round_off_value = fields.Float(compute='_compute_amount', string='Round off amount')
    round_off_value = fields.Float(string='Round off amount')
    rounded_total = fields.Float(compute='_compute_amount', string='Rounded Total')
    round_active = fields.Boolean(string="Round Active",default=True)

    @api.depends('invoice_line_ids.price_subtotal', 'invoice_line_ids.tax_ids.amount',
                 'currency_id', 'company_id', 'invoice_date', 'move_type')
    def _compute_amount(self):
        # print('sssssssssssssssssssssssssssssssss',self.amount_untaxed,self.tax_total)
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        # self.amount_tax = sum(round_curr(line.amount_total) for line in self)
        self.amount_tax = sum(round_curr(self.amount_total) for line in self.invoice_line_ids.tax_ids)
        # self.amount_tax = sum(round_curr(line.amount_total) for line in self.invoice_line_ids.tax_ids)
        self.rounded_total = round(self.amount_untaxed + self.tax_total)
        # self.rounded_total = round(self.amount_untaxed + self.amount_tax)
        # print('sssssssssssssssssssssssssssssssss',self.amount_untaxed,self.amount_tax)


        self.amount_total = self.amount_untaxed + self.tax_total
        # self.amount_total = self.amount_untaxed + self.amount_tax
        # self.invoice_line_ids.price_total = self.amount_total
        # print(self.amount_total,self.rounded_total, 'hsddddddddddddhsdddddddd')
        # self.round_off_value = self.rounded_total - (self.amount_untaxed + self.tax_total)
        # self.round_off_value = self.rounded_total - (self.amount_untaxed + self.amount_tax)
        # print('roundoff', self.round_off_value)
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.invoice_date)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.move_type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_in_currency_signed = amount_total_company_signed * sign
        # self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign


    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.move_type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id == self.account_id:
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(
                        date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        if self.round_active is True and self.move_type in ('in_invoice', 'out_invoice'):
            self.residual = round(abs(residual))
        else:
            self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False


    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """
        account_move = self.env['account.move']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise UserError(_('Please define sequence on the journal related to this invoice.'))
            if not inv.invoice_line_ids:
                raise UserError(_('Please create some invoice lines.'))
            if inv.move_id:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.invoice_date:
                inv.with_context(ctx).write({'invoice_date': fields.Date.context_today(self)})
            if not inv.date_due:
                inv.with_context(ctx).write({'date_due': inv.invoice_date})
            company_currency = inv.company_id.currency_id

            # create move lines (one per invoice line + eventual taxes and analytic lines)
            iml = inv.invoice_line_move_line_get()
            iml += inv.tax_line_move_line_get()

            diff_currency = inv.currency_id != company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total, total_currency, iml = inv.with_context(ctx).compute_invoice_totals(company_currency, iml)

            name = inv.name or '/'
            if inv.payment_term_id:
                totlines = inv.with_context(ctx).payment_term_id.with_context(currency_id=company_currency.id).compute(total, inv.invoice_date)[0]
                res_amount_currency = total_currency
                ctx['date'] = inv._get_currency_rate_date()
                for i, t in enumerate(totlines):
                    if inv.currency_id != company_currency:
                        amount_currency = company_currency.with_context(ctx).compute(t[1], inv.currency_id)
                    else:
                        amount_currency = False

                    # last line: add the diff
                    res_amount_currency -= amount_currency or 0
                    if i + 1 == len(totlines):
                        amount_currency += res_amount_currency

                    # if round off is checked in customer invoice or Vendor Bills
                    if self.round_active is True and self.move_type in ('in_invoice', 'out_invoice'):
                        round_price = self.round_off_value
                        if self.move_type == 'in_invoice':
                            round_price = -self.round_off_value
                        iml.append({
                            'move_type': 'dest',
                            'name': name,
                            'price': t[1] + round_price,
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'move_id': inv.id
                        })
                        acc_id = self.env['ir.config_parameter'].sudo().get_param('foss_roundoff.round_off_account')
                        if not acc_id:
                            raise UserError(_('Please configure Round Off Account in Account Setting.'))
                        iml.append({
                            'move_type': 'dest',
                            'name': "Round off",
                            'price': -round_price,
                            'account_id': int(acc_id),
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'move_id': inv.id
                        })
                    else:
                        iml.append({
                            'move_type': 'dest',
                            'name': name,
                            'price': t[1],
                            'account_id': inv.account_id.id,
                            'date_maturity': t[0],
                            'amount_currency': diff_currency and amount_currency,
                            'currency_id': diff_currency and inv.currency_id.id,
                            'move_id': inv.id
                        })
            else:
                # if round off is checked in customer invoice or Vendor Bills
                if self.round_active is True and self.move_type in ('in_invoice', 'out_invoice'):
                    round_price = self.round_off_value
                    if self.move_type == 'in_invoice':
                        round_price = -self.round_off_value
                    iml.append({
                        'move_type': 'dest',
                        'name': name,
                        'price': total + round_price,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'move_id': inv.id
                    })
                    acc_id = self.env['ir.config_parameter'].sudo().get_param('foss_roundoff.round_off_account')
                    if not acc_id:
                        raise UserError(_('Please configure Round Off Account in Account Setting.'))
                    iml.append({
                        'move_type': 'dest',
                        'name': "Round off",
                        'price': -round_price,
                        'account_id': int(acc_id),
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'move_id': inv.id
                    })
                else:
                    iml.append({
                        'move_type': 'dest',
                        'name': name,
                        'price': total,
                        'account_id': inv.account_id.id,
                        'date_maturity': inv.date_due,
                        'amount_currency': diff_currency and total_currency,
                        'currency_id': diff_currency and inv.currency_id.id,
                        'move_id': inv.id
                    })

            part = self.env['res.partner']._find_accounting_partner(inv.partner_id)
            line = [(0, 0, self.line_get_convert(l, part.id)) for l in iml]
            line = inv.group_lines(iml, line)

            journal = inv.journal_id.with_context(ctx)
            line = inv.finalize_invoice_move_lines(line)

            date = inv.date or inv.invoice_date
            move_vals = {
                'ref': inv.reference,
                'line_ids': line,
                'journal_id': journal.id,
                'date': date,
                'narration': inv.comment_proforma,
            }
            ctx['company_id'] = inv.company_id.id
            ctx['invoice'] = inv
            ctx_nolang = ctx.copy()
            ctx_nolang.pop('lang', None)
            move = account_move.with_context(ctx_nolang).create(move_vals)
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled on
            move.post(invoice = inv)
            # make the invoice point to that move
            vals = {
                'move_id': move.id,
                'date': date,
                'move_name': move.name,
            }
            inv.with_context(ctx).write(vals)
        return True
