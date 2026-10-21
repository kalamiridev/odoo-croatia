# Javni cjenik za potrošače (l10n_hr_price_list)

Modul za Odoo 19 (Community i Enterprise). Objavljuje cjenik proizvoda i usluga za potrošače u
strojno čitljivoj CSV datoteci i uz svaku cijenu vodi **dodatnu cijenu**, prema odlukama Vlade RH
(NN 101/26, na snazi od 1. 10. 2026.):

- *Odluka o objavi cjenika proizvoda i usluga* – tko ima mrežnu stranicu, objavljuje cjenik u .csv ili
  .xml obliku, bez prijave, za **svaki prodajni ili uslužni objekt** posebno (i za web shop), a prethodne
  cjenike drži javno dostupnima najmanje 30 dana;
- *Odluka o isticanju dodatne cijene* – uz cijenu se ističe cijena na dan 10. 9. 2026., a za proizvode
  i usluge uvedene kasnije cijena pri prvom uvrštenju u ponudu, s datumom.

Obveza vrijedi samo za prodaju **potrošačima** (B2C). Pojašnjenje Ministarstva gospodarstva:
[Isticanje dodatne cijene i objava cjenika](https://mingo.gov.hr/UserDocsImages/slike/MINGO_Poja%C5%A1njenja_dodatna%20cijena_objava%20cjenika.pdf).

**Ukratko:** za svaki objekt (prodavaonicu, ured, salon, web shop…) po želji odaberete kategorije proizvoda
koje prodajete potrošačima (bez kategorija: svi proizvodi za prodaju). Odoo sam sastavi cjenik s cijenama
s PDV-om i dodatnim cijenama, objavi ga na javnoj poveznici i objavi novu verziju čim promijenite cijenu
ili proizvod. Vi samo stavite poveznicu na svoju mrežnu stranicu.

## Postavljanje korak po korak

„Administrator“ je korisnik s pravom *Administracija: Postavke*. Samo on može objaviti cjenik ručno,
ispraviti dodatne cijene i upisati webhook.

1. **Instalacija.** *Aplikacije* → potražite „Public Price List“ (`l10n_hr_price_list`) → *Aktiviraj*.
   Treba aplikacija Računovodstvo.

2. **Cijene za potrošače.** Cjenik prikazuje cijenu s PDV-om kakvu Odoo stavlja na ponudu i račun
   građaninu: **prodajnu cijenu** proizvoda (*Prodajna cijena* na proizvodu) s porezima prodaje proizvoda.
   Ako su u Prodaji uključeni **Cjenici** (*Prodaja → Konfiguracija → Postavke → Cijene → Cjenici*), vrijede
   i pravila **zadanog cjenika** – cjenika koji Odoo daje kupcu bez vlastitog cjenika (prvi na popisu
   *Prodaja → Proizvodi → Cjenici*). Tako se rade i akcije (vidi *Akcije*). Na objektu se ništa ne
   postavlja.

   Ako želite okruglu cijenu s PDV-om, prodajnu cijenu upišite tako da cijena s PDV-om bude okrugla
   (npr. 255,20 € + 25 % PDV = 319,00 €) ili koristite porez uključen u cijenu.

3. **Dodajte objekt.** *Računovodstvo → Konfiguracija → Objekti javnog cjenika* → **Novi** (isti popis otvara
   i *Postavke*, blok **Javni cjenik** → **Uredi objekte**):
   - **Oblik objekta** – npr. `prodavaonica`, `ured`, `servis`, `salon`, a za internetsku trgovinu `webshop`;
   - **Adresa objekta** – samo ako je objekt na drugoj adresi od sjedišta tvrtke, npr. `Ilica 150 Zagreb`
     (prazno: ulica i mjesto tvrtke);
   - **Oznaka objekta** – vaša oznaka (npr. `P-01`, `U-03`) ili `01` ako je nemate; svaki objekt svoju;
   - **Kategorije proizvoda** – neobavezno. **Prazno:** objavljuju se svi aktivni proizvodi s kvačicom
     **Prodaja** i prodajnom cijenom većom od 0. Ako neke proizvode ne prodajete potrošačima (npr. dijelove ili
     usluge za tvrtke), odaberite samo kategorije za potrošače (može ih biti više; uključene su i
     podkategorije). Kategorije se uređuju u *Računovodstvo → Konfiguracija → Kategorije proizvoda*.

   Spremite. Odoo objavi prvi cjenik za minutu (administrator može odmah gumbom **Objavi cjenik sada**).
   Ako nešto nedostaje, gumb **Objavi cjenik sada** javi što.

4. **Dopunite proizvode.** Na svakom objavljenom proizvodu (kartica *Opći podaci*, odjeljak **Javni cjenik**,
   koji se pojavi kad je proizvod u cjeniku nekog objekta):
   - **Marka** – za robu (npr. vaša marka ili marka proizvođača);
   - **Interna oznaka** (šifra) i **Barkod** – na proizvodu, ako ih ima; Ministarstvo za robu traži šifru.

5. **Dodatne cijene za ono što ste nudili 10. 9. 2026.** Pri prvoj objavi svaki proizvod dobije dodatnu
   cijenu s **današnjim** datumom. To je ispravno za proizvode i usluge uvedene nakon 10. 9. 2026. Za one
   koje ste nudili 10. 9. 2026. administrator na proizvodu (odjeljak **Javni cjenik**, *Dodatne cijene*)
   upiše cijenu s PDV-om koja je vrijedila toga dana i datum **10. 9. 2026.** Ako je proizvod tada bio na
   akciji, upišite redovnu cijenu.

   Iznimka su hrana, piće, kozmetika, sredstva za čišćenje, toaletne potrepštine i proizvodi za kućanstvo
   kod trgovaca koji su dodatnu cijenu za njih isticali već po odluci iz 2025. (NN 75/25): za njih ostaje
   cijena i datum **2. 5. 2025.** (upišite taj datum, ne 10. 9. 2026.).

6. **Provjerite cjenik.** U prozoru objekta gumb **Verzije** → otvorite zadnju verziju → preuzmite datoteku,
   ili otvorite **Javnu poveznicu**. Provjerite cijene, nazive, jedinice mjere i dodatne cijene.

7. **Objavite poveznicu na webu.** Na mrežnu stranicu objekta stavite poveznicu „Cjenik (CSV)“ na **Javnu
   poveznicu** objekta (npr. `https://<vaš Odoo>/cjenik/01`). Odoo mora biti dostupan s interneta barem za
   put `/cjenik`. Ako to ne želite, cjenik se može slati na vaš web (vidi *Webhook*).

Koraci 4 i 5 objave nove verzije cjenika; prvog dana zato može nastati nekoliko verzija, što je u redu.

Primjer: frizerski salon (`salon`, oznaka `01`, kategorija *Usluge salona*) i web shop za kozmetiku
(`webshop`, oznaka `02`, kategorija *Kozmetika*) – dvije datoteke, dvije javne poveznice (`/cjenik/01`,
`/cjenik/02`), po želji svaka na svoj web (svoj webhook).

## Svakodnevni rad

Ništa posebno ne treba raditi:

- **promijenite cijenu, naziv, šifru ili porez** – nova verzija objavi se za minutu;
- **novi proizvod** (u kategoriji objekta ili, bez kategorija, svaki za prodaju) ulazi u cjenik sam (dobije
  dodatnu cijenu s današnjim datumom);
- **akcija ili sniženje** – vidi *Akcije (posebni oblici prodaje)* niže;
- **zaliha** i **pravila cjenika s razdobljem važenja** (početak i kraj akcije) provjeravaju se svako jutro
  prije 8:00;
- ako nešto nije promijenjeno, nova verzija ne nastaje.

Popis objekata: *Računovodstvo → Konfiguracija → Objekti javnog cjenika*.

## Akcije (posebni oblici prodaje)

Za vrijeme akcije (sniženje, popust, rasprodaja…) cjenik uz cijenu mora pisati da je to cijena u posebnom
obliku prodaje i naziv akcije. Akcija se radi kako je uobičajeno u Odoo-u – **pravilom cjenika**: prodajna
cijena proizvoda ostaje redovna cijena, a pravilo daje popust u zadanom razdoblju. Isto pravilo vrijedi na
ponudama i računima (i u blagajni i web trgovini, ako ih koristite), pa je cijena svugdje ista.

Treba aplikacija **Prodaja** s uključenim **Cjenicima** (*Prodaja → Konfiguracija → Postavke → Cijene →
Cjenici*).

1. *Prodaja → Proizvodi → Cjenici* → otvorite **zadani cjenik** (prvi na popisu) → kartica **Prodajne
   cijene** → **Dodaj stavku**.
2. U pravilu:
   - **Primijeni na** – proizvod, kategorija (npr. sve iz kategorije *Jesen*) ili svi proizvodi;
   - **Vrsta cijene** – *Popust* i postotak (npr. `20`), ili fiksna cijena;
   - **Razdoblje važenja** – od kada do kada akcija traje (Odoo je sam uključi i isključi);
   - **Posebni oblik prodaje** – naziv akcije, npr. `Jesensko sniženje` (polje dodaje ovaj modul).
3. Spremite. Cjenik se objavi za minutu (ili ujutro na dan početka akcije), s akcijskom cijenom i nazivom
   akcije; ujutro nakon kraja akcije opet s redovnom cijenom.

Pravila za jedan proizvod mogu se dodati i na samom proizvodu, kartica **Cijene**.

**Akcija za mnogo artikala** (npr. 100 od 1000): ako su u jednoj kategoriji, dovoljno je jedno pravilo za tu
kategoriju. Ako nisu, pravila se uvezu iz tablice (standardni Odoo uvoz, postojeća pravila ostaju):

1. *Prodaja → Proizvodi → Cjenici*, prikaz popisa → označite zadani cjenik → **⚙ Radnje → Izvoz** s poljima
   *ID* i iz *Pravila cjenika*: *Primijeni na*, *Proizvod*, *Izračunaj cijenu*, *Postotak cijena*, *Datum
   početka*, *Datum završetka*, *Posebni oblik prodaje* – dobijete tablicu s ispravnim stupcima.
2. U tablici ostavite *ID* samo u prvom retku, a ispod upišite jedan redak po artiklu (proizvod, popust
   `20`, datumi, naziv akcije; vrijednosti kao u izvezenom retku).
3. Na popisu cjenika **⚙ → Uvoz zapisa** → odaberite tablicu → **Uvezi**.

Pravilo **bez** naziva u *Posebni oblik prodaje* je redovna cijena za potrošače (npr. stalna cijena), a ne
akcija.
Dodatna cijena se za vrijeme akcije ne mijenja; proizvod koji prvi put ulazi u cjenik za vrijeme akcije
dobije redovnu cijenu kao dodatnu.

**Cijena prije akcije i najniža cijena u 30 dana:** uz akcijsku cijenu u prodaji i na webu morate istaknuti
**najnižu cijenu u 30 dana prije akcije** (Zakon o zaštiti potrošača). Modul je računa iz cjenika koje je
objavio i šalje je webhookom zajedno s cijenom prije akcije (stupci `najniza_cijena_30_dana_eur` i
`cijena_prije_posebnog_oblika_prodaje_eur`), pa ih vaš web može prikazati sam. U propisanoj datoteci tih
stupaca nema.

## Što ako…

- **Cjenik se ne objavljuje** – otvorite objekt i kliknite **Objavi cjenik sada**; poruka kaže što nedostaje
  (npr. adresa).
- **Proizvod nije u cjeniku** – ako objekt ima kategorije, provjerite da je proizvod u jednoj od njih (ili
  podkategoriji; proizvod bez kategorije tada se ne objavljuje); provjerite i da je aktivan, da ima kvačicu
  **Prodaja** i da cijena nije 0 (proizvod bez cijene se ne objavljuje).
- **Akcija nije u cjeniku** – provjerite da je pravilo u **zadanom** cjeniku (prvom na popisu cjenika), da
  ima naziv u **Posebni oblik prodaje**, da je razdoblje važenja počelo i da su Cjenici uključeni.
- **Kriva dodatna cijena ili datum** – administrator je ispravi na proizvodu (odjeljak **Javni cjenik**).
- **Objekt se zatvara** – arhivirajte ga (objekt s objavljenim cjenikom ne može se obrisati; njegove
  datoteke ostaju javne).
- **Webhook: Greška** – razlog piše pod **Verzije** na verziji; Odoo pokušava ponovno svaki sat.

## Kako radi

- **Cijena** je cijena za potrošača s PDV-om, kao na ponudi i računu kupcu bez vlastitog cjenika: pravilo
  zadanog cjenika (uz uključene Cjenike) ili prodajna cijena proizvoda, uz poreze prodaje proizvoda.
  Ispravno se računa i porez uključen u cijenu. Isključeni Cjenici (arhivirani cjenici): prodajna cijena.
- **Dodatna cijena** se sprema po objektu i proizvodu pri prvoj objavi i kasnije promjene cijene je
  **ne mijenjaju**. Ostali korisnici osim administratora dodatne cijene samo vide.
- **Raspoloživost**: roba koja prati skladište (aplikacija Skladište, kvačica *Prati skladište*) je
  `dostupno` kad je ima na zalihi tvrtke (ili odabranog skladišta objekta), inače `nedostupno`; ostala roba
  je `dostupno`; za usluge je prazno.
- **Nova verzija** nastaje samo kad se sadržaj promijeni. Odoo provjerava minutu nakon promjene proizvoda,
  kategorije, objekta, dodatne cijene, cjenika ili pravila cjenika, i svako jutro između 5 i 6 sati (zaliha,
  početak i kraj akcija). Tako je cjenik ažuran prije 8:00, što traže pravila i za trgovce (jednom dnevno) i
  za pružatelje usluga (pri svakoj promjeni). Neka razdoblje važenja akcije počinje u 00:00 (akcija koja
  počinje usred dana objavi se sljedeće jutro, ako u međuvremenu nema druge promjene).
- Svaka verzija ima propisani **naziv**: `oblik objekta_adresa_oznaka_broj pohrane_datum_vrijeme.csv`,
  npr. `servis_Vukovarska 20 Osijek_U-03_015_01.10.2026_07:45.csv`. Broj pohrane vodi se za svaki
  objekt posebno i raste za 1 sa svakom verzijom.
- **Stare verzije** se čuvaju i ostaju javne; verzija mlađa od 30 dana ne može se obrisati.

## Javne adrese (bez prijave)

| Adresa | Što vraća |
|---|---|
| `/cjenik` | jedan objekt: preusmjerava na njegov trenutni cjenik; više objekata: popis njihovih trenutnih cjenika |
| `/cjenik/<oznaka objekta>` | preusmjerava na trenutni cjenik objekta, npr. `/cjenik/01` |
| `/cjenik/<naziv datoteke>` | CSV datoteka te verzije |
| `/cjenik/arhiva` | popis svih verzija s poveznicama |

Ako je Odoo iza proxyja ili tunela koji propušta samo neke putove, propustite `/cjenik`.

## Webhook (neobavezno)

Ako cjenik želite objaviti na svojoj mrežnoj stranici (a ne u Odoo-u), administrator na objektu upiše
**Adresu webhooka** i po želji **Tajni ključ webhooka**. Svaki objekt ima svoj webhook. Bez adrese Odoo
ništa ne šalje. Svaka nova verzija šalje se na tu adresu kao `POST` s JSON tijelom:

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

- `content_base64` je propisana CSV datoteka (objavite je takvu kakva jest).
- `rows` su isti retci kao podaci, za prikaz cijena na vašoj stranici (paketi, „Cijena na …“) bez ručnog
  prepisivanja: svi stupci datoteke i uz njih `prodajna_cijena_bez_pdv_eur` – prodajna cijena proizvoda bez
  PDV-a (npr. cijena za tvrtke), a za vrijeme akcije i `cijena_prije_posebnog_oblika_prodaje_eur` i
  `najniza_cijena_30_dana_eur` (za prikaz uz akcijsku cijenu). Ti stupci nisu u propisanoj datoteci.

- Uz tajni ključ zahtjev ima zaglavlje `X-Price-List-Signature: sha256=<HMAC-SHA256 tijela zahtjeva>`;
  web ga mora provjeriti prije spremanja (inače bi bilo tko mogao poslati lažni cjenik). Isti ključ upišite
  u Odoo i na web.
- Odgovor 2xx znači da je verzija primljena (*Webhook: Poslano*). Preusmjeravanja se ne slijede, pa
  upišite konačnu adresu (npr. s `https://`). Kod greške (*Webhook: Greška*, s razlogom) Odoo pokušava
  ponovno za sat vremena, dok ne uspije, a verzije šalje redom, od najstarije neposlane.
- Kad webhook upišete naknadno, šalje se trenutna verzija.
- Web koji prima cjenik mora i sam čuvati prethodne verzije najmanje 30 dana i objaviti ih (arhiva).

## Datoteka

CSV, UTF-8 s BOM-om (ispravno se otvara u Excelu), odvojeno točkom sa zarezom, decimalni zarez, datumi
`dd.mm.gggg`. Stupci su isti za robu i usluge i za sve objekte (propisana jednaka struktura):

| Stupac | Sadržaj |
|---|---|
| `sifra` | Interna oznaka proizvoda |
| `naziv` | Naziv proizvoda (na hrvatskom ako je hrvatski uključen, inače na jeziku tvrtke) |
| `marka` | Marka (roba) |
| `jedinica_mjere` | Jedinica mjere proizvoda |
| `maloprodajna_cijena_eur` | Cijena za potrošača s PDV-om |
| `cijena_za_jedinicu_mjere_eur`, `jedinica_mjere_za_cijenu` | Cijena po osnovnoj jedinici (npr. po kg ili l), vidi *Cijena za jedinicu mjere* |
| `posebni_oblik_prodaje`, `naziv_posebnog_oblika_prodaje` | `da` i naziv akcije kad cijenu daje pravilo cjenika s *Posebnim oblikom prodaje* (vidi *Akcije*), inače `ne` i prazno |
| `dodatna_cijena_eur`, `datum_dodatne_cijene` | Dodatna cijena objekta i njezin datum |
| `barkod` | Barkod proizvoda |
| `raspolozivost` | `dostupno` / `nedostupno` (roba), prazno (usluge), vidi *Raspoloživost* |

**Cijena za jedinicu mjere** (npr. hrana na težinu ili volumen): proizvod treba osnovnu jedinicu i
količinu u pakiranju. To su standardna polja aplikacije *Web stranica / eCommerce* (*Postavke → Web
stranica → Referentna cijena proizvoda*, pa na proizvodu *Osnovna jedinica* i količina). Bez eCommerce
aplikacije stupci ostaju prazni.

**Raspoloživost**: roba koja prati zalihu (aplikacija *Skladište*) je `dostupno` kad je ima na zalihi.
Uz aplikaciju Skladište sam se instalira modul *Javni cjenik: zaliha po objektu*
(`l10n_hr_price_list_stock`): ako imate više skladišta (uključena *Skladišta* u postavkama Skladišta),
na objektu odaberite **Skladište** – tada se gleda zaliha samo toga skladišta, kako propis traži za
svaki objekt posebno. Prazno: zaliha cijele tvrtke.

## Ograničenja

- **Jedna cijena za sve objekte**: svi objekti imaju cijene zadanog cjenika (ili prodajne cijene). Objekti s
  različitim cijenama istog proizvoda (npr. lanac u kojem svaka trgovina u blagajni ima svoj cjenik) nisu
  podržani.
- **Promocije iz aplikacije *Popusti i vjernost*** (npr. „2+1“, popust na košaricu) su uvjeti na narudžbi, a
  ne cijena proizvoda, pa se u cjeniku ne vide. Sniženje cijene artikla radite pravilom cjenika (vidi
  *Akcije*).
- **Odoo web trgovina sa zasebnim cjenikom za web**: javni cjenik i dalje objavljuje cijene zadanog cjenika
  (kao na ponudama), ne cjenika web trgovine.
- **Najniža cijena u 30 dana prije akcije** nije stupac propisane datoteke: modul je šalje webhookom, a uz
  akcijsku cijenu u prodaji i na webu ističete je vi. Računa se iz cjenika objavljenih ovim modulom (prije
  prve objave nema podataka).
- **Cijene koje nisu unaprijed određene** (izrada po specifikaciji kupca): objavite elemente cijene kao
  zasebne proizvode (npr. sat rada, m², dolazak), ne izračune za pojedinog kupca.
- Pravilnik o „baznim cijenama“ je u nacrtu; ako propiše drukčije nazive ili oblik, modul će se uskladiti.

## Prijevod na hrvatski

Svi tekstovi modula (polja, gumbi, poruke, javne stranice) prevedeni su na hrvatski (`i18n/hr.po`),
pojmovima iz odluka i pojašnjenja Ministarstva (dodatna cijena, oblik, adresa i oznaka objekta, broj
pohrane, raspoloživost). Prijevodi se učitavaju pri instalaciji i nadogradnji. Ako ste hrvatski dodali
u bazu nakon instalacije modula: *Postavke → Jezici*, ažurirajte **Hrvatski**. Javne stranice
prikazuju se na hrvatskom (ako je uključen u bazi).

## Za programere

- Ovisi samo o `account`. Skladište (`is_storable`, `qty_available`) i eCommerce (`base_unit_id`,
  `base_unit_count`) koristi ako su instalirani.
- Modeli: `l10n_hr.price.list.location` (objekt: oblik, adresa, oznaka, kategorije, webhook),
  `l10n_hr.price.list.version` (broj pohrane po objektu, naziv, datoteka kao privitak, `checksum`, retci za
  webhook `rows_json`, stanje webhooka), `l10n_hr.price.list.anchor` (dodatna cijena po objektu i varijanti;
  mijenja je samo `base.group_system`). Nova verzija kad se promijeni SHA-256 redaka (uključujući prodajnu
  cijenu bez PDV-a) i dijela naziva (objekt).
- Predložak proizvoda: `price_list_brand`, `price_list_anchor_ids`.
- Cron *Javni cjenik: objava promjena* jednom dnevno u 04:00 UTC; promjene proizvoda, kategorija,
  objekata, dodatnih cijena, cjenika i pravila cjenika zakažu ga za minutu (jednom po transakciji; ne za
  vrijeme same objave), neuspjeli webhook za sat vremena. Verzije se spremaju (`commit`) prije slanja webhooka.
- Pravilo cjenika (`product.pricelist.item`): `price_list_special_sale` (naziv posebnog oblika prodaje).
  Cijena: `_consumer_pricelist()` (kao `_get_partner_pricelist_multi` za kupca iz države tvrtke bez
  vlastitog cjenika; ništa kad su Cjenici isključeni) i `_compute_price_rule`; pravilo s nazivom = `da`.
  Cijena prije akcije i najniža cijena (`_special_sale_prices`) iz `rows_json` verzija objekta: početak akcije
  je najstarija od zadnjih uzastopnih verzija s `da` (retci spremaju `_product_id`, koji se ne objavljuje i
  nije u `checksum`; starije verzije po šifri). Promjene cjenika i pravila zakažu objavu.
- Modul `l10n_hr_price_list_stock` (auto_install uz `stock`): `warehouse_id` na objektu, `_availability`
  sa zalihom toga skladišta.
- Proširenja na objektu: `_row(product, price, anchor, special_sale)` (redak cjenika), `_prices`,
  `_availability`, `_products`.
- Testovi: `--test-tags /l10n_hr_price_list`.
