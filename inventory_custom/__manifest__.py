{
    'name': 'inventory_custom',
    'description': 'This is using for Inventory Location',
    'version': '15.0.0.0',
    'license': 'AGPL-3',
    'category': 'Administration',
    'website': 'www.odoo.com',
    'depends': ['purchase','stock','base'],
    'data': [
        'views/stock_location.xml',
        'views/res_config.xml'
          
    ],
    'auto_install': False,
    'installable': True,
    'application': True
}