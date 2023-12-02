# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sale Order Module',
    'version': '12.0.1.4',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': """This module will send mail to the portal users""",
    'description': """This module will send mail to the portal users""",
    'category': 'Tools',
    'last_updated_on': '5 jan',
    'depends': ['base','sale','sales_team','sale_to_mrp','account_roundoff'],
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/cron.xml',
    ],
    'installable': True,
    'auto_install': False,
}

