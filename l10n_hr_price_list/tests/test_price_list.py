import base64
import hashlib
import hmac
import json
from datetime import date, datetime, timedelta
from unittest.mock import patch

import requests
from freezegun import freeze_time

from odoo import Command, fields
from odoo.exceptions import AccessError, UserError
from odoo.tests import tagged
from odoo.tests.common import new_test_user
from odoo.tools import mute_logger

from odoo.addons.l10n_hr_price_list.models.price_list_version import COLUMNS

from .common import PriceListCommon

LOGGER = "odoo.addons.l10n_hr_price_list.models"
POST = f"{LOGGER}.price_list_version.requests.post"


@freeze_time("2026-10-20 05:00:00")  # 07:00 in Zagreb
@tagged("post_install", "-at_install")
class TestPriceList(PriceListCommon):

    def test_first_publication(self):
        version = self.location._publish()
        self.assertEqual(version.number, 1)
        self.assertEqual(version.name, "servis_Vukovarska 20 Osijek_U-03_001_20.10.2026_07:00.csv")
        self.assertEqual(self.location.name, "servis_Vukovarska 20 Osijek_U-03")
        self.assertTrue(version.is_current)
        self.assertEqual(version.line_count, 2)
        content = base64.b64decode(version.file).decode("utf-8-sig")
        self.assertEqual(content.split("\r\n")[0], ";".join(COLUMNS))
        lines = self._lines(version)
        self.assertEqual(set(lines), {"SRV-1", "GDS-1"}, "Subcategories in, other categories out")
        self.assertEqual(lines["SRV-1"], {
            "sifra": "SRV-1",
            "naziv": "Setup",
            "marka": "",
            "jedinica_mjere": self.service.uom_id.with_context(lang=self.location._lang()).name,
            "maloprodajna_cijena_eur": "125,00",
            "cijena_za_jedinicu_mjere_eur": "",
            "jedinica_mjere_za_cijenu": "",
            "posebni_oblik_prodaje": "ne",
            "naziv_posebnog_oblika_prodaje": "",
            "dodatna_cijena_eur": "125,00",
            "datum_dodatne_cijene": "20.10.2026",
            "barkod": "",
            "raspolozivost": "",
        })
        goods = lines["GDS-1"]
        self.assertEqual(goods["maloprodajna_cijena_eur"], "125,00", "Tax included in the price")
        self.assertEqual(goods["marka"], "Acme")
        self.assertEqual(goods["barkod"], "3850000000001")
        self.assertEqual(goods["raspolozivost"], "dostupno")
        anchor = self._anchor(self.service)
        self.assertEqual((anchor.price, anchor.date), (125.0, date(2026, 10, 20)))
        self.assertEqual(anchor.product_tmpl_id, self.service.product_tmpl_id)
        self.assertIn(anchor, self.service.product_tmpl_id.price_list_anchor_ids)
        self.assertTrue(self.goods.product_tmpl_id.price_list_published)
        self.assertFalse(self.hidden.product_tmpl_id.price_list_published)

    def test_new_version_only_on_change(self):
        first = self.location._publish()
        self.assertFalse(self.location._publish(), "Nothing changed: no new version")
        with freeze_time("2026-10-21 05:30:00"):
            self.service.list_price = 120.0
            second = self.location._publish()
        self.assertEqual(second.number, 2)
        self.assertEqual(second.name, "servis_Vukovarska 20 Osijek_U-03_002_21.10.2026_07:30.csv")
        self.assertTrue(second.is_current)
        self.assertFalse(first.is_current)
        line = self._lines(second)["SRV-1"]
        self.assertEqual(line["maloprodajna_cijena_eur"], "150,00")
        self.assertEqual(line["dodatna_cijena_eur"], "125,00", "The additional price does not follow the price")
        self.assertEqual(line["datum_dodatne_cijene"], "20.10.2026")
        self.assertEqual(self._lines(first)["SRV-1"]["maloprodajna_cijena_eur"], "125,00", "Old file unchanged")

    def test_new_version_every_day(self):
        """The first check of a day publishes a file of that day also without changes; later the same
        day only changes do."""
        first = self.location._publish()
        with freeze_time("2026-10-21 04:00:00"):  # the morning cron, 06:00 in Zagreb
            second = self.location._publish()
            self.assertFalse(self.location._publish(), "Once a day without changes")
        self.assertEqual(second.number, 2)
        self.assertEqual(second.name, "servis_Vukovarska 20 Osijek_U-03_002_21.10.2026_06:00.csv")
        self.assertEqual(second.checksum, first.checksum, "The same content")
        self.assertEqual(self._lines(second), self._lines(first))
        self.assertTrue(second.is_current)

    def test_new_product_gets_its_own_date(self):
        self.location._publish()
        with freeze_time("2026-11-02 06:00:00"):
            self._product("NEW-1", "New sensor", 40.0, self.tax_25)
            version = self.location._publish()
        line = self._lines(version)["NEW-1"]
        self.assertEqual(line["dodatna_cijena_eur"], "50,00")
        self.assertEqual(line["datum_dodatne_cijene"], "02.11.2026")
        self.assertEqual(self._lines(version)["SRV-1"]["datum_dodatne_cijene"], "20.10.2026")

    def test_reference_day_price_by_admin(self):
        self.Anchor.create({
            "location_id": self.location.id, "product_id": self.service.id, "price": 110.0, "date": date(2026, 9, 10),
        })
        line = self._lines(self.location._publish())["SRV-1"]
        self.assertEqual(line["dodatna_cijena_eur"], "110,00")
        self.assertEqual(line["datum_dodatne_cijene"], "10.09.2026")

    def test_additional_price_admin_only(self):
        self.location._publish()
        user = new_test_user(
            self.env, login="price_list_seller",
            groups="base.group_user,account.group_account_manager,product.group_product_manager",
        )
        anchor = self._anchor(self.service).with_user(user)
        self.assertEqual(anchor.price, 125.0, "Everybody sees it")
        with self.assertRaises(AccessError):
            anchor.price = 1.0
        self.service.with_user(user).list_price = 90.0  # ordinary changes still work

    def test_two_premises(self):
        """Each premises: its own categories, numbers and additional prices."""
        webshop = self.env["l10n_hr.price.list.location"].create({
            "company_id": self.company.id,
            "object_type": "webshop",
            "object_code": "02",
            "category_ids": [Command.set((self.category | self.other_category).ids)],
        })
        self.location._publish()
        self.service.list_price = 120.0
        self.location._publish()
        version = webshop._publish()
        self.assertEqual(version.number, 1, "Own storage numbers")
        self.assertEqual(version.name, "webshop_Vukovarska 20 Osijek_02_001_20.10.2026_07:00.csv")
        lines = self._lines(version)
        self.assertEqual(set(lines), {"SRV-1", "GDS-1", "HID-1"})
        self.assertEqual(lines["SRV-1"]["maloprodajna_cijena_eur"], "150,00")
        self.assertEqual(lines["SRV-1"]["dodatna_cijena_eur"], "150,00", "Own additional price")
        self.assertEqual(self._lines(self.location._current_version())["SRV-1"]["dodatna_cijena_eur"], "125,00")

    def test_sales_price_with_taxes_and_zero_price(self):
        """Pricelists turned off: the sales price with taxes (also when a pricelist has a rule for the
        product); a product without a price is not published."""
        self.env["product.pricelist"].create({
            "name": "Consumers",
            "item_ids": [Command.create({
                "applied_on": "0_product_variant", "product_id": self.service.id,
                "compute_price": "fixed", "fixed_price": 80.0,
            })],
        })
        self._product("FREE-1", "Free", 0.0, self.tax_25)
        version = self.location._publish()
        lines = self._lines(version)
        self.assertEqual(lines["SRV-1"]["maloprodajna_cijena_eur"], "125,00")
        self.assertNotIn("FREE-1", lines, "A product without a price is not published")
        rows = {row["sifra"]: row for row in json.loads(version.rows_json)}
        self.assertEqual(rows["SRV-1"]["prodajna_cijena_bez_pdv_eur"], "100,00")

    def test_without_categories_all_sellable_products(self):
        no_category = self._product("NOC-1", "Without category", 20.0, self.tax_25, categ_id=False)
        self.service.sale_ok = False
        self.location.category_ids = False
        self.env.invalidate_all()
        self.assertTrue(no_category.price_list_published, "Shown on the product")
        self.assertFalse(self.service.price_list_published, "Not sellable")
        lines = self._lines(self.location._publish())
        self.assertLessEqual({"GDS-1", "HID-1", "NOC-1"}, set(lines), "Every category and none")
        self.assertNotIn("SRV-1", lines)
        self.assertEqual(lines["NOC-1"]["maloprodajna_cijena_eur"], "25,00")

    def _pricelist(self):
        """The pricelist of a customer without one of their own, with Pricelists turned on (Sales settings)."""
        self.env["res.config.settings"].create({"group_product_pricelist": True}).execute()
        pricelist = self.location._consumer_pricelist()
        self.assertTrue(pricelist, "Turning Pricelists on gives the company a pricelist")
        return pricelist

    def _sale(self, pricelist, name="Autumn sale", start=None, end=None, product=None):
        return self.env["product.pricelist.item"].create({
            "pricelist_id": pricelist.id,
            "applied_on": "0_product_variant",
            "product_id": (product or self.goods).id,
            "compute_price": "percentage",
            "percent_price": 20.0,
            "date_start": start,
            "date_end": end,
            "price_list_special_sale": name,
        })

    def _rows(self, version):
        return {row["sifra"]: row for row in json.loads(version.rows_json)}

    def _publish_on(self, day, price):
        with freeze_time(f"{day} 05:00:00"):
            self.goods.list_price = price  # tax included: the consumer price
            return self.location._publish()

    def test_consumer_pricelist(self):
        """Prices as on a quotation for a customer without a pricelist of their own; a rule without the
        name of a special sale is a regular price (also for the additional price)."""
        pricelist = self._pricelist()
        pricelist.item_ids = [Command.create({
            "applied_on": "0_product_variant", "product_id": self.service.id,
            "compute_price": "fixed", "fixed_price": 80.0,
        })]
        version = self.location._publish()
        service = self._lines(version)["SRV-1"]
        self.assertEqual(service["maloprodajna_cijena_eur"], "100,00", "Rule price with taxes")
        self.assertEqual((service["posebni_oblik_prodaje"], service["dodatna_cijena_eur"]), ("ne", "100,00"))
        self.assertEqual(self._rows(version)["SRV-1"]["prodajna_cijena_bez_pdv_eur"], "100,00", "Sales price")
        self.assertEqual(self._lines(version)["GDS-1"]["maloprodajna_cijena_eur"], "125,00", "No rule")
        pricelist.action_archive()  # as when Pricelists are turned off
        self.assertEqual(self._lines(self.location._publish())["SRV-1"]["maloprodajna_cijena_eur"], "125,00")

    def test_special_sale_rule(self):
        """A rule with the name of a special sale and a period: the special sale price while it runs, the
        price before it and the lowest price in the 30 days before it (also from the price list that was
        current when the 30 days began) on the webhook."""
        pricelist = self._pricelist()
        self._publish_on("2026-09-01", 105.0)  # current on 20.09., when the 30 days begin
        self._publish_on("2026-10-01", 125.0)
        self._publish_on("2026-10-10", 120.0)
        self._publish_on("2026-10-15", 125.0)
        rule = self._sale(pricelist, start=datetime(2026, 10, 20, 0, 0), end=datetime(2026, 10, 31, 22, 59))
        version = self.location._publish()
        goods = self._lines(version)["GDS-1"]
        self.assertEqual(goods["maloprodajna_cijena_eur"], "100,00", "20 % off the sales price")
        self.assertEqual((goods["posebni_oblik_prodaje"], goods["naziv_posebnog_oblika_prodaje"]), ("da", "Autumn sale"))
        self.assertEqual(goods["dodatna_cijena_eur"], "105,00", "The additional price does not change")
        row = self._rows(version)["GDS-1"]
        self.assertEqual(row["cijena_prije_posebnog_oblika_prodaje_eur"], "125,00")
        self.assertEqual(row["najniza_cijena_30_dana_eur"], "105,00")
        self.assertNotIn("najniza_cijena_30_dana_eur", self._rows(version)["SRV-1"], "Only during a sale")
        content = base64.b64decode(version.file).decode("utf-8-sig")
        self.assertEqual(content.splitlines()[0].split(";"), COLUMNS, "The prescribed file is not changed")
        self.assertNotIn("_product_id", content)

        with freeze_time("2026-10-25 05:00:00"):  # renamed while it runs: the same sale
            rule.price_list_special_sale = "Autumn sale -20%"
            row = self._rows(self.location._publish())["GDS-1"]
        self.assertEqual((row["cijena_prije_posebnog_oblika_prodaje_eur"], row["najniza_cijena_30_dana_eur"]), ("125,00", "105,00"))
        with freeze_time("2026-11-01 05:00:00"):  # the morning after the end
            goods = self._lines(self.location._publish())["GDS-1"]
        self.assertEqual((goods["posebni_oblik_prodaje"], goods["maloprodajna_cijena_eur"]), ("ne", "125,00"))

    def test_special_sale_older_price_lists_not_counted(self):
        pricelist = self._pricelist()
        self._publish_on("2026-08-01", 105.0)
        self._publish_on("2026-09-15", 125.0)  # current on 20.09.: the 105,00 before it does not count
        self._sale(pricelist)
        row = self._rows(self.location._publish())["GDS-1"]
        self.assertEqual((row["cijena_prije_posebnog_oblika_prodaje_eur"], row["najniza_cijena_30_dana_eur"]), ("125,00", "125,00"))

    def test_special_sale_found_by_code_in_older_versions(self):
        """Versions published before 19.0.2.7.0 have no product key in their rows."""
        pricelist = self._pricelist()
        version = self.location._publish()
        rows = [{key: value for key, value in row.items() if key != "_product_id"} for row in json.loads(version.rows_json)]
        version.rows_json = json.dumps(rows)
        self._sale(pricelist)
        self.assertEqual(self._rows(self.location._publish())["GDS-1"]["cijena_prije_posebnog_oblika_prodaje_eur"], "125,00")

    def test_new_product_on_special_sale(self):
        """First published during a special sale: the additional price is the regular price."""
        self._sale(self._pricelist(), name="Opening sale")
        version = self.location._publish()
        goods = self._lines(version)["GDS-1"]
        self.assertEqual((goods["maloprodajna_cijena_eur"], goods["dodatna_cijena_eur"]), ("100,00", "125,00"))
        row = self._rows(version)["GDS-1"]
        self.assertEqual((row["cijena_prije_posebnog_oblika_prodaje_eur"], row["najniza_cijena_30_dana_eur"]), ("0,00", "0,00"))

    def test_special_sale_two_premises(self):
        pricelist = self._pricelist()
        webshop = self.env["l10n_hr.price.list.location"].create({
            "company_id": self.company.id, "object_type": "webshop", "object_code": "02",
            "category_ids": [Command.set(self.category.ids)],
        })
        self._sale(pricelist)
        for location in self.location | webshop:
            goods = self._lines(location._publish())["GDS-1"]
            self.assertEqual((goods["posebni_oblik_prodaje"], goods["maloprodajna_cijena_eur"]), ("da", "100,00"))

    def test_pricelist_rule_change_triggers_check(self):
        pricelist = self._pricelist()
        cron = self.env.ref("l10n_hr_price_list.ir_cron_price_list_publish")
        triggers = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)])
        self.env.cr.precommit.data.pop("l10n_hr_price_list.triggered", None)  # a new transaction
        self._sale(pricelist)
        self.assertTrue(self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)]) - triggers)

    def test_archived_and_not_sellable_left_out(self):
        self.goods.active = False
        self.service.sale_ok = False
        self.assertFalse(self._lines(self.location._publish()))

    def test_file_name_parts(self):
        self.location.write({"object_type": "web_shop", "address": "Ilica 15/2  Zagreb", "object_code": "01"})
        self.assertEqual(self.location.name, "web-shop_Ilica 15-2 Zagreb_01")
        self.assertTrue(self.location.url.endswith("/cjenik/01"))
        self.location.address = False
        self.assertEqual(self.location.name, "web-shop_Vukovarska 20 Osijek_01")

    def test_file_name_change_is_new_version(self):
        self.location._publish()
        self.location.object_code = "U-04"
        version = self.location._publish()
        self.assertEqual(version.name, "servis_Vukovarska 20 Osijek_U-04_002_20.10.2026_07:00.csv")

    def test_missing_settings(self):
        self.company.write({"street": False, "city": False})
        with self.assertRaisesRegex(UserError, "Address of Premises"):
            self.location._publish()
        with mute_logger(f"{LOGGER}.price_list_version"):
            self.Version._cron_publish()  # logged, not raised
        self.assertFalse(self.location.version_ids)

    def test_archive_kept_30_days(self):
        version = self.location._publish()
        with self.assertRaises(UserError):
            version.unlink()
        with self.assertRaises(UserError):
            self.location.unlink()
        version.published_at = fields.Datetime.now() - timedelta(days=31)
        version.unlink()

    def test_change_triggers_check(self):
        cron = self.env.ref("l10n_hr_price_list.ir_cron_price_list_publish")
        triggers = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)])
        self.env.cr.precommit.data.pop("l10n_hr_price_list.triggered", None)  # a new transaction
        self.service.list_price = 99.0
        self.service.barcode = "3850000000002"
        new = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)]) - triggers
        self.assertEqual(new.call_at, datetime(2026, 10, 20, 5, 1), "One check per transaction")

    def test_publish_does_not_schedule_another_check(self):
        """Saving the additional prices while publishing must not schedule the cron again."""
        cron = self.env.ref("l10n_hr_price_list.ir_cron_price_list_publish")
        triggers = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)])
        self.env.cr.precommit.data.pop("l10n_hr_price_list.triggered", None)  # a new transaction
        self.location._publish()
        self.assertTrue(self._anchor(self.service))
        self.assertFalse(self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id)]) - triggers)

    def test_availability_from_stock(self):
        if "is_storable" not in self.env["product.product"]._fields:
            self.skipTest("Inventory is not installed")
        self.goods.is_storable = True
        self.assertEqual(self._lines(self.location._publish())["GDS-1"]["raspolozivost"], "nedostupno")
        warehouse = self.env["stock.warehouse"].search([("company_id", "=", self.company.id)], limit=1)
        self.env["stock.quant"]._update_available_quantity(self.goods, warehouse.lot_stock_id, 3)
        self.service.is_storable = True  # possible in the database, meaningless for a service
        self.env.invalidate_all()  # the cron runs in a new transaction
        lines = self._lines(self.location._publish())
        self.assertEqual(lines["GDS-1"]["raspolozivost"], "dostupno")
        self.assertEqual(lines["SRV-1"]["raspolozivost"], "", "Services have no availability")

    def test_cron(self):
        self.Version._cron_publish()
        self.Version._cron_publish()
        self.assertEqual(self.location.version_ids.mapped("number"), [1])
        self.assertEqual(self.location.version_ids.webhook_state, "none")

    def test_current_version_and_webhook_set_later(self):
        version = self.location._publish()
        self.assertTrue(version.is_current)
        self.assertEqual(self.location._current_version(), version)


@freeze_time("2026-10-20 05:00:00")
@tagged("post_install", "-at_install")
class TestPriceListWebhook(PriceListCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.location.write({"webhook_url": "https://www.example.com/hook", "webhook_secret": "s3cret"})

    def _response(self, status=200):
        response = requests.Response()
        response.status_code = status
        response.url = "https://www.example.com/hook"
        return response

    def test_sent_signed(self):
        with patch(POST, return_value=self._response()) as post:
            self.Version._cron_publish()
        version = self.location.version_ids
        self.assertEqual(version.webhook_state, "sent")
        self.assertEqual(post.call_count, 1)
        self.assertEqual(post.call_args.args[0], "https://www.example.com/hook")
        body = post.call_args.kwargs["data"]
        signature = hmac.new(b"s3cret", body, hashlib.sha256).hexdigest()
        self.assertEqual(post.call_args.kwargs["headers"]["X-Price-List-Signature"], f"sha256={signature}")
        payload = json.loads(body)
        self.assertEqual(payload["event"], "price_list.published")
        self.assertEqual(payload["premises_label"], "U-03")
        self.assertEqual(payload["number"], 1)
        self.assertEqual(payload["file_name"], version.name)
        self.assertEqual(payload["published_at"], "2026-10-20T07:00:00+02:00")
        self.assertEqual(base64.b64decode(payload["content_base64"]), base64.b64decode(version.file))
        rows = {row["sifra"]: row for row in payload["rows"]}
        self.assertEqual(rows["SRV-1"]["maloprodajna_cijena_eur"], "125,00")
        self.assertEqual(rows["SRV-1"]["prodajna_cijena_bez_pdv_eur"], "100,00", "Sales price without VAT")
        self.assertEqual(rows["GDS-1"]["prodajna_cijena_bez_pdv_eur"], "100,00", "Tax included: price without it")
        self.assertNotIn("_product_id", rows["GDS-1"], "Saved with the rows, not sent")
        self.assertNotIn("prodajna_cijena_bez_pdv", base64.b64decode(version.file).decode("utf-8-sig"),
                         "Not in the prescribed file")

    def test_webhook_per_premises(self):
        other = self.env["l10n_hr.price.list.location"].create({
            "company_id": self.company.id,
            "object_type": "webshop",
            "object_code": "02",
            "category_ids": [Command.set(self.category.ids)],
            "webhook_url": "https://shop.example.com/hook",
        })
        with patch(POST, return_value=self._response()) as post:
            self.Version._cron_publish()
        self.assertEqual(sorted(c.args[0] for c in post.call_args_list),
                         ["https://shop.example.com/hook", "https://www.example.com/hook"])
        self.assertNotIn("X-Price-List-Signature", [
            c.kwargs["headers"] for c in post.call_args_list if c.args[0].startswith("https://shop")
        ][0])
        self.assertEqual(other.version_ids.webhook_state, "sent")

    @mute_logger(f"{LOGGER}.price_list_version")
    def test_error_retried_in_order(self):
        with patch(POST, side_effect=requests.ConnectionError("down")):
            self.Version._cron_publish()
            self.service.list_price = 120.0
            self.Version._cron_publish()
        versions = self.location.version_ids.sorted("number")
        self.assertEqual(versions.mapped("webhook_state"), ["error", "pending"], "Stops at the first error")
        self.assertIn("down", versions[0].webhook_error)
        cron = self.env.ref("l10n_hr_price_list.ir_cron_price_list_publish")
        retry = self.env["ir.cron.trigger"].search([("cron_id", "=", cron.id), ("call_at", "=", datetime(2026, 10, 20, 6, 0))])
        self.assertTrue(retry, "Tried again in an hour")
        self.env.invalidate_all()  # nothing computed yet, as after a restart: both versions are read together
        with patch(POST, return_value=self._response()) as post:
            self.Version._cron_publish()
        self.assertEqual(versions.mapped("webhook_state"), ["sent", "sent"])
        self.assertEqual([json.loads(c.kwargs["data"])["number"] for c in post.call_args_list], [1, 2])

    @mute_logger(f"{LOGGER}.price_list_version")
    def test_redirect_is_error(self):
        """A redirect is not followed (a redirected POST becomes a GET) and is not a success."""
        with patch(POST, return_value=self._response(301)) as post:
            self.Version._cron_publish()
        self.assertFalse(post.call_args.kwargs["allow_redirects"])
        version = self.location.version_ids
        self.assertEqual(version.webhook_state, "error")
        self.assertIn("301", version.webhook_error)

    @mute_logger(f"{LOGGER}.price_list_version")
    def test_http_error(self):
        with patch(POST, return_value=self._response(500)):
            self.Version._cron_publish()
        self.assertEqual(self.location.version_ids.webhook_state, "error")

    def test_webhook_set_later_sends_current(self):
        self.location.webhook_url = False
        version = self.location._publish()
        self.assertEqual(version.webhook_state, "none")
        self.location.webhook_url = "https://www.example.com/hook"
        self.assertEqual(version.webhook_state, "pending")

    def test_webhook_admin_only(self):
        user = new_test_user(self.env, login="price_list_manager", groups="base.group_user,account.group_account_manager")
        self.location.with_user(user).object_type = "salon"  # other settings: account managers
        with self.assertRaises(AccessError):
            self.location.with_user(user).write({"webhook_url": "https://evil.example.com"})

    def test_publish_now(self):
        with patch(POST, return_value=self._response()):
            action = self.location.action_publish()
        self.assertIn("New price list published", action["params"]["message"])
        with patch(POST, return_value=self._response()):
            action = self.location.action_publish()
        self.assertIn("No changes", action["params"]["message"])
