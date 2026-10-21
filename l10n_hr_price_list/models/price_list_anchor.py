from odoo import api, fields, models

ANCHOR_HELP = (
    "Additional price for consumers (with VAT), shown next to the price: the price on "
    "10 September 2026, or the price when the product was first offered. Set automatically "
    "when the product is first published in the price list of the premises; later price "
    "changes do not change it. Only administrators can correct it."
)


class L10nHrPriceListAnchor(models.Model):
    """Additional price of a product in the price list of one premises (each premises can
    have its own prices)."""

    _name = "l10n_hr.price.list.anchor"
    _description = "Additional Price"
    _order = "location_id, product_id"

    location_id = fields.Many2one(
        "l10n_hr.price.list.location", string="Premises", required=True, index=True, ondelete="cascade",
    )
    company_id = fields.Many2one(related="location_id.company_id", store=True, index=True)
    product_id = fields.Many2one("product.product", string="Product", required=True, index=True, ondelete="cascade")
    # Set from the product (also the inverse of the list on the product form).
    product_tmpl_id = fields.Many2one("product.template", string="Product Template", index=True, ondelete="cascade")
    currency_id = fields.Many2one(related="company_id.currency_id")
    price = fields.Monetary(string="Additional Price", required=True, help=ANCHOR_HELP)
    date = fields.Date(string="Additional Price Date", required=True, help=ANCHOR_HELP)

    _location_product_uniq = models.Constraint(
        "UNIQUE(location_id, product_id)",
        "A product has one additional price per premises.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        products = self.env["product.product"].browse([vals["product_id"] for vals in vals_list if vals.get("product_id")])
        templates = {product.id: product.product_tmpl_id.id for product in products}
        for vals in vals_list:
            if vals.get("product_id"):
                vals["product_tmpl_id"] = templates[vals["product_id"]]
        anchors = super().create(vals_list)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return anchors

    def write(self, vals):
        if vals.get("product_id"):
            vals["product_tmpl_id"] = self.env["product.product"].browse(vals["product_id"]).product_tmpl_id.id
        result = super().write(vals)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result
