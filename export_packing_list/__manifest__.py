# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Export Packing List ",
    'version': '12.0.2.8 16-june',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'Export Packing List Report',
    'last_updated_on': '4 june',
	'depends':['base',"account","stock","product"],
	'demo':[],
	'data':['report/report.xml','template/template.xml','views/views.xml',],
    'installable': True,
    'auto_install': False,
}
