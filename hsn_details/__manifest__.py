{
	'name':"HSN table",
    'version': '12.0.0.4 3-mar',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'It will show HSN table in the invoice screen',
	'depends':['base', "account", "invoice_freight",],
	'data':[
        'security/ir.model.access.csv',
        'views/account_invoice.xml',
        'views/hsn_line.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
