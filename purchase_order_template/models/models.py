from odoo import models, fields, api
import odoo.addons.decimal_precision as dp
from num2words import num2words
import pdb
import math


class CustInvoice(models.Model):
    _inherit = "purchase.order"

    # @api.depends('amount_total')
    # def _compute_amount_total_words(self):
    #     for po in self:
    #         po.amount_total_words = po.currency_id.amount_to_text(po.amount_total)

    # amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")

    def amount_to_text(self, amount_total):
        # if self.currency_id.name=="INR":
        #     if amount_total.is_integer():
        #         amt = num2words(amount_total,lang='en_IN').title() + ' ' + self.currency_id.currency_unit_label
        #         amt1 = amt.replace("Point Zero Rupees", "Rupees")
        #         return amt1
        #     else:
        #         amt1 = num2words(math.floor(amount_total),lang='en_IN')
        #         amt2 = (amount_total - int(amount_total)) * 100
        #         amt3 = num2words(round(amt2),lang='en_IN')
        #         amt4 = amt1 + ' Rupees' + ' and ' + amt3 + ' Paisa'
        #         amt5 = amt4.title()
        #         return amt5
        # else:
        #     return num2words(amount_total,lang=self.partner_id.lang).title() + ' ' + self.currency_id.currency_unit_label
        if self.currency_id.name == "INR":
            if amount_total.is_integer():
                amt = self.currency_id.currency_unit_label + ' ' + num2words(amount_total, lang='en_IN').title()
                amt1 = amt.replace("Point Zero Rupees", "Rupees")
                print("###########3", amt1)
                return amt1
            else:
                amt1 = num2words(math.floor(amount_total), lang='en_IN')
                amt2 = (amount_total - int(amount_total)) * 100
                amt3 = num2words(round(amt2), lang='en_IN')
                amt4 = 'Rupees' + amt1 + ' and ' + amt3 + ' Paisa Only'
                amt5 = amt4.title()
                return amt5
        else:
            return self.currency_id.currency_unit_label + ' ' + num2words(amount_total,
                                                                          lang=self.partner_id.lang).title() + " Only"


class ResCompany(models.Model):
    _inherit = "res.company"

    fax = fields.Char("Fax")


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    order_no = fields.Char("Vendor Order No")

    freight_charges = fields.Char('Freight')

    packing_charges = fields.Char('Packing')

    inspection = fields.Many2one('res.users', 'Inspection')

    test_certificate = fields.Char("Test Certificate")

    despatch_mode = fields.Char("Despatch Mode")

    warranty = fields.Char("Warranty")

    insurance = fields.Char("Insurance")

    last_delivery_clause = fields.Char("Last Delivery Clause")

    note = fields.Char("Note")

    kind_attn = fields.Many2one('res.partner', string="Kind Attention")

    amount_gst = fields.Float(string='GST Total', digits=dp.get_precision('Account'),
                              store=True, readonly=True, compute='_compute_total_gst', track_visibility='always')
    amount_cgst = fields.Float(string='CGST Total', digits=dp.get_precision('Account'),
                               store=True, readonly=True, compute='_compute_total_gst', track_visibility='always')
    amount_sgst = fields.Float(string='SGST Total', digits=dp.get_precision('Account'),
                               store=True, readonly=True, compute='_compute_total_gst', track_visibility='always')
    amount_igst = fields.Float(string='IGST Total', digits=dp.get_precision('Account'),
                               store=True, readonly=True, compute='_compute_total_gst', track_visibility='always')

    cgst_rate = fields.Float(string='cGST rate', digits=dp.get_precision('Account'),
                             store=True, readonly=True, compute='_compute_total_gst')
    sgst_rate = fields.Float(string='sGST rate', digits=dp.get_precision('Account'),
                             store=True, readonly=True, compute='_compute_total_gst')
    igst_rate = fields.Float(string='iGST rate', digits=dp.get_precision('Account'),
                             store=True, readonly=True, compute='_compute_total_gst')

    @api.depends('order_line.cgst', 'order_line.sgst', 'order_line.igst')
    def _compute_total_gst(self):
        if self.order_line:
            for line in self.order_line:
                self.amount_gst = self.amount_gst + line.cgst + line.sgst + line.igst
                self.amount_cgst = self.amount_cgst + line.cgst
                self.amount_sgst = self.amount_sgst + line.sgst
                self.amount_igst = self.amount_igst + line.igst
                if line.cgst_rate > 0:
                    self.cgst_rate = line.cgst_rate
                if line.sgst_rate > 0:
                    self.sgst_rate = line.sgst_rate
                if line.igst_rate > 0:
                    self.igst_rate = line.igst_rate


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    @api.depends('price_unit', 'taxes_id', 'product_qty', 'product_id')
    def _compute_gst(self):
        if self.taxes_id:
            for tax in self.taxes_id:
                name_str = tax.name
                cgst_rate = 0
                # pdb.set_trace()
                if 'GST' in name_str and tax.amount_type == 'group':
                    if tax.children_tax_ids:
                        for child in tax.children_tax_ids:
                            child_name = child.name
                            if 'CGST' in child_name:
                                self.cgst = ((self.price_unit * self.product_qty) * child.amount) / 100
                                if child.amount.is_integer():
                                    self.cgst_rate = round(child.amount)
                                else:
                                    self.cgst_rate = child.amount
                            elif 'SGST' in child_name:
                                self.sgst = ((self.price_unit * self.product_qty) * child.amount) / 100
                                if child.amount.is_integer():
                                    self.sgst_rate = round(child.amount)
                                else:
                                    self.sgst_rate = child.amount

                elif 'CGST' in name_str:
                    for child in tax.children_tax_ids:
                        child.cgst = ((self.price_unit * self.product_qty) * tax.amount) / 100
                    if tax.amount.is_integer():
                        self.cgst_rate = round(tax.amount)
                    else:
                        self.cgst_rate = tax.amount
                elif 'SGST' in name_str:
                    for child in tax.children_tax_ids:
                        child.sgst = ((self.price_unit * self.product_qty) * tax.amount) / 100
                    if tax.amount.is_integer():
                        self.sgst_rate = round(tax.amount)
                    else:
                        self.sgst_rate = tax.amount
                elif 'IGST' in name_str:
                    for child in tax.children_tax_ids:
                        # child_name = child.name
                        child.igst = ((self.price_unit * self.product_qty) * tax.amount) / 100
                    if tax.amount.is_integer():
                        self.igst_rate = round(tax.amount)
                    else:
                        self.sgst_rate = (tax.amount)

    cgst_rate = fields.Float(string='cGST rate', digits=dp.get_precision('Account'),
                             store=True, readonly=True, compute='_compute_gst')
    sgst_rate = fields.Float(string='sGST rate', digits=dp.get_precision('Account'),
                             store=True, readonly=True, compute='_compute_gst')
    igst_rate = fields.Float(string='iGST rate', digits=dp.get_precision('Account'),
                             store=True, readonly=True, compute='_compute_gst')

    cgst = fields.Float(string='CGST', digits=dp.get_precision('Account'),
                        store=True, readonly=True, compute='_compute_gst')
    sgst = fields.Float(string='SGST', digits=dp.get_precision('Account'),
                        store=True, readonly=True, compute='_compute_gst')
    igst = fields.Float(string='IGST', digits=dp.get_precision('Account'),
                        store=True, readonly=True, compute='_compute_gst')
