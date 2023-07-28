{
    'name': 'sale_products_discount',
    'description':'This module is using for set discount on products',
    'license':'AGPL-3',
    'category':'Administration',
    'version':'15.0.0.0',
    'website':'www.odoo.com',
    'depends':['sale'],
    'data':[
        'views/product_variant.xml',
        'wizard/product_discount.xml',
        'security/ir.model.access.csv',
    ],
    'auto_install':False,
    'installable':True,
    'application':False
}

































































































