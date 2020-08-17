# -*- coding: utf-8 -*-
{
    'name': 'Tuition Plan Merge SO/Invoice Lines',

    'summary': """ Tuition Plan Merge SO/Invoice Lines """,

    'description': """
        Tuition Plan Merge SO/Invoice Lines
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Sales',
    'version': '1.0',

    'depends': [
        'tuition_plan',
        'merge_sale_line',
    ],

    'data': [
        'views/tuition_plan_views.xml',
    ],
}