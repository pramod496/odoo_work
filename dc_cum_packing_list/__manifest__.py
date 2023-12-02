# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Delivery Challan Cum Packing List ",
    'version': '12.0.2.6 12-july',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary':"Delivery Challan Cum Packing List ",
    'last_updated_on': '04-june',
	'depends':['base',"account","stock","product","export_packing_list"],
	'data':['report/report.xml','template/template.xml','views/views.xml',],
    'installable': True,
    'application': True,
}
