# -*- coding: utf-8 -*-
{
	'name':"Debit Note Report",
	'author':"Prime Minds Consulting",
	'version':"1.0",
	'website':"www.pmcs.com",
	'depends':['account','account_roundoff',],
	'data':[
		'data/report_paperformat.xml',
		'views/invoice_view.xml',
		'report/debit_note_report.xml',	
    ],
	'installable':'True',
	'auto install':'False',
}
