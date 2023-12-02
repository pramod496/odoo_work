# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Work Order Report",
    'version': '12.0.1.0',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'Work Order Reports',
	'depends':['base','sale_to_mrp','mrp'],
	'data':['report/report.xml',
         'template/template.xml',
         'views/views.xml',
         'views/master_views.xml',
         'views/product_custom.xml',
         'security/ir.model.access.csv',
			],
    'installable': True,
    'auto_install': False,
}
