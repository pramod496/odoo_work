# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Delivery Report new",
    'version': '12.0.1.3 upfated on 11 feb',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary':"Delivery Report",
	'depends':['base',"sales_team","sale","account","product","stock"],
	'demo':[],
	'data':['report/report.xml','template/template.xml','views/views.xml'],
    'installable': True,
    'auto_install': False,
}
