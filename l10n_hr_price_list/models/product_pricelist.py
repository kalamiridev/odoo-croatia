from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    @api.model_create_multi
    def create(self, vals_list):
        pricelists = super().create(vals_list)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return pricelists

    def write(self, vals):
        result = super().write(vals)  # e.g. archived when Pricelists are turned off
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    price_list_special_sale = fields.Char(
        string="Special Sale",
        help="Name of the special sale (e.g. Autumn sale) when this rule is a sale or discount: the public "
        "price list then marks its price as a special sale price. Empty: a regular price.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        items = super().create(vals_list)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return items

    def write(self, vals):
        result = super().write(vals)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result

    def unlink(self):
        result = super().unlink()
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result
