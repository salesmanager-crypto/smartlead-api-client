---
name: exhibitors-extract
description: Turn a trade show exhibitor list into a ready-to-send outbound list for Albert Scott, in nine phases. Pull every exhibitor with booth, website and social links; drop distributors; find each real seller's own brands; read the exact Amazon store name from the "Visit the X Store" line; pull SmartScout data for that exact store; get 5 sales, marketing and e-commerce decision makers per company from its LinkedIn company page via Surfe (no CEOs or founders); get their emails from Surfe; write a custom cold email for each in Yoni's style; and deliver everything on one master sheet. Use this whenever the user names a trade show, expo, exhibitor list or MapYourShow gallery and wants leads, prospects, decision makers, contacts, emails or a campaign list from it. It applies even if they only ask for one phase, such as "who's exhibiting at X", "find the Amazon brands at X" or "get me contacts for the X exhibitors".
---

# Exhibitors extract

Turns a trade show's exhibitor list into one master sheet of Amazon-selling brands, with 5 sales, marketing and e-commerce decision makers per brand, their Surfe emails, and a first-touch email for each written in Yoni's voice. Albert Scott is a full-service Amazon agency, so the goal is a list of companies that sell their own brands on Amazon and the people there who own that channel.

The reference implementation is in `pipeline/` of the smartlead-api-client repo, built for AAPEX + SEMA 2026. If you are not in that repo, the packaged skill carries a copy under `scripts/pipeline/`. Read `references/runbook.md` for the exact commands, file names and the order to run them in. The rules that decide what counts (exhibitor types, brand ownership, store-name matching, title filters, email rules) are in `references/rules.md`. Read both before starting a new show.

## Before you start

Ask only what you cannot find:
- The show name, dates, city and the exhibitor gallery URL (MapYourShow galleries look like `https://<show>.mapyourshow.com/8_0/explore/exhibitor-gallery.cfm?featured=false`).
- Whether the emails go out before or after the show, and whether Yoni will be at the show. The email context line depends on both. Never say Yoni will be there unless he has said so.
- Where the master sheet should live (an existing Google Sheet, or a new one).

Check the tools: Playwright with Chromium at `/opt/pw-browsers/chromium` (never run `playwright install`), the SmartScout MCP, the Surfe MCP, and Google Sheets / Drive if the sheet goes to Google. Check Surfe credits with `surfe_get_credits` before phases 6 and 7. Email credits limit how many people you can enrich, so spend them on the highest-revenue Amazon brands first.

## How the work is split

Python does the scraping, matching, filtering and file building, so the rules are the same for every row. MCP tools (SmartScout, Surfe) can only be called by you or your subagents, so those phases use work units. A script `export`s chunk files (`pipeline/work/<prefix>_in_NN.jsonl`), one subagent per chunk follows a prompt file (`pipeline/<prefix>_agent_prompt.txt`) and appends results to `<prefix>_out_NN` or `<prefix>_raw_NN`, then the script `collect`s or `build`s. Everything is append-only and resumable: rerunning skips finished keys, so a new session picks up where the last one stopped.

Keep every data file out of git (the repo is public): add new outputs to `.gitignore` and commit only code and prompts.

## The nine phases

### Phase 1: exhibitors, booths, website and social links
Scrape the gallery's ajax endpoint and every exhibitor detail page with Playwright, caching pages to disk. Pull the name, every booth, the website, the company LinkedIn, Facebook, X and Instagram (only from the exhibitor's own social block), the About text, the top categories, the show's Brands section and the address. Dedupe across shows on a normalized name or the domain, and give each exhibitor a stable ID (E0001...). MapYourShow puts contact names behind the My Show Planner login, so they are not public. Say so in the output; don't hunt for them elsewhere.
Output: `phase1_exhibitors.xlsx` and `pipeline/work/social_links.csv`.

### Phase 2: sellers versus distributors
For each exhibitor, get the domain, the parent company (only when a source states it plainly) and one of five types: Brand / Manufacturer, Distributor / Wholesaler, Service / Software / Media / Association, Tool & Equipment / Shop Supplier, or Unclear. Only Brand / Manufacturer goes on. Distributors, service companies, shop suppliers and Unclear exhibitors are dropped. The tests are in `references/rules.md`.
Output: `phase2_domains.xlsx`.

### Phase 3: the brands each seller owns
List every brand the exhibitor sells under its own name: the show page Brands section, its own brand pages, and the About text. Third-party brands it carries don't count. If no brand is named, the exhibitor's own name is the brand only if products are sold under it.
Output: `phase3_brands_amazon.xlsx`.

### Phase 4: the exact Amazon store name
For each owned brand, search amazon.com, open up to 3 product pages whose title names the brand, and read the byline under the product title. "Visit the X Store" gives the store name X and the store URL. "Brand: X" gives a brand with no store. Record the store name exactly as Amazon shows it, never the search term or the product title. Compare it with the brand and the exhibitor to mark it verified, possible, different brand or not found (thresholds in `references/rules.md`). Run 3 workers at most, with 4 to 8 seconds between brands. If Amazon shows its soft check (one "Continue shopping" button, no puzzle), click the button once and keep the cookies. If it shows an image captcha, back off for several minutes. Never try to solve a captcha. Use the shared user agent in `common.py` that matches the installed Chromium. An outdated version string sends every request to the soft check.
Output: `amazon_stores.csv`.

### Phase 5: SmartScout for that exact store
Look up the verified store name (then the Amazon brand field) in SmartScout. Reuse cached profiles whose name matches exactly, and pull the rest with the saved "Full profile of the brand <X>" query, 40 names per call. Pull sellers and top subcategories for the brands you will email. A store that SmartScout doesn't have is still on Amazon; mark it "not in SmartScout".
Output: `smartscout_store.csv`.

### Phase 6: 5 decision makers per company, from the company's LinkedIn
Only for exhibitors with a verified or possible Amazon store. First enrich the company with Surfe (`surfe_enrich_companies`), which returns its LinkedIn company page. Then search people at that company (`surfe_search_people` by domain) with sales, marketing and e-commerce titles only. Pass A covers US leaders (C-Level, VP, Director, Head), pass B adds US managers, and pass C searches any country when nothing was found. Code then removes CEOs, founders, owners, presidents, other chiefs and junior roles, ranks the rest (e-commerce first, then marketing, then sales; more senior first; US first), and keeps the top 5. Run one Surfe search agent at a time. Parallel agents share one short rate window and all fail with PUBLIC_API_PEOPLE_SEARCH_QUOTA_EXCEEDED. On that error, wait 60 seconds and retry. Surfe's API also caps how many people a search may return per window (about 2 people a minute here), so use the people already found by public LinkedIn search as a second source and fill gaps with one slow top-up agent.
Output: `surfe_people.csv` and `surfe_companies.csv`.

### Phase 7: emails from Surfe
Run `surfe_enrich_people`, email only and no mobile, for the selected people. Order them by verified Amazon store first, then by SmartScout revenue, and stop at the credit budget. Never guess or construct an email. A person Surfe can't find stays blank. Credits are spent when Surfe runs the lookup, so let each email agent finish and save its results.
Output: `surfe_emails.csv`.

### Phase 8: a custom cold email per person
Agents write one first-touch email per person following the `my-writing-style` skill in cold mode: 40 to 70 words, "Hi {first_name},", a show and booth line, one line of Amazon fact from the data (rounded, "from what we can see"), one concrete line on what Albert Scott does, an optional proof point, one question as the ask, then "Yoni". People at the same company get different emails. `cold_emails.py check` enforces the hard rules (no dashes, no exclamation marks, one question, word count, banned phrases, no exact figures), and the agents rewrite anything that fails.
Output: `cold_emails.csv`.

### Phase 9: one master sheet
`master_build.py` writes one table with one row per person. Each row carries the exhibitor, shows and booths, website, social links, company LinkedIn, parent, brands, the Amazon store, the SmartScout numbers, the person, their email and their custom email. An in-scope exhibitor with no people gets one row whose Row Status says why. Write it to a single tab of the target Google Sheet (no other tabs), then read it back to verify the row count and a sample of cells.
Output: `master_sheet.csv` and the Google Sheet.

## Rules that hold everywhere

- Never invent data: no names, titles, emails, store names or numbers that a source didn't return. A blank with a reason beats a guess.
- No em dashes or en dashes anywhere, in data or copy.
- Don't query search engines or LinkedIn from scripts or WebFetch. LinkedIn data comes from Surfe.
- Be polite to every site: cache pages, keep delays, back off on errors.
- After each phase, report counts (in, out, dropped and why) and show a few sample rows before moving on.
- Read the show-specific settings (show URLs, dates, prompt wording) at the top of each script and prompt, and update them for a new show.
