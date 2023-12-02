# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'MRP Subcontract Management',

    'version': '12.0.1.0',

    'author': 'Prime Minds',
    
    'website': "https://primeminds.co/",

    'summary': """Subcontract based on Manufacturing""",

    'description': """Subcontract feature in manufacturing is used for delivery of raw materials 
                    to the stores for the supplier. And also it is used for the production order of the products 
                    at the supplier's location and receipt of the finished products in the stores.""",

    'category': 'Manufacturing',
    
    'depends': ['mrp', 'purchase','stock','mail',],

    'data':
    [
        'views/subcontract_views.xml',
         'data/ir_sequence_data.xml',
        'security/ir.model.access.csv',
    ],

    'images': 
    [
        'static/description/banner.png',
        'static/description/icon.jpg',
        'static/description/index.html',
    ],

    'installable': True,
    'auto_install': False,
    'application': True,
}
