# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Invoice Creation in GRN',
    'version': '1.1 Last updated on Jan-20',
    'category': 'Warehouse',
    'summary': 'Invoice Creation in GRN',
    'description': """
    """,
    'depends': ['stock','account','purchase'],
    'data': [
        'stock_picking_views.xml',
    ],
    'demo': [
    ],
    'uninstall_hook': "uninstall_hook",
    'installable': True,
    'auto_install': False
}
