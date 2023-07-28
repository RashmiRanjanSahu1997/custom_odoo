from odoo import models,api

class RequestHistoryReport(models.AbstractModel):
    _name ='report.plastic_credit.request_history_template'
 
    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['request.details.history'].browse(docids)
        return {
                
              'doc_ids': docids,
              'doc_model': 'request.details.history',
              'docs': docs,
              'data': data,
        }


