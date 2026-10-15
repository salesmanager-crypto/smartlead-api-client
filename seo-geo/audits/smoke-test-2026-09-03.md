# Smoke test, 2026-09-03

A miniature of Stage 1 to prove the tooling. Not the real audit. Two pages graded, three baseline searches run. All evidence was captured from the rendered live page in headless Chromium (via Playwright) unless a source is named. Screenshots are in `screenshots/test/`.

## Part A. Discovery

| Path | Result |
|---|---|
| /sitemap.xml | 200. AIOSEO Pro 5.0.1 index, 7 child sitemaps, 105 URLs total. |
| /sitemap_index.xml | 302 to /sitemap.xml |
| /wp-sitemap.xml | 302 to /sitemap.xml |

Child sitemap counts: post 13, page 49, project 23, post-archive 1, category 7, post_tag 2, project_category 10.

Split: 85 content pages (13 posts, 49 pages, 23 projects) and 20 junk URLs (7 category, 2 tag, 10 project_category archives, 1 post-type archive). 32 of the 85 content pages are test, legacy, or duplicate pages that need a keep, redirect, or delete decision before they are worth grading. Full inventory with per-URL evidence: `../config/site-map.md`.

WordPress read-only counts (REST API headers): 50 published pages, 13 posts, 23 projects, 1,075 media items. The one published page missing from the sitemap is `/case-studies/mouthwatchers/`, which carries `meta robots noindex, nofollow`.

## Part B. Page grades

Scoring: each of the 12 points is Pass, Partial, or Fail with the evidence that decides it.

### Page 1: Homepage, https://www.albertscott.com/

HTTP 200. Canonical self. Rendered word count 5,796 (includes nav, footer, and three cloned testimonial carousels, so the real body copy is well under that). Screenshots: `homepage-mobile-390x844.png`, `homepage-desktop-1440x900.png`, full-page versions of both.

| # | Point | Result | Evidence |
|---|---|---|---|
| 1 | Title | Fail | `<title>Home - Albert Scott</title>`, 19 characters. The word "Home" is the only descriptor. No service or category term. By contrast the legacy `/home/` page carries the title "Albert Scott - A Full Service Amazon Agency". |
| 2 | Meta description | Pass | `Albert Scott is a full-service Amazon growth agency helping brands scale with expert marketing, logistics, and retail strategies.` 129 characters, one clear claim. og:description matches. |
| 3 | H1 and hierarchy | Partial | Exactly one H1: "Win on Amazon. Everywhere." It is a slogan and carries no describing term. Hierarchy problems: the testimonial attribution "Danielle King, General Manager, Michel et Augustin" is an H3; three testimonial names are each rendered as H4 three times (carousel clones, 9 H4s); footer column labels "Services", "Our Work", "Legal" and the tagline are H4s. |
| 4 | Content | Pass | Substantive, readable body copy present in the HTML (not injected). Opening paragraph states what the company is: "Albert Scott is a complete marketplace account management partner for brands selling on Amazon." Four partnership models, four divisions, case studies, testimonials with named people and titles, metrics section. |
| 5 | Internal links | Partial | 49 internal links, 19 unique targets, 4 external. Four footer links point at URLs that 301: `/listing-division-2/`, `/marketing-division/`, `/logistics-division-2/`, `/case-studies-2/`. No link from the homepage to `/dsp/`, to any blog post, or to `/project/`. One generic anchor ("Learn more", in the cookie bar). |
| 6 | Image alt text | Fail | 236 `<img>` elements (47 unique files). 236 have `alt=""`; 0 have descriptive alt. The logo `AlbertScott-Logo-Amazon.png` has empty alt. Every client logo tile has empty alt. |
| 7 | Schema | Partial | Two JSON-LD blocks. Block 1 (AIOSEO): BreadcrumbList, Organization (`@id /#organization`, description "E-commerce Management", numberOfEmployees 5 to 10), WebPage, WebSite. Block 2 (custom): Organization plus ProfessionalService (`@id /#org`, numberOfEmployees 30, telephone, email, postal address, areaServed, knowsAbout, OfferCatalog). The two Organization nodes have different ids, different employee counts, and different descriptions. No `sameAs` in either. No FAQPage, no aggregateRating. |
| 8 | Canonical | Pass on this page, Fail sitewide | `<link rel="canonical" href="https://www.albertscott.com/">`. Correct. But `/home/` (title "Albert Scott - A Full Service Amazon Agency", 1,053 words) is live, indexable, and self-canonical, as is `/amazon-management-agency/` (title "FULL SERVICE AMAZON GROWTH AGENCY"). Both are old homepages competing with the current one. |
| 9 | Conversion path | Pass | "GET MY FREE AUDIT" button visible above the fold at both 390 and 1440 wide (see screenshots); it targets the on-page anchor `#freeaudit` and one form is present. "Contact" is a highlighted nav button. Note: the cookie banner covers roughly the bottom fifth of the mobile viewport until accepted. |
| 10 | GEO readability | Partial | Strong: a one-sentence definition of the company in the first paragraph, named divisions, named clients and named testimonial sources, address and phone in schema. Weak: the entity is described three different ways (tagline "E-commerce Management", schema "Amazon. Expertise. Delivered.", meta "full-service Amazon growth agency"), and the two Organization schemas disagree, which makes it harder for an answer engine to resolve one entity. No FAQ section. |
| 11 | Cannibalization | Fail | Live, indexable pages targeting the same agency positioning: `/home/`, `/amazon-management-agency/`, `/for-amazon-brands/`, `/for-amazon-brandsv2/`, `/services/`, `/services-2/`, `/our-service/`. Also a blog category named `amazon-agency`. |
| 12 | Other | Note | Meta generator tags expose "WordPress 7.1", "All in One SEO Pro (AIOSEO) 5.0.1", "Site Kit by Google 1.186.0". `/page/2/` exists (noindex, canonical to homepage). `/blog/` returns 404 although every post lives under `/blog/`. Copy uses em dashes in several sentences, which matters for the house style rule when copy is later rewritten. |

Homepage summary: 4 Pass, 4 Partial, 3 Fail, 1 note.

### Page 2: Marketing Division, https://www.albertscott.com/marketing-devision/

HTTP 200. Canonical self. Rendered word count 4,682. Screenshot: `marketing-devision-desktop-1440-full.png`.

| # | Point | Result | Evidence |
|---|---|---|---|
| 1 | Title | Fail | `<title>Marketing Devision - Albert Scott</title>`. "Devision" is misspelled, and the misspelling is also the URL slug and the og:title. 33 characters, no term a buyer would search (Amazon advertising, PPC, DSP, retail media). |
| 2 | Meta description | Fail | No `<meta name="description">` on the page. No og:description. |
| 3 | H1 and hierarchy | Partial | One H1: "Marketing Division". Problems: an H3 "Albert Scott Divisions" (an eyebrow label) appears before the H1; a full customer quote is set as an H2; footer labels are H4s. The H2 sequence otherwise reads well: "Retail Media Managed by Experts. Scaled by AI.", "Proven Results Across Categories", "Core Advertising Levers", "Full Retail Media Support". |
| 4 | Content | Pass | Deep, specific copy. Opening line: "Albert Scott builds Amazon advertising systems for brands that need more than campaign management." Covers Sponsored plus DSP with an incrementality stance, product-level scaling, retail media platforms (logos for Walmart, Kroger, Instacart, Meta, Google Ads, TikTok, Pinterest, Criteo, Whole Foods, Sam's Club are shown). |
| 5 | Internal links | Partial | 45 internal, 17 unique targets. Beyond nav and footer, the body links only to `/dsp/` and to `/case-studies-2/` (which 301s). No links to the two directly relevant posts `/blog/mastering-amazon-dsp/` and `/blog/tacos-vs-acos-what-amazon-managers-need-to-know/`. |
| 6 | Image alt text | Fail | 44 `<img>` elements, 42 with `alt=""`, 2 with alt. All retail media platform logos have empty alt. The logo has empty alt. |
| 7 | Schema | Partial | Same two sitewide blocks as the homepage. The AIOSEO BreadcrumbList names this page "Marketing Devision" (misspelling propagated). WebPage node has no description. No Service or FAQ schema specific to this page even though the custom Organization block lists "Amazon Advertising" and "Amazon DSP" as offers. |
| 8 | Canonical | Pass on this page, Fail sitewide | Self canonical. But `/marketing-division-2/` is live, indexable, titled "Marketing Division - Albert Scott", has a meta description, 405 words, and its own self canonical. `/marketing-division/` (the correctly spelled slug) 301s to the misspelled page. |
| 9 | Conversion path | Pass | "TALK WITH AN EXPERT" button targets `#become`; one form on page; "Contact" nav button. |
| 10 | GEO readability | Partial | Clear definitional opening line and concrete method language help extraction. Missing meta description and the internal-jargon name "Marketing Division" hurt: an answer engine asked about Amazon advertising agencies has no page title or description that says that. |
| 11 | Cannibalization | Fail | `/marketing-division-2/` duplicates the topic. `/dsp/` (1,428 words, no meta description) overlaps the DSP section. Blog category `amazon-advertising` is indexable. |
| 12 | Other | Note | The typo "Devision" in the slug is the single most visible fix on the site. Changing the slug will need a 301 from the misspelled URL and an update to the AIOSEO breadcrumb. The quote H2 contains an em dash in the source copy. |

Marketing page summary: 3 Pass, 4 Partial, 4 Fail, 1 note.

### Three biggest issues across the two pages

1. Duplicate and legacy pages are live and indexable and compete with the pages that matter: `/home/`, `/amazon-management-agency/`, `/marketing-division-2/`, `/services/`, `/services-2/`, `/our-service/`, plus test pages like `/sample-page/` and `/test-page/`.
2. Titles do not say what the company does: "Home - Albert Scott" and "Marketing Devision - Albert Scott" (misspelled), with no meta description on the service page.
3. Image alt text is effectively absent (278 of 280 images across the two pages have `alt=""`), and the two Organization schema blocks contradict each other.

## Part C. Search baseline

Method: WebSearch. Positions are the order the tool returned results, not a Google rank. No volumes recorded.

### "full service Amazon agency"

- albertscott.com: not present in the 10 results returned.
- Top five domains in order: myamazonguy.com, canopymanagement.com, harvestgroup.com, canopymanagement.com (second URL), salesduo.com. Next: primeteam.agency, sellerplex.com, ensobrands.com, sermondo.com, g2.com.
- Content type that wins: agency homepages and service pages titled with the exact phrase (7 of 10), plus "best full-service agencies" listicles (canopymanagement.com, sermondo.com).

### "Amazon agency"

- albertscott.com: not present in the 7 results returned.
- Top five domains: myamazonguy.com, harvestgroup.com, canopymanagement.com, novadata.io, goamify.com. Next: sermondo.com, cbinsights.com.
- Content type that wins: agency homepages (3) and "best agencies" listicles or directories (3).

### "best Amazon agencies"

- albertscott.com: not present in the 6 results returned.
- Top five domains: supplykick.com, canopymanagement.com, thriveagency.com, clutch.co, novadata.io. Next: salesduo.com.
- Content type that wins: listicles and comparison pages, 6 of 6. Three are published by agencies on their own domains, two are directories.

### Brand query (from the tool check): "Albert Scott Amazon agency"

- albertscott.com homepage at position 8 of 9. Positions 1 to 3: zoominfo.com (two pages), linkedin.com/company/albert-scott-llc. Press releases (prnewswire.com, finance.yahoo.com, martechcube.com) fill positions 4 to 7.

## What this test says about the full spec

- WordPress site-scoped tools through the WordPress.com connector are blocked by plan. The read-only REST API covers inventory and titles. AIOSEO settings can only be read from what the live HTML exposes (generator tag, schema, robots meta, sitemap), not from the plugin's settings screens.
- The headless browser needs the request-routing pattern described in the README; without it every navigation fails.
- WebSearch returns 6 to 10 results per query, so "top five domains" is reliable but anything beyond position 10 is not observable. The Stage 1 baseline should say "not in returned results" rather than "not ranking".
- The 32 triage pages should be dispositioned before Stage 1 grades all content pages, otherwise a third of the grading effort goes to pages that should not exist.
