{
    'name': 'sales incentive',
    'description': 'This is using for store data  to sale incentive',
    'version': '15.0.0.0',
    'license': 'AGPL-3',
    'category': 'Administration',
    'website': 'www.odoo.com',
    'depends': ['base','sale'],
    'data': [
        'views/sale_incentive.xml',
        'security/ir.model.access.csv',
        'views/sale_product.xml',
        'views/res_user.xml'


        ],
    'auto_install': False,
    'installable': True,
    'application': False
}