from odoo import fields, models, tools,_
from odoo.tools import OrderedSet, groupby


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _apply_putaway_strategy(self):
        self = self.with_context(do_not_unreserve=True)
        for package, smls in groupby(self, lambda sml: sml.result_package_id):
            smls = self.env['stock.move.line'].concat(*smls)
            excluded_smls = smls
            if package.package_type_id:
                best_loc = smls.move_id.location_dest_id.with_context(exclude_sml_ids=excluded_smls.ids)._get_putaway_strategy(self.env['product.product'], package=package)
                smls.location_dest_id = smls.package_level_id.location_dest_id = best_loc
            elif package:
                used_locations = set()
                for sml in smls:
                    if len(used_locations) > 1:
                        break
                    sml.location_dest_id = sml.move_id.location_dest_id.with_context(exclude_sml_ids=excluded_smls.ids)._get_putaway_strategy(sml.product_id, quantity=sml.product_uom_qty)
                    excluded_smls -= sml
                    used_locations.add(sml.location_dest_id)
                if len(used_locations) > 1:
                    smls.location_dest_id = smls.move_id.location_dest_id
                else:
                    smls.package_level_id.location_dest_id = smls.location_dest_id
            else:
                for sml in smls:
                    if (sml.move_id._get_available_quantity(sml.location_id) + sml.move_id._get_available_quantity(sml.location_dest_id)) < (sml.location_dest_id.stock_capacity):
                        sml.location_dest_id = sml.move_id.location_dest_id
                    else:
                        sml.location_dest_id = sml.move_id.location_dest_id.with_context(exclude_sml_ids=excluded_smls.ids)._get_putaway_strategy(
                            sml.product_id, quantity=sml.product_uom_qty, packaging=sml.move_id.product_packaging_id,
                        )
                    excluded_smls -= sml
    
