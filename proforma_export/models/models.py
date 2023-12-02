from odoo import models, fields, api
import num2words


# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class Accountinvoice(models.Model):
    _inherit = "account.move"
    

    @api.depends('rounded_total')
    def _compute_amount_total_words(self):
        for invoice in self:
            invoice.amount_total_words = invoice.currency_id.amount_to_text(invoice.rounded_total)

        amount_total_words = fields.Char("Total (In Words)", compute="_compute_amount_total_words")

    def qty_check_exp(self,qty):
        if qty:
            if int(qty) == qty:
                return int(qty)
            return qty
        return qty


    
