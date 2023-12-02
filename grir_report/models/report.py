from odoo import models, fields, api
import pdb


class ReportMyReport(models.AbstractModel):
    _name = 'report.grir_report.report_grir_report_template'


    
    def _get_report_values(self, docids, data=None):
        user_id =False
        docs = self.env['stock.picking'].browse(docids)
        p_id = self.env['purchase.order'].search([('name','=',docs.origin)])
        quality_id = self.env['quality.check'].search([('picking_id','=',docs.id),('quality_state', '!=', 'none')],
            order='id asc', limit=1)
        for el in quality_id:
            if el.user_id:
                user_id=el.user_id.name
        move_ids =[]
        repeat_product=[]
        count =0
#         spec=''        
        
        for val in docs.move_ids_without_package:
            inspect = spec = ""
            q_accept = obs = 0.0
            q_inspect = q_acceptdev = q_reject = 0  
            temp = False               
            for doc in docs.check_ids:
                if doc.product_id.id==val.product_id.id:
                    temp = True
                    if not doc.product_id.id in repeat_product:                        
                        count=count+1
                        repeat_product.append(doc.product_id.id)
                        inspect = doc.point_id.title+", " if doc.point_id.title else ''
                        spec = doc.point_id.norm +", " if doc.point_id.test_type_id.name=='Measure' else "" 
                        obs = doc.measure
                        q_inspect = doc.inspected_qty
                        q_accept = doc.inspected_qty
                        q_acceptdev = doc.qty_accepted_under_dev
                        q_reject = doc.rejected_qty
                    else:                     
                        inspect += doc.point_id.title+", " if doc.point_id.title else ''
                        spec += doc.point_id.norm +", " if doc.point_id.test_type_id.name=='Measure' else ""
                        obs += doc.measure
                        q_inspect = doc.inspected_qty
                        q_accept = doc.inspected_qty
                        q_acceptdev += doc.qty_accepted_under_dev
                        q_reject += doc.rejected_qty
            if temp:                      
                move_ids.append({
                        'sl_no': count,
                        'product_id': val.product_id.name,
                        'uom': val.product_uom.name,
                        'po_quantity': val.po_quantity,
                        'qty_done': val.quantity_done,
                        'inspection': inspect.rstrip(', '),
                        'specification': spec.rstrip(', '),
                        'observation': obs,
                        'qty_inspected': q_inspect,
                        'qty_accepted': round(q_inspect - q_reject, 4) if round(q_inspect - q_reject, 4) > 0 else 0,
                    # 'qty_accepted': round(q_accept+q_acceptdev-q_reject, 4) if round(q_accept+q_acceptdev-q_reject, 4) > 0 else 0,
                        'qty_accepted_dev': q_acceptdev,
                        # 'qty_accepted_dev': q_acceptdev,
                        'qty_rejected': q_reject if q_reject > 0 else q_reject * 0,
                        # 'qty_rejected': q_reject if q_reject > 0 else q_reject * -1,
                        # 'qty_rejected': q_reject,
                        # 'note':doc.note,
                    })
        return {
            'doc_ids': docs.ids,
            'doc_model': 'stock_picking',
            'docs': docs,
            'user_id':user_id,
            'p_id':p_id,
            # 'quality_id': quality_id,
            'move_ids':move_ids
        }

