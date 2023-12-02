# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Terms & Conditions",
    'version': '12.0.1.0',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",
    'description': """
        Long description of module's purpose
    """,
    'category': 'Uncategorized',
    'depends': ['base', 'sale', 'product', 'purchase', 'account'],
    'data': [
        'views/views.xml',
        'views/templates.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}