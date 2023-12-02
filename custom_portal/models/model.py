# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class SaleInherited(models.Model):
    _inherit = 'sale.order'

    msg_count = fields.Integer('Message', compute='_get_needaction',
        help='Need Action')    

    
    def _get_needaction(self):
        """ Need action on a mail.message = notified on my channel """
        subtype = self.env.ref('mail.mt_note').id        
        for res in self:                          
            msg = self.env['mail.message'].search_count([('is_read','=',False),
                ('res_id', '=', res.id),('message_type', '=', 'comment'),('subtype_id','=',subtype),('subject','!=',False)])
            res.msg_count = msg

class Message(models.Model):
    _inherit = 'mail.message'
    
    is_read = fields.Boolean('Read')
    
    
    def read(self, fields=None, load='_classic_read'):
        if fields:
            fields.append('is_read')

        return super(Message, self).read(fields=fields, load=load)    