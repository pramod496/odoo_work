{
    'name': 'Log Backup',
    'version': '12.0.0.1',
    'category': 'Other',
    'license': 'AGPL-3',
    'description': """""",
    'Last Updated': '22 Dec 2021',
    'company': 'Prime Minds Consulting Pvt Ltd',
    'author': 'PMCS Er. Biswajeet',
    'website': 'http://www.primeminds.com',
    'depends': ['base','mail'],
    'data': [
        'views/res_config_settings_inherit.xml',
        'views/res_company_inherit.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
}