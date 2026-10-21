from odoo import models


class ProductCategory(models.Model):
    _inherit = "product.category"

    def write(self, vals):
        result = super().write(vals)
        if "parent_id" in vals:  # the products of a premises (subcategories included) can change
            self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result
