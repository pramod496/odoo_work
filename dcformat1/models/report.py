from odoo import models, fields, api
import pdb

# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ReportMyReport(models.AbstractModel):
    _name = 'report.dcformat1.report_accountinvoice'

    
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        sale_ids =self.env['sale.order'].search([('name','=',docs.origin)])
        #print(lot_id.name)
        
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock_picking',
            'docs': docs,
           
            'sale_ids':sale_ids
        }
