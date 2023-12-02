from odoo import models, fields

class AccountRoundOff(models.Model):
    _inherit = 'account.move'

    ref_date = fields.Date(string='Reference Date')