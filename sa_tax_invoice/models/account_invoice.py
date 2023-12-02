from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
import math
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountInvoice(models.Model):
    _inherit = "account.move"

    sale_id_rel = fields.Many2one('sale.order')

    def get_hsn_count(self):
        a, b = [], []
        docs = self.env['account.move'].browse(self.id)
        origin = docs.name
        po_ref = ""
        po_date = ""
        if origin:
            orig = origin.split(', ')
            for ori in orig:
                # sale = self.env['sale.order'].search([('name', '=', ori)])
                sale = self.env['sale.order'].search([('client_order_ref', '=', self.ref)],limit=1)
                self.sale_id_rel = sale
                # for i in sale:
                #     self.sale_id_rel = i

                a.append(sale.client_order_ref)
                # a.append(sale.client_order_ref)
                if sale.po_date:
                # if sale.po_date == True:
                    b.append(sale.po_date.strftime("%d-%m-%Y"))
                # else:
                #     b.append(sale.po_date.strftime("%d-%m-%Y"))
            po_ref = ' / '.join(map(str, a))
            po_date = ' / '.join(map(str, b))
        sale_id = self.env['sale.order'].search([('name', '=', docs.name)])
        # print(sale_id.price_tax,'sale')
        # stock_id = self.env['stock.picking'].search([('origin', '=', sale_id.name)])
        hsn, hsn_list = [], []
        tax_type = ""
        for i in docs:
            if len(i.invoice_line_ids) == 0:
                raise UserError(_('No Invoice Lines'))
            for j in i.invoice_line_ids:
                # print(j.amount_tax,'invoice line')
                if j.tax_ids:
                    if j.hsn_code in hsn:
                        for l in hsn_list:
                            if l['hsn_code'] == j.hsn_code:
                                if tax_type == "state":
                                    for k in j.tax_ids:
                                    # for k in j.invoice_line_tax_ids:
                                        l['total_taxable_amount'] += self.amount_tax
                                        # l['total_taxable_amount'] += j.price_tax
                                        l['taxable_value'] += j.price_subtotal
                                        l['tax_amount_sgst'] = l['total_taxable_amount'] / 2
                                        l['tax_amount_cgst'] = l['total_taxable_amount'] / 2
                                elif tax_type == "integ":
                                    l['total_taxable_amount'] += self.amount_tax
                                    # l['total_taxable_amount'] += j.price_tax
                                    l['tax_amount_igst'] += self.amount_tax
                                    # l['tax_amount_igst'] += j.price_tax
                                    l['taxable_value'] += j.price_subtotal
                                else:
                                    raise UserError(_('Neither Integrated nor State Taxes'))
                    else:
                        tax_rate_igst = ""
                        hsn.append(j.hsn_code)
                        tax_p = 0
                        for k in j.tax_ids:
                            if tax_type == "":
                                if "cgst" in k.name.lower() or "sgst" in k.name.lower():
                                    tax_type = "state"
                                elif "igst" in k.name.lower():
                                    tax_type = "integ"
                            if tax_type == "state":
                                if "igst" in k.name.lower():
                                    raise UserError(_('Mix of Integrated and State Taxes'))
                                else:
                                    if "cgst" in k.name.lower():
                                        tax_rate_cgst = k.amount
                                    else:
                                        tax_rate_sgst = k.amount
                            elif tax_type == "integ":
                                if "cgst" in k.name.lower() or "sgst" in k.name.lower():
                                    raise UserError(_('Mix of Integrated and State Taxes'))
                                tax_rate_igst = k.amount
                        if tax_type == "state":
                            if tax_rate_sgst.is_integer():
                                tax_rate_sgst = round(tax_rate_sgst)
                            if tax_rate_cgst.is_integer():
                                tax_rate_cgst = round(tax_rate_cgst)
                            hsn_list.append({
                                'hsn_code': j.hsn_code,
                                'taxable_value': j.price_subtotal,
                                'tax_rate_sgst': tax_rate_sgst,
                                'tax_amount_sgst': j.tax_base_amount / 2,
                                'tax_rate_cgst': tax_rate_cgst,
                                'tax_amount_cgst': j.tax_base_amount / 2,
                                'total_taxable_amount': j.tax_base_amount,
                            })
                        elif tax_type == "integ":
                            hsn_list.append({
                                'hsn_code': j.hsn_code,
                                'taxable_value': j.price_subtotal,
                                'tax_rate_igst': round(tax_rate_igst),
                                'tax_amount_igst': j.tax_base_amount,
                                'total_taxable_amount': j.tax_base_amount,
                            })
        return hsn_list

    def page_shift(self):
        rec = self.get_no()
        data_length = len(self.invoice_line_ids)
        if data_length == 1 and len(self.get_hsn_count()) <= 3 and self.extra_charges_count() <= 4:
            return 1
        if data_length == 2 and len(self.get_hsn_count()) <= 2 and self.extra_charges_count() <= 4:
            return 1
        if data_length == 3 and self.extra_charges_count() > 1:  # and len(self.get_hsn_count()) <= 1
            return 3
        if data_length == 3 and self.extra_charges_count() <= 1:
            return 3
            # return 2
        if data_length == 4:
            return 3
        if rec == 4:
            data_length = data_length - 4
            last_page_line_count_data = data_length % 6
            # print("#################", last_page_line_count_data)
            if last_page_line_count_data == 1:
                return 1
            if last_page_line_count_data == 2 and len(self.get_hsn_count()) <= 5:
                return 1
            if last_page_line_count_data == 3 and len(self.get_hsn_count()) <= 5 and self.extra_charges_count() <= 4:
                return 1
            if last_page_line_count_data == 3 and len(self.get_hsn_count()) > 5 and self.extra_charges_count() <= 2:
                return 1
            if last_page_line_count_data == 3 and len(self.get_hsn_count()) > 5:
                return 2
            if last_page_line_count_data == 4:
                if (not self.extra_charges_count()) and len(self.get_hsn_count()) <= 5:
                    return 1
                if self.extra_charges_count() == 1 and len(self.get_hsn_count()) <= 4:
                    return 1
                if self.extra_charges_count() == 2 and len(self.get_hsn_count()) <= 3:
                    return 1
                if self.extra_charges_count() == 3 and len(self.get_hsn_count()) <= 2:
                    return 1
                if self.extra_charges_count() == 4 and len(self.get_hsn_count()) <= 1:
                    return 1
                else:
                    return 2
            if last_page_line_count_data == 5:
                if self.extra_charges_count() < 4:
                    return 2
                else:
                    return 3
            if not last_page_line_count_data:
                return 3

    def hns_line_count(self, hsn_list):
        return len(hsn_list)

    def extra_charges_count(self):
        count = 0
        if self.freight_value:
            count += 1
        if self.packing_value:
            count += 1
        if self.testing_value:
            count += 1
        if self.loading_value:
            count += 1
        return count

    def get_uom_total(self):
        uom = []
        for l in self.invoice_line_ids:
            uom.append(l.product_uom_id.name)
        if len(set(uom)) == 1:
            return uom[0]
        else:
            return False

    def get_no(self):
        data_set, count = 0, 0
        if self.partner_shipping_id:
            count += 1
        elif self.buyer_id:
            count += 1

        if count:
            data_set = 4
        if not count:
            data_set = 5
        return data_set

    # e_invoice report code
    def einvoice_get_no(self):
        data_set, count = 0, 0
        einvoice = 1
        if einvoice:
            count += 1
        if self.partner_shipping_id:
            count += 1
        elif self.buyer_id:
            count += 1
        if count:
            data_set = 1
            # data_set = 4
        if not count:
            data_set = 5
        return data_set

    def page_shift_einvoice(self):
        rec = self.einvoice_get_no()
        data_length = len(self.invoice_line_ids)
        if data_length == 1 and len(self.get_hsn_count()) <= 3 and self.extra_charges_count() <= 4:
            # return 1
            return 0
        if data_length == 2 and len(self.get_hsn_count()) <= 2 and self.extra_charges_count() <= 4:
            return 1
            # return 0
        if data_length == 3 and self.extra_charges_count() > 1:  # and len(self.get_hsn_count()) <= 1
            return 3
        if data_length == 3 and self.extra_charges_count() <= 1:
            return 3
        if data_length == 4:
            return 3
            # added by soyeb
        if data_length == 7:
            return 3
        if data_length == 8:
            return 3
        # if data_length == 7:
        #     return 5
        # if rec == 4:
        #     data_length = data_length - 4
        #     last_page_line_count_data = data_length % 6
        #     print("#################", last_page_line_count_data, data_length)
        #     if last_page_line_count_data == 1:
        #         print("55555555555555555555555555555555555555")
        #         return 1
        #     if last_page_line_count_data == 2 and len(self.get_hsn_count()) <= 5:
        #         print("^6666666666666666666666666666666666666")
        #         return 1
        #     if last_page_line_count_data == 3 and len(self.get_hsn_count()) <= 5 and self.extra_charges_count() <= 4:
        #         print("&7777777777777777777777777777777")
        #         return 1
        #     if last_page_line_count_data == 3 and len(self.get_hsn_count()) > 5 and self.extra_charges_count() <= 2:
        #         print("88888888888888888888888888")
        #         return 1
        #     if last_page_line_count_data == 3 and len(self.get_hsn_count()) > 5:
        #         print("99999999999999999999999999999999")
        #         return 2
        #     if last_page_line_count_data == 4:
        #         print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$4")
        #         if (not self.extra_charges_count()) and len(self.get_hsn_count()) <= 5:
        #             return 1
        #         if self.extra_charges_count() == 1 and len(self.get_hsn_count()) <= 4:
        #             return 1
        #         if self.extra_charges_count() == 2 and len(self.get_hsn_count()) <= 3:
        #             return 1
        #         if self.extra_charges_count() == 3 and len(self.get_hsn_count()) <= 2:
        #             return 1
        #         if self.extra_charges_count() == 4 and len(self.get_hsn_count()) <= 1:
        #             return 1
        #         else:
        #             return 2
        #     if last_page_line_count_data == 5:
        #         print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
        #         if self.extra_charges_count() < 4:
        #             return 2
        #         else:
        #             return 3
        #     if not last_page_line_count_data:
        #         print("###########################################3333")
        #         return 3
        # +++++++++++==========================================================

    def get_page_no(self):
        data_length = len(self.invoice_line_ids)
        dd = self.get_no()
        page = (data_length // dd) + 1
        # if data_length <= 4:
        #     page += 1
        if ((data_length - dd) == 6) and len(self.get_hsn_count()) > 3:
            page += 1
        if self.page_shift() in [1, 2, 3]:
            page += 1
        elif self.page_shift() == 5:
            if len(self.get_hsn_count()) > 3:
                page += 1
        return page

    def get_order_line_list(self):
        return_list = []
        count = 1
        for rec in self.invoice_line_ids:
            data = {
                'count': count,
                'name': rec.get_name(rec.name),
                'name_bold': rec.product_id.name,
                'hsn_code': rec.product_id.product_tmpl_id.l10n_in_hsn_code,
                'quantity': self.qty_check(rec.quantity),
                'is_transport_charges': rec.is_transport_charges,
                'price_unit': rec.price_unit,
                'uom': rec.product_uom_id.name,
                'product_uom_id': rec.product_uom_id,
                'discount': rec.discount,
                'price_subtotal': rec.price_subtotal,
            }
            count += 1
            return_list.append(data)
        return return_list

    def round_down(self, value):
        return math.floor(value * 100) / 100.0

    @api.model
    @api.depends('invoice_line_ids.hsn_value')
    def amount_total_function(self):
        for rec in self:
            qty = 0
            for line in rec.invoice_line_ids:
                qty = qty + line.hsn_value
            rec.update({
                'total_val': qty
            })

    @api.model
    @api.depends('invoice_line_ids.cgst_value')
    def amount_cgst_tax_total_function(self):
        for rec in self:
            qty = 0
            for line in rec.invoice_line_ids:
                qty = qty + line.cgst_value
            rec.update({
                'cgst_val': qty
            })

    @api.model
    @api.depends('invoice_line_ids.sgst_value')
    def amount_sgst_tax_total_function(self):
        for rec in self:
            qty = 0
            for line in rec.invoice_line_ids:
                qty = qty + line.sgst_value
            rec.update({
                'sgst_val': qty
            })

    @api.model
    @api.depends('invoice_line_ids.igst_value')
    def amount_igst_tax_total_function(self):
        for rec in self:
            qty = 0
            for line in rec.invoice_line_ids:
                qty = qty + line.igst_value
            rec.update({
                'igst_val': qty
            })

    @api.model
    @api.depends('invoice_line_ids.total_tax_value')
    def amount_total_tax_amount_function(self):
        for rec in self:
            qty = 0
            if rec.amount_tax > 0.0:
                for line in rec.invoice_line_ids:
                    qty = qty + float(line.total_tax_value)
                rec.update({
                    'total_tax_val': round(qty, 2)
                })
            else:
                rec.update({'total_tax_val': 0.0})

    def get_hsn_code(self, hsn):
        list1 = []
        for invoice_line in self.invoice_line_ids:
            list1.append(invoice_line.product_id.l10n_in_hsn_code)
        hsn_group = list(set(list1))
        return hsn_group

    @api.depends('invoice_line_ids.total_tax_value')
    def _compute_hsn_total_tax(self):
        """Compute the amounts of the Bom line."""
        for rec in self:
            qty = 0
            for line in rec.invoice_line_ids:
                qty = qty + float(line.total_tax_value)
            rec.update({
                'hsn_total_tax': qty,
            })

    def amount_to_text_custm(self, amt):
        if self.currency_id.name == "INR":
            # value = self.currency_id.amount_to_text(amt).replace("Rupees", "")
            # if int(amt) == amt:
            #     value = self.number_to_word(amt).replace("Paisa", "")
            # else:
            value = self.number_to_word(amt)
            if amt % 10:
                have = False
                for wrd in value.split(" "):
                    if 'And' in wrd:
                        have = True
                if not have:
                    new_val = ""
                    for r in value.split(" "):
                        if not r:
                            new_val += ' And'
                        else:
                            new_val += ' ' + r
                    value = new_val

            # print("#$#$#$#$#$#$##########", value)
            # if int(amt) != amt:
            #     value = value.replace('And', '', 1)
            #     value = value.replace('Point', 'And') + " Paisa"
            if not value:
                return "Rupees Zero Only"
            return "Rupees " + value + " Only"
        else:
            # return self.currency_id.name + ' ' + num2words(amt,lang=self.partner_id.lang).title() + " Only"
            value = self.number_to_word(amt)
            # value = self.currency_id.amount_to_text(amt)
            if not value:
                return self.currency_id.name + ' ' + "Zero Only"
            return self.currency_id.name + ' ' + value + " Only"

    def number_to_word(self, number):
        amt = number

        def get_word(n):
            words = {0: "", 1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six", 7: "Seven", 8: "Eight",
                     9: "Nine", 10: "Ten", 11: "Eleven", 12: "Twelve", 13: "Thirteen", 14: "Fourteen", 15: "Fifteen",
                     16: "Sixteen", 17: "Seventeen", 18: "Eighteen", 19: "Nineteen", 20: "Twenty", 30: "Thirty",
                     40: "Forty", 50: "Fifty", 60: "Sixty", 70: "Seventy", 80: "Eighty", 90: "Ninty"}
            if n <= 20:
                return words[n]
            else:
                ones = n % 10
                tens = n - ones
                return words[tens] + " " + words[ones]

        def get_all_word(n):
            d = [100, 10, 100, 100]
            v = ["", "Hundred", "Thousand", "Lakh"]
            w = []
            for i, x in zip(d, v):
                t = get_word(n % i)
                if t != "":
                    t += " " + x
                w.append(t.rstrip(" "))
                n = n // i

            w.reverse()
            w = ' '.join(w).strip()
            if w.endswith("And"):
                w = w[:-3]

            return w

        arr = str(number).split(".")
        number = int(arr[0])
        crore = number // 10000000
        number = number % 10000000
        word = ""
        if crore > 0:
            word += get_all_word(crore)
            word += " Crore "
        word += get_all_word(number).strip()

        if len(arr) > 1:
            if len(arr[1]) == 1:
                arr[1] += "0"

            if int(amt) == amt:
                word += get_all_word(int(arr[1]))
            else:
                word += " And " + get_all_word(int(arr[1])) + " Paisa"
        return word

    @api.model
    def order_formatLang(self, value, currency_obj=False):
        res = value
        if currency_obj and value:
            res = formatLang(self.env, value, currency_obj=False)
        return res

    def order_total_formatLang(self, value, currency_obj=False):
        res = value
        if currency_obj and value:
            res = formatLang(self.env, round(value), currency_obj=False)
        return res

    @api.depends('amount_total')
    def _compute_amount_total_words(self):
        for invoice in self:
            amount_in_words = str(invoice.currency_id.amount_to_text(invoice.hsn_total_tax))
            end = amount_in_words.find('Rupees')
            invoice.amount_total_words = "Rupees" + amount_in_words[0:end]

    amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")

    @api.depends('hsn_total_tax')
    def _compute_amount_total_words1(self):
        for invoice in self:
            amount_in_words = str(invoice.currency_id.amount_to_text(invoice.hsn_total_tax))
            end = amount_in_words.find('Rupees')
            invoice.amount_total_words1 = "Rupees" + amount_in_words[0:end]

    amount_total_words1 = fields.Char("Total (In Words)", compute="_compute_amount_total_words1")
    hsn_total_tax = fields.Monetary(compute='_compute_hsn_total_tax', string='Total Tax Amount', store=True,
                                    default=0.0, copy=False, digits=(12, 3))
    cgst_val = fields.Monetary(compute='amount_cgst_tax_total_function', string='Total Cgst', store=True, default=0.0,
                               copy=False, digits=(12, 3))
    amount_rounding = fields.Monetary('Amount Delta')
    sgst_val = fields.Monetary(compute='amount_sgst_tax_total_function', string='Total Sgst', store=True, default=0.0,
                               copy=False, digits=(12, 3))
    igst_val = fields.Monetary(compute='amount_igst_tax_total_function', string='Total Igst', store=True, default=0.0,
                               copy=False, digits=(12, 3))
    total_val = fields.Monetary(compute='amount_total_function', string='Total Val', store=True, default=0.0,
                                copy=False, digits=(12, 3))
    total_tax_val = fields.Monetary(compute='amount_total_tax_amount_function', string='Total Tax Vat', store=True,
                                    default=0.0,
                                    copy=False)


class AccountInoiceLineInherited(models.Model):
    _inherit = "account.move.line"

    hsn_value = fields.Float('HSN Val', copy=False, digits=(12, 3))
    sgst_value = fields.Float('SGST VAL', copy=False, digits=(12, 3))
    cgst_value = fields.Float('CGST VAL', copy=False, digits=(12, 3))
    igst_value = fields.Float('IGST VAL', copy=False, digits=(12, 3))
    amount_rounding = fields.Monetary('Amount Delta')
    total_tax_value = fields.Monetary('Total Tax Amount', copy=False, digits=(12, 3))

    def get_name(self, name):
        for i in self:
            # if i.name != False and i.product_id.display_name in i.name.split(','):
            #     names = i.name.split(',')
            #     print(names,'nameeeeeeeeeeee')
            #     # return names[1:3]
            #     # raise UserError("wait")
            #     return names[1:7]
            if i.name:
                names = i.name.split(',')
                # raise UserError("dont wait")

                # return names[0:2]
                return names[0:6]
        # if self.product_id.default_code != False and self.product_id.name.split(',')[
        #     0] in self.product_id.default_code.split(','):
        #     names = self.product_id.default_code.split(',')
        #     # return names[1:3]
        #     return names[1:7]
        # elif self.product_id.default_code != False:
        #     names = self.product_id.default_code.split(',')
        #     # return names[0:2]
        #     return names[0:6]


class ResPartner(models.Model):
    _inherit = "res.partner.bank"

    branch_ifsc = fields.Char("Branch Code")
    ifsc_code = fields.Char("IFS Code")
    bank_cif = fields.Char("Swift Code")


class ResCompany(models.Model):
    _inherit = "res.company"

    mobile = fields.Char("Mobile")
    cin = fields.Char("CIN")
    service_tax_no = fields.Char("Service Tax No.")
    pan_no = fields.Char("PAN No.")
    remarks = fields.Char("Remarks")
    iso = fields.Char("ISO Certified")
    exporter_id = fields.Char(string="Exporter's IEC Number")
    ad_code = fields.Char(string="AD Code")
    declare = fields.Char(string="Declaration")


class DeliveryOrder(models.Model):
    _inherit = "stock.picking"

    despatched_through = fields.Char("Despatched Through")
    despatch_document_no = fields.Char("Despatch Document No")
    delivery_note = fields.Char("Delivery Note")
    delivery_note_date = fields.Date("Delivery Note Date")
    delivery_terms = fields.Char("Delivery Terms")
    no_of_packages = fields.Char("No.of Packages")
