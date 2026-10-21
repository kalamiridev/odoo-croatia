from urllib.parse import quote

from odoo import Command
from odoo.tests import HttpCase, tagged

from .common import PriceListCommon


@tagged("post_install", "-at_install")
class TestPriceListPublic(PriceListCommon, HttpCase):

    def setUp(self):
        super().setUp()
        self.authenticate(None, None)  # public visitor of this database
        # Premises of other companies of the test database are not part of the test.
        self.env["l10n_hr.price.list.location"].sudo().search([("id", "!=", self.location.id)]).active = False

    def test_public_without_login(self):
        old = self.location._publish()
        self.service.list_price = 120.0
        current = self.location._publish()

        response = self.url_open("/cjenik", allow_redirects=False)
        self.assertIn(response.status_code, (302, 303))
        self.assertTrue(response.headers["Location"].endswith(f"/cjenik/{quote(current.name)}"))

        response = self.url_open("/cjenik/U-03", allow_redirects=False)
        self.assertTrue(response.headers["Location"].endswith(f"/cjenik/{quote(current.name)}"), "By premises label")

        response = self.url_open(f"/cjenik/{quote(current.name)}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("150,00", response.content.decode("utf-8-sig"))

        response = self.url_open(f"/cjenik/{quote(old.name)}")
        self.assertEqual(response.status_code, 200, "Previous versions stay public")
        self.assertIn("125,00", response.content.decode("utf-8-sig"))

        response = self.url_open("/cjenik/arhiva")
        self.assertEqual(response.status_code, 200)
        self.assertIn(old.name, response.text)
        self.assertIn(current.name, response.text)

        self.assertEqual(self.url_open("/cjenik/nothing.csv").status_code, 404)

    def test_two_premises_listed(self):
        webshop = self.env["l10n_hr.price.list.location"].create({
            "company_id": self.company.id,
            "object_type": "webshop",
            "object_code": "02",
            "category_ids": [Command.set(self.category.ids)],
        })
        office = self.location._publish()
        shop = webshop._publish()
        response = self.url_open("/cjenik", allow_redirects=False)
        self.assertEqual(response.status_code, 200)
        self.assertIn(office.name, response.text)
        self.assertIn(shop.name, response.text)
        response = self.url_open("/cjenik/02", allow_redirects=False)
        self.assertTrue(response.headers["Location"].endswith(f"/cjenik/{quote(shop.name)}"))

    def test_archived_premises_not_listed(self):
        version = self.location._publish()
        self.location.active = False
        self.assertEqual(self.url_open("/cjenik", allow_redirects=False).status_code, 404)
        self.assertEqual(self.url_open(f"/cjenik/{quote(version.name)}").status_code, 200, "Files stay public")
