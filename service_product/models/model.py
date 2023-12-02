from odoo import models, fields

class product_product(models.Model):

    _inherit = "product.product"

    parent_id = fields.Many2one('product.product','Parent Product')

    def copy(self, cr, uid, id, default=None, context=None):
       if not default:
            default = {}
       prod_type = self.pool.get('product.product').browse(cr,uid,id).type
       if prod_type == 'service':
                default.update({
            'type': 'product',
            'parent_id': False,

        })
       return super(product_product, self).copy(cr, uid, id, default, context=context)
           
    _sql_constraints = [
        ('parent_id_uniq', 'unique(parent_id)', 'The Parent Product already exist!')
    ]

product_product()

class product_template(models.Model):

    _inherit = "product.template"

    parent_id = fields.Many2one('product.product','Parent Product')


product_template()

