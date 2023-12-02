from odoo import models, fields, api
import pdb


class ReportMyReport(models.AbstractModel):
    _name = 'report.export_packing_list.report_export_packing_list'

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


class MoveLine(models.Model):
    _inherit = 'stock.move'

    kind_of_pkg = fields.Text('Number and Kind of Packages')
    type_seq = fields.Selection([
        ('normal', 'Normal'), ('shop_floor', 'Shop Floor'), ('subcontract', 'Sub Contract')],
        string='Type', required=True, )
    so_ref = fields.Many2one('sale.order', string="SO Ref")

    @api.model
    def _get_work_order(self):
        for el in self:
            if el.origin:
                wo = self.env['work.order.quotation'].search([('name', '=', el.origin)])
                if wo:
                    for x in wo:
                        el.internal_work_order_id = x.id
                # sale_id = self.env['sale.order'].search([('name','=',el.origin)])
                # mrp_id = self.env['mrp.production'].search([('name', '=', el.origin)],limit=1)
                # print(mrp_id.internal_work_order_id)
                # if sale_id:
                #   el.partner_id = sale_id.partner_id.id
                #   work_id =  self.env['work.order.quotation'].search([('sale_id','=',sale_id.id)])
                #   if work_id:
                #       el.internal_work_order_id = work_id.id
                # if mrp_id.internal_work_order_id:
                #   el.internal_work_order_id = mrp_id.internal_work_order_id.id

    internal_work_order_id = fields.Char('work.order.quotation', compute="_get_work_order")
    #
    # def get_type_seq(self):
    #     for el in self:
    #         if el.bom_id.operation_ids.subcontract:
    #             el.type_seq = 'subcontract'
    #             el.subcontract = True
    #         elif el.bom_id.operation_ids.shoop_floor:
    #             el.type_seq = 'shop_floor'
    #         else:
    #             el.type_seq = 'normal'

    def get_king_of_pkg(self):
        clean_pkg = self.kind_of_pkg
        while clean_pkg and clean_pkg.find('\n\n') != -1:
            clean_pkg = clean_pkg.replace('\n\n', '\n')
        if clean_pkg:
            clean_pkg = clean_pkg.split('\n')
        return clean_pkg



class DeliveryOrder(models.Model):
    _inherit = 'stock.picking'

    notify_id1 = fields.Many2one('res.partner','Notify Partner')
    buyer_id1  = fields.Many2one('res.partner','Buyer')
    partner_id = fields.Many2one('res.partner', 'Partner',states={})
    delivery_address  = fields.Many2one('res.partner','Delivery Address')
    declaration = fields.Char('Declaration')
    declaration1 = fields.Char('Declaration for DC')
    destination_port = fields.Char('Destination Port')
    receiver_ac_no = fields.Char('Receiver A/c No')
    sender_ac_no = fields.Char('Sender A/C No')
    inv_ref = fields.Char('Other References')
    inv_date = fields.Date('Invoice Date')
    bank_name = fields.Char('Bank Name', compute='get_bank_name')
    bank_acc_no = fields.Char('Bank Acc No.', compute='get_details')
    branch_code = fields.Char('Branch Code', compute='get_branch_code')
    branch_ifsc = fields.Char('Bank IFSC', compute='get_branch_ifsc')

    def get_details(self):
        bank = []
        for rec in self:
            for b in rec.company_id.partner_id.bank_ids:
                bank.append(b.acc_number)
            for i in bank:
                hjk = i
            rec.bank_acc_no = i

    def get_bank_name(self):
        name=[]
        for rec in self:
            for b in rec.company_id.partner_id.bank_ids:
                name.append(b.bank_id)
            for i in name:
                hjk = i
            rec.bank_name = i.name

    def get_branch_code(self):
        code=[]
        for rec in self:
            for b in rec.company_id.partner_id.bank_ids:
                code.append(b.branch_ifsc)
            for i in code:
                hjk = i
            rec.branch_code = i

    def get_branch_ifsc(self):
        ifsc=[]
        for rec in self:
            for b in rec.company_id.partner_id.bank_ids:
                ifsc.append(b.ifsc_code)
            for i in ifsc:
                hjk = i
            rec.branch_ifsc = i
