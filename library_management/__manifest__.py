{
    "name": "Library Management",
    "version": "15.0.0.1",
    "category": "Hidden",
    "summary": "Update exchange rates using OCA modules",
    "depends": ["sale_management", "product"],
    "data": [
        "security/ir.model.access.csv",
        "wizard/wizard_register_book.xml",
        "views/library_management.xml",
        "views/books.xml",
        "views/student.xml",
        "views/author.xml",
        "views/sale_order.xml",
        "views/product.xml"
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
