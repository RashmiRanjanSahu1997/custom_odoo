{
    'name':'Excel Report',
    'summary':'This is using for get records',
    'description': '''
        display all reports
    ''',
    'category': 'base',
    'version': '14.0.1',
    'author': 'Tecblic Private Limited',
    'company': 'Tecblic Private Limited',
    'maintainer': 'RSAHU',
    'website': 'https://www.tecblic.com',
    'depends': [
        'base',
        'report_xlsx',
        'sale'  
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/export_excel.xml',
        'wizard/excel_report.xml',
    ],
 
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}