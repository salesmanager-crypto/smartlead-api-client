---
description: Re-check every month of the Trade Show Calendar from the current month through July 2027, adding new shows and updating figures, apps and status
---

# /refresh-all

Re-check the whole Trade Show Calendar (`trade-show-calendar/`) **from the current month through
July 2027**, using the same thorough method as `/research-month`. A refresh is not just a
spot-check of existing rows. For every month in range:

1. **Find newly announced shows** using the full search method (all four angles below, run as
   parallel subagents by sector group), and add the ones that qualify.
2. **Re-check every existing show:**
   - **Exhibitor numbers:** swap "previous year" figures (`exhibitors_status: "previous"`) for this
     edition's figure as soon as one is announced or the exhibitor list can be counted. Retry
     every `not_found` show with the full source order. Update numbers that have changed (e.g. a
     final figure replacing an "expected" one).
   - **Dates and status:** confirm `dates TBC` shows; mark postponements and cancellations
     (`status: "postponed" | "cancelled"`, with the reason in `notes`).
   - **App:** shows often launch their app 4 to 8 weeks before opening. Update `has_app`,
     `app_name`, `app_platform` and `app_source`.
   - **Website:** check it still opens to the right show (and the right edition).
3. **Never delete a show** without writing the id and the reason in CHANGELOG.md. Past shows stay
   in the data as history. Cancelled shows stay with `status: "cancelled"`.

## Setup

- `RUN = $(date +%F)`. The first month = the current month (`date +%Y-%m`); the last month = 2027-07.
- Read `trade-show-calendar/CLAUDE.md` (full rules, sector labels, data model).
- `node trade-show-calendar/tools/datafile.mjs export <scratch>/current.json`, then keep a copy as
  `<scratch>/before.json` for the diff.

## Inclusion rules (same as /research-month)

**Geography:** the EU, UK, Ireland, Switzerland, Norway, Iceland and the Balkans. Include Istanbul as
`country: "Türkiye (Istanbul)"`. Exclude Russia, Belarus and anything outside Europe.

**Qualifies** only if most exhibitors are brands or manufacturers of physical consumer products that
could be sold on Amazon US. The sectors are: packaged/shelf-stable food and soft drinks (snacks,
confectionery, coffee, tea, free-from, organic, health and fine food; **not** fresh produce, frozen
food or alcohol); fashion, footwear, lingerie, swimwear and kids' fashion; bags, luggage, jewellery,
watches and eyewear; gifting, stationery, party and seasonal/Christmas; consumer automotive accessories
and aftermarket; consumer electronics, small appliances, gaming and smart home; toys, games, hobby,
crafts and licensing; kids, baby and maternity; sports, outdoor, fitness, cycling, watersports,
camping, fishing and hunting/shooting accessories; beauty, cosmetics, fragrance, skin, hair, nails and
grooming; health and wellness consumer products and supplements; pet supplies; home, interiors,
housewares, kitchen, tableware, textiles, lighting, garden and consumer DIY. Use only the sector
labels in CLAUDE.md section 2.

**Exclude** services-led shows (marketing, ecommerce, logistics, finance, SaaS, franchising),
industrial/machinery, packaging, ingredients and food processing, B2B enterprise tech,
medical/pharma/dental, construction, agriculture, energy, conferences with no product exhibitors, and
pure retail fairs with no brand exhibitors. Large mixed shows (SIAL, Anuga, Automechanika) are
`amazon_fit: "partial"`, with the relevant halls or sections named in `fit_notes`.

## Search method (same as /research-month)

For each month, split the work across parallel subagents by sector group (food/coffee; fashion and
accessories; home/gift/stationery/Christmas/garden; beauty/health/pet; toys/kids/hobby;
sports/outdoor/auto/tech). Give each one the existing shows for its months, so it updates them rather
than duplicating them. Each agent searches from all four angles and cross-checks:
1. **Trade fair databases:** AUMA, Expodatabase, EventsEye, 10times, TradeFairDates, N-Expo, m+a expo
   database, UFI, the GTAI fair calendar, national associations (AEO for the UK).
2. **Venue and organiser calendars:** Messe Frankfurt, Koelnmesse, Messe München, Messe Düsseldorf,
   NürnbergMesse, Messe Berlin, Spielwarenmesse eG, Fiera Milano, BolognaFiere, IEG, IFEMA, Fira
   Barcelona, Comexposium, RX Global, Informa Markets, Clarion, Hyve, Easyfairs, Jaarbeurs, Bella
   Center/MCH, Stockholmsmässan, Messe Wien, Ptak Warsaw Expo, Poznań, Helexpo, Fira Valencia,
   Exponor/FIL, Brussels Expo, Paris Nord Villepinte, Porte de Versailles, NEC, ExCeL, Olympia,
   Business Design Centre, Harrogate, Manchester Central, SEC Glasgow, Tüyap, Istanbul Expo Center.
3. **Sector searches in English and local languages:** Messe, salon professionnel, fiera, feria,
   beurs, targi, mässa, messe, fuarı, veletrh, feira, combined with each sector and month.
4. **Trade press and associations:** Toy World, Progressive Preview, Drapers, FashionUnited,
   Cosmetics Business, Pet Industry News, Kitchenware International, Gift Focus, Bike Europe...

**Exhibitor numbers**, in order, always with a source URL: (1) this edition's official figure
(organiser site, press release, facts & figures or media kit, newsletter, LinkedIn); (2) count this
edition's online exhibitor list ("counted from exhibitor list on RUN" in `exhibitors_note`);
(3) last edition's final figure (post-show report, closing release, FKM, AUMA, annual report, trade
press); (4) the edition before, labelled with its year. Only use `not_found` after all four, with every
source listed in `sources_checked`. Don't round, guess, or mix up exhibitors with visitors.

**App:** the show website, App Store, Google Play, the organiser's group app, and Swapcard, Grip, Brella,
MapYourShow, N200 and Expo-Platform. Record the exact store name and how to find the show in the app.

## Recording changes

- New shows: `added_on = RUN`, `updated_on = null`, `changes = []`.
- Changed shows: `updated_on = RUN`, with `changes` listing each change in plain words, e.g.
  `"exhibitors: 1,240 (2025 edition) → 1,310 (2026, official)"`, `"dates confirmed: 12–14 Mar 2027"`,
  `"app added: Spielwarenmesse (own app)"`, `"status: confirmed → postponed"`. Overwrite
  `changes` from older runs (the CHANGELOG keeps the history).
- Unchanged shows you re-checked: only `last_verified = RUN`.
- META: `last_updated = RUN`; make sure every month in range is in `researched_months`; append to
  `run_log`.

## Quality checks, save and sync

Follow sections 6 to 8 of `.claude/commands/research-month.md` exactly: check dates against the
official sites, dedupe, check every link, write `fit_notes`, run `datafile.mjs import` and then
`datafile.mjs validate` (must print OK), and add a CHANGELOG.md entry. Then sync the Google Sheet:
for each month, run `datafile.mjs sheet YYYY-MM`, append shows with more than 500 exhibitors that
aren't on the tab yet (columns A–F only), and update **only column D** where a listed show's exhibitor
figure changed. Never touch the rep, "Assigned To" or "Status" columns, and never delete or reorder rows.

## Summary to print at the end

Diff `before.json` against the saved data and print:
- **Added:** each new show (month, name, exhibitor figure)
- **Updated:** each changed show with its `changes`
- **Previous → current figures swapped:** count and list
- **Status changes:** postponed, cancelled, dates confirmed
- **Removed:** ids and reasons (should be rare)
- **Per month:** shows, and current / previous / not_found counts
- **Still not_found:** the list for manual checking
- **Google Sheet:** rows appended and column D cells updated, per tab

Commit `trade-show-calendar/` with a message like "Refresh trade show calendar (RUN)".
