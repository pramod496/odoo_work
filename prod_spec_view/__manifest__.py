# -*- coding: utf-8 -*-
{
    'name': "prod_spec_view",

    'summary': """
        Creates a new custom Widget for showing Product Specification View.
        """,

    'description': """
        Creates a new custom Widget for showing Product Specification View.
    """,

    'author': "Prime Minds Consulting Private Limited",
    'website': "https://primeminds.co",
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
                'sale_to_mrp',
                # 'website_profile'
    ],

    # always loaded
    'data': [
    ],
    'assets': {
        'web.assets_backend': [
            '/prod_spec_view/static/js/prod_spec.js',
            ],
        'web.assets_qweb': [
            'prod_spec_view/static/xml/*',
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}