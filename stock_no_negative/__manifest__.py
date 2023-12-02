# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Stock Disallow Negative',
    'version': '12.0.1.0',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'category': 'Inventory, Logistic, Storage',
    'summary': 'Disallow negative stock levels by default',
    'depends': ['stock'],
    'data': [
        'views/product_product_views.xml',
        'views/stock_location_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
