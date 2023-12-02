from odoo import api, fields, models, _


class ReportMyReport(models.AbstractModel):
    _name = 'report.dc_cum_packing_list.report_dc_cum_packing_list'

    
    def _get_report_values(self, docids, data=None):
        docs = self.env['stock.picking'].browse(docids)
        sale_id = self.env['sale.order'].search([('name','=',docs.origin)])
        invoice_ids = self.env['account.move'].search([('origin','=',sale_id.name)])
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock_picking',
            'docs': docs,
            'invoice_ids':invoice_ids,
            'sale_id': sale_id
        }

class Respartners (models.Model):
    _inherit="res.partner"

    fax = fields.Char(string="Fax")

class StockPickingCustom(models.Model):
    _inherit = "stock.picking"

    uom_custom = fields.Char(string="Uom united", compute='get_uom_united')
    scheduled_date = fields.Datetime(string="Scheduled Date")

    kind_attn_buyer = fields.Many2one('res.partner', string="Kind Attention (Buyer)")
    kind_attn_del = fields.Many2one('res.partner', string="Kind Attention (delivery)")
    # @api.model
    def get_uom_united(self):
        # self.uom_custom = "N/A"
        uom = []
        for rec in self:
            rec.uom_custom = "N/A"
            for l in rec.move_ids_without_package:
                if l.product_uom:
                    uom.append(l.product_uom.name)
                    res = uom.count(uom[0]) == len(uom)
                    if res:
                        print(res)
                        rec.uom_custom = uom[0]
                    else:
                        rec.uom_custom = False
                else:
                    print('final else')
                    rec.uom_custom = False
        print(uom,'uom')

    def qty_check(self,qty):
        if qty:
            if int(qty) == qty:
                return int(qty)
            return "%.3f" % round(qty,3)
        return "%.3f" % round(qty,3)