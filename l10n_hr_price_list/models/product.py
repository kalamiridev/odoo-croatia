from odoo import api, fields, models

# Changes that can change a line of the public price list: checked right away
# (stock and pricelist rules with a period are checked by the morning cron).
PRICE_LIST_FIELDS = {
    "name", "default_code", "barcode", "list_price", "lst_price", "taxes_id", "categ_id", "sale_ok",
    "active", "type", "uom_id", "is_storable", "company_id", "price_list_brand",
}


class ProductTemplate(models.Model):
    _inherit = "product.template"

    price_list_brand = fields.Char(string="Brand", help="Brand of the goods in the public price list.")
    price_list_published = fields.Boolean(
        string="In Public Price List", compute="_compute_price_list_published",
    )
    price_list_anchor_ids = fields.One2many(
        "l10n_hr.price.list.anchor", "product_tmpl_id", string="Additional Prices",
    )
    price_list_can_edit_anchor = fields.Boolean(compute="_compute_price_list_can_edit_anchor")

    @api.depends("categ_id", "categ_id.parent_path", "sale_ok")
    @api.depends_context("company")
    def _compute_price_list_published(self):
        locations = self.env["l10n_hr.price.list.location"].sudo().search([("company_id", "in", self.env.companies.ids)])
        all_products = any(not location.category_ids for location in locations)
        published = set(locations.category_ids.ids)
        for template in self:
            path = template.categ_id.parent_path or ""
            template.price_list_published = template.sale_ok and (
                all_products or any(int(part) in published for part in path.split("/") if part)
            )

    @api.depends_context("uid")
    def _compute_price_list_can_edit_anchor(self):
        self.price_list_can_edit_anchor = self.env.user.has_group("base.group_system")

    @api.model_create_multi
    def create(self, vals_list):
        templates = super().create(vals_list)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return templates

    def write(self, vals):
        result = super().write(vals)
        if PRICE_LIST_FIELDS & vals.keys():
            self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals_list):
        products = super().create(vals_list)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return products

    def write(self, vals):
        result = super().write(vals)
        if PRICE_LIST_FIELDS & vals.keys():
            self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result
