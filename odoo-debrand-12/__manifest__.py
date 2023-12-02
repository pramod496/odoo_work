{
    'name': "Odoo Debranding",

    'summary': """
        Odoo Module for backend and frontend debranding.""",

    'description': """
        To debrand front-end and back-end pages by removing
         odoo promotions, links, labels and other related
         stuffs.
    """,

    'author': "Prime Minds Consulting",
    'website': "https://primeminds.co",
    'category': 'Tools',
    'version': '0.0.1',
    'depends': [
        'base_setup',
        'website',
        'web',
        'website'
        # 'website_profile',
    ],
    'data': [
        # 'data/mailbot_data.xml',
        'views/views.xml',
    ],
    'qweb': ['static/src/xml/base.xml'],
    'assets': {
        'web.assets_backend': [
            'odoo-debrand-12/static/src/js/title.js',
            ],
        'web.assets_qweb': [
            'odoo-debrand-12/static/src/xml/*',
        ],
    },

    'images': ["static/description/banner.gif"],
    'installable': True,
    'application': True,

}
