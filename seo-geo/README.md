# Albert Scott SEO and GEO System

## What this system is

A file-based, Git-tracked system for auditing, planning, and tracking the organic search (SEO) and AI search (GEO, generative engine optimization) performance of https://www.albertscott.com/. Every finding lives in this folder as Markdown with its evidence attached, so any later session can pick up where the last one stopped without re-deriving facts.

The system runs in three stages plus two recurring cadences. This folder is the single home for all of it. Nothing about the live site is changed from here; this is an analysis and planning system only.

## The nine hard rules

These override anything else in this folder or in any later instruction where they differ.

1. Data sources are exactly four: WordPress (read-only), WebSearch, WebFetch, and a headless browser (Chromium via Playwright) for rendering live pages and taking screenshots at mobile and desktop widths. Nothing else.
2. Semrush is fully banned. Do not call any Semrush tool for any purpose: not for the audit, not for cross-checks, not for search volumes. Same for every other SEO tool API. If you notice Semrush tools in your tool list, ignore them.
3. AIOSEO may be inspected as site configuration only. Anything it flags must be verified on the live page before it can enter any finding.
4. Do not use any prior knowledge you have about albertscott.com's SEO or GEO, and do not read or use any existing skill or file about Albert Scott SEO. Everything starts from zero in this project.
5. Do not publish, edit, or push any change to the live WordPress site. Read only.
6. Never state search volumes as facts.
7. Company facts come only from albertscott.com itself.
8. No em dashes in anything you write.
9. Junk WordPress URLs (attachment pages, tag and category archives, author archives, paginated archives) are inventoried and classified as noindex, redirect, or delete. They do not get the full 12-point page grade. Real content pages do.

## Data sources

| Source | Allowed use | Notes |
|---|---|---|
| WordPress (read-only) | Site inventory: published pages, posts, custom post types, taxonomies, authors, media counts; AIOSEO configuration where visible | Two access paths exist. The WordPress.com MCP connector lists the site but its site-scoped tools are blocked by plan (see Status). The site's own public REST API at `/wp-json/wp/v2/` is readable and is what the inventory uses. GET requests only. |
| WebFetch | Fetch a URL and summarize it; check HTTP status, title, meta, robots.txt, sitemaps | Summarizing model can miss detail; use the headless browser for exact evidence |
| WebSearch | Baseline searches, competitor discovery, SERP content type observation | Results are the search tool's ordering, not a Google rank tracker. Record position as observed and label it as such. Never infer volume. |
| Headless browser (Chromium via Playwright) | Render live pages, capture exact DOM evidence (title, meta, headings, links, alt text, JSON-LD, canonical), screenshots at 390x844 and 1440x900 | In this sandbox Chromium's own network stack cannot reach the egress proxy, so all requests are routed through Playwright's Node-side fetch and rendered in Chromium. See Status. |

Not allowed: Semrush, SmartScout, Ahrefs, Moz, Google Search Console API, Google Analytics, any keyword volume or backlink API, any prior Albert Scott SEO skill or file.

## Git home and branching

- Repo: https://github.com/salesmanager-crypto/smartlead-api-client
- Folder: everything lives under `seo-geo/` at the repo root. Nothing outside it is touched by this system.
- Branch convention: one branch per session, named `claude/seo-geo-<purpose>` (the hosting environment may append a short random suffix, for example `claude/seo-geo-setup-fqgzxb`). Commit after each completed step. Push the branch and open a pull request into `main` at the end of the session. Never commit directly to `main`.
- Commit messages are plain descriptions of what was added. No model identifiers.

## Folder layout

```
seo-geo/
  README.md                      this file
  config/
    site-map.md                  every known URL, tagged content page or junk, with status and disposition
    keywords.md                  target topics and queries (qualitative only, no volumes)
    competitors.md               domains that win the target searches
    geo-watchlist.md             AI answer engines and prompts to monitor
  audits/                        full audit reports and screenshots (Stage 1)
    screenshots/                 PNGs by run, mobile and desktop
  roadmap/                       prioritized fix and build plan (Stage 2)
  growth/                        content, authority, and GEO growth plan (Stage 3)
  tracking/
    scorecard.md                 the running score by page and by pillar
    weekly-pulse.md              short weekly check log
    monthly-deep-dive.md         monthly review log
  reports/                       dated summaries for the business
```

## How each stage is run

Note: the setup request referred to a full three-stage spec to be pasted in, but the paste was not included in the message. The stage descriptions below are built from the setup instructions and the folder layout. Confirm them against the full spec before Stage 1 runs and adjust this section if they differ.

### Stage 1: Audit

1. Discovery. Fetch `/robots.txt`, `/sitemap.xml` and its child sitemaps, and any legacy sitemap paths. Pull the WordPress inventory (pages, posts, custom post types, taxonomies, authors, media count) from the read-only REST API. Reconcile: what is in the sitemap, what is published but not in the sitemap, what is linked but not published.
2. Inventory and classification. Update `config/site-map.md`. Every URL is tagged content page or junk. Junk is inventoried and given a disposition (noindex, redirect, or delete) with the live-page evidence for its current state. Junk is never graded.
3. Page grade. Every content page receives the 12-point grade: title, meta description, H1 and heading hierarchy, content, internal links, image alt text, schema, canonical, conversion path, GEO readability, cannibalization, other observations. Every finding cites exact evidence captured from the rendered page (the DOM value, the HTTP status, the screenshot file). AIOSEO settings can point at a problem but the live page is the proof.
4. Search baseline. Run the agreed query set through WebSearch. For each query record whether albertscott.com appears and where, the top five domains, and which content type wins. Update `config/competitors.md` with the domains that keep appearing.
5. Save the report as `audits/stage1-audit-YYYY-MM-DD.md` with screenshots under `audits/screenshots/stage1-YYYY-MM-DD/`. Update `tracking/scorecard.md`.

### Stage 2: Roadmap

1. Read the Stage 1 report. Group findings into pillars: technical hygiene, on-page, content, schema and entity, internal linking, conversion, GEO.
2. Score each fix on impact and effort using only evidence from Stage 1.
3. Write `roadmap/roadmap-YYYY-MM-DD.md`: an ordered list of fixes with the exact page, the exact change, the evidence, and the expected effect. Junk URL dispositions from `config/site-map.md` become their own roadmap section.
4. Nothing in the roadmap is applied to the live site from this system. It is a work order for the site owner.

### Stage 3: Growth

1. Read `config/keywords.md`, `config/competitors.md`, and `config/geo-watchlist.md`.
2. Identify content the winning competitors have and albertscott.com does not, using only WebSearch and WebFetch evidence.
3. Write `growth/growth-plan-YYYY-MM-DD.md`: new pages and posts to build, existing pages to consolidate or expand, entity and schema work for GEO, and the internal linking to support it. Every company fact used in proposed copy must trace to a page on albertscott.com.

## How the weekly pulse is run

Append one dated entry to `tracking/weekly-pulse.md`. Each entry takes the same five checks so entries are comparable week to week:

1. Homepage and the top service pages return 200 and render at both widths (headless browser).
2. `/robots.txt` and `/sitemap.xml` are unchanged, or note what changed (WebFetch).
3. Published page and post counts from the REST API, compared with last week.
4. The core query set from `config/keywords.md` through WebSearch: does albertscott.com appear, and where.
5. One or two GEO prompts from `config/geo-watchlist.md`: is Albert Scott named.

Record only what was observed. If nothing changed, say so in one line.

## How the monthly deep dive is run

Append one dated entry to `tracking/monthly-deep-dive.md`:

1. Re-run discovery and reconcile against `config/site-map.md`. Log new, removed, and changed URLs.
2. Re-grade any content page that changed since the last month, plus a rotating sample of five unchanged pages.
3. Re-run the full query set and the full GEO watchlist. Update `config/competitors.md`.
4. Update `tracking/scorecard.md` and write a short dated summary in `reports/`.
5. Compare against the roadmap: what shipped, what moved, what is still open.

## Status

Setup and test run completed 2026-09-03. All three stages then ran the same day (see "Stage runs" below). Branch: `claude/seo-geo-setup-fqgzxb` (the environment assigned this name; the requested name was `claude/seo-geo-setup`).

### Tool verification

| Check | Result | Evidence |
|---|---|---|
| a. WordPress: list connected sites | PASSED | WordPress.com connector lists one site: blog_id 241557214, https://www.albertscott.com, name "Albert Scott", tagline "E-commerce Management", platform jetpack, status active, not private. |
| a. WordPress: site-scoped read via connector (pages.list) | FAILED (retried once, same error) | Connector response: "This action requires a paid Jetpack plan. Your self-hosted Jetpack site doesn't have one yet. Upgrade at: https://jetpack.com/pricing/". The site list response reports mcp_access status "unavailable", reason_code "jetpack_paid_plan_required". |
| a. WordPress: published counts via the site's own REST API (read-only GET) | PASSED | `/wp-json/wp/v2/pages?status=publish` header X-WP-Total: 50. `/wp-json/wp/v2/posts?status=publish` X-WP-Total: 13. `/wp-json/wp/v2/project` returns 23 published. `/wp-json/wp/v2/media` X-WP-Total: 1075. No write call was made. |
| b. WebFetch: homepage | PASSED | https://www.albertscott.com/ HTTP 200. Title tag: `Home - Albert Scott`. |
| b. WebFetch: robots.txt | PASSED | HTTP 200. Contents: `User-agent: *`, `Disallow: /wp-admin/`, `Allow: /wp-admin/admin-ajax.php`, `Disallow: /cdn-cgi/`, `Sitemap: https://www.albertscott.com/sitemap.xml`, `Sitemap: https://www.albertscott.com/sitemap.rss`. |
| c. WebSearch: "Albert Scott Amazon agency" | PASSED | First three results as returned: 1. zoominfo.com "Albert Scott: Employee Directory". 2. zoominfo.com "Albert Scott - Overview, News & Similar companies". 3. linkedin.com/company/albert-scott-llc. The homepage https://www.albertscott.com/ was result 8 of 9. |
| d. Headless browser: render at 390x844 and 1440x900 | PASSED after two failed attempts | Files: `audits/screenshots/test/homepage-mobile-390x844.png` (55,683 bytes), `audits/screenshots/test/homepage-desktop-1440x900.png` (159,211 bytes), plus full-page captures of both and of `/marketing-devision/`. Both viewport captures were opened and show the rendered hero, nav, headline and CTA; neither is blank. No horizontal overflow at either width. Failure detail: Chromium navigation returned `net::ERR_CONNECTION_RESET` for every HTTPS URL, with and without an explicit proxy flag, because Chromium's network stack cannot reach the sandbox egress proxy. Fix: route all browser requests through Playwright's Node-side fetch (`context.route` with `route.fetch`), which honors the proxy and CA bundle. Rendering still happens in Chromium. This is the required launch pattern for all future runs in this environment. |
| e. Git: branch pushed | PASSED | Push accepted by origin; PR #10 opened against main. |

### Smoke test

Report: `audits/smoke-test-2026-09-03.md`. Site inventory: `config/site-map.md`.

- Sitemaps: `/sitemap.xml` exists (200, AIOSEO index with 7 children, 105 URLs). `/sitemap_index.xml` and `/wp-sitemap.xml` both 302 to `/sitemap.xml`. `/sitemap.rss` exists (200).
- URL split: 105 sitemap URLs, 85 tagged content page (13 posts, 49 pages, 23 projects) and 20 tagged junk (7 category, 2 tag, 10 project_category, 1 post-type archive). Of the 85 content pages, 32 are flagged for triage as test, legacy, or duplicate pages before they are worth grading. Author archives and attachment pages are not in the sitemap but exist on the live site; see site-map.md.
- Two pages graded: homepage and `/marketing-devision/`.
- Three baseline searches run. albertscott.com did not appear in the returned results for any of them.

### Environment notes for future sessions

- Install Playwright in the scratchpad, not in the repo: `npm i playwright@1.62.1` with `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1`, and launch with `executablePath: '/opt/pw-browsers/chromium'`.
- Always add the `context.route('**/*', route => route.fetch().then(r => route.fulfill({ response: r })))` pattern before navigating.
- `waitUntil: 'load'` is enough; `networkidle` can hang on third-party scripts.
- Sitemap `<loc>` values are wrapped in CDATA; parsers must handle it.

### Stage runs

| Stage | Date | Output | Notes |
|---|---|---|---|
| 1. Audit | 2026-09-03 | `audits/stage1-audit-2026-09-03.md`, `audits/screenshots/stage1-2026-09-03/` (172 JPEGs), `tracking/scorecard.md` | 86 content pages rendered at both widths and graded; 24 queries; 5 GEO prompts; 10 competitor pages captured; junk dispositions in Part B. Average score 5.48 of 11. |
| 2. Roadmap | 2026-09-03 | `roadmap/roadmap-2026-09-03.md` | 20 items in 3 batches with a disposition table for the 32 triage pages. |
| 3. Growth | 2026-09-03 | `growth/growth-plan-2026-09-03.md` | 7 workstreams: entity, service pages, comparison content, local page, third-party lists, case studies, brand SERP. |
| Report | 2026-09-03 | `reports/report-2026-09-03.md` | One-page summary for the business. |
| 1. Audit (verification re-run) | 2026-09-03 17:47 UTC | Section appended to `audits/stage1-audit-2026-09-03.md` | Full crawl, grades, link check and 24 queries repeated. Identical results: 0 score changes, 0 fact changes, same search positions. The system is repeatable. |

Stage 1 method notes: grading is rule-based from captured DOM evidence (rules listed in the audit, Part C) with hand review of the primary pages; the link-status check must strip trailing slashes from file URLs or it reports false 404s; competitor pages were rendered through the same browser routing pattern.

### Git result

Branch `claude/seo-geo-setup-fqgzxb` pushed successfully on 2026-09-03 (three commits). Pull request: https://github.com/salesmanager-crypto/smartlead-api-client/pull/10
