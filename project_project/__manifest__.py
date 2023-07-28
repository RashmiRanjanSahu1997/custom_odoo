{
    'name':'project_details',
    'summary':'this is project details',
    'description':'Project details',
    'version':'15.0.0.0',
    'category': 'Administration',
    'website': 'www.odoo.com',
    'depends':['project','hr_timesheet'],
    'data':[
        'views/project_timesheet.xml'
        ],
    'auto_install': False,
    'installable': True,
    'application': False,

}