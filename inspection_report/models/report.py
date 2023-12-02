from odoo import models, fields, api


class ReportMyReport(models.AbstractModel):
    _name = 'report.inspection_report.inspection_report_template'


    
    def _get_report_values(self, docids, data=None):

        docs = self.env['stock.picking'].browse(docids)
        quality_id = self.env['quality.check'].search([('picking_id','=',docs.id)])
        # print(quality_id.note)
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock_picking',
            'docs': docs,
            'quality_id': quality_id
        }

