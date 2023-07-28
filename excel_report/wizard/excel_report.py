import datetime
from odoo import models, _


class GetWizard(models.TransientModel):
    _name = 'excel.report'

    def get_export_excel_wizard(self):
        ctx = {'active_ids':self.env.context['active_ids'],
            'active_model':self.env.context['active_model']}
        
        return {
            'name': _('Export Excel'),
            'view_mode': 'form',
            'res_model': 'excel.report',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': self.env.context
        }

    def get_excel_report(self):
        active_ids = self.env.context['active_ids']  
        active_model = self.env.context['active_model']  
        model = self.env['export.excel'].search([('model_id','=',active_model)])  
        current_active_ids = self.env[active_model].browse(active_ids)
        company_name = []   
        
        if model.is_company_detail:   
            company_name.append(current_active_ids.company_id.name)
            company_name.append(current_active_ids.company_id.street)
            company_name.append(current_active_ids.company_id.city)
            company_name.append(current_active_ids.company_id.state_id.name)
            company_name.append(current_active_ids.company_id.zip)
            company_name.append(current_active_ids.company_id.country_id.name)
            
        h_list = []
        header_list = []   
        for field_name in model.field_ids:
            h_list.append(field_name.name)
            header_list.append(field_name.field_description)
            
        main_field_value = []
        dic = {}
        l=[]
        for rec in current_active_ids:
            field_value = []
            for value in h_list:
                if type(rec[value]) in [str,datetime.date,datetime.datetime]:
                    field_value.append(rec[value])
                elif type(rec[value]) == bool:
                    field_value.append(rec[value])
                elif type(rec[value]) in [int,float]:
                    field_value.append(rec[value])
                    for i in model.field_ids:
                        if i.name == value:
                            if i.field_description not in l:
                                l.append(i.field_description)
                    if value not in dic.keys():
                        dic[value]=rec[value]
                    else:
                        dic[value]=dic[value]+rec[value]
                
                else:
                    field_value.append(rec[value].name)
            main_field_value.append(field_value)
        s=list(dic.values())
        
        total = False
        if model.is_print_sum:
            total = {l[i]: s[i] for i in range(len(l))}

        h_style = {
            'bold':model.ht_bold,'italic':model.ht_italic,
            'border':model.ht_border,
            'align':model.ht_text_align,'fg_color':model.ht_bg_color,
            'font':model.ht_size,'font_color':model.ht_color,
            'size':model.ht_size,
                }

        c_style = {
            'bold':model.ct_bold,'italic':model.ct_italic,
            'border':model.ct_border,
            'align':model.ct_text_align,'fg_color':model.ct_bg_color,
            'font':model.ct_size,'font_color':model.ct_color,'size':model.ct_size,
        }
        
        g_style = {
            'bold':model.gt_bold,'italic':model.gt_italic,
            'border':model.gt_border,
            'align':model.gt_text_align,'fg_color':model.gt_bg_color,
            'font':model.gt_size,'font_color':model.gt_color,'size':model.gt_size,
                }
    
        file_name = model.name
        data = {
            'company_name':company_name,
           'lists':header_list,
           'values':main_field_value,
           'total':total, 
           'file':file_name,
           'hstyle':h_style,
           'cstyle': c_style,
           'gstyle': g_style     
        }
    
        return self.env.ref("excel_report.sale_report_excel").report_action(self.ids, data=data)


        