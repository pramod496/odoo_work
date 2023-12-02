from odoo.exceptions import ValidationError, RedirectWarning, except_orm, UserError
from odoo.addons import decimal_precision as dp
from odoo import api, fields, models, _
import pdb
from odoo.exceptions import ValidationError, RedirectWarning, except_orm

class WorkOrderQuotationInherited(models.Model):
    _inherit = 'work.order.quotation'

    # @api.onchange('product_id')
    # def id_onchange(self):
    #     print(self.product_id.categ_id.name, 'category name')
    #     self.product_category_id = self.product_id.categ_id.name
    #     print(self.product_category_id, 're')

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True,
                                 default=lambda self: self.env.user.company_id)
    iwo_number = fields.Char('IWO No')



    # added my me
    product_id = fields.Many2one('product.product', String='Product')
    product_category_id = fields.Char(related='product_id.categ_id.name', string='Product Category')
    non_line_id = fields.One2many('non.line', 'non_id')
    vfs_line_id = fields.One2many('vfs.line', 'vfs_id')
    sli_line_id = fields.One2many('sli.line', 'sli_id')
    hfs_line_id = fields.One2many('hfs.line', 'hfs_id')
    mli_line_id = fields.One2many('mli.line', 'mli_id')
    excs_line_id = fields.One2many('excs.line', 'excs_id')
    gaskets=fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Gaskets')
    flange_adapter = fields.Selection([('Required', 'Required'), ('Not Required', 'Not Required')],
                                      string='Flange / Adaptor & Stem Interfacing Welding')
    connection_detail = fields.Selection([('Standard', 'Standard'), ('Independent', 'Independent')],
                                         string='Connection Detail')
    isolation_valves = fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Isolation Valves')



    float_dia = fields.Char(string='Float Dia')
    # switch_config = fields.Selection([('D1','D1'),('D2','D2'),('D3','D3'),('D4','D4'),('D5','D5'),('D6','D6')],string='Switch Config')
    flange = fields.Char('Flange')
    no_of_floats = fields.Char('No of Floats')
    flange_dimension = fields.Char(string='Flange Dimension')
    pcd = fields.Char('PCD')
    thickness = fields.Char('Thickness')
    hole_dia = fields.Char('Hole Dia')

    adapter_dimension = fields.Char('Adaptor Dimension')
    standard = fields.Char('Standard')
    lead_wire = fields.Char(string='Lead Wire')
    # partner_id = fields.Many2one(related='work_id.partner_id', string='Partner')
    # fields.Many2one(related='picking_id.picking_type_id', string='Picking Type Id', store=True)
    cls_line_id = fields.One2many('cls.line', 'cls_id')
    customer_ref = fields.Char('Customer Reference')
    # part_no = fields.Char('Part No')
    # ident_no = fields.Char('Ident No')
    application = fields.Char('Application')
    temp_pressure = fields.Char('Temp & Pressure')
    circuit = fields.Char('Circuit')
    output = fields.Char('Output')
    lead_cable = fields.Char('Lead Cable')
    flange_stem = fields.Selection([('Yes', 'Yes'), ('No', 'No')], string="Flange & Stem Interface Welding")
    adapter_standard = fields.Char('Standard(Adapter Dimension)')
    adapter_od = fields.Char('OD(Adapter Dimension)')
    micro_potting = fields.Selection(
        [('Required with Anabond', 'Required with Anabond'), ('Not Required', 'Not Required')],
        string="Micro Switch Protection(Potting)")
    magnets = fields.Selection([('ALNICO','ALNICO'),('Cobalt','Cobalt')],string='Magnets')
    # magnets = fields.Many2many('work.order.magnets',
    #                            'work_order_quotaion_line_work_order_magnets', 'work_order_id', 'magnet_id',
    #                            string='Magnets')

    flange_enclosure = fields.Selection([('Required', 'Required'), ('Not Required', 'Not Required')],
                                        string='Flange and enclosure interface welding')

    # non_total = fields.Monetary(compute='_non_compute_total', currency_field='currency_id',
    #                             digits=dp.get_precision('Account'),
    #                             string='Non Total Wt(Kg)', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id)
    # total = fields.Monetary(compute='_compute_total', currency_field='currency_id', digits=dp.get_precision('Account'),
    #                         string='Total Wt(Kg)', readonly=True, store=True)
    # cls_total = fields.Monetary(compute='_cls_compute_total', currency_field='currency_id',
    #                             digits=dp.get_precision('Account'),
    #                             string='CLS Total Wt(Kg)', readonly=True, store=True)
    # flx_total = fields.Monetary(compute='_flx_compute_total', currency_field='currency_id',
    #                             digits=dp.get_precision('Account'),
    #                             string='FLX Total Wt(Kg)', readonly=True, store=True)
    # sli_total = fields.Monetary(compute='_sli_compute_total', currency_field='currency_id',
    #                             digits=dp.get_precision('Account'),
    #                             string='SLI Total Wt(Kg)', readonly=True, store=True)
    # hfs_total = fields.Monetary(compute='_hfs_compute_total', currency_field='currency_id',
    #                             digits=dp.get_precision('Account'),
    #                             string='HFS Total Wt(Kg)', readonly=True, store=True)
    # mli_total = fields.Monetary(compute='_mli_compute_total', currency_field='currency_id',
    #                             digits=dp.get_precision('Account'),
    #                             string='MLI Total Wt(Kg)', readonly=True, store=True)
    # excs_total = fields.Monetary(compute='_excs_compute_total', currency_field='currency_id',
    #                              digits=dp.get_precision('Account'),
    #                              string='EXCS Total Wt(Kg)', readonly=True, store=True)
    flx_line_id = fields.One2many('flx.line', 'flx_id')
    satuatory = fields.Char('Statuatory & Regulatory Requirements')
    all_dimension = fields.Char('All Dimension ref.')
    other_info = fields.Char('Other Info.')
    # material_of_gaskets = fields.Selection([('Regular','Regular'),('Champion','Champion'),('Silicon','Silicon'),('Neoprene','Neoprene'),('CAF','CAF'),('spiral wound','spiral wound'),('NA','NA'),('Others','Others')],string='Material of gaskets')
    production_sl_no = fields.Many2one('stock.production.lot', 'Product Sl No')
    instrument_sl_no = fields.Char('Instrument Sl No')
    desired_delivery = fields.Date('Desired delivery')
    iwo_prepared_by = fields.Many2one('res.users', 'IWO Prepared by')
    processed_by = fields.Many2one('res.users', 'Processed By')
    verified_by = fields.Many2one('res.users', 'Verified By')
    invoice_no = fields.Char('Invoice No & Date')
    earlier_ref = fields.Char('Earlier Ref No')
    connection = fields.Text('Connection Details')
    tracking_no = fields.Char('Tracking No')
    probe_size = fields.Char('Probe Size')
    enclosure_type = fields.Char('Enclosure Type')

    note = fields.Char('Note')
    od = fields.Char('OD')

    chamber_design_top = fields.Char('Chamber Design for top')
    chamber_design_bottom = fields.Char('Chamber Design for bottom')
    process_flange_details = fields.Char(string='Process Flange Details')
    process_thread_details = fields.Char(string='Process Thread Details')
    indication_type = fields.Char('Indication Type')
    vent_size = fields.Char(string='Vent Size')
    fasteners = fields.Selection([('Required', 'Required'), ('Not Required', 'Not Required')], string='Fasteners')
    fasteners_moc = fields.Char(string='Fasteners MOC')
    drain_size = fields.Char(string='Drain Size')
    special_features = fields.Char('Special Features')
    testing_options = fields.Selection([('Hydrostatic Pressure Test','Hydrostatic Pressure Test'),('Dye-Penetration Test','Dye-Penetration Test'),('Radiography','Radiography'),('Others','Others')],string='Testing Options')
    # testing_options = fields.Many2many('work.order.testing.options',
    #                                    'work_order_quotaion_line_work_order_testing_options', 'work_order_id',
    #                                    'testing_options_id',
    #                                    string='Testing Options')
    float_dimension = fields.Char(string='Float Dimension')
    size = fields.Char('Size')

    other_spec = fields.Char('Other Specification/Requirement')
    approval_cert = fields.Selection([('DP','DP'),('RT L1/L2','RT L1/L2'),('HP','HP'),('UT','UT'),('PWHT','PWHT'),('MPT','MPT'),('NACE MR 0175 Compliance','NACE MR 0175 Compliance'),('ABS','ABS'),('ATEX','ATEX'),('PED','PED'),('PED 97/23/EC Certification','PED 97/23/EC Certification'),('IBR','IBR'),('EN 10204 3.1 Certificate','EN 10204 3.1 Certificate'),('3.1 Material Certificate','3.1 Material Certificate'),('Others','Others')], string='Approvals/Cert')
    # approval_cert = fields.Many2many('work.order.approval.cert',
    #                                  'work_order_quotaion_line_work_order_approval_cert', 'work_order_id',
    #                                  'approval_cert_id',
    #                                  string='Approvals/Cert')
    remarks = fields.Text(string="Remarks")
    tag_no = fields.Char(string="Tag No")
    sale_line_id = fields.Many2one('sale.order.line')
    desired_delivery_date = fields.Datetime(string='Desired Delivery Date',
                                            related='sale_line_id.desired_delivery_date', store=True, editable=True)
    drawing_no = fields.Char("Drawing No")
    moc = fields.Many2one('moc', string="MOC")
    stem_moc = fields.Many2one('stem.moc', string="Stem MOC")
    float_moc = fields.Many2one('float.moc', string="Float MOC")
    flange_moc = fields.Many2one('flange.moc', string="Flange MOC")
    fasteners_moc = fields.Many2one('fasteners.moc', string="Fasteners MOC")
    adaptor_moc = fields.Many2one('adaptor.moc', string="Adaptor MOC")
    gasket_moc = fields.Many2one('gasket.moc', string="Gasket MOC")
    chamber_moc = fields.Many2one('chamber.moc', string="Chamber MOC")
    stem_dia = fields.Many2one('stem.dia', string="Stem Dia")
    wetted_moc = fields.Many2one('wetted.moc', string="All Wetted Parts MOC")
    packing_details = fields.Many2one('packing.details', string="Packing Details")
    mount_type = fields.Many2one('mount.type', string="Mount Type")
    connection_type = fields.Many2one('connection.type', string="Connection Type")
    connector = fields.Many2one('connector', string="Connector")
    connector_vfs = fields.Many2one('connector.vfs', string="Connector")
    connector_flx = fields.Many2one('connector.flx', string="Connector")
    enclosure = fields.Many2one('enclosure', string="Enclosure")
    insulation = fields.Many2one('insulation', string="Insulation Sleeving")
    vent = fields.Many2one('vent', string="Vent")
    drain = fields.Many2one('drain', string="Drain")
    potting = fields.Many2one('potting', string="Potting")
    magnetic_switches = fields.Many2one('magnetic.switches', string="Magnetic Switches")
    level_transmitter = fields.Many2one('level.transmitter', string="Level Transmitter")
    chamber_flange_type = fields.Many2one('chamber.flange.type', string="Chamber Flange Type")
    process_pipe_size = fields.Many2one('process.pipe.size', string="Process Conn. Pipe Size")
    process_connection = fields.Many2one('process.connection', string="Process Connection")
    process_flange_rating = fields.Many2one('process.flange.rating', string="Process Flange Rating")



class WorkOrderQuotationLineInherited(models.Model):
    _inherit = 'work.order.quotation.line'

    @api.depends('vfs_line_id')
    def _compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.vfs_line_id:

                qty = qty+el.quantity
            line.update({
                'total': qty,

            })

    @api.depends('cls_line_id')
    def _cls_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.cls_line_id:
                qty = qty + el.quantity
            line.update({
                'cls_total': qty,

            })
    @api.depends('non_line_id')
    def _non_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.cls_line_id:
                qty = qty + el.quantity
            line.update({
                'non_total': qty,

            })
    @api.depends('flx_line_id')
    def _flx_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:

            qty = 0
            for el in line.flx_line_id:
                qty = qty + el.quantity
            line.update({
                'flx_total': qty,

            })

    @api.depends('sli_line_id')
    def _sli_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.sli_line_id:
                qty = qty + el.quantity
            line.update({
                'sli_total': qty,

            })

    @api.depends('hfs_line_id')
    def _hfs_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.hfs_line_id:
                qty = qty + el.quantity
            line.update({
                'hfs_total': qty,

            })

    @api.depends('mli_line_id')
    def _mli_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.mli_line_id:
                qty = qty + el.quantity
            line.update({
                'mli_total': qty,

            })

    @api.depends('excs_line_id')
    def _excs_compute_total(self):
        """
        Compute the amounts of the Bom line.
        """
        for line in self:
            qty = 0
            for el in line.excs_line_id:
                qty = qty + el.quantity
            line.update({
                'excs_total': qty,

            })

    @api.onchange('total')
    def onchange_total(self):
        if not self.total or self.cls_total:
            return {}
        if self.total>0:
            if self.total>self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))

    @api.onchange('cls_total')
    def onchange_cls_total(self):
        if not self.cls_total:
            return {}
        if self.cls_total>0:
            if self.cls_total>self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))

    @api.onchange('flx_total')
    def onchange_flx_total(self):
        if not self.flx_total:
            return {}
        if self.flx_total > 0:
            if self.flx_total > self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))

    @api.onchange('sli_total')
    def onchange_sli_total(self):
        if not self.sli_total:
            return {}
        if self.sli_total > 0:
            if self.sli_total > self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))
    @api.onchange('non_total')
    def onchange_non_total(self):
        if not self.non_total:
            return {}
        if self.non_total>0:
            if self.non_total>self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))

    @api.onchange('hfs_total')
    def onchange_hfs_total(self):
        if not self.hfs_total:
            return {}
        if self.hfs_total > 0:
            if self.hfs_total > self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))

    @api.onchange('mli_total')
    def onchange_mli_total(self):
        if not self.mli_total:
            return {}
        if self.mli_total > 0:
            if self.mli_total > self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))

    @api.onchange('excs_total')
    def onchange_excs_total(self):
        if not self.excs_total:
            return {}
        if self.excs_total > 0:
            if self.excs_total > self.product_uom_qty:
                raise ValidationError(_('The Quantity in connection details is exceded than the Produced Quantity'))


    def get_serial_numbers(self):
        serial_numbers = ''
        if self.work_id:
            lots = self.env['stock.production.lot'].sudo().search([('so_id','=',self.work_id.sale_id.id),('product_id','=',self.product_id.id)])
            if lots:
                lotids = []
                for lot in lots:
                    lotids.append(lot.id)
                sortedlist = lotids.sort()
                s_lot = lotids[0]
                e_lot = lotids[-1]
                starting_lot = self.env['stock.production.lot'].sudo().search([('id','=',s_lot)])
                ending_lot = self.env['stock.production.lot'].sudo().search([('id','=',e_lot)])
                serial_numbers = str(starting_lot.name) +'  '+ '-' +'  '+str(ending_lot.name)
        return serial_numbers

    def get_magnets(self):
        magnets_val=[]
        if self.magnets:
            for el in self.magnets:
                magnets_val.append(el.name)
        return magnets_val


    def get_testing_options(self):
        testing_options_val=[]
        if self.testing_options:
            for el in self.testing_options:
                testing_options_val.append(el.name)
        return ', '.join(testing_options_val)


    def get_approval_cert(self):
        approval_cert_val=[]
        if self.approval_cert:
            for el in self.approval_cert:
                approval_cert_val.append(el.name)
        return ', '.join(approval_cert_val)

    @api.onchange('product_id')
    def id_onchange(self):
        self.product_category_id = self.product_id.categ_id.name



    product_category_id =fields.Char(related='product_id.categ_id.name', string='Product Category')
    non_line_id = fields.One2many('non.line','non_id')
    vfs_line_id = fields.One2many('vfs.line','vfs_id')
    sli_line_id = fields.One2many('sli.line' , 'sli_id')
    hfs_line_id = fields.One2many('hfs.line','hfs_id')
    mli_line_id = fields.One2many('mli.line', 'mli_id')
    excs_line_id = fields.One2many('excs.line', 'excs_id')

    float_dia = fields.Char(string='Float Dia')
    #switch_config = fields.Selection([('D1','D1'),('D2','D2'),('D3','D3'),('D4','D4'),('D5','D5'),('D6','D6')],string='Switch Config')
    flange = fields.Char('Flange')
    no_of_floats = fields.Char('No of Floats')
    flange_dimension =fields.Char(string='Flange Dimension')
    pcd = fields.Char('PCD')
    thickness = fields.Char('Thickness')
    hole_dia = fields.Char('Hole Dia')
    
    adapter_dimension = fields.Char('Adaptor Dimension')
    standard = fields.Char('Standard')
    lead_wire = fields.Char(string='Lead Wire')
    partner_id = fields.Many2one(related='work_id.partner_id',string='Partner')
    # fields.Many2one(related='picking_id.picking_type_id', string='Picking Type Id', store=True)
    cls_line_id =fields.One2many('cls.line','cls_id')
    customer_ref = fields.Char('Customer Reference')
    #part_no = fields.Char('Part No')
    #ident_no = fields.Char('Ident No')
    application = fields.Char('Application')
    temp_pressure = fields.Char('Temp & Pressure')
    circuit = fields.Char('Circuit')
    output = fields.Char('Output')
    lead_cable = fields.Char('Lead Cable')
    flange_stem = fields.Selection([('Yes','Yes'),('No','No')],string="Flange & Stem Interface Welding")
    adapter_standard=fields.Char('Standard(Adapter Dimension)')
    adapter_od=fields.Char('OD(Adapter Dimension)')
    micro_potting =fields.Selection([('Required with Anabond','Required with Anabond'),('Not Required','Not Required')],string="Micro Switch Protection(Potting)")
    # magnets = fields.Selection([('ALNICO','ALNICO'),('Cobalt','Cobalt')],string='Magnets')
    magnets = fields.Many2many('work.order.magnets',
        'work_order_quotaion_line_work_order_magnets', 'work_order_id', 'magnet_id',
        string='Magnets')

    flange_enclosure = fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Flange and enclosure interface welding')

    non_total = fields.Monetary(compute='_non_compute_total', currency_field='currency_id',
                                digits=dp.get_precision('Account'),
                                string='Non Total Wt(Kg)', readonly=True, store=True)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True,
                                  states={'draft': [('readonly', False)], 'refused': [('readonly', False)]},
                                  default=lambda self: self.env.user.company_id.currency_id)
    total = fields.Monetary(compute='_compute_total', currency_field='currency_id', digits=dp.get_precision('Account'),
                            string='Total Wt(Kg)', readonly=True, store=True)
    cls_total = fields.Monetary(compute='_cls_compute_total', currency_field='currency_id', digits=dp.get_precision('Account'),
                            string='CLS Total Wt(Kg)', readonly=True, store=True)
    flx_total = fields.Monetary(compute='_flx_compute_total', currency_field='currency_id',
                                digits=dp.get_precision('Account'),
                                string='FLX Total Wt(Kg)', readonly=True, store=True)
    sli_total = fields.Monetary(compute='_sli_compute_total', currency_field='currency_id',
                                digits=dp.get_precision('Account'),
                                string='SLI Total Wt(Kg)', readonly=True, store=True)
    hfs_total = fields.Monetary(compute='_hfs_compute_total', currency_field='currency_id',
                                digits=dp.get_precision('Account'),
                                string='HFS Total Wt(Kg)', readonly=True, store=True)
    mli_total = fields.Monetary(compute='_mli_compute_total', currency_field='currency_id',
                                digits=dp.get_precision('Account'),
                                string='MLI Total Wt(Kg)', readonly=True, store=True)
    excs_total = fields.Monetary(compute='_excs_compute_total', currency_field='currency_id',
                                digits=dp.get_precision('Account'),
                                string='EXCS Total Wt(Kg)', readonly=True, store=True)
    flx_line_id = fields.One2many('flx.line', 'flx_id')
    satuatory=fields.Char('Statuatory & Regulatory Requirements')
    all_dimension =fields.Char('All Dimension ref.')
    other_info =fields.Char('Other Info.')
    #material_of_gaskets = fields.Selection([('Regular','Regular'),('Champion','Champion'),('Silicon','Silicon'),('Neoprene','Neoprene'),('CAF','CAF'),('spiral wound','spiral wound'),('NA','NA'),('Others','Others')],string='Material of gaskets')
    production_sl_no =fields.Many2one('stock.production.lot','Product Sl No')
    instrument_sl_no = fields.Char('Instrument Sl No')
    desired_delivery =fields.Date('Desired delivery')
    iwo_prepared_by =fields.Many2one('res.users','IWO Prepared by')
    processed_by = fields.Many2one('res.users','Processed By')
    verified_by=fields.Many2one('res.users','Verified By')
    invoice_no = fields.Char('Invoice No & Date')
    earlier_ref = fields.Char('Earlier Ref No')
    connection=fields.Text('Connection Details')
    tracking_no =fields.Char('Tracking No')
    probe_size = fields.Char('Probe Size')
    enclosure_type = fields.Char('Enclosure Type')

    note=fields.Char('Note')
    od = fields.Char('OD')


    chamber_design_top = fields.Char('Chamber Design for top')
    chamber_design_bottom = fields.Char('Chamber Design for bottom')
    process_flange_details = fields.Char(string='Process Flange Details')
    process_thread_details = fields.Char(string='Process Thread Details')
    indication_type = fields.Char('Indication Type')
    vent_size = fields.Char(string='Vent Size')
    fasteners = fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Fasteners')
    fasteners_moc = fields.Char(string='Fasteners MOC')    
    drain_size=fields.Char(string='Drain Size')
    special_features=fields.Char('Special Features')
    # testing_options = fields.Selection([('Hydrostatic Pressure Test','Hydrostatic Pressure Test'),('Dye-Penetration Test','Dye-Penetration Test'),('Radiography','Radiography'),('Others','Others')],string='Testing Options')
    testing_options = fields.Many2many('work.order.testing.options',
                               'work_order_quotaion_line_work_order_testing_options', 'work_order_id', 'testing_options_id',
                               string='Testing Options')
    float_dimension = fields.Char(string='Float Dimension')
    size = fields.Char('Size')

    other_spec = fields.Char('Other Specification/Requirement')
    # approval_cert = fields.Selection([('DP','DP'),('RT L1/L2','RT L1/L2'),('HP','HP'),('UT','UT'),('PWHT','PWHT'),('MPT','MPT'),('NACE MR 0175 Compliance','NACE MR 0175 Compliance'),('ABS','ABS'),('ATEX','ATEX'),('PED','PED'),('PED 97/23/EC Certification','PED 97/23/EC Certification'),('IBR','IBR'),('EN 10204 3.1 Certificate','EN 10204 3.1 Certificate'),('3.1 Material Certificate','3.1 Material Certificate'),('Others','Others')], string='Approvals/Cert')
    approval_cert = fields.Many2many('work.order.approval.cert',
                                       'work_order_quotaion_line_work_order_approval_cert', 'work_order_id',
                                       'approval_cert_id',
                                       string='Approvals/Cert')
    remarks=fields.Text(string="Remarks")
    tag_no=fields.Char(string="Tag No")
    sale_line_id = fields.Many2one('sale.order.line')
    desired_delivery_date = fields.Datetime(string='Desired Delivery Date',related='sale_line_id.desired_delivery_date',store=True,editable=True)
    drawing_no = fields.Char("Drawing No")

    # Selection Fields

    # stem_moc = fields.Selection([('SS304','SS304'),('SS316L','SS316L'),('PP','PP'),('SS316','SS316'),('Brass','Brass'),('CPVC','CPVC')], string='Stem MOC')
    # stem_dia = fields.Selection([('8mm','8mm'),('12.7mm','12.7mm'),('16mm','16mm')],string='Stem Dia')
    # float_moc_vfs = fields.Selection([('SS304','SS304'),('SS316L','SS316L'),('PP','PP'),('SS316','SS316'),('PU Foam','PU Foam'),('ABS','ABS')],string='Float MOC')
    # float_moc_hfs = fields.Selection([('SS304','SS304'),('SS316L','SS316L'),('PP','PP'),('SS316','SS316')],string='Float MOC')
    # connection_type = fields.Selection([('Flange', 'Flange'),('Adaptor', 'Adaptor')], string='Connection Type')
    # flange_moc_vfs = fields.Selection([('SS304','SS304'),('SS316L','SS316L'),('MS','MS'),('Alu','Alu'),('SS316','SS316')],string='Flange Moc')
    # flange_moc_hfs = fields.Selection([('SS304','SS304'),('SS316','SS316'),('SS316L','SS316L'),('PP','PP')],string='Flange Moc')
    # flange_moc_sli = fields.Selection([('SS304','SS304'),('MS','MS'),('Alu','Alu'),('PVC','PVC')],string='Flange Moc')
    # flange_moc = fields.Selection([('SS304','SS304'),('SS316L','SS316L'),('MS','MS'),('Alu','Alu'),('SS316','SS316'),('PP','PP'),('PVC','PVC')],string='Flange Moc')
    # adapt_moc = fields.Selection([('SS304','SS304'),('SS316L','SS316L'),('MS','MS'),('Alu','Alu'),('SS316','SS316')],string='Adaptor Moc')
    # connector_vfs = fields.Selection([('NA','NA'),('Din Connector','Din Connector'),('TC Head Regular Blk','TC Head Regular Blk'),('TC Head SS304 regular IP 67','TC Head SS304 regular IP 67'),('TC Head SS304 Special','TC Head SS304 Special'),('TC Head IP 66 Ex. Proof AL type','TC Head IP 66 Ex. Proof AL type'),('Weather Proof IP 65-4','Weather Proof IP 65-4'),('weather Proof IP 65-8','Weather Proof IP 65-8'),('AL Junction Box-4','AL Junction Box-4'),('AL Junction Box-8','AL Junction Box-8'),('PP Enclosure','PP Enclosure'),('Polycarbonate Enclosure','Polycarbonate Enclosure')], string='Connector')
    # connector_flx = fields.Selection([('NA','NA'),('Din Connector','Din Connector'),('TC Head Regular Blk','TC Head Regular Blk'),('TC Head SS304 regular IP 67','TC Head SS304 regular IP 67'),('TC Head SS304 Special','TC Head SS304 Special'),('TC Head IP 66 Ex. Proof AL type','TC Head IP 66 Ex. Proof AL type'),('Weather Proof IP 65-4','Weather Proof IP 65-4'),('weather Proof IP 65-8','Weather Proof IP 65-8'),('AL Junction Box-4','AL Junction Box-4'),('AL Junction Box-8','AL Junction Box-8'),('PP Enclosure','PP Enclosure'),('Polycarbonate Enclosure','Polycarbonate Enclosure')], string='Connector')
    # potting = fields.Selection([('Epoxy','Epoxy'),('Anabond','Anabond'),('T.P.','T.P.'),('Fast curing Epoxy','Fast curing Epoxy'),('Gun Epoxy','Gun Epoxy'),('Others','Others')],string='Potting')
    # connector =fields.Selection([('Standard','Standard'),('Independent','Independent')],string="Connector")
    # moc=fields.Selection([('SS304','SS304'),('SS316','SS316'),('SS316L','SS316L'),('PP','PP'),('Monel','Monel'),('Hastelloy','Hastelloy'),('Inconel','Inconel'),('Titanium','Titanium'),('PVDF','PVDF'),('PTFE','PTFE'),('SS316+PTFE','SS316+PTFE')],string='MOC')
    gaskets=fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Gaskets')
    # gasket_moc=fields.Selection([('Regular','Regular'),('Spiral Wound','Spiral Wound'),('PTFE','PTFE'),('Champion','Champion'),('Silicon','Silicon'),('Neoprene','Neoprene'),('O ring','O Ring'),('NA','NA'),('Others','Others')],string='Gasket MOC')
    flange_adapter=fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Flange / Adaptor & Stem Interfacing Welding')
    connection_detail=fields.Selection([('Standard','Standard'),('Independent','Independent')],string='Connection Detail')
    # packing_details =fields.Selection([('Carton Box','Carton Box'),('Plywood Box','Plywood box'),('Corrugated Box','Corrugated Box'),('Bubble Sheet','Bubble Sheet')],stirng='Packing Details')
    # mount_type=fields.Selection([('top','top'),('side','side')],string='Mounting Type')
    # all_wetted_moc = fields.Selection([('SS304','SS304'),('SS316','SS316'),('SS316L','SS316L')],string='All Wetted parts MOC')
    # magnetic_switches = fields.Selection([('NA','NA'),('Reed Switch','Reed Switch'),('Micro Switch','Micro Switch')],string='Magnetic Switches')
    # level_transmitter = fields.Selection([('Reed chain level Tx','Reed chain level Tx'),('magnetostrictive level Tx.','magnetostrictive level Tx.'),('NA','NA')],string='Level Transmitter')
    isolation_valves = fields.Selection([('Required','Required'),('Not Required','Not Required')],string='Isolation Valves')
    # vent = fields.Selection([('Threaded','Threaded'),('Flange','Flange'),('valve','valve')],string='Vent')
    # enclosure = fields.Selection([('Weather Proof/Al','Weather Proof/Al'),('Din','Din'),('Flameproof Gr. IIA & IIB/SS304','Flameproof Gr. IIA & IIB/SS304'),('Flameproof Gr. IIC','Flameproof Gr. IIC'),('PP','PP'),('without approval','without approval'),('Teflon','Teflon'),('AL J/B 4','AL J/B 4')],string='Enclosure')
    # poting = fields.Selection([('Epoxy','Epoxy'),('Anabond','Anabond'),('T.P.','T.P.'),('Fast curing Epoxy','Fast curing Epoxy'),('Gun Epoxy','Gun Epoxy'),('Others','Others')],string='Potting')
    cls_flange =fields.Selection([('Yes','Yes'),('No','No')],string='Flange / Adaptor & Stem Interfacing Welding')
    # insulation = fields.Selection([('PVC','PVC'),('PTFE','PTFE')],string='Insulation Sleeving')
    # drain = fields.Selection([('Threaded','Threaded'),('Flange','Flange'),('valve','valve')],string='Drain')
    # chamber_moc = fields.Selection([('SS304','SS304'),('SS316','SS316'),('SS316L','SS316L'),('CS','CS'),('Others','Others')],string='Chamber MOC')
    # chamber_flange_type = fields.Selection([('SORF','SORF'),('WNRF','WNRF'),('RTJ','RTJ'),('BLRF','BLRF'),('others','others')],string='Chamber Flange Type')
    # process_pipe_size = fields.Selection([('1/2"','1/2"'),('others','others')],string='Process Conn. Pipe Size')
    # process_connection = fields.Selection([('Flange','Flange'),('Adaptor','Adaptor'),('Threaded','Threaded'),('Socket Weld','Socket Weld')],string='Process Connection')
    # process_flange_rating = fields.Selection([('150#','150#'),('300#','300#'),('600#','600#'),('900#','900#'),('others','others')],string='Process Conn. Flange Rating')

    # New Fields

    moc = fields.Many2one('moc', string="MOC")
    stem_moc = fields.Many2one('stem.moc', string="Stem MOC")
    float_moc = fields.Many2one('float.moc', string="Float MOC")
    flange_moc = fields.Many2one('flange.moc', string="Flange MOC")
    fasteners_moc = fields.Many2one('fasteners.moc', string="Fasteners MOC")
    adaptor_moc = fields.Many2one('adaptor.moc', string="Adaptor MOC")
    gasket_moc = fields.Many2one('gasket.moc', string="Gasket MOC")
    chamber_moc = fields.Many2one('chamber.moc', string="Chamber MOC")
    stem_dia = fields.Many2one('stem.dia', string="Stem Dia")
    wetted_moc = fields.Many2one('wetted.moc', string="All Wetted Parts MOC")
    packing_details = fields.Many2one('packing.details', string="Packing Details")
    mount_type = fields.Many2one('mount.type', string="Mount Type")
    connection_type = fields.Many2one('connection.type', string="Connection Type")
    connector = fields.Many2one('connector', string="Connector")
    connector_vfs = fields.Many2one('connector.vfs', string="Connector")
    connector_flx = fields.Many2one('connector.flx', string="Connector")
    enclosure = fields.Many2one('enclosure', string="Enclosure")
    insulation = fields.Many2one('insulation', string="Insulation Sleeving")
    vent = fields.Many2one('vent', string="Vent")
    drain = fields.Many2one('drain', string="Drain")
    potting = fields.Many2one('potting', string="Potting")
    magnetic_switches = fields.Many2one('magnetic.switches', string="Magnetic Switches")
    level_transmitter = fields.Many2one('level.transmitter', string="Level Transmitter")
    chamber_flange_type = fields.Many2one('chamber.flange.type', string="Chamber Flange Type")
    process_pipe_size = fields.Many2one('process.pipe.size', string="Process Conn. Pipe Size")
    process_connection = fields.Many2one('process.connection', string="Process Connection")
    process_flange_rating = fields.Many2one('process.flange.rating', string="Process Flange Rating")




class WorkOrderMagnets(models.Model):
    _name='work.order.magnets'

    name = fields.Char('Name')
    magnet_id = fields.Many2one('work.order.quotation.line', "Magnet Name",invisible="1")


class WorkOrderTestingOptions(models.Model):
    _name='work.order.testing.options'

    name = fields.Char('Name')
    testing_options_id = fields.Many2one('work.order.quotation.line', "Testing Options",invisible="1")

class WorkOrderApprovalCert(models.Model):
    _name='work.order.approval.cert'

    name = fields.Char('Name')
    approval_cert_id = fields.Many2one('work.order.quotation.line', "Approvals/Cert",invisible="1")

class vfsLine(models.Model):
    _name='vfs.line'

    vfs_id = fields.Many2one('work.order.quotation.line')
    l =fields.Integer('L')
    d1 = fields.Integer('D1')
    d1_state = fields.Selection([
        ('R', 'R'),
        ('F', 'F'),
    ], string='State', readonly=False, index=True, copy=False, track_visibility='onchange')

    d2=fields.Integer('D2')
    d2_state = fields.Selection([
        ('R', 'R'),
        ('F', 'F'),
    ], string='State', readonly=False, index=True, copy=False, track_visibility='onchange')

    d3 = fields.Integer('D3')
    d3_state = fields.Selection([
        ('R', 'R'),
        ('F', 'F'),
    ], string='State', readonly=False, index=True, copy=False, track_visibility='onchange')

    d4=fields.Integer('D4')
    d4_state = fields.Selection([
        ('R', 'R'),
        ('F', 'F'),
    ], string='State', readonly=False, index=True, copy=False, track_visibility='onchange')

    d5=fields.Integer('D5')
    d5_state = fields.Selection([
        ('R', 'R'),
        ('F', 'F'),
    ], string='State', readonly=False, index=True, copy=False, track_visibility='onchange')

    d6=fields.Integer('D6')
    d6_state = fields.Selection([
        ('R', 'R'),
        ('F', 'F'),
    ], string='State', readonly=False, index=True, copy=False, track_visibility='onchange')

    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')
class NonLine(models.Model):
    _name='non.line'

    non_id = fields.Many2one('work.order.quotation.line')
    
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')
class ClsLine(models.Model):
    _name='cls.line'

    cls_id = fields.Many2one('work.order.quotation.line')
    l =fields.Integer('L')
    d1 = fields.Integer('D1')
    d2=fields.Integer('D2')
    d3 = fields.Integer('D3')
    d4=fields.Integer('D4')
    d5=fields.Integer('D5')
    d6=fields.Integer('D6')
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')

class FlxLine(models.Model):
    _name='flx.line'

    flx_id = fields.Many2one('work.order.quotation.line')
    gsl = fields.Char('Guided Stem Length(GSL)')
    mr = fields.Char('Measuring range(MR)')
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')

class SliLine(models.Model):
    _name='sli.line'

    sli_id = fields.Many2one('work.order.quotation.line')
    description = fields.Text('Description')
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')

class HfsLine(models.Model):
    _name='hfs.line'

    hfs_id = fields.Many2one('work.order.quotation.line')
    description = fields.Text('Description')
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')

class MliLine(models.Model):
    _name='mli.line'

    mli_id = fields.Many2one('work.order.quotation.line')
    ccdistance = fields.Char('C-C Distance')
    total_length = fields.Char('Total Length')
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')
    tag_no1=fields.Char(string="Tag No")


class ExcsLine(models.Model):
    _name='excs.line'

    excs_id = fields.Many2one('work.order.quotation.line')
    ccdistance = fields.Char('C-C Distance')
    total_length = fields.Char('Total Length')
    quantity=fields.Integer('Quantity')
    product_uom_id = fields.Many2one('uom.uom','UOM')
    tag_no1=fields.Char(string="Tag No")


class ResCompanyFields(models.Model):
    _inherit = 'res.company'

    doc_num_vfs = fields.Char(string="Doc Number for VFS")

    doc_num_cls = fields.Char(string="Doc Number for CLS")

    doc_num_flx = fields.Char(string="Doc Number for FLX")

    doc_num_sli = fields.Char(string="Doc Number for SLI")

    doc_num_hfs = fields.Char(string="Doc Number for HFS")

    doc_num_mli = fields.Char(string="Doc Number for MLI")

    doc_num_excs = fields.Char(string="Doc Number for EXCS")

    doc_num_noncateg= fields.Char(string="Doc Number for Noncategory")

    doc_num_rigs = fields.Char(string="Doc Number for Skid Mounted Test Rigs")

    doc_num_qtn = fields.Char(string="Doc Number for Quatation")

    doc_num_so = fields.Char(string="Doc Number for SO")

    doc_num_po = fields.Char(string="Doc Number for PO")

    doc_num_bom = fields.Char(string="Doc Number for Bill Of Material-Unit 1&2")

    doc_num_inv = fields.Char(string="Doc Number for Invoice")

    doc_num_bill = fields.Char(string="Doc Number for Bill")

    doc_num_grir = fields.Char(string="Doc Number for GRIR")

    doc_num_inspection = fields.Char(string="Doc Number for Inspection")

    doc_num_production_plan = fields.Char(string="Doc Number for Production Plan (Unit 2)")

    doc_num_cgr = fields.Char(string="Doc Number for CUSTOMER GOODS RECEIPT FORM-Diaphragm Seals")

    doc_num_diaphragm = fields.Char(string="Doc Number for Diaphragm Seal Production Report")

    doc_num_fill = fields.Char(string="Doc Number for Filling and Calibration Report")

