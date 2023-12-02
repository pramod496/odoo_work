# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import os
import re
import json
from datetime import datetime
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError
import openerp.addons.decimal_precision as dp
from odoo.exceptions import UserError
import pdb
from odoo.tools.float_utils import float_compare
import collections

class Grnn(models.Model):
    _inherit = 'stock.move'

   
    total_val = fields.Integer("Total Value")
class AccountInvoiceInherited(models.Model):
    _inherit = "stock.picking"

   # hsCode = fields.Char(string="hsCode")
    
    vehicleNo = fields.Char(string="vehicleNo")
    vehicletype=fields.Char(string="vehicleType")
    transMOde = fields.Char(string="transMode")

    transporterName = fields.Char(string="transporterName")

    transDocDate = fields.Date(string="transDocDate")

    total_val = fields.Integer("Total Value")

  #  documentDate = fields.Datetime(string="documentDate")

    transDocNo = fields.Char(string="transDocNo")

    transporterId = fields.Char(string="transporterId")

    transDistance = fields.Char(string="transDistance")

    
    
    #l10n_in_hsn_code = fields.Char('product.product',string="hsnCode")
    
    def jscall(self, **kwargs):

        # for j in self.tax_line_ids:

        # pdb.set_trace()

        ##file_list=[]
        ##with open('data.txt', 'w') as f:
        ##json.dump(data, f, ensure_ascii=False)
        s = self.name
        lists=s.split('/')
        bill_list = []
        bill_list1 = []
        count = 0
        for line in self.move_ids_without_package:
            dict_data = {}

            item_list = []
            # pdb.set_trace()
            

                # print(ori)
                # f.close()
                # if tax_num.name == self.env['account.move.tax'].search([('name','=',str(tax_num.name)),('invoice_id','=',self.id)]).name:
                # pdb.set_trace()

               
                    # if str(tax_num.name) == 'SGST' or 'CGST':
            item_dict = {"itemNo": 1, "productName": line.product_id.name, "productDesc": line.product_id.name,
                                 #"hsnCode": line.product_id.product_hsn_code, 
                                 "quantity": line.product_uom_qty,
                                 "qtyUnit": " ", "taxableAmount":line.total_val,
                                 "sgstRate": 0.0, "cgstRate": 0.0,
                                 "igstRate": 0.0, "cessRate": 0.0}
            item_list.append(item_dict)
            if not self.transDocDate:
                raise UserError(_(
                            'Please Eway-Bill Details'))
            dict_data = {"userGSTIN": self.company_id.vat,
                                 "supplyType": "O",
                                 "subSupplyType": 1,
                                 "docType": "INV",
                                 "transType": 1,
                                 "docNo": self.name,
                                 "docDate": datetime.strptime(str(self.scheduled_date),'%Y-%m-%d %H:%M:%S').strftime('%d-%m-%Y'),
                                 "fromGstin": self.company_id.vat,
                                 "fromTrdName": self.company_id.name,
                                 "fromAddr1": self.company_id.street,
                                 "fromAddr2": " ",
                                 "fromStateCode": self.company_id.state_id.code,
                                 "actualFromStateCode": self.company_id.state_id.code,
                                 "fromPlace": self.company_id.city,
                                 "fromPinCode": self.company_id.zip,
                                 "toGstin": self.partner_id.vat,
                                 "sgstValue": 0.0,
                                 "cgstValue": 0.0,
                                 "igstValue": 0.0,
                                 "itemList": item_list,
                                 "cessValue": 0.0, "toTrdName": self.partner_id.name, "vehicleNo": self.vehicleNo,
                                 "transMode":self.transMOde, "transDistance": self.transDistance,
                                 "transporterName": self.transporterName, "transporterId": self.transporterId,
                                 "transDocNo": " ",
                                 "transDocDate": datetime.strptime(str(self.transDocDate),'%Y-%m-%d').strftime('%d/%m/%Y'),
                                 "toAddr1": self.partner_id.street, "toAddr2": " ",
                                 "toStateCode": self.partner_id.state_id.code,
                                 "actualToStateCode": self.partner_id.state_id.code, "totalValue":line.total_val,
                                 "totInvValue": line.total_val, "toPlace": self.partner_id.city,
                                 "toPinCode": self.partner_id.zip, "vehicleType": self.vehicletype,
                                 #"mainHsnCode": line.product_id.product_hsn_code
                                 }
            bill_list.append(dict_data)
                    # elif tax_num.name == self.env['account.move.tax'].search([('name','=',str(tax_num.name)),('invoice_id','=',self.id)]).name:
        

        d = {"version": "1.0.1118", "billLists": bill_list}
        
#         path = "./custom/addons/dc_ewaybilll/Bills"
        path = "/opt/odoo/custom/addons/dc_ewaybilll/Bills"
        fobj = open(path + lists[2] + ".json", 'w')

    # fobj = open(s,'w')
        fobj.write('\n')
        jsdata = json.dump(d, fobj, indent=4, sort_keys=True)

        fobj.close()

        return {
            'type': 'ir.actions.act_url',
            'url': '/controller/' + lists[2],
            'target': 'new',
        }


