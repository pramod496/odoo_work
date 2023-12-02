from odoo import fields, models,api,_


class SerialInfo(models.Model):
    _name = "serial.info"

    name = fields.Char('Product')
    starting_lot = fields.Char(string="Starting Serial No.")
    ending_lot = fields.Char(string="	Ending Serial No.")
    work_order_id = fields.Many2one('work.order.quotation', ondelete='cascade')


class WorkOrder(models.Model):
    _inherit = "work.order.quotation"

    serial_no_info = fields.One2many('serial.info', 'work_order_id', compute="_index_get_lot")

    def _index_get_lot(self):
        sale_id = self.sale_id.id
        serial_no = []
        for line in self.work_order_line:
            lots = self.env['stock.production.lot'].sudo().search([
                ('so_id', '=', sale_id),
                ('product_id', '=', line.product_id.id)
            ])
            if lots:
                serial_no.append({
                    'name': line.product_id.name,
                    'starting_lot': lots[0].name,
                    'ending_lot': lots[-1].name
                })
        self.serial_no_info.unlink()
        self.serial_no_info += self.env['serial.info'].create(serial_no)

