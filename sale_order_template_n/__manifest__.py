# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Sale Order Report",
    'version': '12.0.1.1 28-mar',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'Sale Order Report',
	'depends':['base',"sales_team","sale"],
	'data':['report/report.xml','template/template.xml','views/views.xml',],
    'installable': True,
    'auto_install': False,
}
