---
name: amazon-check
description: Check whether each brand on a lead list (trade show exports, prospect sheets, any xlsx/csv with a Company or email column) is on Amazon US, who sells it, its exact Amazon brand name and brand store URL, then write the results back into the spreadsheet. Use this whenever Yoni sends a lead list and mentions Amazon, brand presence, "Sells / Does Not Sell", brand store, reseller, Vendor vs Seller Central, or asks to verify or normalize company names against Amazon, even if he does not say "scrape". Includes the sizing rule (how many scrapers for N brands in M minutes), the throttling limits, the review rules that stop wrong names reaching the sheet, and the escalation policy.
---

# Amazon Check for lead lists

Yoni (Albert Scott, Amazon agency) brings lead lists from trade shows and wants to know, per brand: is it on Amazon, who is selling it, and what Amazon calls it. That decides which outreach campaign each contact goes into. Wrong answers cost more than slow answers: a "Sells" that isn't, or a Company renamed to the wrong brand, ends up in a cold email.

## Before anything runs: the plan message

Always send this before starting, and wait for a go if the target time is not reachable:

1. Unique brands to check (not rows: a 557-row list had 228 brands to check).
2. Workers = brands ÷ (0.55 × target minutes), rounded up. Run `scripts/plan_run.py <brands> <minutes>` to get it.
3. If workers ≤ 8: run it, quote the finish time.
4. If workers > 8: the target is not reachable at full quality. Say so, give the realistic time (brands ÷ 4.5 minutes), and offer: accept the longer run, check only Sells/Listed rows, reuse earlier scrape data, or use SmartScout when its monthly allowance is available.

Why the cap: Amazon soft-throttles a single IP above roughly 8 to 10 concurrent browser sessions. It doesn't error; it serves blank product pages. At 32 workers a run looked 3x faster and 75% of its results were empty. Speed above the cap is fake.

## Data sources, in order of preference

1. **SmartScout MCP** (`get_account_capabilities` first). If the monthly AI allowance is exhausted it refuses every query; say so immediately and move on. It's the only source that gives revenue and seller type cleanly.
2. **Direct Amazon scrape** with `scripts/verify_brands.py` (headless Chromium through the session proxy). This is what worked. Search a brand, open matching product pages in a fresh browser context each, read the byline ("Visit the X Store" / "Brand: X"), the store href and "Sold by".
3. **WebSearch limited to amazon.com** finds store pages but has a hard per-session cap (200 calls), so it burns out after ~150 brands. Use only for a handful of stubborn brands.
4. **Bing via curl** returns junk for most queries. Don't.

Amazon pages 503 to plain curl and WebFetch. The browser needs the proxy CA in its NSS store; see `references/setup.md`.

## The run

```
python3 scripts/build_queue.py <leads.xlsx> --sheet "All Contacts" --out queue.json   # unique brands (Company, else business email domain)
python3 scripts/plan_run.py <n_brands> <target_minutes>                              # workers + honest ETA
python3 scripts/verify_brands.py queue.json out.json --workers <w>                  # writes incrementally, resumable
python3 scripts/apply_results.py <leads.xlsx> out.json --out "<name> - Amazon Checked.xlsx"
```

Split the queue across 2 to 4 processes if you want more than 2 workers; each process is one Chromium. Keep total workers at the number from the plan.

**Two minutes in, check the blank-page rate** (`verify_brands.py` records `title` per product page; empty title with no "dog" page means throttled). Above 20%: halve the workers, tell Yoni the new finish time, and re-queue the blank results. Never let a blank page become "Does Not Sell" or NOT FOUND.

**When you replace or stop a run, stop its watcher in the same step.** Yoni will see stale wait loops as "4 running tasks" and ask what they are. Before reporting done, confirm `ps` shows no scrapers, no watchers, no Chromium.

## Classifying a brand

- **Sells**: the brand's own listings, sold by the brand itself or by Amazon (Vendor). Needs a URL.
- **Reseller / Unclear** (Yoni's spelling: "Listed (reseller/unclear)"): listings exist but a third party sells them, or the seller couldn't be read. Name the reseller in the note ("No brand store; sold by third-party reseller Artisan Owl"). This group is an outreach angle in itself: their products are on Amazon but they don't control them.
- **Does Not Sell**: nothing matching. Say why in the note when it's structural: rep agency, distributor, retailer, overseas OEM factory.

Match must be the same company: brand name resembles the Company or its email domain AND the product type fits the business. Amazon returns fuzzy matches for everything; "Haggard Pirate" came back as "THE PIRATE KING", "Lizton Sign Shop" as "SmartSign", "Tribal" as "Tribal Chimp". A 5-character prefix match is not enough; read the product title.

## Amazon brand name and Company rename

When asked to set Company to Amazon's spelling: copy the byline text exactly (capitalisation, punctuation, ®). If a product page has no byline but Amazon's search results label the brand consistently (Cressi, vineyard vines, Maui Jim), use that label and say so in the notes. Never write a guessed name; write NOT FOUND and leave Company alone. Do the offline fill first: earlier scrape passes often already hold the byline for brands a later pass missed.

Review by hand every name whose normalised form doesn't contain a piece of the company name, and every name that only shares a generic word with it (marine, systems, solutions, power, water, quick, metro, love, natural). On a marine trade show list those generic words produced 40 wrong matches (New Douglas Marine -> Marine Tex, Escardo Marine -> a snail brand, Frigibar -> Frigidaire); the exhibitor's distinctive token has to appear in the Amazon name. Dead store links are common (several redirected to a Duracell page); treat those as "no result", not as the brand.

## Report to Yoni

Row count matches; counts per status and per campaign; every Company that changed as `Original -> Amazon name`; every NOT FOUND; any company whose contacts got different names (should be none); the brands you accepted with a name that differs from the company, with the reason, so he can eyeball them.

## Escalation policy (Yoni's standing instruction)

Fix first, then raise it right away: throttling, quota exhaustion, proxy port change, dead links, anything that changes finish time or quality. Same message, not the next status question. If the fix costs quality or needs him (raise a limit, confirm a spelling), raise it the moment you see it with a recommendation and keep the rest running. Silence means on track.

## Files

- `scripts/verify_brands.py`: the scraper. Fresh context per page, UA rotation, brand-table fallback, short backoffs, resumable output.
- `scripts/build_queue.py`: unique brands from a sheet.
- `scripts/plan_run.py`: sizing and ETA.
- `scripts/apply_results.py`: write Status / Sold By / Amazon Brand Name / Name Match? / Amazon URL / Notes columns per row, preserving order and styles.
- `references/setup.md`: Chromium + proxy CA setup, throughput numbers, what failed and why.
- Never commit a lead list. They hold names, emails and phone numbers.
