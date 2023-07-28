{
    'name': "Multiple_appointment_calendar",
    'summary': "Multiple appointment calendar",
    'description': "To show description",
    'website': 'www.odoo.com',
    'license': "AGPL-3",

    'category': 'Extra Tools',
    'version': '15.0.0.0',
    'depends': ['base_setup'],
    'data': [
		'security/ir.model.access.csv',
     	'views/multiple_appointment_calendar.xml'
        ],
    'auto_install': False,
    'installable': True,
    'application': True
}
