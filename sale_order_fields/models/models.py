from odoo import api, fields, models,_
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import pdb

class SaleInheritedFields(models.Model):
    _inherit = 'sale.order'
    ref = fields.Char(string='Ref')
    approve_num = fields.Char( string='Drawing number')
    contact =fields.Many2many('res.users','contact')
    enclosure = fields.Char(string="Enclosure")
    offer_desc= fields.Char(string="Offer Description")
    subject = fields.Char(string="Subject")
    kind_attn = fields.Many2one('res.partner',string="Kind Attention")

    @api.model
    def create(self, vals):
        if vals.get('origin'):
            if vals.get('origin').startswith('SQ'):
                sq = self.env['sale.order'].search([('name','=',vals.get('origin'))])
                vals['ref'] = sq.ref
                vals['approve_num'] = sq.approve_num
                vals['subject'] = sq.subject
                vals['offer_desc'] = sq.offer_desc
                vals['enclosure'] = sq.enclosure
                list_contact = []
                if sq.contact:
                    for con in sq.contact:
                        list_contact.append(con.id)
                vals['contact'] = [(6, 0, list_contact)]
        return super(SaleInheritedFields, self).create(vals)

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    approve_num = fields.Char( string='Drawing number')

class ResPartnerFields(models.Model):
    _inherit = 'res.partner'

    cin_num = fields.Char(string='CIN No.')
    ISO_Num = fields.Char( string='ISO No.')
    pan  = fields.Char(string='Pan No')


class ResCompanyFields(models.Model):
    _inherit = 'res.company'

    logo2 = fields.Binary(string="Company Logo", readonly=False)

    streets = fields.Char(string='streets')
    streets2 = fields.Char(string='streets2')
    zips = fields.Char(string='zips')
    citys = fields.Char(string='citys')
    state_id = fields.Many2one('res.country.state',string="Fed. State")

    country_id = fields.Many2one('res.country',string="Country")
    remarks= fields.Char(string="Remarks")
    quotation_doc = fields.Char(string="Quotation Document Number")
    commer_decl = fields.Char(string="Declaration for commercial")
    declaration= fields.Char(string="Declaration for proforma")
    waranty_inc=fields.Char(string="Waranty for commercial")
    receiver_email_id=fields.Char(string="Receiver Mail")
    lut_no=fields.Many2one('lut.master', string="LUT ARN No")
    lut_date=fields.Date(string="LUT ARN Date")

    @api.onchange("lut_no")
    def _onchange_lut_no(self):
        self.lut_date = self.lut_no.start_date
        return

    @api.model
    def _set_new_lut_arn(self):
        """this is a cron for set LUT ARN No."""
        temp_id = self.env.ref('sale_order_fields.lut_email_template').id
        rec = self.env['mail.template'].browse(temp_id).send_mail(self.env.user.company_id.id, force_send=True)
        # print("##########inside cron#########",self.env.user.company_id, rec)

class StockProductionLotInherited(models.Model):
    _inherit = 'stock.production.lot'

    warranty_date = fields.Datetime('Warranty')
class Accountinvoice(models.Model):
    _inherit = 'account.move'
    despatched_through = fields.Char(string="Despatch Through")


class stockpickingInherit(models.Model):
    _inherit = "stock.picking"


    
    def action_done(self):
        """Changes picking state to done by processing the Stock Moves of the Picking

        Normally that happens when the button "Done" is pressed on a Picking view.
        @return: True
        """
        # TDE FIXME: remove decorator when migration the remaining
        todo_moves = self.mapped('move_lines').filtered(
            lambda self: self.state in ['draft', 'waiting', 'partially_available', 'assigned', 'confirmed'])
        # Check if there are ops not linked to moves yet
        for pick in self:
            # # Explode manually added packages
            # for ops in pick.move_line_ids.filtered(lambda x: not x.move_id and not x.product_id):
            #     for quant in ops.package_id.quant_ids: #Or use get_content for multiple levels
            #         self.move_line_ids.create({'product_id': quant.product_id.id,
            #                                    'package_id': quant.package_id.id,
            #                                    'result_package_id': ops.result_package_id,
            #                                    'lot_id': quant.lot_id.id,
            #                                    'owner_id': quant.owner_id.id,
            #                                    'product_uom_id': quant.product_id.uom_id.id,
            #                                    'product_qty': quant.qty,
            #                                    'qty_done': quant.qty,
            #                                    'location_id': quant.location_id.id, # Could be ops too
            #                                    'location_dest_id': ops.location_dest_id.id,
            #                                    'picking_id': pick.id
            #                                    }) # Might change first element
            # # Link existing moves or add moves when no one is related
            for ops in pick.move_line_ids.filtered(lambda x: not x.move_id):
                # Search move with this product
                moves = pick.move_lines.filtered(lambda x: x.product_id == ops.product_id)
                moves = sorted(moves, key=lambda m: m.quantity_done < m.product_qty, reverse=True)
                if moves:
                    ops.move_id = moves[0].id
                else:
                    new_move = self.env['stock.move'].create({
                        'name': _('New Move:') + ops.product_id.display_name,
                        'product_id': ops.product_id.id,
                        'product_uom_qty': ops.qty_done,
                        'product_uom': ops.product_uom_id.id,
                        'location_id': pick.location_id.id,
                        'location_dest_id': pick.location_dest_id.id,
                        'picking_id': pick.id,
                        'picking_type_id': pick.picking_type_id.id,
                    })
                    ops.move_id = new_move.id
                    new_move._action_confirm()
                    todo_moves |= new_move
                    # 'qty_done': ops.qty_done})
        todo_moves._action_done()
        self.write({'date_done': fields.Datetime.now()})
        if self.date_done:
            for line in self.move_line_ids:
                product = line.product_id
                if product and product.tracking != 'none':
                    if line.lot_id:
                        lot_val = self.env['stock.production.lot'].search([('name', '=', line.lot_id.name),('product_id','=',line.product_id.id)])
                        if lot_val:
                            lot_date=self.date_done
                            lot_val.warranty_date =lot_date+relativedelta(months=12)

        return True

