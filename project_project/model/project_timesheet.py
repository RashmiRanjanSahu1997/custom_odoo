from odoo import models,fields,api,_


class ProjectCount(models.Model):
    _inherit = 'project.project'

    total_timesheet = fields.Integer('Total Timesheet', compute ='totals_timesheet')

    def totals_timesheet(self):
        for rec in self:
            time_sheet = self.env['account.analytic.line'].search_count([
                ('project_id', '=', rec.name)])
            rec.total_timesheet = time_sheet
    
    def timesheet_view(self):
        return {
            'name': 'Time Sheet',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'view_type': 'list',
            'res_model': 'account.analytic.line',
            'target': 'current',
            'domain': [('project_id', '=', self.name)]
            }
     