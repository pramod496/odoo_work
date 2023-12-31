# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import models


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _prepare_invoice_line_from_po_line(self, line):
        vals = super()._prepare_invoice_line_from_po_line(line)
        vals['discount'] = line.discount
        return vals
