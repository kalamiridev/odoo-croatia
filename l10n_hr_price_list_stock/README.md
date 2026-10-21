# Javni cjenik: zaliha po objektu (l10n_hr_price_list_stock)

Dodatak modulu **Javni cjenik za potrošače** (`l10n_hr_price_list`) za Odoo 19 (Community i Enterprise).

Propis traži da je roba u cjeniku svakog objekta `dostupno` samo ako je ima na zalihi **u tom objektu**
(pojašnjenje Ministarstva gospodarstva, točka 2.5). Bez ovog modula raspoloživost se računa iz zalihe
cijele tvrtke.

## Instalacija

Ništa ne treba raditi: modul se instalira sam kad su instalirani *Javni cjenik* i aplikacija *Skladište*.

## Korištenje

Polje se vidi kad imate više skladišta (*Skladište → Konfiguracija → Postavke → Skladišta*).

*Računovodstvo → Konfiguracija → Objekti javnog cjenika* → objekt → **Skladište**:

- odabrano skladište: roba koja prati zalihu je `dostupno` kad je ima u tom skladištu, inače `nedostupno`;
- prazno: zaliha cijele tvrtke (kao bez ovog modula).

Roba koja ne prati zalihu uvijek je `dostupno`, a usluge nemaju raspoloživost. Zaliha se provjerava svako
jutro prije 8:00 i pri svakoj objavi; promjena skladišta na objektu objavi novu verziju za minutu.

## Prijevod na hrvatski

Tekstovi modula prevedeni su u `i18n/hr.po` (učitava se pri instalaciji i nadogradnji).

## Za programere

- `warehouse_id` na `l10n_hr.price.list.location`; `_availability(product)` sa zalihom
  (`qty_available` u kontekstu `warehouse_id`) kad je skladište odabrano.
- `auto_install`: ovisi o `l10n_hr_price_list` i `stock`.
- Testovi: `--test-tags /l10n_hr_price_list_stock`.
