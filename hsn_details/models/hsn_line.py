from odoo import api, fields, models, _


class HsnLine(models.Model):
    _name = "hsn.line"

    invoice_id = fields.Many2one("account.move", string="Invoice Id")
    hsn_code = fields.Char("Hsn/Sac Code")
    taxable_value = fields.Float("Taxable Value")
    total_tax_amount = fields.Float("Total Tax Amount")
    # total_tax_amount_rounded = fields.Float("Total Tax Amount (Rounded)")
    # extra_charges = fields.Float("Fr/P&F/Test/Load")
    cgst_rate = fields.Float("CGST Rate")
    sgst_rate = fields.Float("SGST Rate")
    igst_rate = fields.Float("IGST Rate")
    cgst_amt = fields.Float("CGST Amount")
    sgst_amt = fields.Float("SGST Amount")
    igst_amt = fields.Float("IGST Amount")
