from odoo import fields, models


class Author(models.Model):
    _name = "author"

    name = fields.Char("Name")