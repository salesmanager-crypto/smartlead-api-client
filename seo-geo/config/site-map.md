# Site map

Every URL known for https://www.albertscott.com/, tagged content page or junk (rule 9). First version from the 2026-09-03 smoke test. Sources: `/sitemap.xml` and its seven child sitemaps (fetched through the headless browser request client), the WordPress read-only REST API for titles and for objects not in the sitemap, and live probes for status, canonical and robots meta.

## Sitemap discovery

| Path | Result |
|---|---|
| /sitemap.xml | 200. AIOSEO Pro 5.0.1 sitemap index. 7 child sitemaps. Header `x-robots-tag: noindex, follow`. |
| /sitemap_index.xml | 302 to /sitemap.xml |
| /wp-sitemap.xml | 302 to /sitemap.xml (WordPress core sitemap disabled by AIOSEO) |
| /sitemap.rss | 200, RSS-style sitemap also listed in robots.txt |

| Child sitemap | URLs |
|---|---|
| /post-sitemap.xml | 13 |
| /page-sitemap.xml | 49 |
| /project-sitemap.xml | 23 |
| /post-archive-sitemap.xml | 1 |
| /category-sitemap.xml | 7 |
| /post_tag-sitemap.xml | 2 |
| /project_category-sitemap.xml | 10 |
| **Total** | **105** |

## Split

| Tag | Count |
|---|---|
| Content page | 85 (13 posts, 49 pages, 23 projects) |
| Junk | 20 (7 category, 2 tag, 10 project_category, 1 post-type archive) |
| Content pages flagged TRIAGE (test, legacy, duplicate; decide keep, redirect, or delete before grading) | 32 |

Reconciliation against WordPress: REST reports 50 published pages but the page sitemap lists 49. The missing one is `/case-studies/mouthwatchers/`, which is live (200) with `meta robots noindex, nofollow` and a proper title and description, so AIOSEO is excluding it deliberately. Verify whether that is intended. Posts (13) and projects (23) match exactly.

## Sitemap URLs

| Tag | Type | URL | Title from WordPress and notes |
|---|---|---|---|
| content page | page | https://www.albertscott.com/ | Home |
| content page | page | https://www.albertscott.com/about-us/ | About Us |
| content page | page | https://www.albertscott.com/additional-services/ | Additional Services | TRIAGE: legacy 2019 page |
| content page | page | https://www.albertscott.com/albert-scott-university/ | Albert Scott University |
| content page | page | https://www.albertscott.com/amazon-growth-audit-v2/ | Form Ads v2 | TRIAGE: title "Form Ads v2", 34 words |
| content page | page | https://www.albertscott.com/amazon-growth-audit/ | Form Ads | TRIAGE: title "Form Ads", landing page for ads; check intent |
| content page | page | https://www.albertscott.com/amazon-management-agency/ | FULL SERVICE AMAZON GROWTH AGENCY | TRIAGE: 2025 page titled "FULL SERVICE AMAZON GROWTH AGENCY", 425 words, competes with / |
| content page | page | https://www.albertscott.com/book-a-call/ | Book a Call |
| content page | page | https://www.albertscott.com/case-studies/ | Case Studies |
| content page | page | https://www.albertscott.com/case-studies/atlas-olive-oils/ | Atlas Olive Oils |
| content page | page | https://www.albertscott.com/case-studies/beyoutiful/ | From $0 to $1M+ in Year 1 |
| content page | page | https://www.albertscott.com/clients/ | Clients | TRIAGE: check against homepage client section |
| content page | page | https://www.albertscott.com/contact-us/ | Contact Us |
| content page | page | https://www.albertscott.com/cookies-policy/ | Cookies Policy |
| content page | page | https://www.albertscott.com/dsp/ | DSP |
| content page | page | https://www.albertscott.com/for-amazon-brands/ | For Amazon Brands | TRIAGE: ad landing page, 205 words; check intent |
| content page | page | https://www.albertscott.com/for-amazon-brandsv2/ | For Amazon Brandsv2 | TRIAGE: v2 duplicate of /for-amazon-brands/ |
| content page | page | https://www.albertscott.com/form-ads-test/ | Form Ads - TEST | TRIAGE: form test page, 38 words |
| content page | page | https://www.albertscott.com/hero/ | Hero | TRIAGE: design fragment, 141 words |
| content page | page | https://www.albertscott.com/home/ | Home-old | TRIAGE: old homepage, live and indexable, title "Albert Scott - A Full Service Amazon Agency" competes with / |
| content page | page | https://www.albertscott.com/lets-talk/ | Let's Talk | TRIAGE: possible duplicate of /contact-us/ and /book-a-call/ |
| content page | page | https://www.albertscott.com/listing-division/ | Listing Division |
| content page | page | https://www.albertscott.com/listings-portfolio-gallery/ | Listings Portfolio Gallery |
| content page | page | https://www.albertscott.com/logistics-division/ | Logistics Division |
| content page | page | https://www.albertscott.com/marketing-devision/ | Marketing Devision |
| content page | page | https://www.albertscott.com/marketing-division-2/ | Marketing Division | TRIAGE: live indexable duplicate of /marketing-devision/, 405 words, has meta description |
| content page | page | https://www.albertscott.com/newsroom/ | Newsroom |
| content page | page | https://www.albertscott.com/niftyone-custom-portal/ | NiftyOne Custom Portal | TRIAGE: legacy 2019 page |
| content page | page | https://www.albertscott.com/our-location/ | Our Location | TRIAGE: thin location page; check |
| content page | page | https://www.albertscott.com/our-management/ | Our Management | TRIAGE: legacy 2020 page |
| content page | page | https://www.albertscott.com/our-service/ | Our Service | TRIAGE: legacy 2019 page, raw [vc_row] shortcode in meta description |
| content page | page | https://www.albertscott.com/our-story/ | Our Story | TRIAGE: legacy 2019 page |
| content page | page | https://www.albertscott.com/our-team/ | Our Team | TRIAGE: legacy 2018 page |
| content page | page | https://www.albertscott.com/our-world-wide-team/ | Our World-Wide Team | TRIAGE: legacy 2019 page |
| content page | page | https://www.albertscott.com/overview/ | OVERVIEW | TRIAGE: legacy 2019 page |
| content page | page | https://www.albertscott.com/portfolio/ | Portfolio | TRIAGE: possible duplicate of /listings-portfolio-gallery/ |
| content page | page | https://www.albertscott.com/privacy-policy/ | Privacy Policy |
| content page | page | https://www.albertscott.com/recent-success/ | Recent Success | TRIAGE: legacy 2019 page |
| content page | page | https://www.albertscott.com/retail-division/ | Retail Division |
| content page | page | https://www.albertscott.com/retail-management/ | Retail Management | TRIAGE: possible duplicate of /retail-division/ |
| content page | page | https://www.albertscott.com/sample-page/ | Sample Page | TRIAGE: WordPress default sample page, live and indexable |
| content page | page | https://www.albertscott.com/services-2/ | Services | TRIAGE: legacy duplicate titled "Services" |
| content page | page | https://www.albertscott.com/services/ | Services | TRIAGE: legacy 2022 page, meta description contains raw [vc_row] shortcode |
| content page | page | https://www.albertscott.com/test-modules/ | test-modules | TRIAGE: test page |
| content page | page | https://www.albertscott.com/test-page/ | test page | TRIAGE: test page, live and indexable (200, no noindex) |
| content page | page | https://www.albertscott.com/thank-you/ | Thank you | TRIAGE: form thank-you page, indexable |
| content page | page | https://www.albertscott.com/thankyou/ | Thank You | TRIAGE: second thank-you page, indexable |
| content page | page | https://www.albertscott.com/university/ | University | TRIAGE: possible duplicate of /albert-scott-university/ |
| content page | page | https://www.albertscott.com/videos/ | Videos | TRIAGE: legacy 2019 page |
| content page | post | https://www.albertscott.com/blog/73-originals/ | '73 Originals |
| content page | post | https://www.albertscott.com/blog/atlas-olive-oil-spray/ | Atlas Olive Oil Spray |
| content page | post | https://www.albertscott.com/blog/how-to-conquer-your-competition-with-amazon-keyword-targeting/ | How to Conquer Your Competition with Amazon Keyword Targeting |
| content page | post | https://www.albertscott.com/blog/jose-gourmet/ | Jose Gourmet |
| content page | post | https://www.albertscott.com/blog/mastering-amazon-dsp/ | Mastering Amazon DSP for Mid-to-Large Brands |
| content page | post | https://www.albertscott.com/blog/mouthwatchers/ | Mouthwatchers |
| content page | post | https://www.albertscott.com/blog/objet-dart/ | Objet D'Art |
| content page | post | https://www.albertscott.com/blog/rae-dunn/ | Rae Dunn |
| content page | post | https://www.albertscott.com/blog/streamlining-logistics-for-scalable-amazon-success/ | From Cart to Consumer: Streamlining Logistics for Scalable Amazon Success |
| content page | post | https://www.albertscott.com/blog/subscribe-and-save-strategies/ | Subscribe-and-Save Strategies: A Case Study in 200%+ YoY Growth |
| content page | post | https://www.albertscott.com/blog/tabanero/ | Tabanero |
| content page | post | https://www.albertscott.com/blog/tacos-vs-acos-what-amazon-managers-need-to-know/ | TACoS vs. ACoS: What Amazon Managers Need to Know |
| content page | post | https://www.albertscott.com/blog/yumvs/ | YumVs |
| content page | project (portfolio item) | https://www.albertscott.com/project/3835/ | Bluestem Botanicals |
| content page | project (portfolio item) | https://www.albertscott.com/project/blue-chill/ | Blue Chill |
| content page | project (portfolio item) | https://www.albertscott.com/project/great-western-foods/ | Great Western Foods |
| content page | project (portfolio item) | https://www.albertscott.com/project/guylian/ | Guylian |
| content page | project (portfolio item) | https://www.albertscott.com/project/healthy-heist/ | Healthy Heist |
| content page | project (portfolio item) | https://www.albertscott.com/project/human-beanz/ | Human Beanz |
| content page | project (portfolio item) | https://www.albertscott.com/project/hyp/ | HYP |
| content page | project (portfolio item) | https://www.albertscott.com/project/its-just-smart/ | It's Just Smart |
| content page | project (portfolio item) | https://www.albertscott.com/project/kagi/ | Kagi |
| content page | project (portfolio item) | https://www.albertscott.com/project/magmod/ | Magmod |
| content page | project (portfolio item) | https://www.albertscott.com/project/mannol/ | Mannol |
| content page | project (portfolio item) | https://www.albertscott.com/project/national-public-seatinf/ | National Public Seatinf |
| content page | project (portfolio item) | https://www.albertscott.com/project/nora/ | Nora |
| content page | project (portfolio item) | https://www.albertscott.com/project/out/ | OUT! |
| content page | project (portfolio item) | https://www.albertscott.com/project/renew-rx/ | Renew RX |
| content page | project (portfolio item) | https://www.albertscott.com/project/rufus-teague/ | Rufus Teague |
| content page | project (portfolio item) | https://www.albertscott.com/project/simple-solution/ | Simple Solution |
| content page | project (portfolio item) | https://www.albertscott.com/project/snail-care/ | Snail Care |
| content page | project (portfolio item) | https://www.albertscott.com/project/sunshine-nuts/ | Sunshine Nuts |
| content page | project (portfolio item) | https://www.albertscott.com/project/superior-trading/ | Superior Trading |
| content page | project (portfolio item) | https://www.albertscott.com/project/the-matzo-project/ | The Matzo Project |
| content page | project (portfolio item) | https://www.albertscott.com/project/verve-culture/ | Verve Culture |
| content page | project (portfolio item) | https://www.albertscott.com/project/vianney/ | Vianney |
| junk | category archive | https://www.albertscott.com/blog/category/amazon-advertising/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | category archive | https://www.albertscott.com/blog/category/amazon-agency/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | category archive | https://www.albertscott.com/blog/category/apparel/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | category archive | https://www.albertscott.com/blog/category/beauty-personal-care/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | category archive | https://www.albertscott.com/blog/category/grocery/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | category archive | https://www.albertscott.com/blog/category/health-household/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | category archive | https://www.albertscott.com/blog/category/uncategorized/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (post-type archive /project/) | https://www.albertscott.com/project/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/apparel/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/automotive/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/beauty-cosmetics/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/food/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/furniture/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/homewares/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/outdoors/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/pet/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/tech-accessories/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | other (project_category taxonomy archive) | https://www.albertscott.com/blog/project_category/vitamins-supplements/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | tag archive | https://www.albertscott.com/blog/tag/bags/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |
| junk | tag archive | https://www.albertscott.com/blog/tag/subscribe-and-save/ | in sitemap; live 200 and indexable where sampled (no noindex meta) |

## Junk URLs not in the sitemap but live on the site

Rule 9 dispositions are proposals for the roadmap. Nothing here has been changed on the live site.

| Type | URL or pattern | Live evidence (2026-09-03) | Proposed disposition |
|---|---|---|---|
| Author archive | /blog/author/albertllc/ | 200, indexable (`meta robots max-image-preview:large` only), self canonical, title "Albert Scott - Albert Scott", 502 words | noindex (single-author style site; or redirect to /about-us/) |
| Author archive | /blog/author/hannah-kaufman/ | 200, indexable, title "Hannah Kaufman - Albert Scott" | noindex, or keep only if a real author page with bio is wanted for GEO |
| Author archive | /blog/author/7121525_u8r6t1/ and /blog/author/hashsalacop/ | REST users endpoint lists these two additional accounts. Not fetched. | Verify these accounts with the site owner. The REST users endpoint exposing login-style slugs is a hygiene observation for the roadmap. |
| Attachment pages | 1,075 media items (REST X-WP-Total) | Two sampled: /0x0-4/ and /0x0-3/ both 301 to the file under /wp-content/uploads/. AIOSEO appears to redirect attachment pages to the file. | Already redirect. Confirm the setting covers all media in Stage 1 by sampling more. |
| Pagination | /page/2/ | 200, `meta robots noindex, nofollow`, canonical points to /, title "Home - Albert Scott - Page 2" | Already noindex. Nothing to do unless it appears in crawl paths. |
| Pagination | /blog/page/2/ | 404 | Nothing to do |
| Blog index | /blog/ | 404. All 13 posts live under /blog/ but the index does not exist. | Not junk; a missing hub page. Roadmap item: create or redirect /blog/ to /newsroom/ or /albert-scott-university/. |
| Search results | /?s=amazon | 200, `meta robots noindex` | Already noindex |
| Feed | /feed/ | 200, header `x-robots-tag: noindex, follow` | Already noindex |
| Category archives (in sitemap) | /blog/category/grocery/ (200, indexable after one 503 on first fetch), /blog/category/amazon-advertising/ (200, indexable), and 5 more | Listed in sitemap, no noindex | noindex and remove from sitemap; each holds 1 to 3 posts |
| Tag archives (in sitemap) | /blog/tag/bags/ (200, indexable, 230 words), /blog/tag/subscribe-and-save/ | Listed in sitemap, no noindex | noindex and remove from sitemap; each holds 1 post |
| project_category archives (in sitemap) | /blog/project_category/food/ (200, indexable, 389 words) and 9 more | Listed in sitemap, no noindex. Note the /blog/ prefix on a portfolio taxonomy. | noindex and remove from sitemap |
| Post-type archive (in sitemap) | /project/ | 200, indexable, title "Projects - Albert Scott", 562 words, no meta description | Keep only if it becomes the portfolio hub; otherwise redirect to /listings-portfolio-gallery/ |

## Redirecting URLs still linked from the homepage footer

| Linked URL | Result |
|---|---|
| /listing-division-2/ | 301 to /listing-division/ |
| /marketing-division/ | 301 to /marketing-devision/ (the live slug is misspelled) |
| /logistics-division-2/ | 301 to /logistics-division/ |
| /case-studies-2/ | 301 to /case-studies/ (also linked from /marketing-devision/) |

## Host and protocol

| URL | Result |
|---|---|
| https://albertscott.com/ | 301 to https://www.albertscott.com/ |
| http://www.albertscott.com/ | 301 to https://www.albertscott.com/ |

## Stage 1 additions (2026-09-03)

| URL | Finding | Disposition |
|---|---|---|
| /marketing-management/ | 404, still returned for the site: query, linked from /test-modules/ | 301 to the marketing division page |
| /privacy-policy-2/ | 404, linked from /test-modules/ | 301 to /privacy-policy/ |
| /listing-division-2/, /marketing-division/, /logistics-division-2/ | 301s linked from the homepage divisions section | Update the homepage links (roadmap R2) |
| /case-studies-2/ | 301 linked from 4 pages | Update the links (roadmap R2) |
| Orphans | 33 content pages have no inbound link from any crawled page; list in the audit, Part C item 4 | Resolved by roadmap R1 and R18 |
| Case study PDFs | 9 PDFs under /wp-content/uploads/ linked from pages (Atlas, Flipbelt, Mouthwatchers, Objet D'Art, Great Western, Nora, BeYoutiful, Human Beanz, Roll Comb) | Convert to HTML case studies (growth plan G6) |
