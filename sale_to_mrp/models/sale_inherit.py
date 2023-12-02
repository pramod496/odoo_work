import base64
from datetime import datetime, timedelta

from odoo import api, models, fields, _
from odoo.tests.common import Form
from odoo.exceptions import UserError
import csv
import pdb


# class document_file(models.ModelModel):
#     _inherit = 'ir.attachment'


class ProformaAccountInvoice(models.Model):
    _name = 'proforma.account.move'


class AccountPaymentInherited(models.Model):
    _inherit = 'account.payment'
    performa_id = fields.Many2one('account.move', string='Pro-forma Invoice')

class AccountInvoiceInherited(models.Model):
    _inherit = 'account.move.line'

    name = fields.Char(string='Label', tracking=True, size=200)
    hsn_code = fields.Char(string='HSN/SAC Code',related='product_id.product_tmpl_id.l10n_in_hsn_code')
    origin = fields.Many2one('mrp.production', string='Source Document', readonly=True, copy=False,)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)




class AccountInvoiceInherited(models.Model):
    _inherit = 'account.move'

    # partner_id = fields.Many2one('res.partner', readonly=True, tracking=True,
    #                              states={'draft': [('readonly', False)]},
    #                              check_company=True,
    #                              string='Partner', change_default=True)
    move_id = fields.Many2one(related="line_ids.move_id",string='Journal Entry')
    po_ref = fields.Char('Payment Ref')
    # po_ref = fields.Char('Payment Ref')
    ref_description = fields.Char('Payment/Reference')
    origin = fields.Char(string='Source Document', readonly=True, copy=False,)
    bool_sale_proforma = fields.Boolean(default=False)
    # number = fields.Char(related=move_id.name, readonly=True, copy=False)
    sale_id = fields.Many2one('sale.order',copy=False)
    seq_pro_forma = fields.Char()
    # seq_pro_forma = fields.Char(copy=False)
    revision_no = fields.Char(copy=False)
    rev_count =fields.Integer('Revision',copy=False)
    state_pro = fields.Selection([('draft', 'Draft'),
                                  ('submit', 'Confirm')
                                  ], string='Status', default='draft',copy=False)
    address_state_id = fields.Char( string = "State")
    delivery_term = fields.Many2one('terms.condition',string='Terms and Conditions')
    # delivery_term = fields.Many2one('account.delivery.term',string= 'Terms Of Delivery')
    country_origin = fields.Char('Country of origin', copy=False)
    destination = fields.Char('Destination', copy=False)
    declaration = fields.Char('Declaration', copy=False)
    despatch_through = fields.Char('Despatched Through', copy=False)
    rec_acc_no = fields.Char('Receiver A/c No', copy=False)
    proforma_type = fields.Selection([('local','Local'),('export','Export')], string="Proforma Type",copy=False)
    customer_contact = fields.Many2one('res.partner',string="Customer Contact")
    delivery_contact = fields.Many2one('res.partner',string="Delivery Contact")
    comment_proforma = fields.Text('Additional Information')
    account_id = fields.Many2one('account.account', string='Account',
                                 index=True, ondelete="cascade",
                                 domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
                                 check_company=True,
                                 tracking=True)
    account_analytic_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    # analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags',
    #                                     compute="_compute_analytic_tag_ids", store=True, readonly=False,
    #                                     check_company=True, copy=True)
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags')
    freight_type = fields.Selection([('fixed', 'Fixed Amount'), ('percentage', 'Percentage of Untaxed'), ('none', 'None')])
    freight_value = fields.Float(string='Value', store=True,)
    packing_value = fields.Float(string='Value', store=True,)
    testing_value = fields.Float(string='Value', store=True,)
    loading_value = fields.Float(string='Value', store=True,)
    packing_amount = fields.Float(string='Untaxed Packing Amount', store=True, compute='_compute_amount',)
    testing_amount = fields.Float(string='Untaxed Testing Amount', store=True, compute='_compute_amount',)
    loading_amount = fields.Float(string='Untaxed Loading Amount', store=True, compute='_compute_amount',)
    freight_amount  = fields.Float(
        string='Untaxed Freight Amount', store = True,compute='_compute_amount',
    )
    freight_total = fields.Float(
        string='Freight Total',store = True,compute='_compute_amount',
    )
    packing_total = fields.Float(
        string='Packing Total',store = True,compute='_compute_amount',
    )
    testing_total = fields.Float(
        string='Testing Total', store=True, compute='_compute_amount',
    )
    loading_total = fields.Float(
        string='Loading Total', store=True, compute='_compute_amount',
    )
    freight_tax = fields.Float(
        string='Freight Tax Total',store = True,compute='_compute_amount',
    )
    packing_tax = fields.Float(
        string='Packing Tax Total',store = True,compute='_compute_amount',
    )
    testing_tax = fields.Float(
        string='Testing Tax Total', store=True, compute='_compute_amount',
    )
    loading_tax = fields.Float(
        string='Loading Tax Total', store=True, compute='_compute_amount',
    )
    freight_tax_ids = fields.Many2many(
        'account.tax', 'freight_account_move_tax_rel',
        string='Taxes for Freight',store = True,
    )
    packing_tax_ids = fields.Many2many(
        'account.tax', 'packing_account_move_tax_rel',
        string='Taxes for Packing',store = True,
    )
    testing_tax_ids = fields.Many2many('account.tax', 'testing_account_move_tax_rel', string='Taxes for Testing')
    loading_tax_ids = fields.Many2many('account.tax', 'loading_account_move_tax_rel', string='Taxes for Loading')
    tcs = fields.Many2one('tcs.tcs', string="TCS")
    tcs_value = fields.Float("TCS Amount")
    tcs_amount = fields.Float("TCS Amount", store=True, compute='_compute_amount')

    # def search(self, args, offset=0, limit=None, order=None, count=False):
    #     return 9/0


    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            # self.write({'address_state_id':self.partner_id.state_id.name})
            self.address_state_id = self.partner_id.state_id.name
            addr = self.partner_id.address_get(['delivery'])
            self.partner_shipping_id = addr and addr.get('delivery')
            self.delivery_term = self.partner_id.terms_condition


            # values = {
            #     "terms_condition": self.partner_id.terms_condition,
            #     'partner_shipping_id': self.partner_id.partner_shipping_id.id,
            # }
            # self.update(values)
    
    def confirm(self):
        # self.seq_pro_forma = self.sale_id.write(performa_number)
        # print(self.seq_pro_forma,'sequence performa')
        self.state_pro = 'submit'
        self.action_invoice_open()
        self.amount_residual = self.rounded_total

        # self.state = 'open'
        return True



    
    def reset_to_draft(self):
        self.ensure_one()
        # self.revision_no = self.env['ir.sequence'].next_by_code('revision_number')
        qty =1
        for el in self:
            qty = qty+self.rev_count
        self.rev_count=qty
        self.revision_no = 'Rev0'+str(self.rev_count)
        self.state_pro = 'draft'
        self.state = 'draft'

    
    def name_get(self):
        # print('name get')
        TYPES = {
            'out_invoice': _('Invoice'),
            'in_invoice': _('Vendor Bill'),
            'out_refund': _('Credit Note'),
            'in_refund': _('Vendor Credit note'),
        }
        result = []
        for inv in self:
            # print('inside sale proforma',inv.bool_sale_proforma)
            if inv.bool_sale_proforma:
                result.append((inv.id, "%s" % (inv.seq_pro_forma)))
                # print(result,'result')
            else:
                # result.append((inv.id, "%s %s" % (inv.name or TYPES[inv.type], inv.name or '')))
                result.append((inv.id, "%s %s" % (inv.name or TYPES[inv.type],'')))
                # print(result, inv.name, 'in else')
        # raise UserError('go back soyeb')
        return result

    
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data.check_object_reference('sale_to_mrp', 'email_template_edi_invoice_pro_1')[1]
            mail_template = self.env['mail.template'].browse(template_id)
            mail_template.write({'email_from': self.env.user.partner_id.email})
            mail_template.write({'email_to': self.partner_id.email})
            mail_template.write({'subject': self.company_id.name or '' + " Invoice Ref" + self.seq_pro_forma or 'n/a'})
            if mail_template:
                mail_template.send_mail(self.id, force_send=True)

        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.check_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        res = self.env['account.move'].search([('id','=', self.id)])
        ctx = {
            'default_model': 'account.move',
            'default_res_id': res.id,
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            # 'default_composition_mode': 'comment_proforma',
            'mark_so_as_sent': True,
            'custom_layout': "mail.mail_notification_paynow",
            'proforma': self.env.context.get('proforma', False),
            'force_email': True
        }
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

class AccountDeliveryTerm(models.Model):
    _name='account.delivery.term'

    name= fields.Char('Terms of Delivery')


class SaleInherited(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('customer_lead')
    def calcultetime(self):
        for el in self:
            if el.customer_lead:
                t_date = el.order_id.date_order
                if t_date: 
                    el.desired_delivery_date = fields.Date.to_string(t_date + timedelta(el.customer_lead))
            else:
                self.desired_delivery_date = False

    desired_delivery_date = fields.Datetime(string='Desired Delivery Date',
                                            compute=calcultetime, index=True, copy=False)
    approve_need = fields.Selection([('no', 'No'),
                                     ('yes', 'Yes')
                                     ], string='Status', default='no')
    bom_type = fields.Selection(([('std_bom', 'Repeat Order'),
                                  ('custom_bom', 'New Order'),
                                  ]), string='Order Type', default='custom_bom')


class SaleInherited(models.Model):
    _inherit = 'sale.order'

    def action_view_invoice(self):

        invoices_val = self.mapped('invoice_ids')
        action = self.env.ref('sale_to_mrp.action_invoice_tree1').sudo().read()[0]
        invoices =self.env['account.move'].search([('id', 'in', invoices_val.ids), ('bool_sale_proforma', '=', False)])
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
            action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close',
            # action = {'type': 'ir.actions.act_window',
            #          "domain": [('id', 'in', self.order_line.invoice_lines.move_id.ids), ('move_type', 'in', self.env['account.move'].get_sale_types())],
            #         "res_model": "account.move",
            #           'view_mode': 'tree,form',
            }
        return action

    def action_proforma_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env.ref('sale_to_mrp.action_proforma_invoices').sudo().read()[0]
        sale_id = self.id
        quotation_val = []
        count = 0
        if self.origin:
            quotation = self.env['account.move'].search(
                [('origin', '=', self.origin), ('bool_sale_proforma', '=', True)])
            quotation_val.append(quotation.id)
            for el in invoices:
                if el.bool_sale_proforma == True:
                    quotation_val.append(el.id)
        else:
            invoices = self.env['account.move'].search([('sale_id', '=', sale_id), ('bool_sale_proforma', '=', True)])
            quotation_val = invoices
        if len(quotation_val) > 1:
            invoices = self.env['account.move'].search(
                [('id', 'in', quotation_val.ids), ('bool_sale_proforma', '=', True)])

            action['domain'] = [('id', 'in', invoices.ids)]
            action['views'] = [(self.env.ref('sale_to_mrp.invoice_tree_performa').id, 'tree'),
                               (self.env.ref('sale_to_mrp.account_inherited_form_view').id, 'form')]
        elif len(quotation_val) == 1:
            if self.origin:
                invoices = self.env['account.move'].search(
                    [('id', 'in', quotation_val), ('bool_sale_proforma', '=', True)])
            else:
                invoices = self.env['account.move'].search(
                    [('id', '=', quotation_val.id), ('bool_sale_proforma', '=', True)])
            if invoices.bool_sale_proforma == True:
                # action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
                action['views'] = [(self.env.ref('sale_to_mrp.account_inherited_form_view').id, 'form')]
                action['res_id'] = invoices.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
            # action = self.env.ref('sale_to_mrp.action_proforma_invoices').read()[0]

        return action

    parnter_user_id = fields.Many2one('res.users',string="Partner related User")
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('draft_confirmed', 'Confirm'),
        ('revised', 'Revised'),
        ('confirm_sale', 'Sales Order'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ('hold', 'Hold'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', track_sequence=3, default='draft')
    data = fields.Binary()
    performa_number = fields.Char(copy=False)
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments', store=False)
    work_id = fields.Many2many('work.order.quotation')
    iwo_id = fields.Many2one('work.order.quotation',string="IWO Ref.",copy=False)
    doc_ids = fields.One2many('sale.order.import.wizard', 'order_id', string="Product Specification Docs")
    validity_date = fields.Date(string='Validity', readonly=True, copy=False, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help="Validity date of the quotation, after this date, the customer won't be able to validate the quotation online.")

    type_name = fields.Char('Type Name', compute='_compute_type_name')
    confirm_by=fields.Many2one('res.users','Confirm By')
    revision_no = fields.Char()
    rev_count = fields.Integer('Amendment')
    proforma_count = fields.Integer('Proforma Count', default=0, copy=False, store=True)
    proforma_count_value = fields.Integer('Proforma Count Values', default=0, copy=False, compute='_proforma_invoice_counts')
    revised_date = fields.Datetime('Revised Date')
    is_revised = fields.Boolean('Revised')
    # account_id = fields.Many2one('account.account')

    @api.depends('proforma_count_value')
    def _proforma_invoice_counts(self):
        for record in self:
            print('vvvvvv', record)
            domain = [('sale_id', '=', record.id), ('bool_sale_proforma', '=', True)]
            proforma_invoice = self.env['account.move'].sudo().search(domain)
            record.proforma_count_value = len(proforma_invoice)

    @api.depends('state')
    def _compute_type_name(self):
        for record in self:
            record.type_name = _('Quotation') if record.state in ('draft','draft_confirmed', 'sent', 'cancel') else _('Sales Order')


    def get_product_specifications(self):
        res = []
        if self.order_line:
            for line in self.order_line:
                result = []
                lines_specification = self.env['product.specification.line'].sudo().search([('order_line_id','=', line.id)])
                if lines_specification:
                    for specification in lines_specification:
                        result.append({'spec1':specification.product_specification1,
                            'spec2':specification.product_specification2,
                            'spec3':specification.product_specification3,
                            'spec4':specification.product_specification4,
                            'spec5':specification.product_specification5,
                            'spec6':specification.product_specification6,})
                    res.append(result)
                else:
                    res.append(False)
        return res

    @api.model
    def create(self, vals):
        if vals.get('is_revised') == False:
            vals['revision_no'] = False
            vals['rev_count'] = 0
        if vals.get('is_revised') == True:
            origin_ac = str(vals.get('origin')).split(',')
            vals['name'] = origin_ac[0] + ' ' + vals.get('revision_no')
            vals['is_revised'] = False

        if vals.get('name') == '/':
            vals['origin'] = ''
        # if not vals['origin']:
        #
        #     if vals.get('partner_id'):
        #         partner = self.env['res.partner'].search([('id','=', vals.get('partner_id'))])
        #         if partner.country_id.name == "India":
        #             seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
        #             vals['performa_number'] = 'PI'+str(seq)
        #             vals['number'] = 'PI'+str(seq)
        #         elif not partner.country_id:
        #             raise UserError("Please specify county in customer.")
        #         elif partner.country_id.name != "India":
        #             seq = self.env['ir.sequence'].next_by_code('proforma.shridhan') or '/'
        #             vals['performa_number'] = 'PE'+str(seq)
        #             vals['number'] = 'PE'+str(seq)
        # vals['performa_number'] = self.env['ir.sequence'].next_by_code('proforma.account.invoice')
        company = self.env['res.company']._company_default_get('sale.order')

        if self.env.context.get('ordertype') == 'quotation':
            if 'name' not in vals or vals.get('name') == '/':
                partner = self.env['res.partner'].search([('id', '=', vals.get('partner_id'))])
                if partner.country_id.name == "India":
                    prefix = self.env['ir.sequence'].next_by_code('quotation.shridhan.prefix') or '/'
                    prefix_ss = prefix[0:11]
                    x = self.env['ir.sequence'].next_by_code('quotation.shridhan') or '/'
                    vals['name'] = prefix_ss + 'SQI' + '-' + str(x)
                elif not partner.country_id:
                    raise UserError("Please specify county in customer.")
                elif partner.country_id.name != "India":
                    y = self.env['ir.sequence'].next_by_code('quotation.shridhan') or '/'
                    prefix = self.env['ir.sequence'].next_by_code('quotation.shridhan.prefix') or '/'
                    prefix_ss = prefix[0:11]
                    vals['name'] = prefix_ss + 'SQE' + '-' + str(y)
        if self.env.context.get('ordertype') == 'order':
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order') or _('New')
            vals['state'] = 'confirm_sale'
            # vals['confirmation_date'] = fields.Datetime.now()

        if 'date_order' in vals:
            t_date = datetime.strptime(str(vals['date_order']), "%Y-%m-%d %H:%M:%S").date()
            vals['validity_date'] = fields.Date.to_string(t_date + timedelta(30))
        else:
            today_30day = datetime.now() + timedelta(30)
            vals['validity_date'] = today_30day.strftime("%Y-%m-%d")
        if vals.get('partner_id'):
            user = self.env['res.users'].search([('partner_id', '=', vals.get('partner_id'))])
            vals['parnter_user_id'] = user.id
        res = super(SaleInherited, self).create(vals)
        return res


    def _prepare_invoice(self):
        res = super(SaleInherited, self)._prepare_invoice()
        if res:
            ftax_ids = []
            if self.freight_tax_ids:
                for tax in self.freight_tax_ids:
                    ftax_ids.append(tax.id)
            ptax_ids = []
            if self.packing_tax_ids:
                for tax in self.packing_tax_ids:
                    ptax_ids.append(tax.id)
            res['freight_value'] = self.freight_value
            res['packing_value'] = self.packing_value
            res['freight_tax_ids'] = [[6, False, ftax_ids]]
            res['packing_tax_ids'] = [[6, False, ptax_ids]]

            return res



    def make_amendment(self):
        self.ensure_one()
        # print('make_amendement')
        # self.revision_no = self.env['ir.sequence'].next_by_code('revision_number')
        qty =1
        for el in self:
            qty = qty+el.rev_count
        # self.rev_count=qty
        # self.revision_no = 'Rev0'+str(self.rev_count)
        self.write({'state': 'revised'})
        return self.copy(default={
            'revision_no': 'Rev0'+str(qty),
            'name': self.name+' '+'Rev0'+str(qty),
            'revised_date': fields.Datetime.now(),
            'rev_count': qty,
            'state': 'draft',
            'is_revised': True})
        # return self.write({'state': 'revised'})


    def action_cancel(self):
        if self.iwo_id:
            self.iwo_id.write({'state': 'cancel'})
            lots = self.env['stock.production.lot'].search([('so_id','=', self.id)])
            for lot in lots:
                lot.write({'void': True})
        return self.write({'state': 'cancel'})


    def action_hold(self):
        if self.iwo_id:
            if self.iwo_id != 'approve':
                before_hold = self.iwo_id.state
                self.iwo_id.write({'state': 'hold','hold_before_stage': before_hold})
                self.write({'state': 'hold'})
            else:
                raise UserError("Sale Order can't be Hold as the Internal Work Order is already approved.")
        return


    def action_unhold(self):
        if self.iwo_id:
            status = self.iwo_id.hold_before_stage

            self.iwo_id.write({'state': status})
        return self.write({'state': 'sale'})

    def iwo_confirm_button(self):
        #1: IWO Creation
        #2: Lot Creation
        if not self.iwo_id:
            if not self.order_line:
                raise UserError("Please add product line(s) before confirming for IWO.")
            line_ids = []
            if self.order_line:
                for line in self.order_line:
                    if line.approve_need == 'no':
                        line_ids.append((0, 0, {'product_uom': line.product_uom.id,
                                                'product_id': line.product_id.id,
                                                'sale_line_id':line.id,
                                                'product_uom_qty': line.product_uom_qty,
                                                'description': line.name,
                                                'approve_need': 'no',
                                                'bom_type':line.bom_type,
                                                }))
                    else:
                        line_ids.append((0, 0, {'product_uom': line.product_uom.id,
                                                'product_id': line.product_id.id,
                                                'product_uom_qty': line.product_uom_qty,
                                                'description': line.name,
                                                'approve_need': 'yes',
                                                'bom_type': line.bom_type,
                                               'sale_line_id':line.id,
                                                }))
                name = self.env['ir.sequence'].next_by_code('work.order.quotation.seq')
                work_order = self.env['work.order.quotation'].create({
                    'name': name,
                    'partner_id': self.partner_id.id,
                    'date_order': fields.Date.today(),
                    'origin': self.name,
                    'sale_id': self.id,
                    'work_order_line': line_ids,
                    'state': 'draft',
                    'doc_ids':[(6,0,self.doc_ids.ids)]
                    })

                #passing iwo id back to order and quotation if exist;
                self.write({'iwo_id':work_order.id})
                dos = self.env['stock.picking'].search([('origin','=', self.name)])
                # print("@@@@@@@@@@@@@@@@@",dos)
                for pick in dos:
                    ret = pick.write({'ref_name': work_order.name, 'dc_type': 'normal'})
                if self.origin:
                    if self.origin.startswith('SQ'):
                        quotation = self.env['sale.order'].search([('name','=', self.origin)])
                        if quotation:
                            quotation.write({'iwo_id':work_order.id})
                #generating lots with category concatination;
                # yr = str(self.date_order.year)
                # nextyr = str(self.date_order.year + 1)
                for line in self.order_line:
                    if line.product_id.tracking != 'none':
                        if line.product_id.categ_id:
                            category = line.product_id.categ_id
                        qty = int(line.product_uom_qty)
                        for i in range(qty):
                            ir_seq = self.env['ir.sequence'].search([('category_id','=', category.id)])
                            lotno = self.env['ir.sequence'].next_by_code(ir_seq.code)
                            lot = self.env['stock.production.lot'].create({
                                'name': lotno,
                                'product_id': line.product_id.id,
                                'so_id': self.id,
                                'company_id': self.company_id.id,
                            })
                messages = self.env['mail.message'].search([('res_id', '=', self.id)])
                if messages:
                    for msg in messages:
                        if msg.attachment_ids:
                            msg.copy(default={'res_id': work_order.id, 'model': 'work.order.quotation'})
        self.action_confirm()
        self.confirm_by=self.env.user.id
        # adding the buyer to the picking
        record = self.env['stock.picking'].search([('origin', '=', self.name)])
        for pick in record:
            pick.write({'buyer_id1': self.partner_id.id, 'partner_id': False})
        #SaleOrder Attchments copy to IWO;
        # messages = self.env['mail.message'].search([('res_id','=', self.id)])
        # if messages:
        #     for msg in messages:
        #         if msg.attachment_ids:
        #             msg.copy(default={'res_id': work_order.id, 'model': 'work.order.quotation'})


    def custom_confirm_button(self):
        if not self.order_line:
            raise UserError("Please add product line(s) before confirming Quotation.")

        self.state = 'draft_confirmed'
        self.confirm_by=self.env.user.id
        self.date_order = fields.Datetime.now()
        if self.partner_id:
            user = self.env['res.users'].search([('partner_id','=',self.partner_id.id)])

        won_stages = self.env['crm.lead'].search([('probability', '=', 100)])
        if won_stages:
            won_stage = won_stages[0]
            for order in self:
                if order.opportunity_id:
                    order.opportunity_id.stage_id = won_stage
                    order.opportunity_id.message_post(_(
                        "Stage automatically updated to <i>%s</i> upon "
                        "confirmation of the quotation <b>%s</b>")
                                                      % (won_stage.name, order.name))

        company = self.env['res.company']._company_default_get('sale.order')
        #New Order from Quotation
        order_line = []
        ordervals = {}
        if self.order_line:
            for line in self.order_line:
                tax_ids = []
                if line.tax_id:
                    for tax in line.tax_id:
                        tax_ids.append(tax.id)
                schedule_id = []
                if line.schedule_ids:
                    for schedule in line.schedule_ids:
                        schedule_id.append(schedule.id)
                tag_ids = []
                if self.tag_ids:
                    for tag in self.tag_ids:
                        tag_ids.append(tag.id)
                order_line.append((0, 0, {
                    'qty_delivered_manual': line.qty_delivered_manual,
                    'sequence': line.sequence,
                    'product_uom_qty': line.product_uom_qty,
                    # 'analytic_tag_ids': [[6, False, []]],
                    # 'product_no_variant_attribute_value_ids': [[6, False, []]],
                    'product_id': line.product_id.id,
                    'schedule_ids':[[6, False, schedule_id]],
                    'discount': line.discount,
                    'customer_lead': line.customer_lead,
                    'route_id': line.route_id.id if line.route_id else False,
                    'price_unit': line.price_unit,
                    'approve_need': line.approve_need,
                    'display_type': line.display_type,
                    'tax_id': [[6, False, tax_ids]],
                    'product_uom': line.product_uom.id if line.product_uom else False,
                    'name': line.name,
                    'bom_type': line.bom_type,
                    'approve_num': line.approve_num}))

        ftax_ids = []
        if self.freight_tax_ids:
            for tax in self.freight_tax_ids:
                ftax_ids.append(tax.id)
        ptax_ids = []
        if self.packing_tax_ids:
            for tax in self.packing_tax_ids:
                ptax_ids.append(tax.id)
        ordervals = {'message_attachment_count': self.message_attachment_count,
                     'warehouse_id':self.warehouse_id.id if self.warehouse_id else False,
                     'payment_term_id': self.payment_term_id.id if self.payment_term_id else False,
                     'analytic_account_id': self.analytic_account_id.id if self.analytic_account_id else False,
                     'note': self.note,
                     'date_order': self.date_order,
                     'team_id': self.team_id.id if self.team_id else False,
                     'partner_shipping_id': self.partner_shipping_id.id if self.partner_shipping_id else False,
                     'picking_policy': self.picking_policy,
                     'fiscal_position_id': self.fiscal_position_id.id if self.fiscal_position_id else False,
                     'opportunity_id': self.opportunity_id.id if self.opportunity_id else False,
                     'origin': self.name,
                     'client_order_ref': self.client_order_ref,
                     'medium_id': self.medium_id.id if self.medium_id else False,
                     'partner_id': self.partner_id.id if self.partner_id else False,
                     'sale_order_template_id': self.sale_order_template_id.id if self.sale_order_template_id else False,
                     'campaign_id': self.campaign_id.id if self.campaign_id else False,
                     'require_payment': self.require_payment,
                     'date_order': self.date_order.strftime("%Y-%m-%d %H:%M:%S"),
                     # 'validity_date': self.validity_date,
                     'company_id': self.company_id.id if self.company_id else False,
                     'require_signature': self.require_signature,
                     'user_id': self.user_id.id if self.user_id else False,
                     # 'tag_ids': [[6, False, []]],
                     'source_id': self.source_id.id if self.source_id else False,
                     'incoterm': self.incoterm,
                     'partner_invoice_id': self.partner_invoice_id.id if self.partner_invoice_id else False,
                     'pricelist_id': self.pricelist_id.id if self.pricelist_id else False,
                     'order_line': order_line,
                     'name':self.env['ir.sequence'].next_by_code('sale.order'),
                     'state':'confirm_sale',
                     'date_order': fields.Datetime.now(),
                     'po_date':self.po_date,
                     'tag_ids':[(6, False, tag_ids)],
                     'price_basis':self.price_basis,
                     'packing':self.packing,
                     'delivery':self.delivery,
                     'freight':self.freight,
                     'insurance': self.insurance,
                     'ref': self.ref,
                     'subject': self.subject,
                     'offer_desc': self.offer_desc,
                     'approve_num': self.approve_num,
                     'discount_on_order': self.discount_on_order,
                     'terms_condition': self.terms_condition.id,
                     'freight_value':self.freight_value,
                     'packing_value': self.packing_value,
                     'packing_tax_ids': [[6, False, ptax_ids]],
                     'freight_tax_ids': [[6, False, ftax_ids]],}
        new_order = self.create(ordervals)
        proforma_invoice = self.env['account.move'].search([('sale_id', '=', self.id), ('bool_sale_proforma', '=', True)])
        if proforma_invoice:
            new_order.proforma_count=1
        account_id = self.env['account.move'].search([('sale_id', '=', self.id)])
        if account_id:
            account_id.state_pro = 'submit'
        messages = self.env['mail.message'].search([('res_id','=', self.id)])
        if messages:
            for msg in messages:
                if msg.attachment_ids:
                    msg.copy(default={'res_id': new_order.id})


    def copy(self, default=None):
        self.ensure_one()
        if default is None:
            default = {}
        default['name'] = '/'
        if self.origin and self.origin != '':
            default['origin'] = self.origin + ', ' + self.name
        else:
            default['origin'] = self.name
        return super(SaleInherited, self).copy(default)

    # origin_sale = fields.Char('New source 15')
    # @api.depends('origin_sale')
    # @api.onchange('origin_sale')
    # @api.constrains('origin_sale')
    # def sync_origin(self):
    #     for rec in self:
    #         rec.origin = rec.origin_sale

    def action_proforma_invoice(self):
        view_id = self.env.ref('sale_to_mrp.account_inherited_form_view').id
        account_receivable = self.env['account.account'].search(
            [('user_type_id', '=', self.env.ref('account.data_account_type_receivable').id)], limit=1)

        line_ids = []
        account_id = self.env['account.move'].search([('sale_id', '=', self.id), ('bool_sale_proforma', '=', True)])
       
        quotation_val = []
        invoices = self.mapped('invoice_ids')
        if account_id or self.origin:
            if account_id:
                if len(account_id) == 1:
                    return {
                        'name': _('New'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'tree',
                        'view_mode': 'form',
                        'views': [(view_id, 'form')],
                        'res_model': 'account.move',
                        'view_id': view_id,
                        'target': 'new',
                        'res_id': account_id.id,
                    }
                else:
                    action = self.env.ref('sale_to_mrp.action_proforma_invoices').sudo().read()[0]
                    invoices = self.env['account.move'].search(
                        [('id', 'in', account_id.ids), ('bool_sale_proforma', '=', True)])
                    action['domain'] = [('id', 'in', invoices.ids)]
                    action['views'] = [(self.env.ref('sale_to_mrp.invoice_tree_performa').id, 'tree'),
                                       (self.env.ref('sale_to_mrp.account_inherited_form_view').id, 'form')]
                    return action
            if self.origin:
                quotation = self.env['account.move'].search(
                    [('origin', '=', self.origin), ('bool_sale_proforma', '=', True)])
                quotation_val.append(quotation.id)
                for el in invoices:
                    if el.bool_sale_proforma == True:
                        quotation_val.append(el.id)
                invoices = self.env['account.move'].search(
                    [('id', 'in', quotation_val), ('bool_sale_proforma', '=', True)])
                if invoices:
                    return {
                        'name': _('New'),
                        'type': 'ir.actions.act_window',
                        'view_type': 'tree',
                        'view_mode': 'form',
                        'views': [(view_id, 'form')],
                        'res_model': 'account.move',
                        'view_id': view_id,
                        'target': 'new',
                        'res_id': invoices.id,
                    }
        if self.order_line:

            for line in self.order_line:
                # print(5, line.currency_id)
                line_ids.append((0, 0, {'product_uom_id': line.product_uom.id,
                                        'product_id': line.product_id.id,
                                        'price_unit': line.price_unit,
                                        'quantity': line.product_uom_qty,
                                        'name': line.name,
                                        # 'origin': False,
                                        'account_id': account_receivable.id,
                                        'discount': line.discount,
                                        'currency_id': line.currency_id.id,
                                        'tax_ids': line.tax_id.ids or [(6, 0, line.tax_id.ids)],
                                        'price_subtotal': line.price_subtotal
                                        }))
            context = {'default_partner_id': self.partner_id.id,
                       'default_invoice_date': fields.Date.today(),
                       'default_bool_sale_proforma': True,
                       # 'default_bool_sale_proforma': False,
                       'default_payment_term_id': self.payment_term_id.id,
                       'default_partner_shipping_id': self.partner_shipping_id.id,
                       # 'default_account_id': self.account_id.id,
                       'default_invoice_line_ids': line_ids,
                       'default_sale_id': self.id,
                       'default_seq_pro_forma': self.performa_number,
                       'default_state_pro': 'draft',
                       # 'default_origin': self.origin,
                       'default_number': self.performa_number,
                       'default_freight_tax_ids': self.freight_tax_ids.ids or [(6, 0, self.freight_tax_ids.ids)],
                       'default_packing_tax_ids': self.packing_tax_ids.ids or [(6, 0, self.packing_tax_ids.ids)],
                       'default_freight_value': self.freight_value,
                       'default_packing_value': self.packing_value,
                       # 'default_move_type': 'out_invoice',

                       }
            # if self.order_line:
            #     for line in self.order_line:
            #
            #         move_lines = self.env['account.move.line'].create({'product_uom_id': line.product_uom.id,
            #                                     'product_id': line.product_id.id,
            #                                     'price_unit': line.price_unit,
            #                                     'quantity': line.product_uom_qty,
            #                                     'name': line.name,
            #                                     # 'origin': False,
            #                                     'account_id': account_receivable.id,
            #                                     'discount': line.discount,
            #                                     'currency_id': line.currency_id.id,
            #                                     'tax_ids': line.tax_id.ids or [(6, 0, line.tax_id.ids)],
            #                                     'price_subtotal': line.price_subtotal
            #                                     })

        return {
            'name': _('Pro-Forma Invoice'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'account.move',
            'view_id': view_id,
            'target': 'new',
            'context': context,
            # 'res_id': move_lines,
        }

class SaleOrderImportWizard(models.TransientModel):
    _name = 'sale.order.import.wizard'
    _description = 'Import Your Vendor Bills from Files.'

    def _get_default_journal_id(self):
        return self.env['account.journal'].search([('type', '=', 'purchase')], limit=1)

    order_id = fields.Many2one("sale.order", 'Order')
    work_id = fields.Many2one("work.order.quotation", 'Order')
    attachment_ids = fields.Many2many('ir.attachment', string='Files')
    journal_id = fields.Many2one(string="Journal", comodel_name="account.journal", required=True,
                                 domain="[('type', '=', 'purchase')]", default=_get_default_journal_id,
                                 help="Journal where to generate the bills")

    
    def _create_invoice_from_file(self, attachment):
        invoice_form = Form(self.env['sale.order'], view='sale.view_order_form')
        invoice = invoice_form.save()
        attachment.write({'res_model': 'sale.order', 'res_id': invoice.id})
        invoice.message_post(attachment_ids=[attachment.id])
        return invoice

    
    def add_product_lines(self):

        data = self.attachment_ids.index_content
        filepath = '/opt/odoo/custom/addons/sale_to_mrp/sepcs.csv'
        # filepath = '/opt/odoo_shridan/odoo/odoo/addons/sale_to_mrp/sepcs.csv'
        #filepath = '/opt/odoo/odoo12/shridhan/addons/sale_to_mrp/sepcs.csv'
        lineid = 0
        product_idnew = 0
        with open(filepath, 'w+') as f:
            f.write(data)

        with open(filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            description_pro = ''

            for row in csv_reader:

                if line_count == 0:
                    description_pro = row[0]
                    line_count += 1
                else:
                    if row[0] == 'MODEL NUMBER':
                        product_id = self.env['product.product'].search([('name', '=', row[2])])
                        if product_id:
                            print(product_id)
                        else:
                            product_id = self.env['product.product'].create({'name': row[2]})
                        product_idnew = product_id.id
                        so = self.env['sale.order'].search([('id', '=', self.env.context.get('active_id'))])
                        if so:
                            sol = self.env['sale.order.line'].create({'order_id': so.id,
                                                                'product_id': product_id.id,
                                                                'name': description_pro,
                                                                'product_specification': data})
                            lineid = sol.id
                            self.write({'order_id': so.id})

        with open(filepath) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            specs1 = False
            specs1_list = []
            for y in csv_reader:
                nc = False
                specs2 = False
                specs3 = False
                specs4 = False
                specs5 = False
                specs6 = False
                rep1 = False
                for x in range(len(y)):

                    if x == 0:
                        if y[x]:
                            specs1 = y[x] if y[x] else False
                            if specs1 in specs1_list:
                                nc = True
                            else:
                                nc = False
                                specs1_list.append(y[x])
                        else:
                            specs1 = specs1
                            rep1 = True
                    if x == 1:
                        if y[x]:
                            specs2 = y[x] if y[x] else False
                            
                    if x == 2:
                        if y[x]:
                            specs3 = y[x] if y[x] else False
                    if x == 3:
                        if y[x]:
                            specs4 = y[x] if y[x] else False
                    if x == 4:
                        if y[x]:
                            specs5 = y[x] if y[x] else False
                    if x == 5:
                        if y[x]:
                            specs6 = y[x] if y[x] else False
                if (specs1 != False and rep1 != True) or specs2 != False or specs3 != False or specs4 != False or specs5 != False or specs6 != False:
                    specs_id = self.env['product.specification.line'].sudo().create(
                        {'product_specification1':specs1,
                        'product_specification2':specs2,
                        'product_specification3':specs3,
                        'product_specification4':specs4,
                        'product_specification5':specs5,
                        'product_specification6':specs6,
                        'order_line_id':lineid,
                        'product_id': product_idnew})
                # mapping_id = self.env['product.specification.mapping'].sudo().create({'order_line_id':lineid,'specs_line_id': specs_id.id})
                # specs_id.sudo().write({'mapping_id': mapping_id.id})


    
    def create_invoices(self):
        ''' Create the invoices from files.
         :return: A action redirecting to account.move tree/form view.
        '''
        if not self.attachment_ids:
            return

        invoices = self.env['sale.order']
        for attachment in self.attachment_ids:
            invoices += self._create_invoice_from_file(attachment)

        action_vals = {
            'name': _('Invoices'),
            'domain': [('id', 'in', invoices.ids)],
            'view_type': 'form',
            'res_model': 'sale.order',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        if len(invoices) == 1:
            action_vals.update({'res_id': invoices[0].id, 'view_mode': 'form'})
        else:
            action_vals['view_mode'] = 'tree,form'
        return action_vals



class ProductSpecificationLine(models.Model):
    _name = "product.specification.line"

    order_line_id = fields.Many2one('sale.order.line', string="Order Line")
    # mapping_id = fields.Many2one('product.specification.mapping', string="Mapping Ref#")
    product_specification1 = fields.Char('Product Specification1')
    product_specification2 = fields.Char('Product Specification2')
    product_specification3 = fields.Char('Product Specification3')
    product_specification4 = fields.Char('Product Specification4')
    product_specification5 = fields.Char('Product Specificclient_order_refation5')
    product_specification6 = fields.Char('Product Specification6')
    product_id = fields.Many2one('product.product', string='Product')


class ProductSpecificationMapping(models.Model):
    _name = "product.specification.mapping"

    
    specs_line_id = fields.Many2one('product.specification.line', string="Specification Line")




class Purchase(models.Model):
    _inherit = 'purchase.order'

    po_type = fields.Selection([
        ('spo', 'SPO'),
        ('po', 'PO')],string="PO Type")
    approval_needed_purchase = fields.Boolean('Purchase Approval Needed')
    approval_user_id = fields.Many2one('res.users', string='Approval User', index=True)
    revision_no = fields.Char()
    rev_count =fields.Integer('Amendment')
    rev_bool = fields.Boolean(default=False)

    
    def action_amendment(self):
        self.ensure_one()
        # self.revision_no = self.env['ir.sequence'].next_by_code('revision_number')
        qty =1
        for el in self:
            qty = qty+self.rev_count
        self.rev_count = qty
        self.revision_no = 'Amendment00'+str(self.rev_count)
        self.state = 'draft'
        self.date_order = datetime.now()

    @api.model
    def create(self, vals):
        if vals.get('po_type') == 'spo':
            vals['name'] = self.env['ir.sequence'].next_by_code('service.purchase.order') or _('New')
        res = super(Purchase, self).create(vals)
        if vals.get('approval_user_id'):
            template = self.env.ref('sale_to_mrp.email_template_purchase_approval')
            mail = self.env['mail.template'].browse(template.id).send_mail(res.id, force_send=True)
        return res

    
    def _create_picking(self):
        StockPicking = self.env['stock.picking']
        # for order in self:
        #     if any([ptype in ['product', 'consu'] for ptype in order.order_line.mapped('product_id.type')]):
        #         pickings = order.picking_ids.filtered(lambda x: x.state not in ('done', 'cancel'))
        #         if not pickings:
        #             res = order._prepare_picking()
        #             picking = StockPicking.create(res)
        #         else:
        #             picking = pickings[0]
        #         moves = order.order_line._create_stock_moves(picking)
        #         moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))._action_confirm()
        #         seq = 0
        #         for move in sorted(moves, key=lambda move: move.date_expected):
        #             seq += 5
        #             move.sequence = seq
        #         moves._action_assign()
        #         picking.message_post_with_view('mail.message_origin_link',
        #             values={'self': picking, 'origin': order},
        #             subtype_id=self.env.ref('mail.mt_note').id)
        self.write({'state':'purchase'})
        return True

    
    def approve_order(self, force=False):
        if self.state == 'to approve':
            if self.approval_user_id.id != self.env.uid:
                raise UserError(_('You are not allowed to approve this order.'))
            self.write({'state': 'purchase', 'date_approve': fields.Date.context_today(self)})
        return {}

    
    def button_confirm(self):
        res = super(Purchase, self).button_confirm()
        if self.approval_needed_purchase:
            self.write({'state':'to approve'})
        return res

class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    po_type = fields.Selection(related='order_id.po_type', store=True,)
    not_applicable = fields.Boolean(default=False, copy=False)


    @api.onchange('product_id')
    def onchange_product_id(self):
        result = super(PurchaseLine, self).onchange_product_id()
        if self.po_type == 'spo':
            if self.product_id:
                if self.product_id.type != 'service':
                    raise UserError(_("Please select service type product."))
        return result
