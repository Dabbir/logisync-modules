# -*- coding: utf-8 -*-
{
    'name': "LogiSync",
    'summary': 'Odoo Module for LogiSync',
    'description': 'Odoo Module for storing, tracking, and monitoring the logistics of TikTok Shop',
    'sequence': -100,
    'author': "Kelompok 1 K2",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base'],
    'data': [
        'views/logistics_views.xml',
        'views/logistics_menus.xml',
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
