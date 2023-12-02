# -*- coding: utf-8 -*-

{
    'name': 'Portal Customization',
    'summary': """ Portal Customization including Home, Login, reset page including SO Read/Unread Message Functionality. """,
    'version': '12.0.1.0.3',
    'description': """""",
    'author': 'pmcs',
    'company': 'prime minds consulting pvt ltd',
    'website': 'http://www.primeminds.com',
    'category': 'Website',
    'depends': ['base', 'web', 'website', 'sale_to_mrp', 'mail',
                # 'website_profile'
                ],
    'data': [
        'views/portal_templates.xml',
        'views/sale_view.xml',
    ],
    # 'qweb': ['static/src/xml/message_view.xml',],
    # 'assets': {
    #     'web.assets_backend': [
    #         'custom_portal/static/src/js/web_tree_dynamic_colored_field.js',
    #         ],
    #     'web.assets_qweb': [
    #         'custom_portal/static/src/xml/*',
    #     ],
    #
    # },
    'installable': True,
    'application': True
}


