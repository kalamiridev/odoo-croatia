import base64
import csv
import hashlib
import io
import json
import logging
import re
from collections import defaultdict
from datetime import timedelta
from typing import NamedTuple
from urllib.parse import quote

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError

from .price_list_version import (
    COLUMNS, LOWEST_PRICE_COLUMN, NET_COLUMN, PRICE_BEFORE_SALE_COLUMN, PRODUCT_KEY, format_amount, format_date,
    local_now, local_time, parse_amount, public_rows,
)

# The lowest price before a special sale is looked up in these days before it.
LOWEST_PRICE_DAYS = 30


class Price(NamedTuple):
    consumer: float  # with taxes: from the consumer pricelist or the sales price
    regular: float  # sales price with taxes
    net: float  # sales price without taxes
    special_sale: str  # name of the special sale of the pricelist rule, or ""

_logger = logging.getLogger(__name__)


def file_name_part(value):
    """A part of the prescribed file name: no separators (_) or path characters."""
    return re.sub(r"\s+", " ", re.sub(r"[_/\\]+", "-", value or "")).strip()


class L10nHrPriceListLocation(models.Model):
    _name = "l10n_hr.price.list.location"
    _description = "Price List Premises"
    _order = "company_id, object_code, id"

    name = fields.Char(compute="_compute_name", store=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company", string="Company", required=True, index=True, default=lambda self: self.env.company,
    )
    object_type = fields.Char(
        string="Type of Premises",
        required=True,
        help="First part of the file name, e.g. prodavaonica, ured, servis, salon or webshop.",
    )
    address = fields.Char(
        string="Address of Premises",
        help="Second part of the file name, e.g. Ilica 150 Zagreb. Empty: street and city of the company.",
    )
    object_code = fields.Char(
        string="Premises Label",
        required=True,
        default="01",
        help="Third part of the file name: your label of the premises (e.g. P-01, U-03), or 01 if you have none. "
        "Also the public link of its price list: /cjenik/<label>.",
    )
    category_ids = fields.Many2many(
        "product.category",
        "l10n_hr_price_list_location_category_rel",
        "location_id",
        "category_id",
        string="Product Categories",
        help="Optional. Active sellable products of these categories and their subcategories are published. "
        "Empty: all active sellable products.",
    )
    webhook_url = fields.Char(
        string="Webhook URL",
        groups="base.group_system",
        help="Optional. Every new version of this price list is sent here (POST, JSON), e.g. to "
        "publish it on your own website.",
    )
    webhook_secret = fields.Char(
        string="Webhook Secret",
        groups="base.group_system",
        help="Optional. Each request is signed with it: header X-Price-List-Signature: sha256=<HMAC of the body>.",
    )
    version_ids = fields.One2many("l10n_hr.price.list.version", "location_id", string="Versions")
    version_count = fields.Integer(compute="_compute_version_count")
    url = fields.Char(string="Public Link", compute="_compute_url")

    _company_code_uniq = models.Constraint(
        "UNIQUE(company_id, object_code)",
        "Each premises needs its own label.",
    )

    @api.depends("object_type", "address", "object_code", "company_id.street", "company_id.city")
    def _compute_name(self):
        for location in self:
            location.name = location._file_prefix()

    @api.depends("version_ids")
    def _compute_version_count(self):
        for location in self:
            location.version_count = len(location.version_ids)

    @api.depends("object_code")
    def _compute_url(self):
        for location in self:
            code = file_name_part(location.object_code)
            location.url = f"{location.get_base_url()}/cjenik/{quote(code)}" if code else False

    def _address(self):
        self.ensure_one()
        company = self.company_id
        return self.address or " ".join(part for part in (company.street, company.city) if part)

    def _file_prefix(self):
        """oblik objekta_adresa objekta_oznaka objekta (Ministry of Economy, point 2.4)."""
        self.ensure_one()
        return "_".join(file_name_part(part) for part in (self.object_type, self._address(), self.object_code))

    def _problem(self):
        """What is missing for a price list, or False."""
        self.ensure_one()
        missing = [
            label for label, value in (
                (_("Type of Premises"), file_name_part(self.object_type)),
                (_("Address of Premises"), file_name_part(self._address())),
                (_("Premises Label"), file_name_part(self.object_code)),
            ) if not value
        ]
        if missing:
            return _("The public price list %(premises)s needs: %(fields)s.", premises=self.name, fields=", ".join(missing))
        return False

    @api.model_create_multi
    def create(self, vals_list):
        locations = super().create(vals_list)
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return locations

    def write(self, vals):
        result = super().write(vals)
        if vals.get("webhook_url"):
            # The website gets the current version when the webhook is set.
            for location in self.sudo():
                current = location._current_version()
                if current.webhook_state == "none":
                    current.webhook_state = "pending"
        self.env["l10n_hr.price.list.version"]._trigger_publish()
        return result

    @api.ondelete(at_uninstall=False)
    def _unlink_except_published(self):
        if self.sudo().version_ids:
            raise UserError(_("A published price list must stay public. Archive the premises instead."))

    def _lang(self):
        """Croatian when installed (the price list is for Croatian consumers), otherwise the
        language of the company."""
        self.ensure_one()
        if self.env["res.lang"].sudo().search_count([("code", "=", "hr_HR")], limit=1):
            return "hr_HR"
        return self.company_id.partner_id.lang or self.env.lang

    def _current_version(self):
        self.ensure_one()
        return self.env["l10n_hr.price.list.version"].sudo().search([("location_id", "=", self.id)], limit=1)

    # ------------------------------------------------------------------
    # Content
    # ------------------------------------------------------------------

    def _products(self):
        """Active sellable products of the categories (and their subcategories); without
        categories all active sellable products."""
        self.ensure_one()
        domain = [("categ_id", "child_of", self.category_ids.ids)] if self.category_ids else []
        return self.env["product.product"].with_company(self.company_id).search(domain + [
            ("sale_ok", "=", True),
            ("type", "!=", "combo"),
            ("company_id", "in", [False, self.company_id.id]),
        ], order="default_code, name, id")

    def _consumer_pricelist(self):
        """The pricelist Odoo gives a customer from the country of the company without a pricelist of
        their own (as on a quotation); none when Pricelists are turned off."""
        self.ensure_one()
        Pricelist = self.env["product.pricelist"].sudo().with_company(self.company_id)
        if not self.env["res.groups"]._is_feature_enabled("product.group_product_pricelist"):
            return Pricelist
        country = self.company_id.country_id
        if country:
            return Pricelist._get_country_pricelist_multi([country.id])[country.id]
        return Pricelist.search(Pricelist._get_partner_pricelist_multi_search_domain_hook(self.company_id.id), limit=1)

    def _prices(self, products):
        """{product id: Price}.

        The price for a consumer is the price of the consumer pricelist (its rule for the product, e.g. a
        discount for a period) or the sales price, with the taxes of the product, as on an invoice without
        a fiscal position. A rule with the name of a special sale makes it a special sale price; the regular
        price is the sales price with taxes. The sales price without taxes is sent on the webhook (e.g. for
        showing prices to companies on the website)."""
        self.ensure_one()
        company = self.company_id
        currency = company.currency_id
        pricelist = self._consumer_pricelist()
        rules = pricelist._compute_price_rule(products, 1.0, currency=currency) if pricelist else {}
        names = {rule.id: (rule.price_list_special_sale or "").strip()
                 for rule in self.env["product.pricelist.item"].sudo().browse([rule for __, rule in rules.values() if rule])}
        result = {}
        for product in products:
            taxes = product.taxes_id._filter_taxes_by_company(company)
            regular = taxes.compute_all(product.lst_price, currency=currency, quantity=1.0, product=product)
            price, rule = rules.get(product.id, (0.0, False))
            if rule:
                price = taxes.compute_all(price, currency=currency, quantity=1.0, product=product)["total_included"]
            else:
                price = regular["total_included"]
            result[product.id] = Price(
                consumer=currency.round(price),
                regular=currency.round(regular["total_included"]),
                net=currency.round(regular["total_excluded"]),
                special_sale=names.get(rule, ""),
            )
        return result

    def _availability(self, product):
        """dostupno / nedostupno for goods; empty for services. Stock only counts when the
        Inventory app is installed and the product is tracked (stock of the company; of the
        warehouse of the premises with l10n_hr_price_list_stock)."""
        if product.type == "service":
            return ""
        if "is_storable" in product._fields and product.is_storable:
            return "dostupno" if product.qty_available > 0 else "nedostupno"
        return "dostupno"

    @api.model
    def _base_unit(self, product, price):
        """Price per base unit (e.g. per kg or l) when the product has one (eCommerce)."""
        if "base_unit_id" in product._fields and product.base_unit_id and product.base_unit_count:
            return format_amount(price / product.base_unit_count), product.base_unit_id.name
        return "", ""

    def _row(self, product, price, anchor, special_sale=""):
        """One line of the price list."""
        unit_price, base_unit = self._base_unit(product, price)
        return {
            "sifra": product.default_code or "",
            "naziv": product.with_context(display_default_code=False).display_name,
            "marka": product.price_list_brand or "",
            "jedinica_mjere": product.uom_id.name or "",
            "maloprodajna_cijena_eur": format_amount(price),
            "cijena_za_jedinicu_mjere_eur": unit_price,
            "jedinica_mjere_za_cijenu": base_unit,
            "posebni_oblik_prodaje": "da" if special_sale else "ne",
            "naziv_posebnog_oblika_prodaje": special_sale,
            "dodatna_cijena_eur": format_amount(anchor.price),
            "datum_dodatne_cijene": format_date(anchor.date),
            "barkod": product.barcode or "",
            "raspolozivost": self._availability(product),
        }

    def _rows(self):
        """Lines of the price list. A product published here for the first time gets its
        additional price: its current price, dated today (during a special sale the regular price).
        Products without a price are left out (their additional price would be 0)."""
        self.ensure_one()
        currency = self.company_id.currency_id
        products = self._products().with_context(lang=self._lang())
        prices = self._prices(products)
        products = products.filtered(lambda product: not currency.is_zero(prices[product.id].consumer))
        # Saving the additional prices must not schedule another check of this price list.
        Anchor = self.env["l10n_hr.price.list.anchor"].sudo().with_context(l10n_hr_price_list_publishing=True)
        anchors = {anchor.product_id.id: anchor for anchor in Anchor.search([("location_id", "=", self.id)])}
        today = local_now().date()
        new = Anchor.create([
            {"location_id": self.id, "product_id": product.id, "date": today,
             "price": prices[product.id].regular if prices[product.id].special_sale else prices[product.id].consumer}
            for product in products if product.id not in anchors
        ])
        anchors.update({anchor.product_id.id: anchor for anchor in new})
        on_sale = [product.id for product in products if prices[product.id].special_sale]
        sale_prices = self._special_sale_prices(products, on_sale) if on_sale else {}
        rows = []
        for product in products:
            price = prices[product.id]
            row = self._row(product, price.consumer, anchors[product.id], price.special_sale)
            row[NET_COLUMN] = format_amount(price.net)
            if product.id in sale_prices:
                price_before, lowest_price = sale_prices[product.id]
                row[PRICE_BEFORE_SALE_COLUMN] = format_amount(price_before)
                row[LOWEST_PRICE_COLUMN] = format_amount(lowest_price)
            row[PRODUCT_KEY] = product.id
            rows.append(row)
        return rows

    def _special_sale_prices(self, products, product_ids):
        """{product id: (price before its special sale, lowest price in the LOWEST_PRICE_DAYS days before
        it)} from the price lists published for this premises. The sale began with the oldest of the
        latest versions in a row that show it on special sale (now, when none does yet)."""
        self.ensure_one()
        by_code = {product.default_code: product.id for product in products if product.default_code}
        start = dict.fromkeys(product_ids, fields.Datetime.now())
        price_before, prices = {}, defaultdict(list)
        looking, done = set(product_ids), set()
        versions = self.env["l10n_hr.price.list.version"].sudo().search(
            [("location_id", "=", self.id)], order="published_at desc, id desc",
        )
        for version in versions:
            rows = {}
            for row in json.loads(version.rows_json or "[]"):
                product_id = row.get(PRODUCT_KEY) or by_code.get(row.get("sifra"))  # older versions: by code
                if product_id:
                    rows[product_id] = row
            for product_id in product_ids:
                if product_id in done:
                    continue
                row = rows.get(product_id)
                if product_id in looking:
                    if row and row.get("posebni_oblik_prodaje") == "da":
                        start[product_id] = version.published_at
                        continue
                    looking.discard(product_id)
                    price_before[product_id] = parse_amount(row["maloprodajna_cijena_eur"]) if row else 0.0
                # Published before the sale: valid in the days before it, back to the version that was
                # current when they began.
                if row:
                    prices[product_id].append(parse_amount(row["maloprodajna_cijena_eur"]))
                if version.published_at <= start[product_id] - timedelta(days=LOWEST_PRICE_DAYS):
                    done.add(product_id)
            if len(done) == len(product_ids):
                break
        return {
            product_id: (price_before.get(product_id, 0.0), min(prices[product_id], default=0.0))
            for product_id in product_ids
        }

    @api.model
    def _csv(self, rows):
        """UTF-8 with BOM (opens correctly in Excel), semicolons, decimal comma."""
        buffer = io.StringIO()
        writer = csv.DictWriter(buffer, fieldnames=COLUMNS, delimiter=";", lineterminator="\r\n", extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue().encode("utf-8-sig")

    # ------------------------------------------------------------------
    # Publication
    # ------------------------------------------------------------------

    def _publish(self):
        """Publish a new version when the rows (also the sales prices sent on the webhook) or the
        file name changed, and the first time each day also without changes, so there is a file of
        the day (shops update the price list every day by 08:00; the morning cron runs before).

        :returns: the new version, or an empty recordset when nothing changed today
        """
        self.ensure_one()
        problem = self._problem()
        if problem:
            raise UserError(problem)
        location = self.sudo()
        rows = location._rows()
        content = location._csv(rows)
        prefix = location._file_prefix()
        rows_json = json.dumps(rows, ensure_ascii=False, sort_keys=True)
        published = json.dumps(public_rows(rows), ensure_ascii=False, sort_keys=True)
        checksum = hashlib.sha256(prefix.encode() + b"\0" + published.encode()).hexdigest()
        current = location._current_version()
        if current.checksum == checksum and local_time(current.published_at).date() == local_now().date():
            return current.browse()
        number = current.number + 1
        name = f"{prefix}_{number:03d}_{local_now():%d.%m.%Y_%H:%M}.csv"
        version = current.create({
            "location_id": location.id,
            "number": number,
            "name": name,
            "published_at": fields.Datetime.now(),
            "file": base64.b64encode(content),
            "checksum": checksum,
            "rows_json": rows_json,
            "line_count": len(rows),
            "webhook_state": "pending" if location.webhook_url else "none",
        })
        _logger.info("Price list %s published for %s", name, location.company_id.name)
        return version

    def _send_webhooks(self):
        """Send unsent versions oldest first; stop at the first error (tried again later),
        so the website gets them in order."""
        for location in self.sudo():
            if not location.webhook_url:
                continue
            versions = location.version_ids.filtered(lambda v: v.webhook_state in ("pending", "error"))
            for version in versions.sorted("number"):
                if not version._webhook_send():
                    break

    def action_publish(self):
        """Publish now (administrators): a new version if anything changed, then the webhook."""
        self.ensure_one()
        if not self.env.user.has_group("base.group_system"):
            raise AccessError(_("Only administrators can publish the price list."))
        version = self._publish()
        self._send_webhooks()
        current = self._current_version()
        if version:
            message = _("New price list published: %(name)s", name=current.name)
        else:
            message = _("No changes: the current price list is %(name)s", name=current.name)
        notification_type = "success"
        if current.webhook_state == "error":
            message += "\n" + _("Not sent to the webhook: %(error)s. Odoo tries again in an hour.", error=current.webhook_error)
            notification_type = "warning"
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": message,
                "type": notification_type,
                "sticky": notification_type == "warning",
                "next": {"type": "ir.actions.client", "tag": "soft_reload"},
            },
        }

    def action_versions(self):
        action = self.env["ir.actions.act_window"]._for_xml_id("l10n_hr_price_list.action_price_list_version")
        action["domain"] = [("location_id", "in", self.ids)]
        return action
