{
    'name': 'BOM Raw Products Report',
    'summary': 'Display all raw products of BOM in reports',
    'description': '''
        display all raw products of BOM in reports
    ''',
    'category': 'Manufacturing/Report',
    'version': '14.0.1',
    'author': 'Tecblic Private Limited',
    'company': 'Tecblic Private Limited',
    'maintainer': 'calkikhunt',
    'website': 'https://www.tecblic.com',
    'depends': [
        'mrp',
    ],
    'data': [
        'security/ir.model.access.csv',
        'templates/assets.xml',
        'views/product.xml',
        'report/mrp_report_bom_structure.xml',
        'wizard/get_report.xml',
        'wizard/get_report_wizard.xml'
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
