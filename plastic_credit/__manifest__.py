
{
    'name': 'plastic_credits',
    'version': '1.3',
    'category': 'Marketing/Events',
    'summary': 'Adding field in database',
    'description': """This is using for data add in database""",
    'depends': ['base','mail','hr','contacts','web','prt_report_attachment_preview'],
    'data': [
        'security/data.xml',
        'security/ir.model.access.csv',
        'views/pc_request_details_history.xml',
        'views/request_status.xml',
        'views/pc_type.xml',
        'views/user_invitation.xml',
        'views/user_invitation_status.xml',
        'views/pc_request_details.xml',
        'views/user_wallet.xml',
        'views/setting.xml',
        'data/external_layout.xml',
        'data/reports.xml',
        'views/database.xml',
        'views/css.xml',
        'views/materials.xml',
        'views/match_data.xml',
        'views/unmatch_data.xml',
        'views/res_user.xml',
        'data/server_reports.xml',
        'views/res_country.xml',
        'views/res_company.xml',
        'views/res_state.xml',
        'views/res_documents.xml',
        'reports/mail_template.xml',
        # 'wizard/sale_wizard.xml'
        'views/request_line.xml',
        'reports/history_mail_template.xml',
        

        

        

    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'LGPL-3',
}
