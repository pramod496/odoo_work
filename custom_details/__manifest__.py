# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Vendor Code',
    'author':"Prime Minds Consulting",
    'version':"1.7",
    'website':"https://primeminds.co",
    'category': 'customers',
    'summary': 'Fields creation',
    'description': """
    """,
    'depends': ['base','stock','account','sale','purchase','crm','quality_control','mrp','sale_to_mrp'],
    'data': [
        'custom_details.xml',
    ],
    'demo': [
    ],
    'installable': True,
    'auto_install': False
}
