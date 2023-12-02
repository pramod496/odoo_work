from odoo import models,fields,api, _
from num2words import num2words
import pdb
import re

class Accountinvoice (models.Model):
    _inherit = "account.move"

    notify_id = fields.Many2one('res.partner','Notify Party')
    buyer_id  = fields.Many2one('res.partner','Consignee')
    total_package = fields.Char('Total No Of Package')
    # exporter_id= fields.Char(string="Exporter's IEC Number")
    # ad_code = fields.Char(string="AD Code")
    country_of_export = fields.Char(string="Country Of Export")
    country_of_origin_goods = fields.Char(string="Country Of Origin Of Goods")
    destination_port = fields.Char(string="Destination port")
    destination_airport = fields.Char(string="Destination Airport")
    sender_ac_no =fields.Char(string="Sender A/c No ")
    receiver_ac_no = fields.Char(string="Receiver A/c No")
    payment = fields.Char(string="Payment")
    report_type = fields.Many2one('invoice.type', string='Invoice Type')
    # declare = fields.Char("Declaration")
    other_ref = fields.Char("Other References")
    despatched_through1 = fields.Char("Despatched Through")
    despatch_document_no1 = fields.Char("Despatch Document No")
    delivery_note1 = fields.Char("Delivery Note")
    delivery_note_date1 = fields.Date("Delivery Note Date")
    delivery_terms1 = fields.Char("Delivery Terms")
    no_of_packages = fields.Char("No.of Packages")
    customer_contact = fields.Many2one('res.partner',string="Customer Contact")
    delivery_contact = fields.Many2one('res.partner',string="Delivery Contact")
    notify_contact = fields.Many2one('res.partner',string="Notify Party Contact")
    consignee_contact = fields.Many2one('res.partner',string="Consignee Contact")
    uom_custom = fields.Char('UOM united', compute='get_uom_unique')
    converted_inr = fields.Monetary(string='Value in INR')

    def convert_currency(self):
        self.converted_inr = False
        conversion_rate = self.env['res.currency.rate'].search(
            [('company_id', '=', self.company_id.id), ('currency_id', '=', self.currency_id.id)])
        if not conversion_rate:
            raise ValidationError(
                _('Please Assign the currency conversion rate in Accounting/Configuration/Currencies'))
        self.converted_inr = round((1 / conversion_rate.rate) * self.amount_total, 2)
        for i in self.hsn_line_ids:
            if not i.taxable_value == self.converted_inr:
                i.taxable_value = round((1/conversion_rate.rate)*i.taxable_value, 2)
        # print(amount_inr)
        # raise ValidationError('saa')
        return self.converted_inr

    def amount_to_text(self, rounded_total):
        if self.currency_id.name == "INR":
            return self.currency_id.currency_unit_label + ' ' + num2words(rounded_total,lang='en_IN').title() + " Only"
        else:
            # return self.currency_id.name + ' ' + num2words(rounded_total,lang='en').title() + " Only"
            if self.currency_id.name == "GBP":
                vals = self.currency_id.amount_to_text(rounded_total).replace("-", " ").replace("Penny", "Pence")
                if int(rounded_total) != rounded_total:
                    vals = vals.replace("And", "")
                if 'Sterling' in vals:
                    vals = vals.replace("Sterling", "")
                amt = rounded_total - int(rounded_total)
                return self.currency_id.name + ' ' + vals + " Only"

            vals = self.currency_id.amount_to_text(rounded_total)
            if 'Euros' in vals:
                vals = vals.replace("Euros", "")
            if 'Dollars' in vals:
                vals = vals.replace("Dollars", "")
            if int(rounded_total) != rounded_total:
                vals = vals.replace("And", "")
            vals = vals.replace(",", "").replace("-", " ")
            return self.currency_id.name + ' ' + vals + " Only"
            # return self.currency_id.currency_unit_label + ' ' + num2words(rounded_total,lang=self.partner_id.lang).title() + " Only"

    def get_uom_unique(self):
        uom = []
        for rec in self:
            rec.uom_custom = "N/A"

            for l in rec.invoice_line_ids:
                if l.product_uom_id:
                    uom.append(l.product_uom_id.name)
                    res = uom.count(uom[0]) == len(uom)
                    if res:
                        rec.uom_custom = uom[0]
                    else:
                        rec.uom_custom = False
                else:
                    rec.uom_custom = False

    def get_lut_arn_no(self):
        # if (self.invoice_date >= self.company_id.lut_no.start_date) and (self.invoice_date <= self.company_id.lut_no.end_date):
        #     return self.company_id.lut_no.name
        # else:
        if self.invoice_date:
            lut_rec = self.env['lut.master'].search([('start_date', '<=', self.invoice_date),('end_date', '>=', self.invoice_date)])
            return lut_rec.name
        else:
            return False

    def get_lut_arn_date(self):
        # if (self.invoice_date >= self.company_id.lut_no.start_date) and (self.invoice_date <= self.company_id.lut_no.end_date):
        #     return self.company_id.lut_date.strftime('%d/%m/%Y')
        # else:
        if self.invoice_date:
            lut_rec = self.env['lut.master'].search([('start_date', '<=', self.invoice_date),('end_date', '>=', self.invoice_date)])
            return lut_rec.start_date.strftime('%d/%m/%Y')
        else:
            return False

    def get_invoice_line_length(self):
        return len(self.invoice_line_ids)

    def get_invoice_line_ids(self):
        data_list = []
        for rec in self.invoice_line_ids:
            data = {
                'name': rec.product_id.name,
                'desc': rec.get_product_name(rec),
                'hsn_code': rec.product_id.l10n_in_hsn_code,
                'quantity': str(int(rec.quantity)) + ' ' + 'No.' if rec.product_uom_id and rec.quantity == 1 else str(int(rec.quantity)) + ' ' + rec.product_uom_id.name ,
                'price_unit': rec.price_unit,
                'price_subtotal': rec.price_subtotal,
                'currency': rec.currency_id.name,
            }
            data_list.append(data)
        return data_list


class AccountinvoiceLine (models.Model):
    _inherit = "account.move.line"

    is_transport_charges = fields.Boolean('Tick', default=False)

    @api.onchange('product_id')
    @api.constrains('is_transport_charges')
    def check_service_product(self):
        for i in self:
            if i.product_id.detailed_type in ['service', 'SERVICE'] and i.product_id.name in ['Freight Charges', 'Freight charges', 'freight charges', 'Testing Charges', 'Testing charges', 'TESTING CHARGES', 'packing charges', 'Packing Charges', 'Loading charges', 'Loading Charges', 'Tcs charges', 'Tcs Charges']:
                i.is_transport_charges = True

    def get_product_name(self, id):
        if self.product_id.default_code != False and self.product_id.name.split(',')[0] in self.product_id.default_code.split(
                ','):
            names = self.product_id.default_code.split(',')
            return names[1:3]
        elif self.product_id.default_code != False:
            names = self.product_id.default_code.split(',')
            return names[0:2]


class ResPartner (models.Model):
    _inherit = "res.partner"

    warranty = fields.Char(string="Warranty")
    trn = fields.Char(string="TRN Number")
    tin = fields.Char(String="TIN")


class ResCompanyCustom(models.Model):
    _inherit = "res.company"

    guarantee = fields.Char(string="Guarantee")


class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    po_date = fields.Date('PO Date')


class InvoiceType(models.Model):
    _name = "invoice.type"
    _description = "Invoice Type"
    _rec_name = 'invoice_type'

    invoice_type = fields.Char("Invoice Type")


class AccountEdiFormat(models.Model):
    _inherit = "account.edi.format"

    def _l10n_in_validate_partner(self, partner, is_company=False):
        self.ensure_one()
        message = []
        if not re.match("^.{3,100}$", partner.street or ""):
            message.append(_("\n- Street required min 3 and max 100 characters"))
        if partner.street2 and not re.match("^.{3,100}$", partner.street2):
            message.append(_("\n- Street2 should be min 3 and max 100 characters"))
        if partner.phone and not re.match("^[0-9]{10,12}$",
            self._l10n_in_edi_extract_digits(partner.phone)
        ):
            message.append(_("\n- Mobile number should be minimum 10 or maximum 12 digits"))
        if partner.email and (
            not re.match(r"^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$", partner.email)
            or not re.match("^.{6,100}$", partner.email)
        ):
            message.append(_("\n- Email address should be valid and not more then 100 characters"))
        return message
