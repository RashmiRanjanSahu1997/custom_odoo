import json
from odoo.http import content_disposition, request, route, serialize_exception
from odoo.tools import html_escape
from odoo.tools.safe_eval import safe_eval
from odoo.addons.report_xlsx.controllers.main import ReportController


class ExportExcel(ReportController):
    def _report_routes_xlsx(self, reportname, docids=None, converter=None, **data):
        try:
            report = request.env["ir.actions.report"]._get_report_from_name(reportname)
            context = dict(request.env.context)
            if docids:
                docids = [int(i) for i in docids.split(",")]
            if data.get("options"):
                data.update(json.loads(data.pop("options")))
            if data.get("context"):
                # Ignore 'lang' here, because the context in data is the one
                # from the webclient *but* if the user explicitely wants to
                # change the lang, this mechanism overwrites it.
                data["context"] = json.loads(data["context"])
                if data["context"].get("lang"):
                    del data["context"]["lang"]
                context.update(data["context"])
            xlsx = report.with_context(context)._render_xlsx(docids, data=data)[0]
            report_name = report.report_file
            try:
                if report.print_report_name and not len(docids) > 1:
                    obj = request.env[report.model].browse(docids[0])
                    report_name = safe_eval(report.print_report_name, {"object": obj})
            except:
                report_name = data["context"].get("active_model").replace(".", " ").capitalize() + " Report"
            xlsxhttpheaders = [
                (
                    "Content-Type",
                    "application/vnd.openxmlformats-"
                    "officedocument.spreadsheetml.sheet",
                ),
                ("Content-Length", len(xlsx)),
                ("Content-Disposition", content_disposition(report_name + ".xlsx")),
            ]
            return request.make_response(xlsx, headers=xlsxhttpheaders)
        except Exception as e:
            se = serialize_exception(e)
            error = {"code": 200, "message": "Odoo Server Error", "data": se}
            return request.make_response(html_escape(json.dumps(error)))
