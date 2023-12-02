# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Status',
    'version': '12.0.1.0',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': """This module will create a new menu under sale""",
    'category': 'Sales',
    'depends': ['base','sale','account','purchase','portal'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/sale_portal_templates.xml',
    ],
    'installable': True,
    'application': True
}


