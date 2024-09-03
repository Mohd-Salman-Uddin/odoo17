# -*- coding: utf-8 -*-
{
    'name': "My_School",
    'summary': "Module To Manage The School",
    'description': """
As The Difficulty Increases In Management Of School. It's Better To Automate The Process.
    """,
    'author': "Mohammed Salman Uddin",
    'version': '0.1',
    'depends' : [
        'mail',
        'sale' ,
        'account'
    ],
    'data': [
        'security/ir.model.access.csv',

        'views/invoice_views.xml',
        'views/sale_views.xml',
        'views/query_views.xml',
        'views/feestructure_views.xml',
        'views/student_views.xml',
        'views/suggestions_views.xml',
        'views/teacher_views.xml',
        'views/menu.xml',
        'wizard/student_suggestion_views.xml',
    ],
}

