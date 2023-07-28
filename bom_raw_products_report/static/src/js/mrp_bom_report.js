odoo.define("bom_raw_products_report.bom_report", function(require){
    "use strict";

    const bom_report = require("mrp.mrp_bom_report");

    bom_report.include({
        set_html: function() {
            var self = this;
            var model = ["product.product", "product.template"];
            if(model.includes(self.given_context.model)) {
                var lines = "";
                Object.entries(self.data).forEach(([key, value]) => {
                    lines = value.lines ? lines.concat(value.lines) : lines.concat("");
                });
                self.data.lines = lines;
            }
            return this._super(...arguments);
        },
    });
});