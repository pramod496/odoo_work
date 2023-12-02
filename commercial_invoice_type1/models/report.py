from odoo import models, fields, api
import pdb
import datetime
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ReportMyReport(models.AbstractModel):
    _name = 'report.commercial_invoice_type1.report_accountinvoice'


    
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        a=[]
        b=[]
        origin=docs.origin
        po_ref = ""
        po_date = ""
        if origin:
            orig=origin.split(', ')
            for ori in orig: 
                sale = self.env['sale.order'].search([('name','=', ori)])
                for rec in sale:
                    a.append(rec.client_order_ref)
                    b.append(rec.po_date.strftime("%d-%m-%Y"))
            po_ref =' / '.join(map(str, a))
            po_date =' / '.join(map(str, b))
        sale_ids =self.env['sale.order'].search([('name','=',docs.name)])
        stock_ids =self.env['stock.picking'].search([('origin','=',sale_ids.name)])
        
        return {
            'doc_ids': docs.ids,
            'doc_model': 'account_invoice',
            'docs': docs,
            'po_ref': po_ref,
            'po_date': po_date,
            'sale_ids':sale_ids,
            'stock_ids':stock_ids
           
            
        }
