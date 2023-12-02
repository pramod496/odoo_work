{
    'name': "INR Convesions",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        INR Conversion from One Currency to another
    """,

    'author': "Shivashanth",
    'website': "http://www.pmcpl.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '12.0.0.3 updated on Nov-28',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        'views/view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'application': True
}
# -*- coding: utf-8 -*-
