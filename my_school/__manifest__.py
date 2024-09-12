# -*- coding: utf-8 -*-
{
    'name': "My_School",
    'summary': "Module To Manage The School",
    'description': """
As The Difficulty Increases In Management Of School. It's Better To Automate The Process.
    """,
    'author': "Mohammed Salman Uddin",
    'version': '0.1',
    'depends': [
        'mail',
        'sale',
        'account'
    ],
    'data': [
        "security/school_groups.xml",
        "security/record_rule.xml",
        'security/ir.model.access.csv',

        'views/invoice_views.xml',
        'views/sale_views.xml',
        'views/query_views.xml',
        'views/feestructure_views.xml',
        'views/student_views.xml',
        'views/suggestions_views.xml',
        'views/teacher_views.xml',
        'views/product_brand_views.xml',
        'views/menu.xml',
        'wizard/student_suggestion_views.xml',

        "data/student_mail_template.xml",
        "data/teacher_mail_template.xml",
        "reports/report_template.xml",
        "reports/report_views.xml",

        "data/cron.xml",
        "data/fee_due_reminder_email_template.xml",
    ],
    'images': ['static/description/icon.png'],

}
