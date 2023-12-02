# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Tax Invoice Report",
    'version': '12.0.3.5 1-oct',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'Tax Invoice Reports',
	'depends':['base',"account","sale","product"],
	'data':['report/report.xml','template/template.xml','views/views.xml',],
    'installable': True,
    'auto_install': False,
}
