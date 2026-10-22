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

    def unlink(self):
        result = super().unlink()  # the database deletes its rules, without their unlink
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result

    def _get_applicable_rules(self, products, date, **kwargs):
        rules = super()._get_applicable_rules(products, date, **kwargs)
        if self.env.context.get("l10n_hr_price_list_regular_price"):
            # The regular price of the public price list: without the rules of special sales.
            rules = rules.filtered(lambda rule: not (rule.price_list_special_sale or "").strip())
        return rules


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
