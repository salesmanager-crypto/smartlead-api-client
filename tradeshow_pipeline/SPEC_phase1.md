# Phase 1 spec (exhibitor lists) - shared by all workers

Folder: /home/user/smartlead-api-client/tradeshow_pipeline  (cd there; `from common import fetch, norm_name, domain_of`; `from browser import new_browser, LAUNCH`)
- `common.fetch(url)` = polite cached GET via requests (1-2 s delay per host, backoff, 10 min pause on 429). Cache at cache/pages/. Use it for every plain HTTP request.
- Playwright: ALWAYS launch with `browser.LAUNCH` (preinstalled chromium + proxy CA pin). Never run `playwright install`. Never disable TLS verification.
  Cache rendered pages / captured JSON under cache/pages/<SID>/ yourself.
- Politeness: one request at a time per site, 1 to 2 seconds between requests. Backoff on errors. On captcha / 429 pause 10 minutes then retry once; if still blocked use fallbacks.
- Long scrapes: run the python script with Bash run_in_background (or nohup) and poll its log; each Bash call has a 10 minute cap.

## Finding the list
Start at the show's Event Link. Look for Exhibitors / Exhibitor List / Exhibitor Directory / Show Floor / Floor Plan / Who's Exhibiting / Brands / Vendors.
Identify the platform (mapyourshow, a2z/Personify (*.a2zinc.net, *.expocad.com), Swapcard, Eventscribe, Map Dynamics, ExpoFP, Cvent, custom, PDF).
Prefer the JSON/ajax endpoint the gallery calls (Playwright network capture), paginate it; else render and scroll/paginate. Open detail pages when they carry website / description / LinkedIn / categories / location.
PDF: download, extract with pdfplumber, Source = "<pdf url> p.<page>".
Fallbacks in order when no current list: 2025 list on same site or Wayback Machine (web.archive.org); floor plan; sponsor + featured brand pages; WebSearch "<show name> 2026 exhibitor list".
List Status = "current list" / "prior-year list" / "partial (sponsors and featured only)" / "none".
If nothing at all: write ONE row with Exhibitor Name blank and Notes = "No public exhibitor list; needs registration or PDF from Yoni".

## Output per show (exact file names, UTF-8)
1. raw/<SID>_exhibitors.csv with EXACT columns:
   Show ID, Show Name, Exhibitor Name, Booth, Website, LinkedIn, About, About Summary, Categories, City, State, Country, Detail URL, Source, List Status, Notes
   - Only what the page shows; never fill from memory. Blank if not shown.
   - LinkedIn = company page URL only (linkedin.com/company/...); ignore other socials.
   - About = full description text as shown. About Summary = YOUR 1-2 sentence plain summary of the About (blank if About blank). No em dashes.
   - Categories = up to 5 categories/product tags shown, joined with "; ".
   - Source = the list URL (or PDF url + page, or wayback url) the row came from.
   - Dedupe within the show on norm_name(Exhibitor Name) or domain_of(Website); merge fields (keep the richest).
   - Artists Alley / individual artists rows: include them, put "Artists Alley" in Categories so phase 2 can type them.
   - Notes: explain anything missing that a reader would expect (e.g. "detail page had no website").
2. raw/<SID>_meta.json: {"show_id","show_name","list_status","exhibitor_list_url","platform","exhibitors","notes"}
   notes = how you got it, what was not available, anything Yoni should know (e.g. needs login, list is 2025).
Write the CSV incrementally (checkpoint) so a crash does not lose work; on restart skip rows already written.

Report back (short): per show list status, list URL, platform, exhibitor count, count with website/LinkedIn/About, problems.
