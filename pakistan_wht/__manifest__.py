# -*- coding: utf-8 -*-
{
    'name': "Pakistan Wht",

    'summary': """ Pakistan """,

    'description': """ Pakistan Tax """,

    'author': "Eduwebgroup",
    'website': "http://www.eduwebgroup.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Taxes',
    'version': '0.2.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'purchase',
        'sale',
        'report_xlsx',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'data/base_automation_data.xml',
        'views/res_company_views.xml',
        'wizards/pakistan_tax_report_wizard_views.xml',
        'wizards/res_partner_report_tax_wizard_views.xml',
        'reports/pakistan_tax_reports.xml',
        'reports/res_partner_reports.xml',
    ],
}
