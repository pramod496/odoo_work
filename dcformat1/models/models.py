from odoo import models,fields,api
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
class Stockpicking (models.Model):
    _inherit="stock.picking"

    inv_no = fields.Char(string='Invoice Number') 
    remarks=fields.Char(string="Remarks")
    approx_value=fields.Char(string="Approx value")
    service=fields.Char(string="Service description")
    sale_type=fields.Char(string="Type of sale")
    spo_ref=fields.Char(string="SPO Reference")

class Respartner (models.Model):
    _inherit="res.partner"

    GSM =fields.Char(string="GSM")
