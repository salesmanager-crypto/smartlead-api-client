# Trade Show Calendar: rules and research method

This folder holds Albert Scott's calendar of European and UK trade shows where most exhibitors are
consumer-product brands that could sell on Amazon US. Albert Scott helps brands (mostly European)
launch and grow on Amazon US and runs its own US warehouse. The team goes to these shows to meet
exhibiting brands.

```
trade-show-calendar/
├── index.html        # the calendar page: self-contained, opens by double-clicking
├── data/shows.js     # all data: window.SHOWS = [...]; window.META = {...};
├── CHANGELOG.md      # one entry per research or update run
├── CLAUDE.md         # this file
└── tools/datafile.mjs  # validate | export | import | sheet: load, check and save shows.js
```

Slash commands live in the repo root at `.claude/commands/`:
- `/research-month <Month Year>`: research one month, from scratch or adding to what is there.
- `/refresh-all`: re-check every month from the current month through July 2027.

Both commands follow the method in this file. If you change the method, change it here and in both
command files.

---

## 1. Geography

Include: the EU, the UK, Ireland, Switzerland, Norway, Iceland and the Balkans (Serbia, Bosnia and
Herzegovina, Montenegro, North Macedonia, Albania, Kosovo, plus EU members Slovenia, Croatia,
Bulgaria, Romania and Greece).
Include shows in **Istanbul**, with `country: "Türkiye (Istanbul)"` so they're clearly marked.
Exclude Russia, Belarus and anything outside Europe (Dubai, Hong Kong, US, etc.).

Use English country names: `Germany`, `United Kingdom`, `France`, `Italy`, `Spain`, `Netherlands`,
`Belgium`, `Switzerland`, `Austria`, `Poland`, `Denmark`, `Sweden`, `Norway`, `Finland`, `Ireland`,
`Portugal`, `Czech Republic`, `Hungary`, `Greece`, `Romania`, `Bulgaria`, `Croatia`, `Slovenia`,
`Serbia`, `Türkiye (Istanbul)`, etc.

## 2. Which shows qualify

Include a show only if **most of its exhibitors are brands or manufacturers of physical consumer
products that could be sold on Amazon US.**

Relevant sectors. Use these exact labels in `sectors[]`, so the filters work:

| Label | Covers |
|---|---|
| `Food & Beverage` | packaged, shelf-stable food and soft drinks: snacks, confectionery, sweets, free-from, organic/natural, health foods, speciality and fine food, non-alcoholic drinks |
| `Coffee & Tea` | coffee, tea and related consumer equipment |
| `Fashion & Apparel` | clothing, womenswear, menswear, denim, streetwear |
| `Footwear` | shoes |
| `Lingerie & Swimwear` | lingerie, underwear, swimwear, beachwear |
| `Kids & Baby` | kids' fashion, baby goods, nursery, maternity |
| `Accessories & Jewellery` | bags, luggage, leather goods, jewellery, watches, eyewear |
| `Gift & Stationery` | gifting, stationery, paper, office supplies for consumers, party goods |
| `Christmas & Seasonal` | Christmas, seasonal decorations, festive goods |
| `Home & Interiors` | home decor, lifestyle, furniture accessories, home textiles, lighting |
| `Housewares & Kitchen` | housewares, kitchenware, tableware, cookware, small domestic appliances |
| `Garden & DIY` | garden, outdoor living, BBQ, consumer DIY tools and hardware |
| `Beauty & Personal Care` | cosmetics, fragrance, skincare, hair, nails, grooming |
| `Health & Supplements` | consumer health and wellness products, supplements, vitamins, sports nutrition |
| `Toys & Games` | toys, games, puzzles |
| `Licensing` | licensed consumer products |
| `Hobby & Crafts` | crafts, DIY creative, model making, hobby |
| `Sports & Outdoor` | sports, outdoor, fitness, camping, surf/watersports, winter sports |
| `Cycling` | bikes, e-bikes, cycling gear |
| `Hunting & Fishing` | fishing tackle, hunting and shooting accessories, optics |
| `Automotive Aftermarket` | consumer car and motorbike accessories, car care, tuning (not workshop equipment) |
| `Consumer Electronics & Tech` | consumer electronics, small appliances, gaming, smart home, mobile accessories |
| `Pet Supplies` | pet food, accessories and care |

**Exclude these sub-sectors:** fresh produce, frozen food, and alcoholic drinks (wine, beer, spirits).

**Exclude these show types:** services-led shows (marketing, ecommerce, logistics, finance, SaaS,
franchising), industrial, machinery or manufacturing shows, packaging, ingredients and food
processing, B2B enterprise tech, medical, pharma or dental, construction, agriculture, energy,
conferences with no product exhibitors, and pure retail fairs with no brand exhibitors (e.g.
Christmas markets where traders resell).

**Large mixed shows** (e.g. SIAL, Anuga, Automechanika, Gulfood-style generalists): include them with
`amazon_fit: "partial"` when a large share of exhibitors fit, and name the relevant halls or sections
in `fit_notes`.

**Consumer shows** (public fairs) count only if most exhibitors are brands or manufacturers (not
resellers or services). Mark them `audience: "consumer"` or `"trade+consumer"`.

**Amazon-fit rating**
- `strong`: most exhibitors are consumer-product brands in the sectors above.
- `partial`: a large share fits, but the show is mixed (name the halls or sections in `fit_notes`).
- Anything less doesn't go in the calendar.

Every show needs a one-line `fit_notes` explaining why it passes the consumer-brand/Amazon test.

**Reference shows the team has attended** (use them to judge fit): London Coffee Festival, World of
Coffee, Coffee Fest, Formex, Nordstil, Home & Gift Harrogate, Autumn Fair, Spring Fair, IFA Berlin,
ISM Cologne, Free From Vienna, Cosmoprof, Tones of Beauty, Premier, Toy Fair, Global Pet, SuperZoo,
Expo West, Newtopia Now, Sweets & Snacks, Winter Fancy Food, Tea Expo, IHS, ABC Kids, CES, SHOT Show,
ICAST, Surf Expo, Outdoor Retailer, JCK, New York Now, ASD and MAGIC. Find their European equivalents
(Ambiente, Christmasworld, Spielwarenmesse, Kind + Jugend, ISPO, IWA OutdoorClassics, Interzoo,
Maison&Objet, Paperworld, Cosmoprof Bologna, Beautyworld, Spring Fair, Top Drawer, Pure London, Toy
Fair London, Natural & Organic Products Europe, Vitafoods, SIAL, Anuga, Biofach, ISM, Eurobike,
Automechanika and so on). These are examples, not a checklist. Find everything.

## 3. Where to search (be exhaustive; one search is never enough)

Search each month from several angles and cross-check the results:

1. **Trade fair databases:** AUMA (auma.de), Expodatabase, EventsEye, 10times, TradeFairDates,
   N-Expo, the m+a expo database, UFI, the GTAI fair calendar and national associations (AEO events
   calendar for the UK, FKM, CENTREX, Unimev, AEFI and so on).
2. **Venue and organiser calendars:** Messe Frankfurt, Koelnmesse, Messe München, Messe Düsseldorf,
   NürnbergMesse, Messe Berlin, Messe Stuttgart, Messe Essen, Hamburg Messe, Spielwarenmesse eG,
   Fiera Milano, BolognaFiere, IEG (Rimini/Vicenza), Pitti Immagine, Veronafiere, IFEMA, Fira
   Barcelona, Comexposium, RX Global, Informa Markets, Clarion, Hyve, Easyfairs, Jaarbeurs, RAI
   Amsterdam, Bella Center/MCH, Stockholmsmässan, Messe Wien, Ptak Warsaw Expo, Poznań, Helexpo, Fira
   Valencia, Exponor/FIL Lisbon, Brussels Expo, Paris Nord Villepinte and Porte de Versailles. UK:
   NEC Birmingham, ExCeL, Olympia, Business Design Centre, Harrogate Convention Centre, Manchester
   Central and SEC Glasgow. Istanbul: Tüyap, Istanbul Expo Center (IFM) and the Lütfi Kırdar centre.
3. **Sector searches in English and local languages:** German "Messe", French "salon
   professionnel", Italian "fiera", Spanish "feria", Dutch "beurs", Polish "targi", Swedish "mässa",
   Danish/Norwegian "messe", Turkish "fuarı", Czech "veletrh", Portuguese "feira". Combine each with
   each sector and the month.
4. **Trade press and industry associations** that publish show calendars: Toy World, Progressive
   Preview, Drapers, Fashion United, Cosmetics Business, Premium Beauty News, Pet Industry News,
   Kitchenware International, Gift Focus, Giftware Review, Bike Europe, Spielwaren, Textilwirtschaft,
   Food Navigator and so on.

Use subagents in parallel (split by sector group or by country) to cover ground, then merge the
results and remove duplicates.

## 4. Exhibitor numbers: never give up early

Follow this order and record the source URL for each figure:

1. **This edition's official figure:** the organiser's website, press releases, "facts & figures"
   or media kit pages, newsletters, or the organiser's LinkedIn posts. Set `exhibitors_current`,
   `exhibitors_current_source`, and `exhibitors_status: "current"`.
2. **Count it yourself** if no figure has been announced: open the online exhibitor
   directory or list for this edition and count the entries (page through it, or use its total).
   Note "counted from exhibitor list on YYYY-MM-DD" in `exhibitors_note`. Status `"current"`.
3. **Last edition's final figure** if this edition's isn't available: the post-show report or
   closing press release, FKM-certified statistics (fkm.de), AUMA statistics, the organiser's annual
   report, or trade press reviews. Set `exhibitors_previous`, `exhibitors_previous_year` and
   `exhibitors_previous_source`, with status `"previous"`.
4. **The edition before that** if that's still missing, clearly labelled with its year (also
   status `"previous"`).

Only use `"not_found"` after trying all of the above, and list **every** source checked in
`sources_checked`. Don't round, guess, or mix up exhibitors with visitors. If the figure counts
"exhibitors and brands", "co-exhibitors" or "represented companies", say so in `exhibitors_note`.
An "expected" or "planned" figure for this edition counts as current, but say "expected" in
`exhibitors_note`. A "500+" claim is stored as 500 with "500+ (organiser claim)" in `exhibitors_note`.

## 5. App

Check the show's website (search "app", "download", "mobile app", "plan your visit"), the Apple App
Store and Google Play, and the organiser's group app (e.g. Messe Frankfurt's shared "Messe Frankfurt
Navigator"-style apps, Koelnmesse's app, the "Spielwarenmesse" app). Also check event platforms like
Swapcard, Grip, Brella, MapYourShow, N200 and Expo-Platform, where the show may sit inside a generic
app with an event code. Record the exact app name as listed in the store (`app_name`), the platform
(`app_platform`), and in `notes` how to find the show inside the app. If you can't tell, use
`has_app: "unknown"`.

## 6. Data model (`data/shows.js`)

```js
window.META = {
  last_updated: "YYYY-MM-DD",           // date of the latest research or update run
  researched_months: ["2026-11", ...],  // months that have been researched (even if empty)
  month_notes: { "2026-11": "..." },    // optional per-month coverage notes
  run_log: [{ date, command, summary }] // short history; full detail in CHANGELOG.md
};
window.SHOWS = [ { ...show }, ... ];
```

Show fields:

| field | type / values | notes |
|---|---|---|
| `id` | string | slug of name + edition year, e.g. `ambiente-2027`. Stable across runs. |
| `name` | string | official name |
| `edition_year` | number | |
| `start_date`, `end_date` | `"YYYY-MM-DD"` or null | null only when `status: "dates TBC"` and no date is known |
| `months_covered` | `["YYYY-MM", ...]` | every month the show touches (a show crossing two months appears in both) |
| `city`, `country`, `venue` | string | |
| `organiser` | string | |
| `website` | URL | the official show page, checked to open to the right show |
| `sectors` | string[] | labels from section 2 |
| `audience` | `"trade"` \| `"trade+consumer"` \| `"consumer"` | |
| `exhibitors_current` | number \| null | this edition |
| `exhibitors_current_source` | URL \| null | |
| `exhibitors_previous` | number \| null | latest earlier edition with a figure |
| `exhibitors_previous_year` | number \| null | |
| `exhibitors_previous_source` | URL \| null | |
| `exhibitors_status` | `"current"` \| `"previous"` \| `"not_found"` | |
| `exhibitors_note` | string | e.g. "incl. co-exhibitors", "counted from exhibitor list on 2026-10-27" |
| `sources_checked` | string[] | every source tried (URLs or names) |
| `has_app` | `true` \| `false` \| `"unknown"` | |
| `app_name` | string \| null | exact store name |
| `app_platform` | string \| null | own app, Swapcard, Grip, Brella, MapYourShow, ... |
| `app_source` | URL \| null | |
| `amazon_fit` | `"strong"` \| `"partial"` | |
| `fit_notes` | string | one line on why it passes; halls or sections for partial |
| `status` | `"confirmed"` \| `"dates TBC"` \| `"postponed"` \| `"cancelled"` | |
| `added_on` | `"YYYY-MM-DD"` | the run that first added it (drives the "New" badge) |
| `updated_on` | `"YYYY-MM-DD"` \| null | the latest run that changed data (drives the "Updated" badge) |
| `changes` | string[] | what changed in that run, e.g. "exhibitors: 1,240 (2025) → 1,310 (2026)" |
| `last_verified` | `"YYYY-MM-DD"` | |
| `notes` | string | anything else: app instructions, co-located shows, caveats |

A show is labelled **New** when `added_on === META.last_updated` and **Updated** when
`updated_on === META.last_updated`.

Never delete a show silently. If a show is cancelled, set `status: "cancelled"` and explain in
`notes`. If a record has to be removed (a duplicate, or out of scope), log the id and the reason in
CHANGELOG.md.

## 7. Quality checks before saving

- Check the dates against the official website. Third-party databases are often out of date. If the
  dates aren't confirmed, use `status: "dates TBC"`.
- Remove duplicates (the same show under different names or translations; co-located shows that
  share one exhibitor count). Co-located but separately branded shows can stay as separate rows if
  each has its own exhibitors.
- Check that every `website` opens to the right show.
- Every show needs `fit_notes`.
- `months_covered` must match the dates.
- Run `node trade-show-calendar/tools/datafile.mjs validate`. It must print `OK`, which means the
  page will load. `import` refuses to write data that fails the schema check.
- Finish with a short report: shows per month; how many have current vs previous vs missing
  exhibitor figures; and the list of `not_found` shows for manual checking.

## 8. Team Google Sheet sync

Sheet: https://docs.google.com/spreadsheets/d/1-k0Vo7qEbA04p5WCWhWwIbICEJNOCIZ7LLqzhKcCIxE/edit

- Every show with **more than 500 exhibitors** (current or last edition's figure) goes on the
  tab for the month **it starts in**.
- If that month's tab doesn't exist, duplicate the latest month tab (`duplicateSheet`), rename it
  to the month name (e.g. "January"; if a month already appears inside another tab, such as the
  2026 "June/July" tab, add the year, e.g. "June 2027"), then clear the copied rows below the header
  (columns A–F only; the copied rep and status cells below the header are also cleared on a
  brand-new tab, because they belong to the old month).
- Only write in **columns A–F**: Show, Location, Dates, Exhibitors, Sector, Website. **Never**
  edit, clear or reformat the rep-name columns, "Assigned To" or "Status" on existing rows, and never
  delete or reorder existing rows.
- Append new shows below the last filled row. Skip any show already on that tab (match by name,
  allowing for small spelling differences).
- When an exhibitor number changes, change only column D of that row.
- Formats: Location `City (Venue), Country`; Dates `05–08 Nov 2026` (en dash, two-digit days;
  `28 Nov–06 Dec 2026` across months); Exhibitors `1,240` for this edition or `861 (2025)` for the
  last edition's figure; Website is the full URL.
