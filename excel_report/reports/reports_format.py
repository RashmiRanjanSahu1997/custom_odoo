from odoo import fields, models


class ExcelReportXLS(models.AbstractModel):
    _name = 'report.excel_report.excel_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet(data['file'])
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format(data['hstyle'])
        company_format = workbook.add_format(data['cstyle'])
        group_style = workbook.add_format(data['gstyle'])
    
        if data['company_name']:
            row = 0
            col = 0
            n=1
            for addr in data['company_name']:
                s='A'+str(n)+':'+'D'+str(n)
                sheet.merge_range(s, addr, company_format)
                n+=1
            row=row+7
            col=0
            for rec in data['lists']:
                sheet.write(row,col,rec,header_format)
                if data['total']:
                    if rec in data['total'].keys():
                        l=len(data['values'])
                        r=row+l+1
                        sheet.write(r,col,data['total'][rec],bold)
                ro = row 
                col=col+1
            row=ro+1
            col=0
            for record in data['values']:
                for rec in record:
                    sheet.write(row,col,rec,group_style)
                    col = col+1
                row=row+1
                col= 0
                
        else:
            row=0
            col=0
            for rec in data['lists']:
                sheet.write(row,col,rec,header_format)
                if data['total']:
                    if rec in data['total'].keys():
                        l=len(data['values'])
                        r=row+l+1
                        sheet.write(r,col,data['total'][rec],bold)
                ro = row 
                col=col+1
            row=ro+1
            col=0
            for record in data['values']:
                for rec in record:
                    sheet.write(row,col,rec,group_style)
                    col = col+1
                row=row+1
                col= 0