# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Updates of Task Prgoress & Delays',
    'version': '14.0.1',
    'sequence': 0,
    'summary': 'Calculate task progress based on stages completed.',
    'description': "",
    'depends': ['project','timesheet_grid'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_views.xml',
    ],
    'installable': True,
    'application': True,
    'website': 'https://www.technovicinfotech.com',
    'author': 'Mohamed Zarroug'
}
