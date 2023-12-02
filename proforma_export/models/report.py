from odoo import models, fields, api,_
import pdb
from odoo.exceptions import UserError
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
# from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

class ReportMyReport(models.AbstractModel):
    _name = 'report.proforma_export.report_proforma_export'


    
    def _get_report_values(self, docids, data=None):
        docs = self.env['account.move'].browse(docids)
        sale_id = self.env['sale.order'].search([('name','=', docs.name)])                    
        lot_id = self.env['stock.picking'].search([('name','=',docs.name)])
        ori_id = self.env['sale.order'].search([('name','=',docs.name)]) 
                
        hsn = []
        hsn_list = []
        tax_type = ""
        for i in docs:
            if len(i.invoice_line_ids) == 0:
                raise UserError(_('No Invoice Lines'))
            for j in i.invoice_line_ids:
                if j.hsn_code in hsn:
                    for l in hsn_list:
                        if l['hsn_code'] == j.hsn_code:
                            if tax_type == "state":
                                for k in j.tax_ids:
                                    l['total_taxable_amount'] += j.tax_base_amount
                                    l['taxable_value'] += j.price_subtotal
                                    l['tax_amount_sgst'] = l['total_taxable_amount']/2
                                    l['tax_amount_cgst'] = l['total_taxable_amount']/2
                            elif tax_type == "integ":
                                l['total_taxable_amount'] += j.tax_base_amount
                                l['tax_amount_igst'] += j.tax_base_amount
                                l['taxable_value'] += j.price_subtotal
                            else :
                                raise UserError(_('Neither Integrated nor State Taxes'))
                else:
                    tax_rate_igst=0.0
                    tax_rate_cgst=0.0
                    tax_rate_sgst=0.0
                    hsn.append(j.hsn_code)
                    tax_p = 0
                    for k in j.tax_ids:
                        if tax_type == "":
                            if "cgst" in k.name.lower() or "sgst" in k.name.lower():
                                tax_type = "state"
                            elif "igst" in k.name.lower():
                                tax_type = "integ"
                        if tax_type == "state":
                            if "igst" in k.name.lower():
                                raise UserError(_('Mix of Integrated and State Taxes'))
                            else:
                                if "cgst" in k.name.lower():
                                    tax_rate_cgst = k.amount
                                else:
                                    tax_rate_sgst = k.amount
                        elif tax_type == "integ":
                            if "cgst" in k.name.lower() or "sgst" in k.name.lower():
                                raise UserError(_('Mix of Integrated and State Taxes'))
                            tax_rate_igst = k.amount
                    if tax_type == "state":
                        if tax_rate_sgst.is_integer():
                            tax_rate_sgst = round(tax_rate_sgst)
                        if tax_rate_cgst.is_integer():
                            tax_rate_cgst = round(tax_rate_cgst)
                        hsn_list.append({
                            'hsn_code':j.hsn_code,
                            'taxable_value': j.price_subtotal,
                            'tax_rate_sgst': tax_rate_sgst,
                            'tax_amount_sgst': j.tax_base_amount/2,
                            'tax_rate_cgst': tax_rate_cgst,
                            'tax_amount_cgst': j.tax_base_amount/2,
                            'total_taxable_amount': j.tax_base_amount,
                            })
                    elif tax_type == "integ":
                        hsn_list.append({
                            'hsn_code':j.hsn_code,
                            'taxable_value': j.price_subtotal,
                            'tax_rate_igst': round(tax_rate_igst),
                            'tax_amount_igst': j.tax_base_amount,
                            'total_taxable_amount': j.tax_base_amount,
                            })

        for j in docs.invoice_line_ids:
            if j.hsn_code in hsn:
                for l in hsn_list:
                    if l['hsn_code'] == j.hsn_code:
                        for hsn_val in hsn:
                            product_hsn = self.env['account.move.line'].search(
                                [('hsn_code', 'in', [hsn_val]), ('move_id', '=', docs.id)])
                            if len(product_hsn) > 1:
                                hsn_rep=[]
                                for line1 in product_hsn:
                                    hsn_rep.append(line1.id)
                                if len(product_hsn) > 1:
                                    hsn_repeated= self.env['account.move.line'].search([('id', 'in', hsn_rep)])
                                    hsn_rep_val=0.0
                                    for line in hsn_repeated:
                                        hsn_rep_val = hsn_rep_val+line.price_subtotal



                                    bb_total = 0.0
                                    price=0.0
                                    for bb in docs.invoice_line_ids:
                                        bb_total = bb_total + bb.price_subtotal
                                    val = hsn_rep_val * (docs.freight_value + docs.packing_value) / (
                                            bb_total) + hsn_rep_val
                                    # line1.hsn_value= val
                                    # line1.update({
                                    #     'hsn_value': round(val,2),
                                    # })
                                    if l['hsn_code']==hsn_val:


                                        for k in line.tax_ids:
                                            price = price + (val * k.amount) / 100
                                        if tax_type == "state":
                                            if docs.amount_tax>0.0:

                                                l['taxable_value'] =val
                                                l['total_taxable_amount'] = price

                                                l['tax_amount_sgst'] = l['total_taxable_amount'] / 2
                                                l['tax_amount_cgst'] = l['total_taxable_amount'] / 2
                                                line1.update({
                                                    'hsn_value': val,
                                                    'cgst_value': price/2,
                                                    'sgst_value': price/2,
                                                    'total_tax_value':round(price/2+price/2,2)
                                                })

                                            else :  
                                                l['taxable_value'] =0.00
                                                l['total_taxable_amount'] = 0.00

                                                l['tax_amount_sgst'] = 0.00
                                                l['tax_amount_cgst'] = 0.00
                                                line1.update({
                                                    'hsn_value': 0.00,
                                                    'cgst_value': 0.00,
                                                    'sgst_value': 0.00,
                                                    'total_tax_value':0.00
                                                })
                                              

                                        elif tax_type == "integ":
                                            if docs.amount_tax>0.0:
                                                l['total_taxable_amount'] = price
                                                l['tax_amount_igst'] = price
                                                l['taxable_value']= val

                                                line1.update({
                                                    'hsn_value': val,
                                                    'igst_value': price,
                                                    'total_tax_value':price
                                                })

                                            else :
                                                l['total_taxable_amount'] = 0.00
                                                l['tax_amount_igst'] = 0.00
                                                l['taxable_value']= 0.00

                                                line1.update({
                                                    'hsn_value': 0.00,
                                                    'igst_value': 0.00,
                                                    'total_tax_value':0.00
                                                })

                            else:
                                if len(product_hsn) == 1:
                                    price=0
                                    single_hsn = self.env['account.move.line'].search([('id', 'in', [product_hsn.id])])
                                    bb_total = 0.0
                                    for bb in docs.invoice_line_ids:
                                        bb_total = bb_total + bb.price_subtotal
                                    val = single_hsn.price_subtotal * (docs.freight_value + docs.packing_value) / (
                                                bb_total ) + single_hsn.price_subtotal
                                    # single_hsn.update= val

                                    if l['hsn_code'] == hsn_val:
                                        for k in single_hsn.tax_ids:
                                            price = price + (val * k.amount) / 100
                                        if tax_type == "state":
                                            if docs.amount_tax>0.0:

                                                l['taxable_value'] =val
                                                l['total_taxable_amount'] = price

                                                l['tax_amount_sgst'] = l['total_taxable_amount'] / 2
                                                l['tax_amount_cgst'] = l['total_taxable_amount'] / 2

                                                single_hsn.update({
                                                    'hsn_value': val,
                                                    'cgst_value':price/2,
                                                    'sgst_value':price/2,
                                                    'total_tax_value':round(price/2+price/2,2)
                                                })
                                            else:
                                                l['taxable_value'] = 0.00
                                                l['total_taxable_amount'] = 0.00

                                                l['tax_amount_sgst'] = 0.00
                                                l['tax_amount_cgst'] = 0.00

                                                single_hsn.update({
                                                    'hsn_value': 0.00,
                                                    'cgst_value':0.00,
                                                    'sgst_value':0.00,
                                                    'total_tax_value':0.00
                                                })


                                        elif tax_type == "integ":

                                            
                                            if docs.amount_tax>0.0:
                                                l['total_taxable_amount'] = price
                                                l['tax_amount_igst'] = price
                                                l['taxable_value']= val

                                                single_hsn.update({
                                                    'hsn_value': val,
                                                    'igst_value':price,
                                                    'total_tax_value':price,
                                                })
                                            else:
                                                l['total_taxable_amount'] = 0.00
                                                l['tax_amount_igst']= 0.00
                                                l['taxable_value']= 0.00

                                                single_hsn.update({
                                                    'hsn_value': 0.00,
                                                    'igst_value': 0.00,
                                                    'total_tax_value':0.00,
                                                })




        if tax_type == "state":
            tax_type = True
        else:
            tax_type = False




        return {
            'doc_ids': docs.ids,
            'doc_model': 'account_invoice',
            'docs': docs,
            'sale_id': sale_id,
            'ori_id':ori_id,
            'lot_id': lot_id,
            'tax_type' : tax_type,
                }
