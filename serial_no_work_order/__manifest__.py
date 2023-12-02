{
	'name':"Serial Number Of Product",
    'version': '15.0.0.1',
    'author': 'Prime Minds',
    'website': "https://primeminds.co/",
    'summary': 'It will show serial no  of product in the internal work order',
	'depends':["base", "web", "product",
                'sale_to_mrp',
                ],
	'data':[
        'security/ir.model.access.csv',
        'views/serial_no_info.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}