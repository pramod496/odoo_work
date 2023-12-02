# -*- encoding: utf-8 -*-
##############################################################################
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.     
#
##############################################################################


from odoo import SUPERUSER_ID, models, fields
from odoo import api, fields, models, _
import pdb


class purchase_order(models.Model):
    _inherit = 'purchase.order'

    
    def button_confirm(self):
        res = super(purchase_order, self).button_confirm()
        for po_id in self:
            po_id._update_product_cost_price()
        return res

    
    def _update_product_cost_price(self):
        purchase_order_line_obj =  self.env['purchase.order.line']
        product_template_obj =  self.env['product.template']
        for po in self:
            for po_line in po.order_line:
                product_tmpl = po_line.product_id.product_tmpl_id
                update_price = po_line.price_unit
                ## check if user chose to update cost price & current cost price is same as po line unit cost (update_price)
                if po_line.update_cost_price and (product_tmpl.standard_price != update_price):
                    vals = {
                        'standard_price' : update_price
                    }
                    product_tmpl.write({'standard_price': update_price})

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'
    
    update_cost_price = fields.Boolean(string="Update Cost Price?", default= True, help="Select to update cost price of product after confirming invoice")