# Odoo modules for Croatia

Modules for **Odoo 19** (Community and Enterprise) for Croatian companies, by
[Kalamiri d.o.o.](https://kalamiri.hr) This branch (`19.0`) holds the **released modules, ready to install**.

> **Source code and development** – history, tests and work in progress – are in
> **[kalamiri-labs/odoo](https://github.com/kalamiridev/kalamiri-labs/tree/main/odoo)**; please open pull requests
> there. Report problems and questions here, in **Issues**.

**Hrvatski:** Odoo 19 moduli za hrvatske tvrtke, spremni za instalaciju. Svaki modul ima README na hrvatskom s
uputama. Razvoj je u repozitoriju [kalamiri-labs](https://github.com/kalamiridev/kalamiri-labs/tree/main/odoo), a
greške i pitanja prijavite ovdje (Issues).

## Modules

<!-- modules -->
| Module | Version | Description |
|---|---|---|
| [`l10n_hr_price_list`](./l10n_hr_price_list/) | 19.0.2.9.10 | Machine-readable price list (CSV) with the additional (anchor) price, as required by NN 101/26 |
| [`l10n_hr_price_list_stock`](./l10n_hr_price_list_stock/) | 19.0.1.0.3 | Availability in the public price list (NN 101/26) from the warehouse of each premises |
<!-- /modules -->

## Installation

1. Install from the **Odoo Apps Store**
   ([Public Price List for Consumers](https://apps.odoo.com/apps/modules/19.0/l10n_hr_price_list)), or download this
   branch (or clone it: `git clone -b 19.0 https://github.com/kalamiridev/odoo-croatia.git`) into a folder on the addons
   path of your Odoo.
2. Apps → Update Apps List → search the module → Activate.

Each module's README (in Croatian) describes the setup step by step.

## License

AGPL-3 (see `LICENSE` in each module).

These are unofficial modules of Kalamiri d.o.o. and are not affiliated with or endorsed by Odoo S.A.
