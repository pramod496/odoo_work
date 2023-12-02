from odoo import fields, models,api,_
import pdb
from odoo.exceptions import ValidationError, RedirectWarning, except_orm
import time
from datetime import date
from datetime import datetime


from odoo.osv.expression import AND, NEGATIVE_TERM_OPERATORS

from itertools import groupby
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from odoo.exceptions import UserError
from odoo.addons.stock.models.stock_move import PROCUREMENT_PRIORITIES
from operator import itemgetter


class AccountInvoiceInherit(models.Model):
    _inherit = "account.move"

    
    def action_invoice_open(self):

        if self:
            if self.origin:
                if self.origin.startswith('SO'):
                    order = self.env['sale.order'].search([('name','=', self.origin)])
                    if order.iwo_id:
                        order.iwo_id.write({'invoice_number':self.name,
                            'invoice_date':self.date})
        return super(AccountInvoiceInherit, self).action_invoice_paid()

class SaleAdvancePaymentInvInherited(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInvInherited, self)._create_invoice(order, so_line, amount)
        if res:
            if res.origin:
                if res.origin.startswith('SO'):
                    order = self.env['sale.order'].search([('name','=', res.origin)])
                    if order.iwo_id:
                        order.iwo_id.write({'invoice_number':res.number,
                            'invoice_date':res.date})
        return res

class WorkOrderQuotationSeq(models.Model):
    _name = 'work.order.quotation.seq'

class WorkOrderQuotationProduction(models.Model):
    _name = 'work.order.lot.productin.allotment'

    date_allocate = fields.Datetime(string='Date')
    quantity = fields.Char(string='Order Reference', required=True)
    starting_allocate_lot = fields.Char(string='From', required=True)
    ending_allocate_lot = fields.Char(string='To', required=True)
    iwo_id = fields.Many2one('work.order.quotation',string="IWO Ref.")



class WorkOrderQuotation(models.Model):
    _name = 'work.order.quotation'
    _order ='id desc'
    _description = 'Internal Work Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'

    @api.depends('origin')
    def get_invoice(self):
        for el in self:
            account_id = self.env['account.move'].search(
                [('origin', '=', el.origin), ('state', 'not in', ['draft', 'cancel'])])
            if account_id:
                for acc in account_id:
                    el.invoice_number = acc.name
                    el.invoice_date = acc.invoice_date

    approve_need = fields.Selection ([('no', 'No'),
        ('yes', 'Yes')], string='Approval Status',  default='no',track_visibility='onchange')
    name = fields.Char(string='Order Reference', 
        required=True, copy=False, readonly=True, 
        states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('New'),track_visibility='onchange')
    origin = fields.Char(string='Source Document', copy=False, help="Reference of the document that generated this sales order request.",track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Submitted'),
        ('approve', 'Approved'),
        ('cancel', 'Cancelled'),
        ('hold', 'Hold'),
        ], string='Status',  default='draft',track_visibility='onchange')
    hold_before_stage = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Submitted'),
        ],track_visibility='onchange')
    date_order = fields.Datetime(string='Order Date', default=fields.Datetime.now,track_visibility='onchange')
    work_order_line = fields.One2many('work.order.quotation.line','work_id',string='Order line' ,states={'draft': [('readonly', False)]},copy=False,)
    lot_allocation = fields.One2many('work.order.lot.productin.allotment','iwo_id',string='Lot Allocation Lines',copy=False,)


    partner_id = fields.Many2one('res.partner',string='Customer',track_visibility='onchange')
    sale_id = fields.Many2one('sale.order',copy=False,)
    bom_id = fields.Many2one('mrp.bom','Bill Of Materials',copy=False,)
    doc_ids = fields.One2many('sale.order.import.wizard', 'work_id', string="Product Specification Docs")
    invoice_number = fields.Char(string='Invoice No',copy=False,track_visibility='onchange')
    invoice_date = fields.Date(string='Invoice Date',copy=False,track_visibility='onchange')




    
    def action_confirm_work_order(self):
        self.state = 'confirmed'
        for line in self.work_order_line:
            #line.bool_state = True
            count = 0
            for el in line.bom_work_line:
                if el.select_bom==True:
                    count=count+1
            if count >1:
                raise ValidationError(_('Please make sure multiple BOMs are not selected.'))

    
    def action_approve_work_order(self):

        for line in self.work_order_line:
            line.bool_state = True
            if line.state == 'confirmed':
                pass
            # else:
            #      raise UserError(_('Before confirmation of this work order, please ensure that all the work order lines are confirmed'
            #                   ))
        self.state = 'approve'
        dict ={}
        for line in self.work_order_line:
            if line.bom_id:
                if line.bom_id.operation_ids:
                    if line.bom_id.operation_ids.subcontract:
                        dict[line.product_id.id]='subcontract'
                    elif line.bom_id.operation_ids.shoop_floor:
                        dict[line.product_id.id]='shoop_floor'
                    else :
                        dict[line.product_id.id]='normal'
        bom_id = False
        if self.work_order_line:
            for line in self.work_order_line:
                if line.bom_type == 'std_bom':
                    if line.bom_work_line:
                        for bom in line.bom_work_line:
                            if bom.select_bom == True:
                                bom_id = bom
                else:
                    if line.bom_line_custom_id:
                        for x in line.bom_line_custom_id:
                            bom_id = x.bom_id

                lot = self.env['stock.production.lot'].sudo().search([
                    ('so_id', '=', self.sale_id.id),
                    ('product_id', '=', line.product_id.id)
                ])
                mo_record = {}
                if lot:
                    mo_record = self.env['mrp.production'].create({
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom_id': line.product_uom.id,
                        'bom_id': bom_id.id,
                        'origin': self.name,
                        'so_ref': self.sale_id.id,
                        'partner_id': self.partner_id.id,
                        'lot_producing_id': lot and lot[0].id or False,

                    })
                else:
                    mo_record = self.env['mrp.production'].create({
                        'product_id': line.product_id.id,
                        'product_qty': line.product_uom_qty,
                        'product_uom_id': line.product_uom.id,
                        'bom_id': bom_id.id,
                        'origin': self.name,
                        'so_ref': self.sale_id.id,
                        'partner_id': self.partner_id.id,
                        'lot_producing_id': lot.id,

                    })
                # print(mo_record,'mo record')
                count_product_qty = line.product_uom_qty
                location_id = mo_record.location_src_id.id
                location_dest_id = self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
                for component in mo_record.bom_id.bom_line_ids:
                    mo_record.move_raw_ids += self.env['stock.move'].create({
                                        'name': component.product_id.name,
                                        'product_id': component.product_id.id,
                                        'product_uom_qty': component.product_qty * count_product_qty,
                                        'origin': self.name,
                                        # 'reserved_availability':line.product_qty,
                                        # 'quantity_done':line.product_qty,
                                        'product_uom': component.product_id.uom_id.id,
                                        # 'picking_id': picking1.id,
                                        'location_id': location_id,
                                        'location_dest_id': location_dest_id,
                                        })
                # mo_record._onchange_move_raw()

        bom_id.write({'select_bom': True})
        # raise UserError('wait')
        return True

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('work.order.quotation.seq') or _('New')
        result = super(WorkOrderQuotation, self).create(vals)
        return result

class WorkOrderQuotationLine(models.Model):
    _name = 'work.order.quotation.line'
    _description = 'Internal Work Order Line'

    
    def confirm(self):
        count = 0
        for el in self.bom_work_line:
            if el.select_bom==True:
                count=count+1
        if count >1:
            raise ValidationError(_('Please make sure Multiple Bom\'s are not selected.'))

        self.state = 'confirmed'

    
    def approval_request(self):
        self.state = 'waiting'

    
    def approve(self):
        self.state = 'approve'
    def map_many2_many(self,list):
        return [(6,0,[x.id for x in list])]

    
    def boq_update_repeat(self):
        for el in self:
            if el.product_id and el.bom_type == 'std_bom':
                bom_ids = self.env['mrp.bom'].search([('product_id','=',el.product_id.id)])
                lists=[]
                for ele in bom_ids:
                    lists.append(ele)
                el.bom_work_line = self.map_many2_many(lists)


    @api.onchange('product_id')
    def _onchange_product_id(self):
        for order in self:
            defcode = ''
            if order.product_id.product_tmpl_id.default_code:
                defcode = "["+str(order.product_id.product_tmpl_id.default_code)+"]"
            if defcode:
                self.description = defcode + order.product_id.product_tmpl_id.name
            self.product_uom = order.product_id.product_tmpl_id.uom_id.id
            self.product_category_id = order.product_id.product_tmpl_id.categ_id.id

    approve_need = fields.Selection([('no', 'No'),
                                     ('yes', 'Yes')
                                     ], string='Status', default='no')
    bool_state = fields.Boolean(default=False)

    work_id = fields.Many2one('work.order.quotation')
    product_id = fields.Many2one('product.product', String='Product')
    description = fields.Text(string='Description')
    product_uom_qty = fields.Float(String='Quantity',default=1.0)
    product_uom = fields.Many2one('uom.uom')
    state = fields.Selection(([('draft', 'Draft'),
                            ('waiting', 'Waiting Drawing Approval'),
                            ('approve', 'Drawing Approved'),
                            ('confirmed', 'Confirmed'),]), string='Status',default='draft')

    bom_id =fields.Many2one('mrp.bom')
    special_instruction = fields.Text(string='Special Instruction')
    bom_line_custom_id = fields.One2many('mrp.bom.custom', 'work_custom_id')
    sale_line_id = fields.Many2one('sale.order.line')
    desired_delivery_date = fields.Datetime(string='Desired Delivery Date',related='sale_line_id.desired_delivery_date',store=True,)
    material_delivery_date = fields.Datetime(string='Raw Materials Delivery Date',store=True,)

    # bool = fields.Boolean(compute=OnchangeBomLine)
    bom_work_line = fields.One2many('mrp.bom','work_order_id_bom',string='Bom Old',states={'draft': [('readonly', False)]},)
    bom_type = fields.Selection(([('std_bom', 'Repeat Order'),
                                  ('custom_bom', 'New Order'),
                                  ]), string='Order Type', default='custom_bom')

    schedule = fields.Char(compute='_total_qty', string="Schedule")
    @api.model
    def _total_qty(self):
        val=[]
        for j in self:
            line = j.sale_line_id
            stoc = self.env['sale.order.line.schedule'].search([('sale_order_line_id','=',line.id)])
            if stoc:
                for el in stoc:
                    if el.planned_quantity:
                        # date_1 = datetime.strftime(el.planned_date, "%d-%m-%Y")
                        date = datetime.strptime(str(el.planned_date).split(' ')[0], "%Y-%m-%d")
                        if j.schedule:
                            j.schedule = str(j.schedule) + " , " + str(date) + ' : ' + str(int(el.planned_quantity))
                        else:
                            j.schedule = str(date) + ' : ' + str(int(el.planned_quantity))
            j.schedule = 'F'

    
    def boq_update(self):
        view_id = self.env.ref('mrp.mrp_bom_form_view').id
        context = {'default_product_id': self.product_id.id,
                   'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                   'default_product_qty': 1,
                   'default_work_id': self.id ,
                   'default_type': 'normal',

                   }

        if self.bom_id:
            return {
                'name': _('Mrp/BOM'),
                'type': 'ir.actions.act_window',
                'view_type': 'tree',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'mrp.bom',
                'view_id': view_id,
                'res_id': self.bom_id.id,
                'target': 'new',
            }

        return {
            'name': _('Mrp/BOM'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'mrp.bom',
            'view_id': view_id,
            'target': 'new',
            'context':context,
        }


class MrpBomInherit(models.Model):
    _inherit = 'mrp.bom'


    work_id = fields.Many2one('work.order.quotation.line',string='Work Order Line')
    work_bom_line_id = fields.Many2one('mrp.bom.line', string='Work Order Line')
    work_order_id_bom = fields.Many2one('work.order.quotation.line')
    select_bom = fields.Boolean('Select Bom',default=True)
    partner_id = fields.Many2one('res.partner',string='Customer')
    operation_id = fields.Many2one('mrp.routing.workcenter', string='Consumed In Operation')
    bom_work_custom_id = fields.Many2one('mrp.bom.custom')

    @api.model
    def create(self, vals):
        res = super(MrpBomInherit, self).create(vals)
        if res.work_id:
            res.work_id.bom_id = res.id
            res.work_id.bom_line_custom_id = [(6, 0, res.bom_line_ids.ids)]
            list =[]
            for el in  res.bom_line_ids:
                custom_bom = self.env['mrp.bom.custom']
                bom_custom = custom_bom.create({'product_id':el.product_id.id,
                                    'product_qty':el.product_qty,
                                    'product_uom_id':el.product_uom_id.id ,
                                    'bom_id': res.id,
                                    })
                list.append(bom_custom)
            list_id =[]
            for lel in list:
                list_id.append(lel.id)

            res.work_id.bom_line_custom_id = [(6, 0, list_id)]
            if res.work_id.work_id:
                if res.work_id.work_id.partner_id:
                    res.partner_id = res.work_id.work_id.partner_id.id

        if res.bom_work_custom_id:
            res.bom_work_custom_id.bom_id = res.id
        return res

    
    def write(self, vals):
        # return 9/0
        res = super(MrpBomInherit, self).write(vals)
        for el in self:
            if el.work_id:
                el.work_id.bom_id = el.id
                el.work_id.bom_line_custom_id = [(6, 0, el.bom_line_ids.ids)]
                list =[]
                for ell in  el.bom_line_ids:
                    custom_bom = self.env['mrp.bom.custom']
                    bom_custom = custom_bom.create({'product_id':ell.product_id.id,
                                    'product_qty':ell.product_qty,
                                    'product_uom_id':ell.product_uom_id.id ,
                                    'bom_id': el.id,
                                    })
                    list.append(bom_custom)
                list_id =[]
                for lel in list:
                    list_id.append(lel.id)
                el.work_id.bom_line_custom_id = [(6, 0, list_id)]
            if el.bom_work_custom_id:
                el.bom_work_custom_id.bom_id = res.id
        return res

    @api.onchange('select_bom')
    def onchangebom(self):
        for el in self:
            if 'params' in self._context:
                if self._context['params']['model'] == 'work.order.quotation':
                    if 'id' in self._context['params']:
                        work_id = self.env['work.order.quotation'].search([('id','=',self._context['params']['id'])])
                        if len(work_id)>0:
                            for line in work_id.work_order_line:
                                if line.product_id.id == el.product_id:
                                        line.bom_line_custom_id = [(6, 0, el.bom_line_ids.ids)]

    @api.model
    def _bom_find_domain(self, products, picking_type=None, company_id=False, bom_type=False):
        domain = ['|', ('product_id', 'in', products.ids), '&', ('product_id', '=', False),
                  ('product_tmpl_id', 'in', products.product_tmpl_id.ids)]
        if company_id or self.env.context.get('company_id'):
            domain = AND([domain, ['|', ('company_id', '=', False),
                                   ('company_id', '=', company_id or self.env.context.get('company_id'))]])
        if picking_type:
            domain = AND([domain, ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]])
        if bom_type:
            domain = AND([domain, [('type', '=', bom_type)]])
        domain = AND([domain, [('select_bom', '=', True)]])
        return domain


    # @api.model
    # def _bom_find(self, product_tmpl=None, product=None, picking_type=None, company_id=False, bom_type=False):
    #     """ Finds BoM for particular product, picking and company """
    #     if product:
    #         if not product_tmpl:
    #             product_tmpl = product.product_tmpl_id
    #         domain = ['|', ('product_id', '=', product.id), '&', ('product_id', '=', False), ('product_tmpl_id', '=', product_tmpl.id)]
    #     elif product_tmpl:
    #         domain = [('product_tmpl_id', '=', product_tmpl.id)]
    #     else:
    #         # neither product nor template, makes no sense to search
    #         return False
    #     if picking_type:
    #         domain += ['|', ('picking_type_id', '=', picking_type.id), ('picking_type_id', '=', False)]
    #     if company_id or self.env.context.get('company_id'):
    #         domain = domain + [('company_id', '=', company_id or self.env.context.get('company_id'))]

        # order to prioritize bom with product_id over the one without
        # domain_add = domain +[('select_bom', '=', True)]
        # if len(self.search(domain_add)) == 1:
        #     return self.search(domain_add)
        # else:
        #     return self.search(domain, order='id desc, product_id', limit=1)


class MrpBomcustom(models.Model):
    _name = 'mrp.bom.custom'
    _description = 'Bom Custom'

    @api.model
    def get_bool(self):
        mo_type = self.env.ref('mrp.route_warehouse0_manufacture', raise_if_not_found=False)
        for el in self:
            if mo_type.id in el.product_id.route_ids.ids:
                el.bool = True
            else:
                el.bool = False

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for order in self:
            self.product_uom_id = order.product_id.product_tmpl_id.uom_id.id

    product_id = fields.Many2one('product.product',string='Component')
    product_qty = fields.Float(string='Product Quantity',default=1.0)
    bom_id =fields.Many2one('mrp.bom')
    product_uom_id = fields.Many2one('uom.uom',string='Product Unit Measure')
    operation_id = fields.Many2one('mrp.routing.workcenter',string='Consumed In Operation')
    work_custom_id = fields.Many2one('work.order.quotation.line', string='Work Order Line')
    bool = fields.Boolean(default=False, compute=get_bool)



    
    def bom_line_update(self):
        view_id = self.env.ref('mrp.mrp_bom_form_view').id
        context = {'default_product_id': self.product_id.id,
                   'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                   'default_product_qty': self.product_qty,
                   'default_type': 'normal',
                   'default_bom_work_custom_id': self.id,

                   }
        #
        if self.bom_id:
            return {
                'name': _('Mrp/BOM'),
                'type': 'ir.actions.act_window',
                'view_type': 'tree',
                'view_mode': 'form',
                'views': [(view_id, 'form')],
                'res_model': 'mrp.bom',
                'view_id': view_id,
                'res_id': self.bom_id.id,
                'target': 'new',
            }

        return {
            'name': _('Mrp/BOM'),
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'form',
            'views': [(view_id, 'form')],
            'res_model': 'mrp.bom',
            'view_id': view_id,
            'target': 'new',
            'context':context,
        }

class StockMoveLine(models.Model):
    _inherit = "stock.move.line"
    
    lot_id = fields.Many2one('stock.production.lot', 'Serial Number')
    lot_name = fields.Char('Serial Number Name') 
    mo_id = fields.Many2one(related='picking_id.mo_id', string="Manufacturing Order Ref") 
    sale_id = fields.Many2one(related='picking_id.sale_id', string="Sale Order Ref")

    @api.onchange('sale_id')
    def _get_sale_related_lots(self):
        res = []
        lots = self.env['stock.production.lot'].search([('so_id','=', self.sale_id.id)])
        for lot in lots:
            res.append(lot.id)
        return {'domain': {'lot_id': [('id', 'in', res)],}}

class StockPickingInherit(models.Model):
    _inherit = "stock.production.lot"

    void = fields.Boolean(string='Void', default=False)
    so_id = fields.Many2one('sale.order',string="Order Id")

    use_next_on_work_order_id = fields.Many2one('mrp.workorder',
        string="Next Work Order to Use",
        help='Technical: used to figure out default serial number on work orders')





class MrpProducesubcontract(models.Model):
    _name = "mrp.production.subcontract"
class MrpProduceShopFloor(models.Model):
    _name = "mrp.production.shop.floor"



class MrproutingInherit(models.Model):
    _inherit = "mrp.routing.workcenter"


    shoop_floor = fields.Boolean('Shop Floor')
    subcontract = fields.Boolean('Subcontract')

class MrpProduceInherit(models.Model):
    _inherit = "mrp.production"

    @api.depends('bom_id.operation_ids')
    def get_type_seq(self):
        for el in self:
            if el.bom_id.operation_ids.subcontract:
                el.type_seq = 'subcontract'
                el.subcontract = True
            elif el.bom_id.operation_ids.shoop_floor:
                el.type_seq = 'shop_floor'
            else:
                el.type_seq = 'normal'

    
    def open_produce_product(self):
        self.ensure_one()
        stock_req = self.env['stock.request'].search([('origin','=',self.id)])
        for line in stock_req.stock_line:
            if line.state == 'draft':
                raise ValidationError(_('Please Make sure issue of the items is done'))

        action = self.env.ref('mrp.act_mrp_product_produce').read()[0]
        return action

    
    def button_plan(self):
        # print('before')
        res = super(MrpProduceInherit, self).button_plan()
        # print('after')
        stock_req = self.env['stock.request'].search([('origin','=',self.id)])
        for line in stock_req.stock_line:
            if line.state == 'draft':
                raise ValidationError(_('Please Make sure issue of the items is done'))

        saleorder = self.env['sale.order'].search([('name','=',self.internal_work_order_id.origin)])
        lots = self.env['stock.production.lot'].search([('so_id','=',saleorder.id),('product_id','=', self.product_id.id)])
        production_id = self.env['mrp.workorder'].search([('production_id','=',self.id),('state','=','ready')])
        for lot in lots:
            lot.write({'use_next_on_work_order_id':production_id.id})
        return res

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            if 'bom_id' in values:
                bom = self.env['mrp.bom'].search([('id','=',values['bom_id'])])
                if bom.operation_ids:
                    if bom.operation_ids.subcontract:
                        values['name'] = self.env['ir.sequence'].next_by_code('mrp.production.subcontract') or _('New')
                    elif bom.operation_ids.shoop_floor:
                        values['name'] = self.env['ir.sequence'].next_by_code('mrp.production.shop.floor') or _('New')
                    else:
                        values['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
            elif 'type_seq' in values:
                if values['type_seq'] == 'subcontract':
                    values['name'] = self.env['ir.sequence'].next_by_code('mrp.production.subcontract') or _('New')
                elif values['type_seq'] == 'shop_floor':
                    values['name'] = self.env['ir.sequence'].next_by_code('mrp.production.shop.floor') or _('New')
                else:
                    values['name'] = self.env['ir.sequence'].next_by_code('mrp.production') or _('New')
            else:
                pass

        if values.get('origin'):
            if values.get('origin').startswith('SO'):
                return {}
        production = super(MrpProduceInherit, self).create(values)
        if production.bom_id.select_bom:
            production.bom_id.select_bom=False

        return production

    
    def write(self, values):
        if values.get('move_raw_ids'):
            for moveid in values.get('move_raw_ids'):
                if moveid[0] == 0:
                    bomline = self.env['mrp.bom.line'].create({
                        'product_id': moveid[2].get('product_id'),
                        'product_qty': moveid[2].get('product_uom_qty'),
                        'product_uom_id': moveid[2].get('product_uom'),
                        'bom_id': self.bom_id.id,})
                if moveid[0] == 1:
                    move = self.env['stock.move'].search([('id','=', moveid[1])])
                    bom_line = self.env['mrp.bom.line'].search([('bom_id','=', self.bom_id.id),('product_id','=', move.product_id.id)])
                    if bom_line:
                        self.env['mrp.bom.line'].write(moveid[2])
                if moveid[0] == 2:
                    move = self.env['stock.move'].search([('id','=', moveid[1])])
                    bom_line = self.env['mrp.bom.line'].search([('bom_id','=', self.bom_id.id),('product_id','=', move.product_id.id)])
                    bom_line.unlink()
        return super(MrpProduceInherit, self).write(values)



    type_seq = fields.Selection([
        ('normal', 'Normal'), ('shop_floor', 'Shop Floor'), ('subcontract', 'Sub Contract')],
        string='Type',compute='get_type_seq',required=True,)
    so_ref = fields.Many2one('sale.order', string="SO Ref")
    internal_work_order_id = fields.Many2one('work.order.quotation',compute="_get_work_order")

    @api.model
    def _get_work_order(self):
        for el in self:
            el.internal_work_order_id = False
            if el.origin:
                wo = self.env['work.order.quotation'].search([('name','=',el.origin)])
                if wo:
                    for x in wo:
                        el.internal_work_order_id = x.id
                sale_id = self.env['sale.order'].search([('name','=',el.origin)])
                mrp_id = self.env['mrp.production'].search([('name', '=', el.origin)],limit=1)
                if sale_id:
                  el.partner_id = sale_id.partner_id.id
                  work_id =  self.env['work.order.quotation'].search([('sale_id','=',sale_id.id)])
                  if work_id:
                      el.internal_work_order_id = work_id.id
                if mrp_id.internal_work_order_id:
                  el.internal_work_order_id = mrp_id.internal_work_order_id.id

    # partner_id = fields.Many2one('res.partner',compute=_get_work_order)

class MrpProductProduce(models.TransientModel):
    _inherit = "mrp.immediate.production.line"

    sale_id = fields.Many2one('sale.order', string="Order Ref#")

    @api.model
    def default_get(self, fields):
        res = super(MrpProductProduce, self).default_get(fields)
        if self._context and self._context.get('active_id'):
            production = self.env['mrp.production'].browse(self._context['active_id'])

            #Added sale id for lot filter
            res['sale_id'] = production.so_ref.id
        return res

    
    def do_produce(self):
        # Relieve the lot which is producing
        res = super(MrpProductProduce, self).do_produce()
        if self.lot_id:
            self.lot_id.write({'so_id':False})
        return {'type': 'ir.actions.act_window_close'}
