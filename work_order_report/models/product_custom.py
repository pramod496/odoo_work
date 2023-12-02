from odoo import models, fields


class Product(models.Model):
    _inherit = "product.product"

    int_ref_temp = fields.Char(string="Int Ref", compute='compute_internal_ref')

    def compute_internal_ref(self):
        for rec in self:
            default_code = rec.default_code
            final_val = default_code.replace('–', '-')
            rec.int_ref_temp = final_val
