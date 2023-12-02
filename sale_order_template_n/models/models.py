from odoo import models,fields,api
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
#from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ResCompanyInherited(models.Model):
    _inherit = 'res.company'

    iso_clause=fields.Integer('ISO Clause')
    iso_date = fields.Date('Date')
    format_no = fields.Char('Format No')


class ResPartnerInherited(models.Model):
    _inherit = 'res.partner'

    fax=fields.Char('Fax')

class SaleOrderInherited(models.Model):
    _inherit = 'sale.order'

    price_basis=fields.Char('Price Basis')
    packing =fields.Char('Packing & Forwading')
    delivery = fields.Date('Delivery Date')
    freight =fields.Char('Freight')
    insurance = fields.Char('Insurance')
    client_order_ref = fields.Char(string='Customer Reference', copy=False)
    po_date = fields.Date(string='PO Date',copy=False)
