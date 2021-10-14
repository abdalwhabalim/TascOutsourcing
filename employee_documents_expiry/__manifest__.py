# -*- coding: utf-8 -*-
{
    'name': 'Employee Document',
    'version': '14.0.1.1.1',
    'summary': """Manages Employee and Customer Documents With Expiry Notifications.""",
    'description': """Manages Employee and Customer Related Documents with Expiry Notifications""",
    'category': 'Generic Modules/Human Resources',
    'author': 'TechnovicInfotech',
    'company': 'TechnovicInfotech',
    'maintainer': 'TechnovicInfotech',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/documents_threshold.xml',
        'views/employee_check_list_view.xml',
        'views/employee_document_view.xml',
        'views/customer_document_view.xml',
        'views/customer_checklist_view.xml',
        'data/customer_reminder.xml',
        'data/employee_reminder.xml',

    ],
    'demo': ['data/data.xml'],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
