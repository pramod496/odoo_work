from odoo import models, fields, api
import pdb


class StockPickingInherited(models.Model):
    _inherit = "stock.picking"

    @api.model
    def serial_number_function(self, product_id):
        value_num = 0
        qc_lot = self.env['quality.check']
        qc_serial_num = qc_lot.search(
            [('product_id', '=', product_id.id), ('picking_id', '=', self.id), ('quality_state', '!=', 'none')],
            order='id asc', limit=1)
        if qc_serial_num:
            qc = qc_serial_num.lot_id.name
            return qc

    @api.model
    def inspection_activities_function(self, product_id):
        value_num = 0
        qc_lot = self.env['quality.check']
        qc_serial_num = qc_lot.search(
            [('product_id', '=', product_id.id), ('picking_id', '=', self.id), ('quality_state', '!=', 'none')],
            order='id asc', limit=1)
        if qc_serial_num:
            qc_val = qc_serial_num.point_id.title
            return qc_val

    @api.model
    def observation_function(self, product_id):
        value_num = 0
        qc_lot = self.env['quality.check']
        qc_serial_num = qc_lot.search(
            [('product_id', '=', product_id.id), ('picking_id', '=', self.id), ('quality_state', '!=', 'none')],
            order='id asc', limit=1)
        if qc_serial_num:
            qc_state = qc_serial_num.quality_state
            return qc_state

    @api.model
    def inspection_quantity_function(self, product_id):
        value_num = 0
        qc_lot = self.env['quality.check']
        qc_serial_num = qc_lot.search(
            [('product_id', '=', product_id.id), ('picking_id', '=', self.id)],
            order='id asc', limit=1)
        if qc_serial_num:
            qc_inspected_qty = qc_serial_num.inspected_qty
            return qc_inspected_qty

    @api.model
    def quantity_function(self,name):
        qc_lot=self.env['quality.check']
        qc_quantity = qc_lot.search([('picking_id','=',self.id)])
        qty = 0
        for el in qc_quantity:
            if el.inspected_qty:
                qty=qty+int(el.inspected_qty)
        return qty




    conclusion=fields.Text('Conclusion')


class ResCompanyInherited(models.Model):
    _inherit = "res.company"

    report_format = fields.Char('Report Format')

    doc_num_grn = fields.Char('Doc Number For Goods Reciept')



# class ReportMyReport(models.AbstractModel):
#     _name = 'report.inspection_report.inspection_report_template'
#
#
#     
#     def _get_report_values(self, docids, data=None):
#
#         docs = self.env['stock.picking'].browse(docids)
#         quality_id = self.env['quality.check'].search([('picking_id', '=', docs.id)])
#         print(quality_id.name)
#         return {
#             'doc_ids': docs.ids,
#             'doc_model': 'stock_picking',
#             'docs': docs,
#             'quality_id': quality_id
#         }
