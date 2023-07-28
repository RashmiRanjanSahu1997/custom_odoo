{
    'name':'invoicing_custom',
    'description': 'This is using for print pdf reports of vendors',
    'category':'Administrative',
    'license':'AGPL-3',
    'version':'15.0.0.0',
    'website':'www.odoo.com',
    'depends':['base','account'],
    'data':[
        'wizard/invoicing_date.xml',
        'security/ir.model.access.csv',
        'views/account_move.xml',
        'report/invoice_template.xml',
        'report/invoicing_pdf.xml'
    ],
    'auto_install':False,
    'installable':True,
    'application':False


}