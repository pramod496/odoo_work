# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "UOM Convesions",

    'version': '12.0.1.0',

    'author': 'Prime Minds',

    'website': "https://primeminds.co/",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'depends': ['base', 'mrp','product','stock_request','stock','send_mail_n','account_roundoff','subcontract'],

    'data': [
        'views/view.xml',
    ],
    'demo': [
    ],
    'application': True,

    'auto_install': False,
}
