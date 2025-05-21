# -*- coding: utf-8 -*-
{
    'name': "LogiSync",
    'summary': 'Odoo Module for LogiSync',
    'description': 'Odoo Module for storing, tracking, and monitoring the logistics of TikTok Shop',
    'sequence': -100,
    'author': "Kelompok 1 K2",
    'category': 'Uncategorized',
    'version': '1.0',
    'depends': ['base', 'website'],
    'data': [
        'security/res_groups.xml',
        'security/ir.model.access.csv',
        'views/order_views.xml',
        'views/shipment_views.xml',
        'views/transaction_views.xml',
        'views/partner_views.xml',
        'views/performance_views.xml',
        'views/staff_views.xml',
        'views/tracking_views.xml',
        'views/templates/homepage.xml',
        'views/templates/tracking.xml',
        'views/menus.xml',
        'views/website_routes.xml',
        'data/seq_logistics_shipment.xml',
        'data/seq_logistics_order.xml',
        'data/seq_logistics_transaction.xml'
    ],
    'assets': {
        'web.assets_frontend': [
            'logisync-modules/static/src/css/homepage.css',
            'logisync-modules/static/src/css/tracking.css',
            'logisync-modules/static/src/js/homepage.js'
        ],
    },
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
