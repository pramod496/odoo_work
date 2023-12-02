from odoo import api, fields, models, _
from odoo.tools.misc import formatLang
from odoo.exceptions import UserError
import math
from datetime import datetime, date
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class AccountInvoice(models.Model):
    _inherit = "account.move"

    irn_no = fields.Char(string="IRN")
    ack_no = fields.Char(string="ACK No")
    ack_date = fields.Date(string="ACK Date")
    qr_image = fields.Binary(string="Qr Image")
