from odoo import api, fields, models, _


class LutNumber(models.Model):
    _name = "lut.master"
    _description = "LUT Number"


    name = fields.Char(string="LUT ARN No.")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")