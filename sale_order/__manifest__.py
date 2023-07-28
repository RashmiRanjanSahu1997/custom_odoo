{
    'name': 'sale order',
    'version': '15.1',
    'category': 'Administration',
    'sequence': 5,
    'summary': 'Credit limit set',
    'license': 'LGPL-3',

    'depends': ['sale','base','website','stock'],

    'data': [
        'views/res_partner.xml',
        'security/data.xml',
        # 'security/ir.model.access.csv',
        # 'views/res_user.xml',
        'views/website.xml'
    ],

    'installable': True,
    'auto_install': False,
    'application': False,

}