# -*- encoding: UTF-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today Laxicon Solution.
#    (<http://laxicon.in>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import pdb


class account_invoice(models.Model):
    _inherit = "account.move"

   # name = fields.Char(related=move_id.name,readonly=True, copy=False)
    type = fields.Char('ss')

    @api.model
    def create(self, vals):
        # commented on oct 13 to print invoice number with invoice type
        if vals.get('move_type') == 'entry' or vals.get('move_type') == 'out_receipt' or vals.get(
                'move_type') == 'in_receipt':
            # if vals.get('report_type') == 1 or vals.get('report_type') == 6 or vals.get('report_type') == 7:

            name = self.env['ir.sequence'].next_by_code('inter.state.invoice.number') or '/'

            vals['name'] = name

        if vals.get('type') == 'out_invoice' and self.env.context.get('bool_sale_proforma') == False:
            # if vals.get('report_type') == 2:
            # The below code is for the Normal Invoice when u create from invoices tab manually
            name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
            # self.name = name
            vals['name'] = name

        if vals.get('type') == 'in_invoice':
            # if vals.get('report_type') == 4 or vals.get('type') == 'in_invoice':
            name = self.env['ir.sequence'].next_by_code('bill.sequence.shridhan') or '/'
            vals['name'] = name


        elif vals.get('move_type') == 'out_refund':
            # elif vals.get('report_type') == 3:

            # raise UserError("refund")
            name = self.env['ir.sequence'].next_by_code('creditnote.sequence.shridhan') or '/'

            vals['name'] = name



        elif vals.get('move_type') == 'in_refund':
            # elif vals.get('report_type') == 5:

            name = self.env['ir.sequence'].next_by_code('refund.sequence.shridhan') or '/'

            vals['name'] = name

        elif self.env.context.get('default_bool_sale_proforma') == True:
            # raise UserError("wsas")
            # elif vals.get('report_type') == 2 and self.env.context.get('default_bool_sale_proforma') == True or vals.get('proforma_type') in ['local','export'] and self.env.context.get('default_bool_sale_proforma') == True:
            if vals.get('partner_id'):
                partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
                if partner.country_id.name == "India":
                    seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
                    vals['seq_pro_forma'] = 'PI' + str(seq)
                    vals['bool_sale_proforma'] = True
                    name = 'PI' + str(seq)


                elif not partner.country_id:
                    raise UserError("Please specify country in customer.")
                elif partner.country_id.name != "India":
                    seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
                    vals['seq_pro_forma'] = 'PE' + str(seq)
                    vals['bool_sale_proforma'] = True
                    name = 'PE' + str(seq)

                if vals.get('sale_id'):
                    sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
                    sale_order_id.proforma_count = 1
        elif vals.get('report_type') == 2 and self.env.context.get(
                'ordertype') == 'order' and self.env.context.get('default_bool_sale_proforma') == True:
            # This code is from sale order profoma invoie created
            name = self.env.context.get('default_seq_pro_forma')
            if vals.get('sale_id'):
                sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
                sale_order_id.proforma_count = 1
        # if self.env.context.get('default_seq_pro_forma') == self.env.context.get('default_name'):
        # elif self.env.context.get('default_seq_pro_forma') == self.env.context.get('default_name'):
        #     # This code is from quotation proforma invoice is created
        #     name = self.env.context.get('default_seq_pro_forma')
        #     print('hu123')
        #     if vals.get('sale_id'):
        #         sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
        #         sale_order_id.proforma_count = 1

        # raise UserError("ds")
        return super(account_invoice, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     # print(self.name,'came',vals.get('report_type'), vals['bool_sale_proforma'], vals.get('move_type'), vals.get('type'))
    #     # vb = vals.get('type')
    #     # print('hi soyeb')
    #     if vals.get('report_type') == 1 or vals.get('report_type') == 6 or vals.get('report_type') == 7:
    #         # print('first invoice')
    #         name = self.env['ir.sequence'].next_by_code('inter.state.invoice.number') or '/'
    #         # self.name = name
    #         vals['name'] = name
    #         # print(vals['name'])
    #     if vals.get('report_type') == 2:
    #     # The below code is for the Normal Invoice when u create from invoices tab manually
    #         name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
    #         # self.name = name
    #         vals['name'] = name
    #         # print('hello')
    #     # elif vals['bool_sale_proforma'] == True and vals.get('report_type') == 2:
    #     #     # This code is for the Performa invoice when u create manually
    #     #     print('name4')
    #     #
    #     #     if vals.get('partner_id'):
    #     #         partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
    #     #         if partner.country_id.name == "India":
    #     #             seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or ''
    #     #             # print(vals['seq_pro_forma'], 'hiiiiiiiiiii')
    #     #             vals['seq_pro_forma'] = 'PI' + str(seq)
    #     #             vals['bool_sale_proforma'] = True
    #     #             name = 'PI' + str(seq)
    #     #             print(name, 'name1pi')
    #     #
    #     #         elif not partner.country_id:
    #     #             raise UserError("Please specify county in customer.")
    #     #         elif partner.country_id.name != "India":
    #     #             seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #     #             vals['seq_pro_forma'] = 'PE' + str(seq)
    #     #             vals['bool_sale_proforma'] = True
    #     #             name = 'PE' + str(seq)
    #     #             print(name, 'namePE')
    #     if vals.get('report_type') == 4 or vals.get('type') == 'in_invoice':
    #         name = self.env['ir.sequence'].next_by_code('bill.sequence.shridhan') or '/'
    #         vals['name'] = name
    #
    #         # print(name,'name1')
    #     elif vals.get('report_type') == 3:
    #         name = self.env['ir.sequence'].next_by_code('creditnote.sequence.shridhan') or '/'
    #         print(name,'name2')
    #         # vals['seq_pro_forma'] = name
    #         vals['name'] = name
    #
    #         # print(vals['seq_pro_forma'],'hty')
    #
    #
    #     elif vals.get('report_type') == 5:
    #         name = self.env['ir.sequence'].next_by_code('refund.sequence.shridhan') or '/'
    #         # print(name,'name3')
    #         vals['name'] = name
    #
    #
    #
    #     # elif self.env.context.get('bool_sale_proforma') == True and vals.get('report_type') == 2:
    #     #     # This code is for the Performa invoice when u create manually
    #     #     print(name,'name4')
    #     #
    #     #     if vals.get('partner_id'):
    #     #         partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
    #     #         if partner.country_id.name == "India":
    #     #             seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or 'hiii'
    #     #             print(vals['seq_pro_forma'], 'hiiiiiiiiiii')
    #     #             vals['seq_pro_forma'] = 'PI' + str(seq)
    #     #             vals['bool_sale_proforma'] = True
    #     #             name = 'PI' + str(seq)
    #     #             print(name, 'name1pi')
    #     #
    #     #         elif not partner.country_id:
    #     #             raise UserError("Please specify county in customer.")
    #     #         elif partner.country_id.name != "India":
    #     #             seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #     #             vals['seq_pro_forma'] = 'PE' + str(seq)
    #     #             vals['bool_sale_proforma'] = True
    #     #             name = 'PE' + str(seq)
    #     #             print(name, 'namePE')
    #     elif self.env.context.get('default_bool_sale_proforma') == True and self.seq_pro_forma==False:
    #     # elif vals.get('report_type') == 2 and self.env.context.get('default_bool_sale_proforma') == True or vals.get('proforma_type') in ['local','export'] and self.env.context.get('default_bool_sale_proforma') == True:
    #         if vals.get('partner_id'):
    #             partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
    #             if partner.country_id.name == "India":
    #                 seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #                 vals['seq_pro_forma'] = 'PI' + str(seq)
    #                 vals['bool_sale_proforma'] = True
    #                 name = 'PI' + str(seq)
    #                 # self.name = name
    #
    #                 # print(name, 'namepI')
    #
    #             elif not partner.country_id:
    #                 raise UserError("Please specify country in customer.")
    #             elif partner.country_id.name != "India":
    #                 seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #                 vals['seq_pro_forma'] = 'PE' + str(seq)
    #                 vals['bool_sale_proforma'] = True
    #                 name = 'PE' + str(seq)
    #                 # self.name = name
    #
    #                 print(name, 'namePE2')
    #
    #             if vals.get('sale_id'):
    #                 sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
    #                 sale_order_id.proforma_count = 1
    #     elif vals.get('report_type') == 2 and self.env.context.get(
    #             'ordertype') == 'order' and self.env.context.get('default_bool_sale_proforma') == True:
    #         # This code is from sale order profoma invoie created
    #         name = self.env.context.get('default_seq_pro_forma')
    #         if vals.get('sale_id'):
    #             sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
    #             sale_order_id.proforma_count = 1
    #
    #     #                elif vals.get('type') == 'out_invoice' and self.env.context.get('ordertype') == 'order':
    #     # This code is from sale order invoice is got created
    #     #                    name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
    #     elif self.env.context.get('default_seq_pro_forma') == self.env.context.get('default_name'):
    #         # This code is from quotation proforma invoice is created
    #         name = self.env.context.get('default_seq_pro_forma')
    #         if vals.get('sale_id'):
    #             sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
    #             sale_order_id.proforma_count = 1
    #
    #
    #         # else:
    #         #     name = '/'
    #         # vals['name'] = str(name)
    #     # print(self.name, 'namu',vals.get('sale_id'), vals.get('type'))
    #     # raise UserError('wait soyeb')
    #
    #     return super(account_invoice, self).create(vals)

    def write(self, vals):
        # print('hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh', self.seq_pro_forma,self.env.context.get('default_bool_sale_proforma') )
        if self.env.context.get('default_bool_sale_proforma') == True and self.seq_pro_forma==False:
            # elif vals.get('report_type') == 2 and self.env.context.get('default_bool_sale_proforma') == True or vals.get('proforma_type') in ['local','export'] and self.env.context.get('default_bool_sale_proforma') == True:
            if vals.get('partner_id'):
                partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
                if partner.country_id.name == "India":
                    seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
                    vals['seq_pro_forma'] = 'PI' + str(seq)
                    vals['bool_sale_proforma'] = True
                    name = 'PI' + str(seq)
                    # self.name = name

                    # print(name, 'namepI')

                elif not partner.country_id:
                    raise UserError("Please specify country in customer.")
                elif partner.country_id.name != "India":
                    seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
                    vals['seq_pro_forma'] = 'PE' + str(seq)
                    vals['bool_sale_proforma'] = True
                    name = 'PE' + str(seq)
                    # self.name = name

                    # print(name, 'namePE2')

                if vals.get('sale_id'):
                    sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
                    sale_order_id.proforma_count = 1
        # raise UserError('aaaaaaaaaaaa')

        return super(account_invoice, self).write(vals)
    # @api.model
    # def create(self, vals):
    #     print('in create', vals.get('name'))
    #     # if vals.get('partner_id'):
    #     #     print('')
    #     #     partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
    #     #     if partner.country_id.name == "India":
    #     #         seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #     #         vals['seq_pro_forma'] = 'PI' + str(seq)
    #     #         vals['bool_sale_proforma'] = True
    #     #         name = 'PI' + str(seq)
    #     #     elif not partner.country_id:
    #     #         raise UserError("Please specify county in customer.")
    #     #     elif partner.country_id.name != "India":
    #     #         seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #     #         vals['seq_pro_forma'] = 'PE' + str(seq)
    #     #         vals['bool_sale_proforma'] = True
    #     #         name = 'PE' + str(seq)
    #     # raise UserError('wait')
    #     if vals.get('name'):
    #         # if not vals.get('name'):
    #         print('inside move type000', vals.get('move_type'))
    #         if vals.get('move_type'):
    #             print('inside move type')
    #             #                if vals.get('type') == 'out_invoice' and self.env.context.get('bool_sale_proforma') == False:
    #             # The below code is for the Normal Invoice when u create from invoices tab manually
    #             #                    name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
    #             if vals.get('move_type') == 'in_invoice':
    #                 name = self.env['ir.sequence'].next_by_code('bill.sequence.shridhan') or '/'
    #             elif vals.get('move_type') == 'out_refund':
    #                 name = self.env['ir.sequence'].next_by_code('creditnote.sequence.shridhan') or '/'
    #             elif vals.get('move_type') == 'in_refund':
    #                 name = self.env['ir.sequence'].next_by_code('refund.sequence.shridhan') or '/'
    #             elif self.env.context.get('bool_sale_proforma') == True and vals.get('move_type') == 'out_invoice':
    #                 # This code is for the Performa invoice when u create manually
    #                 if vals.get('partner_id'):
    #                     partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
    #                     if partner.country_id.name == "India":
    #                         seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or 'hiii'
    #                         print(vals['seq_pro_forma'], 'hiiiiiiiiiii')
    #                         vals['seq_pro_forma'] = 'PI' + str(seq)
    #                         vals['bool_sale_proforma'] = True
    #                         name = 'PI' + str(seq)
    #                     elif not partner.country_id:
    #                         raise UserError("Please specify county in customer.")
    #                     elif partner.country_id.name != "India":
    #                         seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #                         vals['seq_pro_forma'] = 'PE' + str(seq)
    #                         vals['bool_sale_proforma'] = True
    #                         name = 'PE' + str(seq)
    #             elif vals.get('type') == 'out_invoice' and self.env.context.get('default_bool_sale_proforma') == True:
    #                 if vals.get('partner_id'):
    #                     partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
    #                     if partner.country_id.name == "India":
    #                         seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #                         vals['seq_pro_forma'] = 'PI' + str(seq)
    #                         vals['bool_sale_proforma'] = True
    #                         name = 'PI' + str(seq)
    #                     elif not partner.country_id:
    #                         raise UserError("Please specify county in customer.")
    #                     elif partner.country_id.name != "India":
    #                         seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
    #                         vals['seq_pro_forma'] = 'PE' + str(seq)
    #                         vals['bool_sale_proforma'] = True
    #                         name = 'PE' + str(seq)
    #                     if vals.get('sale_id'):
    #                         sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
    #                         sale_order_id.proforma_count = 1
    #             elif vals.get('type') == 'out_invoice' and self.env.context.get(
    #                     'ordertype') == 'order' and self.env.context.get('default_bool_sale_proforma') == True:
    #                 # This code is from sale order profoma invoie created
    #                 name = self.env.context.get('default_seq_pro_forma')
    #                 if vals.get('sale_id'):
    #                     sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
    #                     sale_order_id.proforma_count = 1
    #
    #             #                elif vals.get('type') == 'out_invoice' and self.env.context.get('ordertype') == 'order':
    #             # This code is from sale order invoice is got created
    #             #                    name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
    #             elif self.env.context.get('default_seq_pro_forma') == self.env.context.get('default_name'):
    #                 # This code is from quotation proforma invoice is created
    #                 name = self.env.context.get('default_seq_pro_forma')
    #                 if vals.get('sale_id'):
    #                     sale_order_id = self.env['sale.order'].search([('id', '=', vals['sale_id'])])
    #                     sale_order_id.proforma_count = 1
    #
    #
    #             else:
    #                 name = '/'
    #             vals['name'] = str(name)
    #     raise UserError('wait soyeb')
    #     return super(account_invoice, self).create(vals)

    # @api.model
    # def create(self, vals):
    #     pdb.set_trace()
    #     if not self.name:
    #         name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
    #         vals['name'] = str(name)
    #     return super(account_invoice, self).create(vals)

    #
    # def write(self, vals):
    #     pdb.set_trace()
    #     if not self.name:
    #         name = self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan') or '/'
    #         vals['name'] = str(name)
    #     return super(account_invoice, self).write(vals)

    # 
    # def invoice_validate(self):
    #     self.write({'state': 'open', 'name':self.env['ir.sequence'].next_by_code('invoice.sequence.shridhan')})

    #     res = super(account_invoice, self).invoice_validate()

    #     return res

    
    def action_reopen(self):
        x = self.action_invoice_cancel()
        y = self.action_invoice_draft()

    # 
    # def action_reopen(self):
    #     if self.payments_widget != 'false':
    #         raise UserError(_("Please Unreconsile all privious payment of current invoice"))
    #     self.write({'state': 'draft', 'date': False})
    #     # self.delete_workflow()
    #     # self.create_workflow()
    #     self.write({'move_id': False})
    #     return True
