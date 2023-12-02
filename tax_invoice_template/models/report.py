from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ReportMyReport(models.AbstractModel):
    _name = 'report.tax_invoice_template.report_tax_invoice_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        a, b = [], []
        docs = self.env['account.move'].browse(docids)
        origin = docs.origin
        po_ref = ""
        po_date = ""
        if origin:
            orig = origin.split(', ')
            for ori in orig:
                sale = self.env['sale.order'].search([('name','=', ori)])
                a.append(sale.client_order_ref)
                b.append(sale.po_date.strftime("%d-%m-%Y"))
            po_ref =' / '.join(map(str, a))
            po_date =' / '.join(map(str, b))
        sale_id = self.env['sale.order'].search([('name', '=', docs.name)])
        stock_id = self.env['stock.picking'].search([('origin', '=', sale_id.name)])
        hsn = []
        hsn_list = []
        tax_type = ""
        for i in docs:
            if len(i.invoice_line_ids) == 0:
                raise UserError(_('No Invoice Lines'))
            for j in i.invoice_line_ids:
                if j.tax_ids:
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
                                else:
                                    raise UserError(_('Neither Integrated nor State Taxes'))
                    else:
                        tax_rate_igst = ""
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
        # print("#############hsn###",hsn_list)
        for j in docs.invoice_line_ids:
            if j.hsn_code in hsn:
                for l in hsn_list:
                    if l['hsn_code'] == j.hsn_code:
                        for hsn_val in hsn:
                            product_hsn = self.env['account.move.line'].search(
                                [('hsn_code', 'in', [hsn_val]), ('move_id', '=', docs.id)])
                            if len(product_hsn) > 1:
                                hsn_rep = []
                                for line1 in product_hsn:
                                    hsn_rep.append(line1.id)
                                if len(product_hsn) > 1:
                                    hsn_repeated = self.env['account.move.line'].search([('id', 'in', hsn_rep)])
                                    hsn_rep_val = 0.0
                                    for line in hsn_repeated:
                                        hsn_rep_val = hsn_rep_val+line.price_subtotal

                                    bb_total = 0.0
                                    price = 0.0
                                    for bb in docs.invoice_line_ids:
                                        bb_total = bb_total + bb.price_subtotal

                                    extra_charges = 0
                                    if docs.freight_tax_ids:
                                        extra_charges += docs.freight_value
                                    if docs.packing_tax_ids:
                                        extra_charges += docs.packing_value
                                    if docs.loading_tax_ids:
                                        extra_charges += docs.loading_value
                                    if docs.testing_tax_ids:
                                        extra_charges += docs.testing_value
                                    # if not extra_charges:
                                    #     extra_charges = 1
                                    val = (hsn_rep_val * extra_charges / bb_total) + hsn_rep_val
                                    # val = hsn_rep_val * (docs.freight_value + docs.packing_value + docs.loading_value + docs.testing_value) / (
                                    #         bb_total) + hsn_rep_val
                                    # line1.hsn_value= val
                                    # line1.update({
                                    #     'hsn_value': round(val,2),
                                    # })
                                    if l['hsn_code'] == hsn_val:


                                        for k in line.tax_ids:
                                            price = price + (val * k.amount) / 100
                                        if tax_type == "state":
                                            if docs.amount_tax > 0.0:
                                                l['taxable_value'] = val
                                                l['total_taxable_amount'] = price

                                                l['tax_amount_sgst'] = l['total_taxable_amount'] / 2
                                                l['tax_amount_cgst'] = l['total_taxable_amount'] / 2
                                                line1.update({
                                                    'hsn_value': val,
                                                    'cgst_value': price/2,
                                                    'sgst_value': price/2,
                                                    'total_tax_value': round(price/2 + price/2, 2)
                                                })

                                            else:
                                                l['taxable_value'] = 0.00
                                                l['total_taxable_amount'] = 0.00

                                                l['tax_amount_sgst'] = 0.00
                                                l['tax_amount_cgst'] = 0.00
                                                line1.update({
                                                    'hsn_value': 0.00,
                                                    'cgst_value': 0.00,
                                                    'sgst_value': 0.00,
                                                    'total_tax_value': 0.00
                                                })

                                        elif tax_type == "integ":
                                            if docs.amount_tax>0.0:
                                                l['total_taxable_amount'] = price
                                                l['tax_amount_igst'] = price
                                                l['taxable_value'] = val

                                                line1.update({
                                                    'hsn_value': val,
                                                    'igst_value': price,
                                                    'total_tax_value': price
                                                })

                                            else:
                                                l['total_taxable_amount'] = 0.00
                                                l['tax_amount_igst'] = 0.00
                                                l['taxable_value'] = 0.00

                                                line1.update({
                                                    'hsn_value': 0.00,
                                                    'igst_value': 0.00,
                                                    'total_tax_value': 0.00
                                                })

                            else:
                                if len(product_hsn) == 1:
                                    price = 0
                                    single_hsn = self.env['account.move.line'].search([('id', 'in', [product_hsn.id])])
                                    bb_total = 0.0
                                    for bb in docs.invoice_line_ids:
                                        bb_total = bb_total + bb.price_subtotal

                                    extra_charges = 0
                                    if docs.freight_tax_ids:
                                        extra_charges += docs.freight_value
                                    if docs.packing_tax_ids:
                                        extra_charges += docs.packing_value
                                    if docs.loading_tax_ids:
                                        extra_charges += docs.loading_value
                                    if docs.testing_tax_ids:
                                        extra_charges += docs.testing_value
                                    # if not extra_charges:
                                    #     extra_charges = 1
                                    val = (single_hsn.price_subtotal * extra_charges / bb_total) + single_hsn.price_subtotal
                                    # print("!!!!!!!!!!!!", val)
                                    # single_hsn.update= val

                                    if l['hsn_code'] == hsn_val:
                                        for k in single_hsn.tax_ids:
                                            price = price + (val * k.amount) / 100
                                        if tax_type == "state":
                                            if docs.amount_tax > 0.0:
                                                l['taxable_value'] = val
                                                l['total_taxable_amount'] = price
                                                l['tax_amount_sgst'] = l['total_taxable_amount'] / 2
                                                l['tax_amount_cgst'] = l['total_taxable_amount'] / 2

                                                single_hsn.update({
                                                    'hsn_value': val,
                                                    'cgst_value': price/2,
                                                    'sgst_value': price/2,
                                                    'total_tax_value': round(price/2 + price/2, 2)
                                                })
                                            else:
                                                l['taxable_value'] = 0.00
                                                l['total_taxable_amount'] = 0.00

                                                l['tax_amount_sgst'] = 0.00
                                                l['tax_amount_cgst'] = 0.00

                                                single_hsn.update({
                                                    'hsn_value': 0.00,
                                                    'cgst_value': 0.00,
                                                    'sgst_value': 0.00,
                                                    'total_tax_value': 0.00
                                                })
                                        elif tax_type == "integ":
                                            if docs.amount_tax>0.0:
                                                l['total_taxable_amount'] = price
                                                l['tax_amount_igst'] = price
                                                l['taxable_value'] = val
                                                single_hsn.update({
                                                    'hsn_value': val,
                                                    'igst_value': price,
    						                        'total_tax_value': price,
                                                })
                                            else:
                                                l['total_taxable_amount'] = 0.00
                                                l['tax_amount_igst'] = 0.00
                                                l['taxable_value'] = 0.00

                                                single_hsn.update({
                                                    'hsn_value': 0.00,
                                                    'igst_value': 0.00,
                                                    'total_tax_value': 0.00,
                                                })


        if tax_type == "state":
            tax_type = True
        else:
            tax_type = False

        # print('-------------------------',hsn_list)

        return {
            'doc_ids': docs.ids,
            'doc_model': 'account_invoice',
            'docs': docs,
            'stock_id': stock_id,
            'sale_id': sale_id,
            'po_ref': po_ref,
            'po_date': po_date,
            'hsn_list':hsn_list,
            'tax_type' : tax_type,

        }