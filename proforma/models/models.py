from odoo import models, fields, api
import num2words


# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class Accountinvoice(models.Model):
    _inherit = "account.move"

    # drawing_number = fields.Float('Drawing Number')

    @api.depends('rounded_total')
    def _compute_amount_total_words(self):
        for invoice in self:
            invoice.amount_total_words = invoice.currency_id.amount_to_text(invoice.rounded_total)

        amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")

    def qty_check(self,qty):
        if qty:
            if int(qty) == qty:
                return int(qty)
            return qty
        return qty

    # def calculate_freight_taxes(self,tax_ids):
    #     tax_amount = 0
    #     for ids in tax_ids:
    #         tax_amount += self.freight_value * (ids.amount / 100)
    #     return tax_amount
    #
    # def calculate_packing_taxes(self,tax_ids):
    #     tax_amount = 0
    #     for ids in tax_ids:
    #         tax_amount += self.packing_value * (ids.amount / 100)
    #     return tax_amount

    def amount_tax_cal(self):
        amount = self.amount_untaxed + self.packing_value + self.freight_value
        tax_id_amt = []
        tax_value = 0
        for rec in self.invoice_line_ids:
            for r in rec.tax_ids:
                tax_id_amt.append(r.amount)
            break
        for amt in tax_id_amt:
            tax_value += amount * (amt / 100)
        # print("@@@@@@@@@@",tax_id_amt,tax_value,amount,self.amount_untaxed + tax_value)
        return amount + tax_value

    def tax_cal(self):
        amount = self.amount_untaxed + self.packing_value + self.freight_value
        tax_id_amt = []
        tax_value = 0
        for rec in self.invoice_line_ids:
            for r in rec.tax_ids:
                tax_id_amt.append(r.amount)
            break
        for amt in tax_id_amt:
            tax_value += amount * (amt / 100)
        # print("@@@@@@@@@@",tax_id_amt,tax_value,amount,self.amount_untaxed + tax_value)
        return tax_value