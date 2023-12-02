from odoo import api, fields, models, _
import pdb
from odoo.addons import decimal_precision as dp
from num2words import num2words
import math
from odoo.tools.misc import formatLang


class AccountInvoice(models.Model):
    _inherit = "account.move"


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
            if rec.amount_tax>0.0:
                for line in rec.invoice_line_ids:
                    qty = qty + float(line.total_tax_value)
                rec.update({
                    'total_tax_val': round(qty,2)

                })
            else:
                rec.update({'total_tax_val':0.0})


    
    def get_hsn_code(self, hsn):
        list1 = []
        for invoice_line in self.invoice_line_ids:
            list1.append(invoice_line.product_id.l10n_in_hsn_code)
        hsn_group = list(set(list1))
        return hsn_group

    @api.depends('invoice_line_ids.total_tax_value')
    def _compute_hsn_total_tax(self):
       """
       Compute the amounts of the Bom line.
       """
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
            if int(amt) != amt:
                value = value.replace('And', '')
            #     value = value.replace('Point', 'And') + " Paisa"
            if not value:
                return "Rupees Zero Only"
            return "Rupees " + value + " Only"
        else:
            # return self.currency_id.name + ' ' + num2words(amt,lang=self.partner_id.lang).title() + " Only"
            value = self.currency_id.amount_to_text(amt)
            if not value:
                return self.currency_id.name + ' ' + "Zero Only"
            return self.currency_id.name + ' ' + value + " Only"

    def number_to_word(self,number):
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
            v = ["", "Hundred And", "Thousand", "lakh"]
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
            word += " crore "
        word += get_all_word(number).strip()
        if len(arr) > 1:
            if len(arr[1]) == 1:
                arr[1] += "0"

            if int(amt) == amt:
                word += get_all_word(int(arr[1]))
            else:
                word += " and " + get_all_word(int(arr[1])) + " Paisa"
        return word

    @api.model
    def order_formatLang(self, value, currency_obj=False):
        res = value
        # print("####################", formatLang(self.env, value , currency_obj=currency_obj))
        if currency_obj and value:
            res = formatLang(self.env, value, currency_obj=False)
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

    hsn_total_tax = fields.Monetary(compute='_compute_hsn_total_tax', string='Total Tax Amount', store=True, default=0.0,copy=False,digits = (12,3) )
    cgst_val=fields.Monetary(compute='amount_cgst_tax_total_function',string='Total Cgst',store=True,default=0.0,copy=False,digits = (12,3))
    amount_rounding = fields.Monetary('Amount Delta')
    sgst_val = fields.Monetary(compute='amount_sgst_tax_total_function', string='Total Sgst', store=True, default=0.0,
                            copy=False, digits=(12, 3))
    igst_val = fields.Monetary(compute='amount_igst_tax_total_function', string='Total Igst', store=True, default=0.0,
                            copy=False, digits=(12, 3))
    total_val = fields.Monetary(compute='amount_total_function', string='Total Val', store=True, default=0.0,
                            copy=False, digits=(12, 3))
    total_tax_val = fields.Monetary(compute='amount_total_tax_amount_function', string='Total Tax Vat', store=True, default=0.0,
                            copy=False)


class AccountInoiceLineInherited(models.Model):

    _inherit = "account.move.line"

    hsn_value =fields.Float('HSN Val',copy=False,digits = (12,3) )
    sgst_value =fields.Float('SGST VAL',copy=False,digits = (12,3) )
    cgst_value =fields.Float('CGST VAL',copy=False,digits = (12,3) )
    igst_value = fields.Float('IGST VAL',copy=False,digits = (12,3) )
    amount_rounding = fields.Monetary('Amount Delta')
    total_tax_value = fields.Monetary('Total Tax Amount',copy=False,digits = (12,3) )

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
    exporter_id= fields.Char(string="Exporter's IEC Number")
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


