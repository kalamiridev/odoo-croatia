from odoo import fields, models


class L10nHrPriceListLocation(models.Model):
    _inherit = "l10n_hr.price.list.location"

    warehouse_id = fields.Many2one(
        "stock.warehouse",
        string="Warehouse",
        domain="[('company_id', '=', company_id)]",
        help="Availability of the goods from the stock of this warehouse only. Empty: stock of the company.",
    )

    def _availability(self, product):
        # Services have no availability, also when stock tracking is ticked on them.
        if self.warehouse_id and product.type != "service" and product.is_storable:
            stock = product.with_context(warehouse_id=self.warehouse_id.id).qty_available
            return "dostupno" if stock > 0 else "nedostupno"
        return super()._availability(product)
