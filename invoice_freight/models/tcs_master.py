from odoo import models, fields, api, _


class TcsMaster(models.Model):
    _name = 'tcs.tcs'

    name = fields.Char("Name")
