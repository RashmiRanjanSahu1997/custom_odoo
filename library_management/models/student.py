from email.policy import default
from odoo import fields, models, api


class LibStudent(models.Model):
    _name = "student"

    name = fields.Char("Name")
    library_id = fields.Many2one("library.management", "Library")
    is_active = fields.Boolean("Active")
    date_of_joining = fields.Date("Joining Date", default=fields.Date.context_today)
    state = fields.Selection([
        ("draft", "Draft"),
        ("consideration", "Consideration"),
        ("confirmed", "Confirmed")
        ],
        default="draft")

    notice = fields.Char(related="library_id.notice")
    

    def set_consideration(self):
        self.state = "consideration"

    @api.onchange("name")
    def onchange_name(self):
        self.is_active = False

    @api.depends("library_id.notice")
    def _compute_notice(self):
        for rec in self:
            rec.notice = rec.library_id.notice

    @api.model
    def create(self, vals):
        # if not vals.get("library_id"):
        #     lib_id = self.env["library.management"].search([("name", "!=", "qwe")], limit=1)
        #     vals.update({
        #         "library_id": lib_id.id,
        #     })
        res = super(LibStudent, self).create(vals)
        if not res.library_id:
            lib_id = self.env["library.management"].search([("name", "!=", "qwe")], limit=1)
            res.library_id = lib_id.id
        return res

    def write(self, vals):
        if not vals.get("library_id"):
            lib_id = self.env["library.management"].search([("name", "!=", "qwe")], limit=1)
            vals.update({
                "library_id": lib_id.id,
            })
        res = super(LibStudent, self).write(vals)

        res
