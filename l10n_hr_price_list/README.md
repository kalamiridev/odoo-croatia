# Javni cjenik za potrošače (l10n_hr_price_list)

Modul za Odoo 19 (Community i Enterprise). Sam sastavlja i objavljuje cjenik za potrošače u CSV datoteci,
za svaki vaš objekt, s **dodatnom cijenom** uz svaku cijenu, kako traže odluke Vlade RH (NN 101/26; primjena od
**17. 11. 2026.**, odgođena izmjenama u NN 110/26; referentni datum ostaje 10. 9. 2026.). Vi upišete objekt i
stavite poveznicu na svoju web stranicu; sve ostalo ide samo.

## Što propis traži i što radi modul

Obveza vrijedi za prodaju **potrošačima** (B2C), za sve koji imaju web stranicu. Detalji: pojašnjenje
Ministarstva gospodarstva,
[Isticanje dodatne cijene i objava cjenika](https://mingo.gov.hr/UserDocsImages/slike/MINGO_Poja%C5%A1njenja_dodatna%20cijena_objava%20cjenika.pdf).

| Propis traži | Modul |
|---|---|
| cjenik u CSV datoteci, javno, bez prijave | objavljuje ga na javnoj poveznici ili šalje na vaš web |
| zaseban cjenik za svaki objekt i web shop | jedan objekt = jedan cjenik, s propisanim nazivom datoteke |
| dodatna cijena uz svaku cijenu (cijena 10. 9. 2026. ili pri prvoj ponudi) | upiše je sama pri prvoj objavi; kasnije se ne mijenja |
| oznaka i naziv akcije uz akcijsku cijenu | iz pravila cjenika s nazivom akcije |
| ažurno do 8:00 (trgovci svaki dan, usluge pri svakoj promjeni) | nova verzija svako jutro prije 8:00 i minutu nakon svake promjene |
| prethodni cjenici javni najmanje 30 dana | arhiva; verzija mlađa od 30 dana ne može se obrisati |
| raspoloživost robe po objektu | iz zalihe (aplikacija Skladište), po želji iz skladišta objekta |

## Brzi početak

„Administrator“ je korisnik s pravom *Administracija: Postavke*.

1. **Instalirajte** modul: *Aplikacije* → potražite „Public Price List“ → *Aktiviraj*. Treba aplikacija
   Računovodstvo.
2. **Dodajte objekt:** *Računovodstvo → Konfiguracija → Objekti javnog cjenika* → **Novi**:
   - **Oblik objekta** – npr. `prodavaonica`, `ured`, `servis`, `salon`, za internetsku trgovinu `webshop`;
   - **Adresa objekta** – samo ako nije adresa sjedišta tvrtke, npr. `Ilica 150 Zagreb`;
   - **Oznaka objekta** – vaša oznaka (npr. oznaka poslovnog prostora iz internog akta, `P-01`) ili `01`;
   - **Kategorije proizvoda** – neobavezno: prazno znači svi proizvodi za prodaju; odaberite kategorije ako
     neke proizvode ne prodajete potrošačima.

   Spremite. Cjenik se objavi za minutu (ili odmah gumbom **Objavi cjenik sada**, koji javi i ako nešto
   nedostaje).
3. **Dopunite proizvode:** na proizvodu, kartica *Opći podaci*, odjeljak **Javni cjenik**: **Marka** za robu;
   na proizvodu još **Interna oznaka** (šifra) i **Barkod** ako ih imate.
4. **Ispravite dodatne cijene** za proizvode koje ste nudili 10. 9. 2026. (vidi *Dodatne cijene*).
5. **Stavite poveznicu na web:** „Cjenik (CSV)“ na **Javnu poveznicu** objekta i „Arhiva cjenika“ na
   `…/cjenik/arhiva` (vidi *Objava na vašoj web stranici*).

Provjera: na objektu gumb **Verzije** → zadnja verzija → preuzmite datoteku. Prvog dana zbog dopuna nastane
nekoliko verzija; to je u redu.

## Odakle su cijene

Cijena u cjeniku je cijena s PDV-om kakvu Odoo stavlja na ponudu i račun građaninu:

- **Prodajna cijena** proizvoda s njegovim *Prodajnim porezima*, ili
- ako su uključeni **Cjenici** (*Prodaja → Konfiguracija → Postavke → Cjenici*): cijena iz **zadanog cjenika**
  (prvi na popisu *Prodaja → Proizvodi → Cjenici*), tj. cjenika kupca bez vlastitog cjenika.

Na objektu se cijene ne postavljaju. Okrugla cijena s PDV-om: prodajnu cijenu upišite tako da s PDV-om bude
okrugla (npr. 255,20 € + 25 % = 319,00 €) ili koristite porez uključen u cijenu.

## Svakodnevni rad

Ne treba ništa raditi. Odoo objavljuje novu verziju sam:

| Što se dogodi | Kada se objavi |
|---|---|
| promijenite cijenu, naziv, šifru, porez ili kategoriju proizvoda | za minutu (obično 1–4 minute) |
| dodate novi proizvod za prodaju | za minutu, s dodatnom cijenom i današnjim datumom |
| dodate, promijenite ili obrišete pravilo cjenika (akciju) | za minutu |
| svako jutro (5–6 h) | uvijek nova verzija s današnjim datumom, i bez promjena (zaliha, početak i kraj akcija) |

Tijekom dana bez promjena nova verzija ne nastaje. Objavu odmah radi gumb **Objavi cjenik sada** na objektu.

## Akcije (posebni oblici prodaje)

Akcija se radi kao inače u Odoo-u, **pravilom cjenika**: prodajna cijena proizvoda ostaje redovna, a pravilo
daje popust u zadanom razdoblju. Isto pravilo vrijedi na ponudama i računima, pa je cijena svugdje ista.
Treba aplikacija **Prodaja** s uključenim **Cjenicima**.

1. *Prodaja → Proizvodi → Cjenici* → **zadani cjenik** (prvi na popisu) → kartica **Prodajne cijene** →
   **Dodaj stavku** (ili na proizvodu, kartica **Cijene**).
2. U pravilu: **Primijeni na** (proizvod, kategorija ili sve), **Vrsta cijene** *Popust* i postotak (ili
   fiksna cijena), **Razdoblje važenja** (od 00:00 do 23:59) i **Posebni oblik prodaje** – naziv akcije, npr.
   `Jesensko sniženje`.
3. Spremite. Cjenik prikazuje akcijsku cijenu i naziv od početka akcije, a ujutro nakon kraja opet redovnu
   cijenu.

**Primjer:** senzor ima *Prodajnu cijenu* 19,00 € (bez PDV-a, uz porez 25 %). U zadani cjenik dodate pravilo:

| Polje | Vrijednost |
|---|---|
| Primijeni na | Proizvod: *Senzor vrata/prozora* |
| Vrsta cijene | Popust, `20` % |
| Razdoblje važenja | 1. 11. 2026. 00:00 – 30. 11. 2026. 23:59 |
| Posebni oblik prodaje | `Jesensko sniženje` |

Od 1. 11. ujutro redak senzora u cjeniku glasi:

| Stupac | Prije akcije | Za vrijeme akcije |
|---|---|---|
| `maloprodajna_cijena_eur` | 23,75 | **19,00** (15,20 € + PDV) |
| `posebni_oblik_prodaje` | ne | **da** |
| `naziv_posebnog_oblika_prodaje` | | **Jesensko sniženje** |
| `dodatna_cijena_eur`, `datum_dodatne_cijene` | 26,25 · 19.10.2026 | 26,25 · 19.10.2026 (ne mijenja se) |

Ponuda građaninu u studenom ima istu cijenu (15,20 € + PDV), a 1. 12. ujutro cjenik je opet na 23,75.

- Pravilo **bez** naziva akcije je redovna cijena za potrošače, a ne akcija.
- **Mnogo artikala:** jedno pravilo za njihovu kategoriju; ako nisu u jednoj kategoriji, pravila uvezite iz
  tablice: popis cjenika → označite zadani cjenik → **⚙ Radnje → Izvoz** s poljima *ID* i iz *Pravila
  cjenika*: *Primijeni na*, *Proizvod*, *Izračunaj cijenu*, *Postotak cijena*, *Datum početka*, *Datum
  završetka*, *Posebni oblik prodaje*; u tablici *ID* samo u prvom retku, ispod jedan redak po artiklu; zatim
  **⚙ → Uvoz zapisa**. Postojeća pravila ostaju.
- **Najniža cijena u 30 dana prije akcije** (mora stajati uz akcijsku cijenu u prodaji i na webu): modul je
  računa iz objavljenih cjenika i šalje webhookom; u propisanoj datoteci nema tog stupca.
- Računi napravljeni izravno u Računovodstvu (bez ponude) ne koriste cjenike – tako radi Odoo. Za akcijske
  artikle radite ponudu i iz nje račun.

## Dodatne cijene

- Pri **prvoj objavi** proizvod dobije dodatnu cijenu: svoju trenutnu cijenu s **današnjim** datumom
  (za vrijeme akcije redovnu cijenu). To je ispravno za proizvode uvedene nakon 10. 9. 2026.
- Za proizvode i usluge koje ste **nudili 10. 9. 2026.** administrator na proizvodu (odjeljak **Javni
  cjenik**, popis dodatnih cijena) upiše cijenu s PDV-om toga dana i datum **10. 9. 2026.** Ako je tada bila
  akcija, upiše redovnu cijenu.
- **Hrana, piće, kozmetika, sredstva za čišćenje, toaletne potrepštine i proizvodi za kućanstvo** kod trgovaca
  koji su dodatnu cijenu isticali već po odluci iz 2025. (NN 75/25): cijena i datum **2. 5. 2025.**
- Kasnije promjene cijene dodatnu cijenu **ne mijenjaju**; promijeniti je može samo administrator. Svaki objekt
  ima svoje dodatne cijene.

## Objava na vašoj web stranici

Propis traži da su cjenik i prethodni cjenici (najmanje 30 dana) javno dostupni na vašoj web stranici.
Dvije mogućnosti:

**A) Poveznica na Odoo** – na web stavite poveznice na Odoo (Odoo mora biti dostupan s interneta barem za put
`/cjenik`):

| Adresa | Što vraća |
|---|---|
| `https://<vaš Odoo>/cjenik/<oznaka objekta>` | trenutni cjenik objekta (npr. `/cjenik/01`) |
| `https://<vaš Odoo>/cjenik` | jedan objekt: njegov cjenik; više objekata: popis |
| `https://<vaš Odoo>/cjenik/arhiva` | sve verzije (arhiva) |

**B) Webhook** – svaka nova verzija šalje se na vaš web, koji je objavi sam (i čuva arhivu). Administrator na
objektu upiše **Adresu webhooka** i **Tajni ključ webhooka**; tehnički opis je u *Za programere*.

## Više objekata i skladišta

- Svaki objekt (prodavaonica, salon, web shop…) ima svoju datoteku, poveznicu, brojeve pohrane i dodatne cijene.
  Primjer: salon (`salon`, oznaka `01`, kategorija *Usluge salona*) i web shop (`webshop`, oznaka `02`,
  kategorija *Kozmetika*).
- Cijene su iste u svim objektima (zadani cjenik).
- **Raspoloživost:** roba koja prati zalihu je `dostupno` kad je ima na zalihi, inače `nedostupno`; roba bez
  praćenja zalihe je `dostupno`, usluge nemaju raspoloživost. Uz aplikaciju Skladište sam se instalira modul
  *Javni cjenik: zaliha po objektu*: s više skladišta na objektu odaberete **Skladište** i gleda se samo
  njegova zaliha.

## Što ako…

- **Cjenik se ne objavljuje** – na objektu **Objavi cjenik sada**; poruka kaže što nedostaje (npr. adresa).
- **Proizvod nije u cjeniku** – mora biti aktivan, s kvačicom **Prodaja** i cijenom većom od 0; ako objekt ima
  kategorije, mora biti u jednoj od njih (ili podkategoriji).
- **Akcija nije u cjeniku** – pravilo mora biti u **zadanom** cjeniku, s nazivom u **Posebni oblik prodaje**,
  razdoblje važenja mora biti počelo, a Cjenici uključeni.
- **Kriva dodatna cijena ili datum** – administrator je ispravi na proizvodu (odjeljak **Javni cjenik**).
- **Objekt se zatvara** – arhivirajte ga; objavljeni cjenici ostaju javni.
- **Webhook: Greška** – razlog piše na verziji (**Verzije**); Odoo pokušava ponovno svaki sat.

## Ograničenja

- **Jedna cijena za sve objekte** (zadani cjenik): objekti s različitim cijenama istog proizvoda (npr. lanac
  u kojem svaka trgovina u blagajni ima svoj cjenik) nisu podržani.
- **Promocije iz *Popusti i vjernost*** (npr. „2+1“, popust na košaricu) su uvjeti na narudžbi, ne cijena
  proizvoda, pa se u cjeniku ne vide.
- **Odoo web trgovina sa zasebnim cjenikom za web:** objavljuju se cijene zadanog cjenika, ne cjenika web
  trgovine.
- **Najnižu cijenu u 30 dana** uz akcijsku cijenu ističete vi (modul je šalje webhookom; računa se iz cjenika
  objavljenih ovim modulom).
- **Cijene koje nisu unaprijed određene** (izrada po specifikaciji): objavite elemente cijene kao zasebne
  proizvode (sat rada, m², dolazak).
- **Cijena za jedinicu mjere** (po kg ili l) puni se samo uz eCommerce (*Postavke → Web stranica →
  Referentna cijena proizvoda*, pa na proizvodu osnovna jedinica i količina).
- **Pravilnici u savjetovanju** (do 13. 11. 2026., planirano stupanje na snagu 17. 11. 2026.): o isticanju
  **bazne cijene** (novi naziv za dodatnu cijenu) i o sadržaju i načinu objave cjenika. Ako konačni tekst propiše
  drukčije nazive, stupce ili pravila objave, modul će se uskladiti.

## Prijevod na hrvatski

Svi tekstovi modula (polja, gumbi, poruke, javne stranice) prevedeni su na hrvatski (`i18n/hr.po`), pojmovima
iz odluka i pojašnjenja Ministarstva (dodatna cijena, oblik, adresa i oznaka objekta, broj pohrane,
raspoloživost). Prijevodi se učitavaju pri instalaciji i nadogradnji. Ako ste hrvatski dodali nakon
instalacije modula: *Postavke → Jezici* → ažurirajte **Hrvatski**.

## Za programere

**Datoteka:** CSV, UTF-8 s BOM-om, točka sa zarezom, decimalni zarez, datumi `dd.mm.gggg`; isti stupci za robu
i usluge i za sve objekte. Naziv: `oblik objekta_adresa_oznaka_broj pohrane_datum_vrijeme.csv`, npr.
`servis_Vukovarska 20 Osijek_U-03_015_01.10.2026_07:45.csv` (broj pohrane po objektu, +1 za svaku verziju).

| Stupac | Sadržaj |
|---|---|
| `sifra`, `naziv`, `marka`, `jedinica_mjere` | interna oznaka, naziv (hrvatski ako je uključen), marka, jedinica mjere |
| `maloprodajna_cijena_eur` | cijena za potrošača s PDV-om |
| `cijena_za_jedinicu_mjere_eur`, `jedinica_mjere_za_cijenu` | cijena po osnovnoj jedinici (eCommerce) |
| `posebni_oblik_prodaje`, `naziv_posebnog_oblika_prodaje` | `da` i naziv akcije iz pravila cjenika, inače `ne` |
| `dodatna_cijena_eur`, `datum_dodatne_cijene` | dodatna cijena objekta i njezin datum |
| `barkod`, `raspolozivost` | barkod; `dostupno` / `nedostupno` (roba), prazno (usluge) |

**Webhook:** `POST` s JSON tijelom na adresu objekta, za svaku novu verziju, redom od najstarije neposlane:

```json
{
  "event": "price_list.published",
  "company": "Primjer d.o.o.",
  "company_vat": "HR12345678903",
  "premises": "servis_Vukovarska 20 Osijek_U-03",
  "premises_label": "U-03",
  "number": 15,
  "file_name": "servis_Vukovarska 20 Osijek_U-03_015_01.10.2026_07:45.csv",
  "published_at": "2026-10-01T07:45:00+02:00",
  "url": "https://odoo.example.com/cjenik/servis_Vukovarska%2020%20Osijek_U-03_015_01.10.2026_07%3A45.csv",
  "content_type": "text/csv; charset=utf-8",
  "content_base64": "77u/c2lmcmE7...",
  "rows": [
    {"sifra": "U-1", "naziv": "Servis", "maloprodajna_cijena_eur": "125,00", "dodatna_cijena_eur": "125,00",
     "datum_dodatne_cijene": "10.09.2026", "prodajna_cijena_bez_pdv_eur": "100,00", "...": "..."}
  ]
}
```

- `content_base64` je propisana datoteka (objavite je takvu kakva jest). `rows` su njezini retci za prikaz na
  webu, uz `prodajna_cijena_bez_pdv_eur` (prodajna cijena bez PDV-a, npr. za tvrtke), a za vrijeme akcije i
  `cijena_prije_posebnog_oblika_prodaje_eur` i `najniza_cijena_30_dana_eur`.

Redak u `rows` za vrijeme akcije (primjer iz poglavlja *Akcije*):

```json
{
  "sifra": "SL-S-DOOR",
  "naziv": "Senzor vrata/prozora",
  "marka": "Aqara / Shelly",
  "jedinica_mjere": "kom",
  "maloprodajna_cijena_eur": "19,00",
  "cijena_za_jedinicu_mjere_eur": "",
  "jedinica_mjere_za_cijenu": "",
  "posebni_oblik_prodaje": "da",
  "naziv_posebnog_oblika_prodaje": "Jesensko sniženje",
  "dodatna_cijena_eur": "26,25",
  "datum_dodatne_cijene": "19.10.2026",
  "barkod": "",
  "raspolozivost": "dostupno",
  "prodajna_cijena_bez_pdv_eur": "19,00",
  "cijena_prije_posebnog_oblika_prodaje_eur": "23,75",
  "najniza_cijena_30_dana_eur": "23,75"
}
```

Na webu uz akcijsku cijenu (19,00 €) prikažite najnižu cijenu u 30 dana prije akcije (23,75 €), npr.
„Jesensko sniženje: 19,00 € · najniža cijena u 30 dana prije akcije: 23,75 € · cijena na 19.10.2026.: 26,25 €“.
`prodajna_cijena_bez_pdv_eur` je redovna prodajna cijena bez PDV-a, bez akcije.
- Uz tajni ključ zaglavlje `X-Price-List-Signature: sha256=<HMAC-SHA256 tijela>`; web ga mora provjeriti.
- Odgovor 2xx = primljeno (*Webhook: Poslano*); preusmjeravanja se ne slijede. Kod greške Odoo pokušava ponovno
  za sat vremena. Kad se webhook upiše naknadno, šalje se trenutna verzija. Web mora sam čuvati i objaviti
  prethodne verzije najmanje 30 dana.

**Kod:**

- Ovisi samo o `account`; Skladište (`is_storable`, `qty_available`) i eCommerce (`base_unit_id`,
  `base_unit_count`) koristi ako su instalirani. Most `l10n_hr_price_list_stock` (auto_install uz `stock`):
  `warehouse_id` na objektu.
- Modeli: `l10n_hr.price.list.location` (objekt), `l10n_hr.price.list.version` (verzija: broj pohrane, datoteka
  kao privitak, `checksum`, `rows_json`, stanje webhooka), `l10n_hr.price.list.anchor` (dodatna cijena po objektu
  i varijanti; mijenja je samo `base.group_system`). Predložak proizvoda: `price_list_brand`,
  `price_list_anchor_ids`. Pravilo cjenika: `price_list_special_sale`.
- Cijena: `_consumer_pricelist()` (kao `_get_partner_pricelist_multi` za kupca iz države tvrtke; ništa kad su
  Cjenici isključeni) i `_compute_price_rule`; pravilo s nazivom = `da`. Cijena prije akcije i najniža cijena
  (`_special_sale_prices`) iz `rows_json` verzija (retci spremaju `_product_id`, koji se ne objavljuje i nije u
  `checksum`; starije verzije po šifri).
- Objava (`_publish`): nova verzija kad se promijeni SHA-256 redaka (uključujući prodajnu cijenu bez PDV-a) ili
  naziva, a prvi put svaki dan i bez promjena. Cron *Javni cjenik: objava promjena* svaki dan u 04:00 UTC;
  promjene proizvoda, kategorija, objekata, dodatnih cijena, cjenika i pravila zakažu ga za minutu (jednom po
  transakciji), neuspjeli webhook za sat vremena. Verzije se spremaju prije slanja webhooka.
- Proširenja na objektu: `_row(product, price, anchor, special_sale)`, `_prices`, `_availability`, `_products`.
- Testovi: `--test-tags /l10n_hr_price_list`.
