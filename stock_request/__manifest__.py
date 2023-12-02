# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Request - MRP',
    'version': '12.0.1.0',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'Stock Request Summary',
    'category': 'Manufacturing',
    'depends': ['stock', 'mrp', 'send_mail_n', 'sale_to_mrp'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_request_sequence.xml',
        'views/stock_request_view.xml',
        'views/mrp_production_views.xml',
        'views/stock_request_inventory_view.xml',
        'views/stock_request_line_views.xml',
        'views/stock_move_views_inherited.xml',
    ],
    'installable': True,
    'auto_install': False,
}
