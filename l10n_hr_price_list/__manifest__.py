{
    "name": "Croatia - Public Price List for Consumers",
    "version": "19.0.2.9.10",
    "category": "Accounting/Localizations",
    "summary": "Machine-readable price list (CSV) with the additional (anchor) price, as required by NN 101/26",
    "description": """
Croatian companies that sell to consumers and have a website must publish their
price list in a machine-readable file (Government decisions NN 101/26) and show the
additional price (price on 10 September 2026, or at the first offer) next to every price.

* one price list per premises (shop, office, web shop…), each with its own product
  categories (subcategories included; none: all sellable products), webhook and
  storage numbers,
* consumer price as on a quotation for a customer without a pricelist of their own: the default
  pricelist of the company (or the sales price), with the taxes of the product,
* special sales are pricelist rules (discount, period) with the name of the special sale; the
  price before the sale and the lowest price in the 30 days before it (from the published price
  lists) are sent on the webhook,
* additional price and its date saved per premises at the first publication of the product;
  later price changes do not change it,
* a new version (storage number + 1, file name as prescribed) a minute after a change and
  every morning before 08:00 (a file of the day also without changes; stock, rules with a
  period);
  old versions are kept,
* public pages without login: /cjenik, /cjenik/<premises label> (current file),
  /cjenik/arhiva (all versions),
* optional webhook: every new version is sent to your website (JSON, HMAC-SHA256 signature).
""",
    "author": "Kalamiri d.o.o.",
    "website": "https://kalamiri.hr",
    "maintainer": "Kalamiri d.o.o.",
    "support": "info@kalamiri.com",
    "images": ["static/description/banner.png"],
    "license": "AGPL-3",
    "depends": ["account"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_cron.xml",
        "views/price_list_version_views.xml",
        "views/price_list_location_views.xml",
        "views/product_views.xml",
        "views/res_config_settings_views.xml",
        "views/product_pricelist_views.xml",
    ],
    "installable": True,
    "application": False,
}
