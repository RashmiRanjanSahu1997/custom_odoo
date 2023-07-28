from email.policy import default
from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError


class LibraryManagement(models.Model):
    _name = "library.management"
    _description = "library management"

    name = fields.Char("Name")
    student_ids = fields.One2many("student", "library_id", "Students")
    no_of_students = fields.Integer(compute="_compute_no_of_students")
    notice = fields.Char("Notice", copy=False)

    def get_student(self):
        return {
            'name': "students",
            'type': 'ir.actions.act_window',
            'res_model': 'student',
            'view_mode': 'tree',
            'domain': [('library_id','=',self.id)],
            'target': 'current',
        }

    def _compute_no_of_students(self):
        for rec in self:
            rec.no_of_students = len(rec.student_ids)

    def unlink(self):
        self.ensure_one()   
        res = super(LibraryManagement, self).unlink()

        return res
        # if self.no_of_students:
        #     raise ValidationError("Sorry, there is students in this library.")
        # return super(LibraryManagement, self).unlink()

    
