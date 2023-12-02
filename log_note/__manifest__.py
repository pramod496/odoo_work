# -*- coding: utf-8 -*-
{
    'name': "log_note",

    'summary': """
        Log Notes in chatter.""",

    'description': """
        Log Notes in chatter from One Object to another Object(if link is exist).
    """,

    'author': "Prime Minds Consulting",
    'website': "https://primeminds.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1 last updated on Feb-03',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'sale_to_mrp',],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}