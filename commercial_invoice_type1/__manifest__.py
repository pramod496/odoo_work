# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
	'name':"Commercial Invoice Reports",
    'version': '12.0.3.2 11-apr',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'Commercial Invoice Reports',
	'depends':['base',"sales_team","sale","account","product","sale_order_fields"],
	'data':['report/report.xml','report/e_commercial_report.xml','template/template.xml','template/e_com_report_temp.xml', 'views/views.xml','views/invoice_type.xml','security/ir.model.access.csv',],
    'installable': True,
    'auto_install': False,
}
