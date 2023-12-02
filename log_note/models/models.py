# -*- coding: utf-8 -*-

from odoo import models, fields, api
# class log_note(models.Model):
#     _name = 'log_note.log_note'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         self.value2 = float(self.value) / 100


class SaleOrder(models.Model):
    _inherit = 'sale.order'


    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        res = super(SaleOrder, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if res.attachment_ids:
            if self.iwo_id:
                self.iwo_id.message_post(**kwargs)
        return res

class WorkOrderQuotation(models.Model):
    _inherit = 'work.order.quotation'

    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        return super(WorkOrderQuotation, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)


class QualityCheck(models.Model):
    _inherit = 'quality.check'
    
    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, **kwargs):
        res = super(QualityCheck, self.with_context(mail_post_autofollow=True)).message_post(**kwargs)
        if self.picking_id:
            self.picking_id.message_post(**kwargs)
        return res