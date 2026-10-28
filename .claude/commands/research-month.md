---
description: Research every qualifying Europe/UK consumer-brand trade show for one month and add it to the Trade Show Calendar
argument-hint: <Month Year>, e.g. March 2027 or 03/2027
---

# /research-month $ARGUMENTS

Research **every** trade show in Europe and the UK that starts in, or runs into, **$ARGUMENTS** and
where most exhibitors are consumer-product brands that could sell on Amazon US. Add the results to the
Trade Show Calendar in `trade-show-calendar/`. If the month already has data, keep it, add to it and
update it. Don't start over.

Albert Scott helps brands (mostly European) launch and grow on Amazon US and runs a US warehouse. The
team goes to these shows to meet exhibiting brands, so missing a relevant show is the costliest mistake.

## 0. Setup

1. Turn `$ARGUMENTS` into `YYYY-MM` (accept "March 2027", "Mar 2027", "03/2027", "2027-03"). If it
   can't be parsed, ask.
2. Read `trade-show-calendar/CLAUDE.md`, which has the full rules, sector labels and data model.
   The essentials are repeated below so this command works on its own.
3. Export the current data: `node trade-show-calendar/tools/datafile.mjs export <scratch>/current.json`
   and list the shows already in this month (`months_covered` includes `YYYY-MM`).
4. Today's date (`date +%F`) is the run date: `RUN`.

## 1. Inclusion rules

**Geography:** the EU, UK, Ireland, Switzerland, Norway, Iceland and the Balkans. Include Istanbul with
`country: "Türkiye (Istanbul)"`. Exclude Russia, Belarus and anything outside Europe.

**Qualifies** only if most exhibitors are brands or manufacturers of physical consumer products that
could be sold on Amazon US. The sectors are:
- Food and beverage (packaged, shelf-stable): snacks, confectionery, sweets, coffee, tea, free-from,
  organic/natural, health foods, speciality and fine food, non-alcoholic drinks. **Exclude** fresh
  produce, frozen food and alcohol (wine, beer, spirits).
- Clothing, fashion, footwear, lingerie, swimwear, kids' fashion
- Accessories: bags, luggage, jewellery, watches, eyewear
- Gifting, stationery, paper, party goods, seasonal/Christmas
- Automotive accessories and aftermarket (consumer products, not workshop equipment)
- Tech, consumer electronics, small home appliances, gaming, smart home
- Toys, games, hobbies, crafts, licensing
- Kids and baby, maternity
- Sports, outdoor, fitness, cycling, surf/watersports, camping, fishing, hunting/shooting accessories
- Beauty, cosmetics, fragrance, skincare, hair, nails, personal care, grooming
- Health and wellness consumer products, supplements, vitamins
- Pet supplies
- Home: interiors, decor, lifestyle, housewares, kitchenware, tableware, home textiles, lighting,
  garden, consumer DIY tools and hardware

Use only the `sectors[]` labels listed in CLAUDE.md section 2.

**Exclude** services-led shows (marketing, ecommerce, logistics, finance, SaaS, franchising),
industrial/machinery/manufacturing, packaging, ingredients and food processing, B2B enterprise tech,
medical/pharma/dental, construction, agriculture, energy, conferences with no product exhibitors, and
pure retail fairs with no brand exhibitors.

**Large mixed shows** (SIAL, Anuga, Automechanika...) get `amazon_fit: "partial"` when a large share
of exhibitors fit. Name the relevant halls or sections in `fit_notes`.

**Reference shows the team has attended:** London Coffee Festival, World of Coffee, Coffee Fest, Formex,
Nordstil, Home & Gift Harrogate, Autumn Fair, Spring Fair, IFA Berlin, ISM Cologne, Free From Vienna,
Cosmoprof, Tones of Beauty, Premier, Toy Fair, Global Pet, SuperZoo, Expo West, Newtopia Now, Sweets &
Snacks, Winter Fancy Food, Tea Expo, IHS, ABC Kids, CES, SHOT Show, ICAST, Surf Expo, Outdoor Retailer,
JCK, New York Now, ASD, MAGIC. Find their European equivalents (Ambiente, Christmasworld,
Spielwarenmesse, Kind + Jugend, ISPO, IWA OutdoorClassics, Interzoo, Maison&Objet, Paperworld,
Cosmoprof Bologna, Beautyworld, Spring Fair, Top Drawer, Pure London, Toy Fair London, Natural &
Organic Products Europe, Vitafoods, SIAL, Anuga, Biofach, ISM, Eurobike, Automechanika...). These are
examples, not a checklist. **Find everything.**

## 2. Search exhaustively (one search is never enough)

Run subagents in parallel, one per sector group, each covering the whole geography for this one month
(more agents for big months):
1. Food & beverage + coffee/tea
2. Fashion, footwear, lingerie, kids' fashion, accessories, jewellery, watches, eyewear
3. Home, interiors, housewares, gift, stationery, Christmas, garden/DIY
4. Beauty, health and supplements, pet
5. Toys, licensing, kids and baby, hobby and crafts
6. Sports, outdoor, cycling, hunting/fishing, automotive aftermarket, consumer tech

Give each agent this method, the inclusion rules and the data model, the list of shows already
in this month (so it updates them rather than duplicating them), and a scratch file to write a JSON array
to. Each agent must search from all of these angles and cross-check:

1. **Trade fair databases:** AUMA (auma.de), Expodatabase, EventsEye, 10times, TradeFairDates, N-Expo,
   m+a expo database, UFI, the GTAI fair calendar, national associations (AEO events calendar for the UK).
2. **Venue and organiser calendars:** Messe Frankfurt, Koelnmesse, Messe München, Messe Düsseldorf,
   NürnbergMesse, Messe Berlin, Spielwarenmesse eG, Fiera Milano, BolognaFiere, IEG (Rimini/Vicenza),
   IFEMA, Fira Barcelona, Comexposium, RX Global, Informa Markets, Clarion, Hyve, Easyfairs, Jaarbeurs,
   Bella Center/MCH, Stockholmsmässan, Messe Wien, Ptak Warsaw Expo, Poznań, Helexpo, Fira Valencia,
   Exponor/FIL Lisbon, Brussels Expo, Paris Nord Villepinte, Porte de Versailles; UK: NEC Birmingham,
   ExCeL, Olympia, Business Design Centre, Harrogate Convention Centre, Manchester Central, SEC Glasgow;
   Istanbul: Tüyap, Istanbul Expo Center.
3. **Sector searches in English and local languages:** German "Messe", French "salon professionnel",
   Italian "fiera", Spanish "feria", Dutch "beurs", Polish "targi", Swedish "mässa", Danish/Norwegian
   "messe", Turkish "fuarı", Czech "veletrh", Portuguese "feira". Combine each with each sector and the
   month.
4. **Trade press and associations** with show calendars: Toy World, Progressive Preview, Drapers,
   FashionUnited, Cosmetics Business, Pet Industry News, Kitchenware International, Gift Focus, Bike
   Europe and so on.

Also include shows that start in the previous month but run into this one, and record every month a
show touches in `months_covered`.

## 3. Exhibitor numbers: never give up early

Record the source URL for each figure, in this order:
1. **This edition's official figure:** organiser website, press releases, "facts & figures" or media
   kit pages, newsletters, organiser LinkedIn posts. → `exhibitors_current`, status `"current"`.
2. **Count it yourself:** open this edition's online exhibitor directory or list and count the
   entries (page through it, or use the directory's total). Note
   "counted from exhibitor list on RUN" in `exhibitors_note`. → status `"current"`.
3. **Last edition's final figure:** post-show report or closing press release, FKM-certified
   statistics (fkm.de), AUMA statistics, organiser annual report, trade press review.
   → `exhibitors_previous` + `exhibitors_previous_year` + source, status `"previous"`.
4. **The edition before that**, clearly labelled with its year.

Only use `"not_found"` after trying all of these, and list every source checked in
`sources_checked`. Don't round, guess, or mix up exhibitors with visitors. "Exhibitors and brands" or
"incl. co-exhibitors" goes in `exhibitors_note`.

## 4. App

Check the show website ("app", "download", "mobile app", "plan your visit"), the Apple App Store,
Google Play, the organiser's group app, and platforms like Swapcard, Grip, Brella, MapYourShow,
N200 and Expo-Platform (the show may be inside a generic app with an event code). Record the exact store
name (`app_name`), `app_platform`, `app_source`, and in `notes` how to find the show inside the app.
Use `has_app: "unknown"` only if you really can't tell.

## 5. Data model

Each show has: `id` (slug + edition year, stable), `name`, `edition_year`, `start_date`, `end_date`
(`YYYY-MM-DD` or null if TBC), `months_covered` (`["YYYY-MM"]`, every month touched), `city`,
`country`, `venue`, `organiser`, `website`, `sectors[]`, `audience`
(`"trade"|"trade+consumer"|"consumer"`), `exhibitors_current`, `exhibitors_current_source`,
`exhibitors_previous`, `exhibitors_previous_year`, `exhibitors_previous_source`, `exhibitors_status`
(`"current"|"previous"|"not_found"`), `exhibitors_note`, `sources_checked[]`, `has_app`
(`true|false|"unknown"`), `app_name`, `app_platform`, `app_source`, `amazon_fit` (`"strong"|"partial"`),
`fit_notes`, `status` (`"confirmed"|"dates TBC"|"postponed"|"cancelled"`), `added_on`, `updated_on`,
`changes[]`, `last_verified`, `notes`.

- New shows: `added_on = RUN`, `updated_on = null`, `changes = []`.
- Existing shows whose data changed: keep `added_on`, set `updated_on = RUN`, and list each change in
  `changes` ("exhibitors: 1,240 (2025) → 1,310 (2026)", "dates confirmed", "app added: X").
- Set `last_verified = RUN` on every show you re-checked.

## 6. Quality checks before saving

- Check the dates against the official website, because third-party databases are often out of date.
  If they aren't confirmed, use `status: "dates TBC"`.
- Remove duplicates (the same show under different names or translations, or a show that both agents
  found).
- Check that every `website` opens to the right show. If you can't fetch it, it must at least
  appear as the show's official site in search results.
- Every show needs a one-line `fit_notes` explaining why it passes the consumer-brand/Amazon test.
- Never delete an existing show without logging the id and the reason in CHANGELOG.md. Cancelled shows
  stay, with `status: "cancelled"`.

## 7. Save

1. Merge into `current.json`: update `META.last_updated = RUN`, add `YYYY-MM` to
   `META.researched_months` (even if no show qualifies), set `META.month_notes[YYYY-MM]` to a one-line
   coverage note, and append `{date: RUN, command: "/research-month $ARGUMENTS", summary}` to
   `META.run_log`.
2. `node trade-show-calendar/tools/datafile.mjs import <scratch>/current.json` (this refuses to write
   if the schema check fails; fix and repeat).
3. `node trade-show-calendar/tools/datafile.mjs validate` must print `OK`.
4. Add an entry at the top of `trade-show-calendar/CHANGELOG.md`: date, command, shows added (names),
   shows updated (what changed), anything removed and why.

## 8. Team Google Sheet sync

Sheet: https://docs.google.com/spreadsheets/d/1-k0Vo7qEbA04p5WCWhWwIbICEJNOCIZ7LLqzhKcCIxE/edit
(read the google-workspace skill before writing to it).

`node trade-show-calendar/tools/datafile.mjs sheet YYYY-MM` lists the shows with **more than 500
exhibitors** (current or last-edition figure) that start in this month, with their rows ready to paste.
- Put each one on the tab for the month **it starts in**. If that tab doesn't exist, duplicate the
  latest month tab (`duplicateSheet`), rename it to the month name (add the year if the name is already
  used inside another tab, e.g. "June 2027" next to "June/July"), then clear the copied rows below the
  header.
- Only write in columns **A–F** (Show, Location, Dates, Exhibitors, Sector, Website). **Never** edit,
  clear or reformat the rep-name columns, "Assigned To" or "Status", and never delete or reorder
  existing rows.
- Read the tab first. Skip shows already listed (match names loosely). Append new shows below the last
  filled row (write to an explicit `A{n}:F{m}` range).
- If an exhibitor figure changed for a show already on the tab, update **only column D** of that row.
- Formats: Dates `05–08 Nov 2026`; Exhibitors `1,240`, or `861 (2025)` for the last edition's figure.

## 9. Report

Print a short report: shows in the month (new vs updated), how many have current vs previous vs
missing exhibitor figures, the `not_found` list for manual checking, the rows written to the Google
Sheet, and anything rejected as out of scope (one line each). Then commit `trade-show-calendar/` with
a message like "Research <Month Year> trade shows".
