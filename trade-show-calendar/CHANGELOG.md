# Changelog

Newest run first. Each entry: what was added, changed or removed, and why.

## 2026-10-28: initial build, November 2026 – February 2027

**Command:** initial build (the equivalent of `/research-month` for Nov 2026, Dec 2026, Jan 2027 and Feb 2027).
The user narrowed the first build to these four months. March–July 2027 tabs show "Not researched yet".

**How it was researched.** 16 parallel subagents ran in two rounds: 8 split by sector, then 8 gap-fill
agents, followed by a merge, dedupe and manual review. **Limitation:** the research environment could
not open web pages directly (network policy blocked page fetches), so every fact comes from web-search
results and the URLs they cite. As a result:
- Many dates come from trade fair listings rather than the official site. These are marked
  `dates TBC` (54 shows).
- "Link checked" means the domain appeared as the show's official site in search results; it was not
  clicked through. Where even that failed, `notes` says "official domain not confirmed by search".
- App data is thin. Only 18 shows have a confirmed app; the rest are "unknown".

**Added: 112 shows** (counted in every month they touch):

| Month | Shows | Current figure | Last-edition figure | Not found |
|---|---|---|---|---|
| Nov 2026 | 30 | 11 | 10 | 9 |
| Dec 2026 | 4 | 3 | 0 | 1 |
| Jan 2027 | 38 | 2 | 27 | 9 |
| Feb 2027 | 49 | 0 | 27 | 22 |

(Six shows that start in late October and run into November also appear under Oct 2026 when you type
that month. One show, Athens International Jewellery Show, runs into March.)

**Removed during the merge** (never published):
- `ifco-winter-2027`: duplicate of `ifco-istanbul-2027-02`.
- `hohe-jagd-fischerei-2027`: duplicate of `die-hohe-jagd-fischerei-2027`.
- `milan-games-week-cartoomics-2026`: out of scope on review (mostly video-game publishers, esports
  and comics/merch retail; no reliable exhibitor figure).
- Merged duplicates found by two agents (kept the better-sourced record): Salon Marjolaine, Formland
  Spring, Athens International Jewellery Show, FeHoVa.

**Notable decisions:**
- Golosaria Milano: its 615 figure includes ~200 wineries (alcohol is out of scope), so it was left off
  the team sheet.
- Heim+Handwerk: the team sheet's 785 (2025) couldn't be sourced; the calendar uses 769 (2024),
  which has a source.
- IFCO Istanbul: 450 (Feb 2026, organiser post-show release) replaces the ~400 pre-show figure.
- Babykid Spain + FIMI: dates confirmed by the organisers via FashionUnited.

**Rejected as out of scope or outside the window** (examples): Sirha Lyon (foodservice), Interfilière and
Modtissimo (materials), Stockholm Furniture & Light Fair (contract/architect-led), HIT Show Vicenza
(discontinued), ORNARIS January (discontinued), Bubble London (closed), Premium/Panorama Berlin
(discontinued), spoga+gafa 2027 (moved to Sept), Kind + Jugend (Sept), Interzoo (next in 2028), Alimentaria
and SIAL (biennial, not in window), Professional Beauty London (October), Paris Games Week (October).

**Not researched yet** (follow-ups for the next `/refresh-all`): Tranoï, Madridjoya, Neonyt, Paris Déco
Off, January Furniture Show, Les Automnales (on the team sheet), Salon de l'Agriculture, spoga dog,
Milan Coffee Festival, Balkan and most CEE regional fairs, Istanbul lingerie/kids fairs, and app checks
for most shows.

**Leads for March–July 2027:** 29 unverified records from the partial first pass are saved in
`data/leads-mar-jul-2027.json` (not loaded by the page). `/research-month` uses them as a starting list.

**Team Google Sheet:** shows with more than 500 exhibitors were synced to columns A–F only.
- October tab: appended Equita Lyon and Lucca Comics & Games (rows 13–14).
- November and December tabs: every qualifying show was already listed, so nothing changed.
- January tab: new tab (duplicated from December, copied rows cleared); 15 shows.
- February tab: new tab (duplicated from December, copied rows cleared); 10 shows.
- Rows with listing-only dates have "(dates TBC)" added to the Dates column.
