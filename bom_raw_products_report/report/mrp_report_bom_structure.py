from odoo import models, api


class ReportBomStructure(models.AbstractModel):
    _inherit = 'report.mrp.report_bom_structure'

    @api.model
    def get_html(self, bom_id=False, searchQty=1, searchVariant=False):
        model = self.env.context.get("model")
        if model not in ["product.product", "product.template"]:
            return super(ReportBomStructure, self).get_html(
                bom_id=bom_id, searchQty=searchQty, searchVariant=searchVariant
            )
        if model == "product.template":
            product_tmpl_id = self.env[model].browse(
                self.env.context.get("active_id")
            )
            bom_id = self.env['mrp.bom'].search([
                ('product_tmpl_id', '=', product_tmpl_id.id)
            ]).ids
            searchQty = self.get_search_qty(product_tmpl_id)
        elif model == "product.product":
            product_id = self.env[model].browse(
                self.env.context.get("active_id")
            )
            bom_id = self.env['mrp.bom'].search([
                '|', 
                ('product_id', '=', product_id.id), 
                '&', 
                ('product_id', '=', False), 
                ('product_tmpl_id', '=', product_id.product_tmpl_id.id)]).ids
            searchQty = self.get_search_qty(product_id)
        res = {"is_from_product": True}
        for rec in range(len(bom_id)):
            res[rec] = self._get_report_data(bom_id=bom_id[rec], searchQty=searchQty, searchVariant=searchVariant)
            res[rec]['lines']['report_type'] = 'html'
            res[rec]['lines']['report_structure'] = 'all'
            res[rec]['lines']['has_attachments'] = res[rec]['lines']['attachments'] or any(component['attachments'] for component in res[rec]['lines']['components'])
            res[rec]['lines']['is_from_product'] = True
            res[rec]['lines'] = self.env.ref('mrp.report_mrp_bom')._render({'data': res[rec]['lines']})
        return res

    def get_search_qty(self, product_id):
        total_manufacturing_qty = []
        for line in product_id.bom_ids.bom_line_ids:
            if not line.product_id.bom_count:
                qty = line.product_id.qty_available // line.product_qty
                total_manufacturing_qty.append(qty)
            else:
                qty = self.get_search_qty(line.product_id.product_tmpl_id)
                total_manufacturing_qty.append(
                    qty + line.product_id.product_tmpl_id.qty_available
                )
        return min(total_manufacturing_qty) + product_id.qty_available