# -*- coding: utf-8 -*-
{
    'name': 'Merge SO/Invoice Lines',

    'summary': """ Merge SO/Invoice Lines """,

    'description': """
        Merge SO/Invoice Lines
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Sales',
    'version': '1.0',

    'depends': [
        'account',
        'sale_management',
    ],

    'data': [
        'views/account_move_views.xml',
        'views/sale_order_views.xml',
        'views/product_template_views.xml',
        'reports/account_move_report_templates.xml',
        'reports/sale_order_report_templates.xml',
    ],
}