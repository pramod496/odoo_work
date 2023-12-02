# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd. (<http://www.devintellecs.com>).
#
##############################################################################


{
    'name': 'Proforma Export Invoice',
    'version': '12.0.1.6 updated on 20-july',
    'sequence':1,
    'category': 'Account',
    'description': """
        App will print New Invocie Format of Indian GST.
    """,
    'author': 'Prime Minds Consultancy Services.',
    'summary': 'App will print New Invocie Format of Indian GST.',
    'website': 'sales@primemindz.com', 'images': ['images/main_screenshot.jpg'],
    'depends': ['base','account','product','sale','sale_to_mrp'],
    'data': [
        
        'report/proforma.xml',
        'template/template.xml',
    ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

