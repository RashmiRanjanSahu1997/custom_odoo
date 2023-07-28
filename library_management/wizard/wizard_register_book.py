from odoo import models, fields


class RegisterBook(models.TransientModel):
    _name = "wizard.register.book"

    name = fields.Char("Book Name")

    def register_book(self):
        book_id = self.env["books"].create({
            "name": self.name,
            # "author_ids": [self.env.context.get("active_id")]
        })
        book_id.author_ids = [6, 0, self.env.context.get("active_id")]