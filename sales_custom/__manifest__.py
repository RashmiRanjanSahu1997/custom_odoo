
{
    'name': 'sale field add',
    'version': '1.3',
    'category': 'Marketing/Events',
    'summary': 'Fields add in Sale',
    'description': """This is using for field addd""",
    'depends': ['base','mrp','sale'],
    'data': [
        'views/sale_add.xml',
        'views/stock_picking.xml'
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
