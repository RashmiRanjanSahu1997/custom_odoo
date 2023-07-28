from odoo import fields, models


class Books(models.Model):
    _name = "books"

    name = fields.Char("Book Name")
    author_ids = fields.Many2many(
        "author",
        "books_author_rel",
        "books_id",
        "author_id",
        "Author"
    )