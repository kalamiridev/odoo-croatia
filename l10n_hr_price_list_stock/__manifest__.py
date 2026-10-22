{
    "name": "Croatia - Public Price List: Stock per Premises",
    "version": "19.0.1.0.3",
    "category": "Accounting/Localizations",
    "summary": "Availability in the public price list (NN 101/26) from the warehouse of each premises",
    "description": """
The public price list must show availability (dostupno / nedostupno) for each premises.
With several warehouses, choose the warehouse of a premises: its availability then comes
from the stock of that warehouse only. Empty: stock of the company.

Installed automatically with Inventory and the Public Price List.
""",
    "author": "Kalamiri d.o.o.",
    "website": "https://kalamiri.hr",
    "maintainer": "Kalamiri d.o.o.",
    "support": "info@kalamiri.com",
    "images": ["static/description/banner.png"],
    "license": "AGPL-3",
    "depends": ["l10n_hr_price_list", "stock"],
    "data": [
        "views/price_list_location_views.xml",
    ],
    "installable": True,
    "auto_install": True,
}
