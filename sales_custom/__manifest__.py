{
    'name': ' sales_amount',
    'description': 'This is using for Sales amount',
    'version': '15.0.0.0',
    'license': 'AGPL-3',
    'category': 'Administration',
    'website': 'www.odoo.com',
    'depends': ['base','sale','mail','contacts'],
    'data': [
        
        'views/res_config_setting.xml',
        'views/sale_order.xml',
        'data/mail_template.xml',
        'wizard/reasons.xml',
        'security/data.xml',
        # 'security/ir.model.access.csv',
        
    ],
    'auto_install': False,
    'installable': True,
    'application': True
}