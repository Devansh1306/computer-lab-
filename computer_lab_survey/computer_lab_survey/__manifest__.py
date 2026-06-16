# -*- coding: utf-8 -*-
{
    'name': 'Computer Lab Utilization Survey',
    'version': '19.0.1.0.0',
    'category': 'Education',
    'summary': 'Track and manage computer lab utilization with weekly slot scheduling',
    'description': """
        Computer Lab Utilization Survey Module
        =======================================
        - Weekly slot scheduling (Mon–Fri, 8am–6pm, 5 slots × 2hrs)
        - Lab & department details management
        - Real-time utilization statistics
        - Slot detail tracking (course, batch, student count)
        - Availability & sharing management
        - Beautiful modern UI with dynamic stats
    """,
    'author': 'Beyond Guni',
    'website': 'https://www.beyondguni.com',
    'depends': ['base', 'mail', 'web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'views/computer_lab_survey_views.xml',
        'views/computer_lab_slot_views.xml',
        'views/portal_templates.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'computer_lab_survey/static/src/css/lab_survey.css',
            'computer_lab_survey/static/src/js/lab_survey_widget.js',
        ],
        'web.assets_frontend': [
            'computer_lab_survey/static/src/css/lab_survey.css',
        ],
    },
    'images': [],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
