# Part of Odoo. See LICENSE file for full copyright and licensing details. 
{
    'name': 'Send Mail',
    'version': '12.0.1.0',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': """This module will send mail to the portal users""",
    'description': """This module will send mail to the portal users""",
    'category': 'Tools',
    'depends': ['base','sale','mrp'],
    'data': [
        'security/sale_security.xml',
        'security/ir.model.access.csv',
        'views/views.xml',
        # 'views/workorder_portal_template.xml',
    ],
    'installable': True,
    'auto_install': False,
}

