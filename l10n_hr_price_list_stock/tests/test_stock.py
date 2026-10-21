from odoo.tests import tagged

from odoo.addons.l10n_hr_price_list.tests.common import PriceListCommon


@tagged("post_install", "-at_install")
class TestPriceListStock(PriceListCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.goods.is_storable = True
        cls.main = cls.env["stock.warehouse"].search([("company_id", "=", cls.company.id)], limit=1)
        cls.shop = cls.env["stock.warehouse"].create({"name": "Shop 2", "code": "SH2", "company_id": cls.company.id})
        cls.env["stock.quant"]._update_available_quantity(cls.goods, cls.main.lot_stock_id, 3)

    def _availability(self):
        self.env.invalidate_all()  # the cron runs in a new transaction
        return self._lines(self.location._publish() or self.location._current_version())["GDS-1"]["raspolozivost"]

    def test_availability_per_warehouse(self):
        self.assertEqual(self._availability(), "dostupno", "Without a warehouse: stock of the company")
        self.location.warehouse_id = self.shop
        self.assertEqual(self._availability(), "nedostupno", "Nothing in the warehouse of the premises")
        self.env["stock.quant"]._update_available_quantity(self.goods, self.shop.lot_stock_id, 1)
        self.assertEqual(self._availability(), "dostupno")
        self.assertEqual(self._lines(self.location._current_version())["SRV-1"]["raspolozivost"], "", "Services")

    def test_two_premises_two_warehouses(self):
        shop = self.env["l10n_hr.price.list.location"].create({
            "company_id": self.company.id,
            "object_type": "prodavaonica",
            "object_code": "P-02",
            "category_ids": [(6, 0, self.category.ids)],
            "warehouse_id": self.shop.id,
        })
        self.location.warehouse_id = self.main
        self.env.invalidate_all()
        self.assertEqual(self._lines(self.location._publish())["GDS-1"]["raspolozivost"], "dostupno")
        self.assertEqual(self._lines(shop._publish())["GDS-1"]["raspolozivost"], "nedostupno")

    def test_service_without_availability(self):
        self.service.is_storable = True  # possible in the database, meaningless for a service
        self.location.warehouse_id = self.shop
        self.env.invalidate_all()
        self.assertEqual(self._lines(self.location._publish())["SRV-1"]["raspolozivost"], "")

    def test_not_tracked_goods_available(self):
        self.goods.is_storable = False
        self.location.warehouse_id = self.shop
        self.assertEqual(self._availability(), "dostupno", "Goods without stock tracking")
