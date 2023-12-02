# Part of Odoo. See LICENSE file for full copyright and licensing details. 
{
    'name': 'Sale Fields',
    'description': """This module will send mail to the portal users""",
    'author':"Prime Minds Consulting",
    'version':"12.0.0.4",
    'website':"https://primeminds.co",
    'category': 'Tools',
    'depends': ['base', 'sale','stock','sale_to_mrp'],
    'license': 'AGPL-3',
    'data': [
        'security/ir.model.access.csv',
        'data/lut_arn_cron.xml',
        'data/mail_template.xml',
        'views/views.xml',
        'views/lut_master_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
