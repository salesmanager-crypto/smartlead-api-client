# Trade show exhibitor to Amazon pipeline: run log

Built 2026-09-27 19:36 UTC. Scope: 20 shows, Sep 25 to Dec 31, 2026 (AAPEX and SEMA excluded).

## Totals

- Exhibitors pulled: 7,989 rows, 7,414 unique companies (445 exhibit at 2 or more shows)
- In scope for brand research (Brand / Manufacturer, Distributor / Wholesaler, Unclear): 5,654 rows, 5,127 companies
- Brands found: 5,393 unique (6,100 rows)
- Brands selling on Amazon (SmartScout match with category fit and active products): 1,088; Possible (known to SmartScout, 0 active products): 396
- SmartScout phase 4: 1,481 brands with data; full profile 350; sellers and subcategories 370; the rest carry the phase 3 snapshot (monthly revenue, category, product count)

## Per show

| Show | List status | Exhibitors | Researched | Brands | On Amazon | Exhibitors w/ Amazon brand | Combined $/mo | File |
|---|---|---|---|---|---|---|---|---|
| Greensboro Gift & Jewelry Show | current list | 32 | 29 | 26 | 0 | 0 | $0 | show_S01_greensboro_gift_jewelry_show.xlsx |
| White & Private Label World Expo | current list | 75 | 17 | 22 | 5 | 5 | $93,443 | show_S02_white_private_label_world_expo.xlsx |
| Las Vegas Souvenir & Resort Gift Show | current list | 556 | 494 | 542 | 119 | 101 | $18,095,507 | show_S03_las_vegas_souvenir_resort_gift_show.xlsx |
| New York Comic-Con | current list | 1197 | 335 | 409 | 96 | 77 | $82,127,178 | show_S04_new_york_comic_con.xlsx |
| Electrify Expo | current list | 32 | 19 | 19 | 9 | 9 | $4,969,088 | show_S05_electrify_expo.xlsx |
| Premiere Columbus | current list | 102 | 68 | 66 | 14 | 13 | $9,321,621 | show_S06_premiere_columbus.xlsx |
| NASGW Expo | current list | 227 | 212 | 286 | 81 | 68 | $44,333,708 | show_S07_nasgw_expo.xlsx |
| Jewelers International Showcase (JIS) Fall | current list | 562 | 473 | 429 | 6 | 6 | $3,076,065 | show_S08_jewelers_international_showcase_jis_fall.xlsx |
| Coffee Fest Dallas / Ft. Worth | current list | 128 | 93 | 94 | 31 | 28 | $24,167,825 | show_S09_coffee_fest_dallas_ft_worth.xlsx |
| High Point Market, Fall | current list | 1709 | 1392 | 1478 | 142 | 144 | $77,825,954 | show_S10_high_point_market_fall.xlsx |
| JA New York International Jewelry Show | current list | 167 | 154 | 142 | 3 | 3 | $607,709 | show_S11_ja_new_york_international_jewelry_show.xlsx |
| IGES, International Gift Exposition in the Smokies | current list | 554 | 518 | 567 | 136 | 114 | $23,485,193 | show_S12_iges_international_gift_exposition_in_th.xlsx |
| DEMA Show | current list | 518 | 196 | 205 | 57 | 56 | $82,737,221 | show_S13_dema_show.xlsx |
| Smoky Mountain Gift Show | current list | 298 | 271 | 256 | 43 | 43 | $5,222,351 | show_S14_smoky_mountain_gift_show.xlsx |
| Snowbound Expo | current list | 131 | 83 | 87 | 34 | 34 | $22,490,698 | show_S15_snowbound_expo.xlsx |
| Ocean City Resort Gift Expo | current list | 92 | 87 | 70 | 19 | 19 | $1,973,988 | show_S16_ocean_city_resort_gift_expo.xlsx |
| The Running Event (TRE) | current list | 350 | 307 | 322 | 166 | 160 | $410,233,419 | show_S17_the_running_event_tre.xlsx |
| Anime Frontier | none | 0 | 0 | 0 | 0 | 0 | $0 | show_S18_anime_frontier.xlsx |
| Grand Strand Gift & Resort Merchandise Show | current list | 250 | 227 | 235 | 44 | 39 | $3,996,331 | show_S19_grand_strand_gift_resort_merchandise_sho.xlsx |
| PRI Show, Performance Racing Industry | current list | 1009 | 679 | 724 | 178 | 168 | $42,814,720 | show_S20_pri_show_performance_racing_industry.xlsx |

## Shows with no list or a changed show

- S18 Anime Frontier: no public exhibitor list. Cloudflare blocked every automated attempt; the 2026 Map Your Show site (anif1226) exists but has no exhibitors assigned. Recheck in November or get the list from the organizer.
- S01 Greensboro Gift & Jewelry Show: the event link returns 404; the show is now the Greensboro Importers & Wholesalers Expo (Sep 25 to 27 and Dec 4 to 6, 2026). The listing page gives 32 names with no websites; none matched SmartScout.
- S05 Electrify Expo: only the Dallas stop (Nov 7 to 8) is live, inside Demo Days Festival; the Atlanta and San Diego pages are gone.
- S14 Smoky Mountain Gift Show publishes no websites; S11 JA New York publishes 16 of 167; S20 PRI publishes 16 descriptions of 1,009.

## Pending work (needs a session with web search or a machine Amazon does not block)

- Domain search: 1,274 companies have no website; input chunks phase2_work/search_chunk_*.csv, outputs search_out_*.csv (resume by key). Then rerun build_phase2.py and downstream builds.
- amazon.com check: 4,892 brand rows (4,307 brands) are marked 'Amazon check pending'. Queue: phase3_work/amz_queue_full.csv; script amz_check.py (resumable; amazon.com served a block page to this environment). Then rerun build_phase3.py.
- SmartScout phase 4 gaps: 1131 brands lack the full profile and 1111 lack seller/subcategory data because SmartScout's query engine was down or flickering from 16:21 UTC on 2026-09-27. Workers resume from phase4_work/*.jsonl (SPEC_phase4.md); then rerun build_phase4.py and build_deliverables.py.
- Phase 5 decision makers: not run (session web search cap of 200 reached in phase 2). Each show workbook's People sheet lists the target exhibitors with a note.

## Brands not found in SmartScout

3,622 brand rows (3,193 brands) had no SmartScout brand of the same name or a 2-variant spelling; they are 'On Amazon = No' pending the amazon.com check. Full list: phase3_brands_amazon_ALL.xlsx, filter SmartScout Match = not found. 755 further name matches were rejected as wrong category matches (see SmartScout Match Note).

## Method notes

- Exhibitor lists were pulled from the show sites' own directories (Map Your Show, a2z, Small World Labs, RX, Leap, custom); every field is as shown, nothing filled from memory. Em dashes in source text were replaced.
- About Summary is a written summary on 11 shows and the first sentence of the description on S02, S04, S07, S10, S13, S15, S17 and S20 (accepted by Yoni).
- Exhibitor Type and brand lists were judged by workers from show text, the company homepage and About page, and brand pages; parents only where a source states it plainly (copyright lines alone were not counted).
- SmartScout: Business plan, US only, no revenue history or ad data. Match = same brand name (or 2 spelling variants) and a category that fits the exhibitor's products. Dominant Seller Type is by seller-name match to the brand, exhibitor or parent.
- Combined Monthly Amazon Revenue sums each exhibitor's brands; a brand listed by two exhibitors is counted under each.
- Scripts and specs are in the repo (tradeshow_pipeline/); data files are gitignored because the repository is public. run_state.json holds phase status and SmartScout handles.