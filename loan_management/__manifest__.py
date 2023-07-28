# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': "Loan Management",

    'summary': """
        Loan Management
        """,

    'description': """
        This Loan Management app is an incredibly powerful and versatile loan app that help you 
        to manage loan with invoices, Journal Entries, Outstanding balance, principal and interest balalnce,
        payments etc. Also provides different ways to pay loan installments and provides functionality to change
        loan installments date.
    """,

    'sequence': -110,
    'author': "Krishna",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base', 'account', 'mail',],
    'data': [
        'security/ir.model.access.csv',
        'security/account_loan_security.xml',
        'wizard/account_loan_pay_amount_view.xml',
        'views/payment_interest.xml',

        'views/properties.xml',
        'wizard/account_loan_post_view.xml',
        'views/account_loan_view.xml',
        'views/loan_meanus.xml',
        'data/seq.xml',
        'wizard/account_loan_generate_entries_view.xml',
        
        
        'views/loans.xml',
        'views/account.xml',
        
        
        'views/account_move_view.xml',
        'views/templates.xml',

        'wizard/mail_customer.xml',
        'data/mail_template.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
