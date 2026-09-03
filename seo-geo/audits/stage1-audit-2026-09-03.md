# Stage 1 audit, 2026-09-03

Full audit of https://www.albertscott.com/ under the nine hard rules in `../README.md`. Sources used: the site's WordPress read-only REST API (inventory), WebFetch (robots.txt and third-party list pages), WebSearch (baseline and GEO prompts), and headless Chromium via Playwright (every content page rendered at 1440x900 and 390x844, DOM evidence captured, screenshots saved to `screenshots/stage1-2026-09-03/`). Nothing on the live site was changed.

Grading method: each of the 12 points is scored Pass, Partial, or Fail from the captured DOM evidence by a fixed rule set (documented in Part C), then reviewed by hand for the primary pages. Score per page is Pass = 1, Partial = 0.5, Fail = 0 across the 11 scored points (point 12 is observational). Dashes in quoted site copy are shown as " - " to keep this file free of em dashes.

## Summary

| Measure | Value |
|---|---|
| Content pages crawled | 86 (85 sitemap content URLs plus the noindexed /case-studies/mouthwatchers/) |
| All returned HTTP 200 | Yes |
| Average score (of 11) | 5.48 |
| Best page | /blog/mastering-amazon-dsp/ (8.0) |
| Worst page | /thankyou/ (2.5) |
| Titles that fail (no descriptive term or generic) | 68 of 86 |
| Pages with no meta description | 19 |
| Pages whose meta description is raw shortcode | 11 |
| Pages with zero or multiple H1s | 12 |
| Images with empty alt | 1504 of 1601 (93%) |
| Pages where every image has empty alt | 63 |
| Pages under 350 words of body copy | 63 |
| Orphan pages (no inbound link from any crawled page) | 33 |
| Pages linking to redirecting internal URLs | 4 |
| Pages with no og:image | 86 |
| Pages with horizontal overflow at 390px | 7 |
| Pages with a FAQ section | 4 |
| Pages with page-level FAQPage or Article schema | 13 |

### Results by grade point

| Point | Pass | Partial | Fail |
|---|---|---|---|
| Title | 16 | 2 | 68 |
| Meta description | 53 | 3 | 30 |
| H1 and hierarchy | 5 | 59 | 22 |
| Content | 19 | 23 | 44 |
| Internal links | 37 | 49 | 0 |
| Image alt text | 0 | 5 | 81 |
| Schema | 0 | 86 | 0 |
| Canonical | 82 | 4 | 0 |
| Conversion path | 2 | 81 | 3 |
| GEO readability | 0 | 39 | 47 |
| Cannibalization | 82 | 0 | 4 |

## Part A. Discovery

| Path | Result |
|---|---|
| /robots.txt | 200. Disallows /wp-admin/ and /cdn-cgi/, allows admin-ajax.php, lists /sitemap.xml and /sitemap.rss |
| /sitemap.xml | 200. AIOSEO Pro 5.0.1 index, 7 children, 105 URLs. Header x-robots-tag: noindex, follow |
| /sitemap_index.xml, /wp-sitemap.xml | 302 to /sitemap.xml |
| /sitemap.rss | 200 |

| Child sitemap | URLs |
|---|---|
| /post-sitemap.xml | 13 |
| /page-sitemap.xml | 49 |
| /project-sitemap.xml | 23 |
| /post-archive-sitemap.xml | 1 |
| /category-sitemap.xml | 7 |
| /post_tag-sitemap.xml | 2 |
| /project_category-sitemap.xml | 10 |

WordPress read-only REST API: 50 published pages (49 in sitemap; /case-studies/mouthwatchers/ excluded and noindexed), 13 posts, 23 projects, 1,075 media items, 4 user accounts with public author archives.

Reconciliation: 105 sitemap URLs = 85 content + 20 junk. Linked but not published or not in sitemap: /marketing-division/, /listing-division-2/, /logistics-division-2/, /case-studies-2/ (all 301; the first three are linked from the homepage divisions section, the last from four pages), /privacy-policy-2/ and /marketing-management/ (both 404, linked from /test-modules/; /marketing-management/ is also still held in the search index per the site: query). Blog index /blog/ returns 404 although all 13 posts live under it.

## Part B. Junk URL dispositions (rule 9)

Junk URLs are not graded. Each gets a disposition for the roadmap. Live evidence from 2026-09-03 probes.

| Type | URLs | Live state | Disposition |
|---|---|---|---|
| Category archives | 7 in sitemap (/blog/category/...) | 200, indexable, self canonical, 1 to 3 posts each; grocery returned 503 once then 200 | noindex, remove from sitemap |
| Tag archives | 2 in sitemap (/blog/tag/bags/, /blog/tag/subscribe-and-save/) | 200, indexable, 1 post each, 230 words | noindex, remove from sitemap; delete the tags |
| project_category archives | 10 in sitemap (/blog/project_category/...) | 200, indexable, 389 words sampled; taxonomy sits under the /blog/ prefix | noindex, remove from sitemap |
| Post-type archive | /project/ (in sitemap) | 200, indexable, "Projects - Albert Scott", no meta description, 562 words | redirect to /listings-portfolio-gallery/ unless it becomes the portfolio hub |
| Author archives | /blog/author/albertllc/, /blog/author/hannah-kaufman/, plus two accounts (7121525_u8r6t1, hashsalacop) exposed by the REST users endpoint | 200, indexable, self canonical | noindex all author archives; verify the two unfamiliar accounts with the site owner |
| Attachment pages | 1,075 media items | Sampled two: 301 to the file | already redirect; no action beyond a wider sample in the monthly deep dive |
| Pagination | /page/2/ | 200, noindex, canonical to / | already noindex |
| Search, feed | /?s=, /feed/ | noindex via meta and x-robots-tag | already noindex |
| Dead URLs | /marketing-management/, /privacy-policy-2/ | 404 | redirect /marketing-management/ to /marketing-devision/ (or its renamed successor); redirect /privacy-policy-2/ to /privacy-policy/ |
| Missing hub | /blog/ | 404 | redirect to /newsroom/ or build a blog index |

## Part C. Site-wide findings with evidence

These recur on many pages; the per-page tables in Part D cite them per URL.

1. **Titles do not describe the service.** 68 of 86 titles are the page label plus " - Albert Scott" with no term a buyer searches. Examples: "Home - Albert Scott", "Listing Division - Albert Scott", "Retail Division - Albert Scott", "DSP - Albert Scott", "Marketing Devision - Albert Scott" (misspelled, also in the slug and breadcrumb schema). The 16 passing titles are the 5 blog articles, the two case study pages with descriptive titles, and legacy pages whose old titles happened to include "Amazon".
2. **Image alt text is effectively absent.** 1504 of 1601 images across the site have alt="". 63 pages have no alt on any image. Client logos, portfolio images, division icons and the site logo are all unlabeled. The 23 project pages are image galleries with 10 to 14 words of text and no alt, so they carry no indexable content at all.
3. **Thin pages dominate the inventory.** 63 of 86 pages have under 350 words of body copy. The four division pages run 336 to 706 words; /dsp/ at 1,396 words is the deepest service page and has 1 inbound link.
4. **33 orphan pages.** No crawled page links to them, so they are reachable only through the sitemap: /blog/mouthwatchers/, /blog/rae-dunn/, /blog/73-originals/, /blog/jose-gourmet/, /marketing-division-2/, /for-amazon-brandsv2/, /test-page/, /book-a-call/, /for-amazon-brands/, /amazon-growth-audit-v2/, /form-ads-test/, /amazon-growth-audit/, /university/, /home/, /test-modules/, /hero/, /our-location/, /amazon-management-agency/, /thankyou/, /thank-you/, /services-2/, /services/, /our-management/, /our-service/, /overview/, /additional-services/, /videos/, /niftyone-custom-portal/, /recent-success/, /our-world-wide-team/, /sample-page/, /our-story/, /our-team/. This set is almost exactly the triage list, plus /book-a-call/, /our-location/, /university/ and four brand posts.
5. **Internal links through redirects.** The homepage divisions section links /listing-division-2/, /marketing-division/ and /logistics-division-2/, all of which 301 to the live division pages; the homepage, /listings-portfolio-gallery/, /marketing-devision/ and /marketing-division-2/ link /case-studies-2/, which 301s to /case-studies/. The most important page on the site reaches its service pages only through redirects.
6. **Meta descriptions.** 19 pages have none, including /marketing-devision/, /dsp/, /book-a-call/, /our-location/ and all 23 projects. 13 legacy pages expose raw Visual Composer shortcode ("[vc_row css_animation=...") as their description and as visible body text.
7. **Heading structure.** Every division page places an H3 eyebrow "Albert Scott Divisions" before the H1. /about-us/, /listings-portfolio-gallery/, /book-a-call/, /our-location/ and /contact-us/ have no H1 or a non-descriptive one; /home/ has six H1s. Testimonial quotes and attributions are set as H2, H3 and H4 across the homepage and /marketing-devision/.
8. **Schema.** Two Organization nodes on every page disagree (AIOSEO: @id /#organization, description "E-commerce Management", 5 to 10 employees; custom: @id /#org, ProfessionalService, 30 employees, address, phone, OfferCatalog). Neither has sameAs. No page has FAQPage schema even though /dsp/ and /albert-scott-university/ have FAQ text. Blog posts carry BlogPosting; case study pages and projects carry nothing page-specific. No page has og:image, so social and AI previews fall back to nothing.
9. **Conversion path on mobile.** Only the homepage shows a CTA inside the first 844px on a 390px screen. On every other page the only CTA above the fold is the "Contact" nav button, which is inside the hamburger menu on mobile. /contact-us/ has 54 words and no H1 that says contact; /book-a-call/ (68 words, orphan) and /lets-talk/ (50 words) duplicate it.
10. **Cannibalization and duplicates.** Live indexable pairs: /marketing-devision/ and /marketing-division-2/; /services/ and /services-2/ and /our-service/; /thank-you/ and /thankyou/; /university/ and /albert-scott-university/; /portfolio/ and /listings-portfolio-gallery/; /retail-management/ and /retail-division/; /home/ and /amazon-management-agency/ and /for-amazon-brands/ and /for-amazon-brandsv2/ against /. Eight of the 13 blog posts are brand write-ups that duplicate the project and case study post types (for example /blog/mouthwatchers/ and /case-studies/mouthwatchers/).
11. **Rendering.** 7 pages overflow horizontally at 390px (/listings-portfolio-gallery/, /about-us/, /test-modules/, /services/, /overview/, /videos/, /our-team/); /about-us/, /services/, /overview/ and /videos/ also overflow at 1440px. Screenshots are in `screenshots/stage1-2026-09-03/`.
12. **Copy style.** 83 em dashes across 18 pages, which matters for the house style rule when copy is rewritten.

### Grading rules applied

- Title: Fail if generic ("Home", "Services", a test or form label) or no term from the set amazon, vendor, seller, PPC, advertising, DSP, listing, logistics, retail, FBA, A+, brand, case study, marketplace. Partial if outside 30 to 65 characters. Pass otherwise.
- Meta description: Fail if missing or contains shortcode. Partial if under 70 or over 165 characters.
- H1 and hierarchy: Fail if zero or several H1s or headings appear before the H1. Partial if the H1 carries no descriptive term or levels skip. Pass otherwise.
- Content: Fail under 150 body words or with placeholder text. Partial under 350 or with visible shortcode. Body words exclude header, footer, nav and cookie bar.
- Internal links: Fail if no body links out and at most one inbound link. Partial if any link targets a redirect or 404, or the page has at most one inbound link, or no body links.
- Image alt: Fail if over half the images have empty alt. Partial if any do.
- Schema: Partial everywhere because the two Organization nodes conflict; note whether page-level schema exists.
- Canonical: Pass if self-referencing and no other crawled page shares the title.
- Conversion path: Pass if a CTA is visible in the first mobile screen and a CTA or form exists. Partial if the CTA exists but only in the nav or below the fold. Fail if none.
- GEO readability: Pass if the opening paragraph states what the page or company is, a meta description exists, and a FAQ exists. Partial if the opening is definitional but the rest is missing. Fail if the opening is missing or not definitional.
- Cannibalization: Fail if another crawled page has the same title; topic-level overlap is recorded in Part C item 10 and the roadmap.

## Part D. Page grades

### A. Primary pages

#### /retail-division/

Score 7.5 of 11. Title: "Retail Division - Albert Scott". 378 body words. Inbound links: 78. Screenshots: `retail-division--desktop-1440x900.jpg`, `retail-division--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Retail Division - Albert Scott" (30 chars) |
| 2. Meta description | Pass | 134 chars: "Scale your retail presence with Albert Scott’s retail division, connecting brands to major..." |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H3) |
| 4. Content | Pass | 378 words, 7 paragraphs |
| 5. Internal links | Pass | 1 body links out, 78 inbound |
| 6. Image alt text | Fail | 19 of 19 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott’s Retail Division provides executive-level control across operations, profitability, an" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /

Score 7.0 of 11. Title: "Home - Albert Scott". 984 body words. Inbound links: 78. Screenshots: `homepage--desktop-1440x900.jpg`, `homepage--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Home - Albert Scott" (19 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 129 chars: "Albert Scott is a full-service Amazon growth agency helping brands scale with expert marke..." |
| 3. H1 and hierarchy | Partial | 2 level skip(s) |
| 4. Content | Pass | 984 words, 11 paragraphs |
| 5. Internal links | Partial | 4 link(s) to redirecting or broken URLs: /marketing-division/, /listing-division-2/, /case-studies-2/, /logistics-division-2/ |
| 6. Image alt text | Fail | 236 of 236 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Pass | CTAs: Contact, GET MY FREE AUDIT; form(s): 1; CTA visible in mobile first screen |
| 10. GEO readability | Partial | no FAQ or Q&A section; 4 em dashes in body copy. Opening: "Albert Scott is a complete marketplace account management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /logistics-division/

Score 7.0 of 11. Title: "Logistics Division - Albert Scott". 336 body words. Inbound links: 78. Screenshots: `logistics-division--desktop-1440x900.jpg`, `logistics-division--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Logistics Division - Albert Scott" (33 chars) |
| 2. Meta description | Pass | 136 chars: "Optimize fulfillment with Albert Scott’s logistics division - streamlining inventory, shippi..." |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H3) |
| 4. Content | Partial | 336 words |
| 5. Internal links | Pass | 1 body links out, 78 inbound |
| 6. Image alt text | Fail | 10 of 10 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott provides Amazon-focused logistics infrastructure built to support marketplace growth. O" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /listing-division/

Score 7.0 of 11. Title: "Listing Division - Albert Scott". 451 body words. Inbound links: 78. Screenshots: `listing-division--desktop-1440x900.jpg`, `listing-division--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Listing Division - Albert Scott" (31 chars) |
| 2. Meta description | Pass | 131 chars: "Improve product listings with Albert Scott’s listing division - optimized content, images, a..." |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H3); 1 level skip(s) |
| 4. Content | Pass | 451 words, 12 paragraphs |
| 5. Internal links | Pass | 2 body links out, 78 inbound |
| 6. Image alt text | Fail | 19 of 21 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section; 6 em dashes in body copy |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /newsroom/

Score 6.5 of 11. Title: "Newsroom - Albert Scott". 610 body words. Inbound links: 78. Screenshots: `newsroom--desktop-1440x900.jpg`, `newsroom--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Newsroom - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 134 chars: "Stay updated with Albert Scott’s Newsroom - expert insights on Amazon eCommerce, logistics..." |
| 3. H1 and hierarchy | Partial | H1 "Newsroom" carries no descriptive term |
| 4. Content | Pass | 610 words, 12 paragraphs |
| 5. Internal links | Partial | 10 generic anchors |
| 6. Image alt text | Fail | 5 of 5 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "David Greenblatt, CEO of Albert Scott, is a recognized thought leader in Amazon strategy, ecommerce " |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /privacy-policy/

Score 6.5 of 11. Title: "Privacy Policy - Albert Scott". 612 body words. Inbound links: 85. Screenshots: `privacy-policy--desktop-1440x900.jpg`, `privacy-policy--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Privacy Policy - Albert Scott" (29 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 121 chars: "Read Albert Scott’s privacy policy to understand how we collect, use, and protect your per..." |
| 3. H1 and hierarchy | Partial | H1 "Privacy Policy" carries no descriptive term; 1 level skip(s) |
| 4. Content | Pass | 612 words, 17 paragraphs |
| 5. Internal links | Pass | 18 body links out, 85 inbound |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /listings-portfolio-gallery/

Score 6.0 of 11. Title: "Listings Portfolio Gallery - Albert Scott". 229 body words. Inbound links: 78. Screenshots: `listings-portfolio-gallery--desktop-1440x900.jpg`, `listings-portfolio-gallery--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Listings Portfolio Gallery - Albert Scott" (41 chars) |
| 2. Meta description | Pass | 123 chars: "View Albert Scott’s portfolio of optimized Amazon listings designed to boost engagement, v..." |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Partial | 229 words |
| 5. Internal links | Partial | 1 link(s) to redirecting or broken URLs: /case-studies-2/ |
| 6. Image alt text | Fail | 219 of 219 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | horizontal overflow at 390px; slow load through proxy: 24s; no og:image |

#### /about-us/

Score 6.0 of 11. Title: "About Us - Albert Scott". 647 body words. Inbound links: 78. Screenshots: `about-us--desktop-1440x900.jpg`, `about-us--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "About Us - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 137 chars: "Learn about Albert Scott, a leading Amazon growth agency dedicated to helping brands succe..." |
| 3. H1 and hierarchy | Fail | no H1; 1 level skip(s) |
| 4. Content | Pass | 647 words, 10 paragraphs |
| 5. Internal links | Pass | 2 body links out, 78 inbound |
| 6. Image alt text | Fail | 93 of 93 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section; 7 em dashes in body copy |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | horizontal overflow at 390px; horizontal overflow at 1440px; no og:image |

#### /contact-us/

Score 6.0 of 11. Title: "Contact Us - Albert Scott". 54 body words. Inbound links: 78. Screenshots: `contact-us--desktop-1440x900.jpg`, `contact-us--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Contact Us - Albert Scott" (25 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 143 chars: "Contact Albert Scott to learn how our Amazon growth experts can help scale your brand with..." |
| 3. H1 and hierarchy | Partial | H1 "Get in Touch" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 54 words of body copy |
| 5. Internal links | Pass | 1 body links out, 78 inbound |
| 6. Image alt text | Fail | 6 of 6 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Schedule a Chat; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /dsp/

Score 6.0 of 11. Title: "DSP - Albert Scott". 1396 body words. Inbound links: 1. Screenshots: `dsp--desktop-1440x900.jpg`, `dsp--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Partial | "DSP - Albert Scott" (18 chars): outside 30 to 65 |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Partial | 6 level skip(s) |
| 4. Content | Pass | 1396 words, 36 paragraphs |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 175 of 175 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: none; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; 6 em dashes in body copy. Opening: "Albert Scott helps established Amazon brands scale beyond search with DSP strategies built around AM" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /albert-scott-university/

Score 5.5 of 11. Title: "Albert Scott University - Albert Scott". 176 body words. Inbound links: 78. Screenshots: `albert-scott-university--desktop-1440x900.jpg`, `albert-scott-university--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Albert Scott University - Albert Scott" (38 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 112 chars: "Albert Scott University offers expert insights, guides, and resources to help brands grow ..." |
| 3. H1 and hierarchy | Partial | H1 "Albert Scott University" carries no descriptive term |
| 4. Content | Partial | 176 words |
| 5. Internal links | Partial | 3 generic anchors |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Download Now; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /marketing-devision/

Score 5.0 of 11. Title: "Marketing Devision - Albert Scott". 706 body words. Inbound links: 78. Screenshots: `marketing-devision--desktop-1440x900.jpg`, `marketing-devision--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Marketing Devision - Albert Scott" (33 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H3); H1 "Marketing Division" carries no descriptive term; 2 level skip(s) |
| 4. Content | Pass | 706 words, 16 paragraphs |
| 5. Internal links | Partial | 1 link(s) to redirecting or broken URLs: /case-studies-2/ |
| 6. Image alt text | Fail | 42 of 44 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, TALK WITH AN EXPERT; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "Albert Scott builds Amazon advertising systems for brands that need more than campaign management." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /cookies-policy/

Score 5.0 of 11. Title: "Cookies Policy - Albert Scott". 167 body words. Inbound links: 77. Screenshots: `cookies-policy--desktop-1440x900.jpg`, `cookies-policy--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Cookies Policy - Albert Scott" (29 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H2); H1 "Disclaimer" carries no descriptive term |
| 4. Content | Partial | 167 words |
| 5. Internal links | Pass | 1 body links out, 77 inbound |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "Certain information set forth in this communication may contain “forward-looking” information. These" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /book-a-call/

Score 3.0 of 11. Title: "Book a Call - Albert Scott". 68 body words. Inbound links: 0. Screenshots: `book-a-call--desktop-1440x900.jpg`, `book-a-call--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Book a Call - Albert Scott" (26 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Fail | 68 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 2 of 2 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Fail | no CTA text or form found |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

### B. Posts and case studies

#### /blog/mastering-amazon-dsp/

Score 8.0 of 11. Title: "Mastering Amazon DSP for Mid-to-Large Brands - Albert Scott". 719 body words. Inbound links: 20. Screenshots: `blog__mastering-amazon-dsp--desktop-1440x900.jpg`, `blog__mastering-amazon-dsp--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Mastering Amazon DSP for Mid-to-Large Brands - Albert Scott" (59 chars) |
| 2. Meta description | Pass | 104 chars: "Learn how to master Amazon DSP with proven strategies to scale ads, improve targeting, and..." |
| 3. H1 and hierarchy | Pass | One H1 "Mastering Amazon DSP for Mid-to-Large Brands", 12 body headings in order |
| 4. Content | Pass | 719 words, 21 paragraphs |
| 5. Internal links | Pass | 18 body links out, 20 inbound |
| 6. Image alt text | Fail | 5 of 5 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section; 9 em dashes in body copy |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/tacos-vs-acos-what-amazon-managers-need-to-know/

Score 8.0 of 11. Title: "TACoS vs. ACoS: What Amazon Managers Need to Know - Albert Scott". 806 body words. Inbound links: 20. Screenshots: `blog__tacos-vs-acos-what-amazon-managers-need-to-know--desktop-1440x900.jpg`, `blog__tacos-vs-acos-what-amazon-managers-need-to-know--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "TACoS vs. ACoS: What Amazon Managers Need to Know - Albert Scott" (64 chars) |
| 2. Meta description | Pass | 108 chars: "Understand TACoS vs ACoS and what Amazon managers need to know to optimize ad spend and dr..." |
| 3. H1 and hierarchy | Pass | One H1 "TACoS vs. ACoS: What Amazon Managers Need to Know", 13 body headings in order |
| 4. Content | Pass | 806 words, 30 paragraphs |
| 5. Internal links | Pass | 18 body links out, 20 inbound |
| 6. Image alt text | Fail | 4 of 5 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/subscribe-and-save-strategies/

Score 8.0 of 11. Title: "Subscribe-and-Save Strategies: A Case Study in 200%+ YoY". 842 body words. Inbound links: 20. Screenshots: `blog__subscribe-and-save-strategies--desktop-1440x900.jpg`, `blog__subscribe-and-save-strategies--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Subscribe-and-Save Strategies: A Case Study in 200%+ YoY" (56 chars) |
| 2. Meta description | Pass | 127 chars: "Learn effective Amazon Subscribe and Save strategies to increase repeat purchases, boost r..." |
| 3. H1 and hierarchy | Pass | One H1 "Subscribe-and-Save Strategies: A Case Study in 200%+ YoY Growth", 19 body headings in order |
| 4. Content | Pass | 842 words, 30 paragraphs |
| 5. Internal links | Pass | 18 body links out, 20 inbound |
| 6. Image alt text | Fail | 6 of 6 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/how-to-conquer-your-competition-with-amazon-keyword-targeting/

Score 7.5 of 11. Title: "Amazon Keyword Targeting: How to Beat Your Competition". 769 body words. Inbound links: 20. Screenshots: `blog__how-to-conquer-your-competition-with-amazon-keyword-targeting--desktop-1440x900.jpg`, `blog__how-to-conquer-your-competition-with-amazon-keyword-targeting--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Amazon Keyword Targeting: How to Beat Your Competition" (54 chars) |
| 2. Meta description | Pass | 106 chars: "Learn how Amazon keyword targeting helps you outperform competitors, boost rankings, and d..." |
| 3. H1 and hierarchy | Partial | 1 level skip(s) |
| 4. Content | Pass | 769 words, 28 paragraphs |
| 5. Internal links | Pass | 18 body links out, 20 inbound |
| 6. Image alt text | Fail | 4 of 5 images have empty alt |
| 7. Schema | Partial | BlogPosting, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/streamlining-logistics-for-scalable-amazon-success/

Score 7.5 of 11. Title: "Streamlining Logistics for Scalable Amazon Success / Albert Scott". 1129 body words. Inbound links: 20. Screenshots: `blog__streamlining-logistics-for-scalable-amazon-success--desktop-1440x900.jpg`, `blog__streamlining-logistics-for-scalable-amazon-success--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Streamlining Logistics for Scalable Amazon Success / Albert Scott" (65 chars) |
| 2. Meta description | Pass | 135 chars: "Learn how optimized logistics can drive scalable Amazon success, reduce costs, and improve..." |
| 3. H1 and hierarchy | Partial | 1 level skip(s) |
| 4. Content | Pass | 1129 words, 25 paragraphs |
| 5. Internal links | Pass | 18 body links out, 20 inbound |
| 6. Image alt text | Fail | 5 of 5 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section; 20 em dashes in body copy |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /case-studies/mouthwatchers/

Score 6.5 of 11. Title: "Mouthwatchers Case Study / Amazon Growth & Strategy". 517 body words. Inbound links: 1. Screenshots: `case-studies__mouthwatchers--desktop-1440x900.jpg`, `case-studies__mouthwatchers--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Mouthwatchers Case Study / Amazon Growth & Strategy" (51 chars) |
| 2. Meta description | Pass | 142 chars: "Albert Scott’s Mouthwatchers case study shows how strategic Amazon marketing and campaigns..." |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H4); H1 "Mouthwatchers: Unlocking Growth in a Commodity Category" carries no descriptive term; 2 level skip(s) |
| 4. Content | Pass | 517 words, 8 paragraphs |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 11 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section; 5 em dashes in body copy |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | meta robots noindex, nofollow, max-snippet:-1, max-image-preview:large, max-video-preview:-1; no og:image |

#### /blog/mouthwatchers/

Score 6.0 of 11. Title: "Mouthwatchers on Amazon / Growth Strategy & Insights". 108 body words. Inbound links: 0. Screenshots: `blog__mouthwatchers--desktop-1440x900.jpg`, `blog__mouthwatchers--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Mouthwatchers on Amazon / Growth Strategy & Insights" (52 chars) |
| 2. Meta description | Pass | 110 chars: "See how Mouthwatchers scaled on Amazon with strategic growth, branding, and performance op..." |
| 3. H1 and hierarchy | Partial | H1 "Dr Plotka / Mouthwatchers" carries no descriptive term |
| 4. Content | Fail | 108 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 6 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, GET A QUOTE TODAY; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /case-studies/

Score 6.0 of 11. Title: "Case Studies - Albert Scott". 276 body words. Inbound links: 78. Screenshots: `case-studies--desktop-1440x900.jpg`, `case-studies--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Partial | "Case Studies - Albert Scott" (27 chars): outside 30 to 65 |
| 2. Meta description | Pass | 119 chars: "Explore Albert Scott case studies showing how brands achieved growth, increased sales, and..." |
| 3. H1 and hierarchy | Partial | 1 level skip(s) |
| 4. Content | Partial | 276 words |
| 5. Internal links | Partial | 4 generic anchors |
| 6. Image alt text | Fail | 7 of 7 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/objet-dart/

Score 5.0 of 11. Title: "Objet D’Art - Albert Scott". 61 body words. Inbound links: 1. Screenshots: `blog__objet-dart--desktop-1440x900.jpg`, `blog__objet-dart--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Objet D’Art - Albert Scott" (26 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 109 chars: "Discover how Objet d’Art brands grow on Amazon with expert strategies, positioning, and ma..." |
| 3. H1 and hierarchy | Partial | H1 "Objet D’art – Side Table" carries no descriptive term |
| 4. Content | Fail | 61 words of body copy |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 5 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, GET A QUOTE TODAY; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/rae-dunn/

Score 5.0 of 11. Title: "Rae Dunn - Albert Scott". 65 body words. Inbound links: 0. Screenshots: `blog__rae-dunn--desktop-1440x900.jpg`, `blog__rae-dunn--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Rae Dunn - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 111 chars: "Learn how Rae Dunn’s brand strategy and presence on Amazon contribute to its growth and st..." |
| 3. H1 and hierarchy | Partial | H1 "Rae Dunn – Laundry Hamper" carries no descriptive term |
| 4. Content | Fail | 65 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 5 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, GET A QUOTE TODAY; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/yumvs/

Score 5.0 of 11. Title: "YumVs - Albert Scott". 93 body words. Inbound links: 1. Screenshots: `blog__yumvs--desktop-1440x900.jpg`, `blog__yumvs--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "YumVs - Albert Scott" (20 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 121 chars: "Discover how YumVs achieved growth on Amazon with strategic marketing, optimized listings,..." |
| 3. H1 and hierarchy | Partial | H1 "YumVs Vitamins" carries no descriptive term |
| 4. Content | Fail | 93 words of body copy |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 5 of 6 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/tabanero/

Score 5.0 of 11. Title: "Tabanero - Albert Scott". 119 body words. Inbound links: 1. Screenshots: `blog__tabanero--desktop-1440x900.jpg`, `blog__tabanero--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Tabanero - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 140 chars: "Albert Scott helped Tabanero Hot Sauce turn up the heat with bold digital marketing and st..." |
| 3. H1 and hierarchy | Partial | H1 "Tabanero" carries no descriptive term |
| 4. Content | Fail | 119 words of body copy |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 5 of 6 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/73-originals/

Score 5.0 of 11. Title: "’73 Originals - Albert Scott". 123 body words. Inbound links: 0. Screenshots: `blog__73-originals--desktop-1440x900.jpg`, `blog__73-originals--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "’73 Originals - Albert Scott" (28 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 115 chars: "See how Albert Scott helped promote 73 Originals - a streetwear brand blending grit, ambitio..." |
| 3. H1 and hierarchy | Partial | H1 "’73 Originals" carries no descriptive term |
| 4. Content | Fail | 123 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 5 of 6 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /blog/jose-gourmet/

Score 5.0 of 11. Title: "Jose Gourmet - Albert Scott". 139 body words. Inbound links: 0. Screenshots: `blog__jose-gourmet--desktop-1440x900.jpg`, `blog__jose-gourmet--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Jose Gourmet - Albert Scott" (27 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 150 chars: "We brought Jose Gourmet’s premium canned seafood to life with lifestyle-rich listings, a v..." |
| 3. H1 and hierarchy | Partial | H1 "Jose Gourmet" carries no descriptive term |
| 4. Content | Fail | 139 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 6 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /case-studies/atlas-olive-oils/

Score 5.0 of 11. Title: "Atlas Olive Oils - Albert Scott". 555 body words. Inbound links: 1. Screenshots: `case-studies__atlas-olive-oils--desktop-1440x900.jpg`, `case-studies__atlas-olive-oils--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Atlas Olive Oils - Albert Scott" (31 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H4); 2 level skip(s) |
| 4. Content | Pass | 555 words, 13 paragraphs |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 11 of 13 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section; 5 em dashes in body copy. Opening: "Atlas Olive Oils is a premium olive oil brand produced in Morocco at the foothills of the Atlas Moun" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /case-studies/beyoutiful/

Score 5.0 of 11. Title: "From $0 to $1M+ in Year 1 - Albert Scott". 566 body words. Inbound links: 1. Screenshots: `case-studies__beyoutiful--desktop-1440x900.jpg`, `case-studies__beyoutiful--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "From $0 to $1M+ in Year 1 - Albert Scott" (40 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H4); 2 level skip(s) |
| 4. Content | Pass | 566 words, 11 paragraphs |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 10 of 13 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "BeYoutiful is a skincare brand designed specifically for kids and teens, focused on gentle, effectiv" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | slow load through proxy: 18s; no og:image |

#### /blog/atlas-olive-oil-spray/

Score 4.5 of 11. Title: "Atlas Olive Oil Spray - Albert Scott". 70 body words. Inbound links: 1. Screenshots: `blog__atlas-olive-oil-spray--desktop-1440x900.jpg`, `blog__atlas-olive-oil-spray--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Atlas Olive Oil Spray - Albert Scott" (36 chars): no descriptive term a buyer would search |
| 2. Meta description | Partial | 47 chars: "Listing Optimization for Atlas Olive Oil Spray...." |
| 3. H1 and hierarchy | Partial | H1 "Atlas – Olive Oil Spray" carries no descriptive term |
| 4. Content | Fail | 70 words of body copy |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BlogPosting, ImageObject, BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

### C. Portfolio projects

#### /project/rufus-teague/

Score 6.0 of 11. Title: "Rufus Teague - Albert Scott". 12 body words. Inbound links: 3. Screenshots: `project__rufus-teague--desktop-1440x900.jpg`, `project__rufus-teague--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Rufus Teague - Albert Scott" (27 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 104 chars: "See how Rufus Teague grew on Amazon using strategic branding, advertising, and marketplace..." |
| 3. H1 and hierarchy | Partial | H1 "Rufus Teague" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 12 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 11 of 11 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/renew-rx/

Score 6.0 of 11. Title: "Renew RX - Albert Scott". 14 body words. Inbound links: 3. Screenshots: `project__renew-rx--desktop-1440x900.jpg`, `project__renew-rx--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Renew RX - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 107 chars: "Discover how Renew RX scaled its presence with Amazon-focused strategies, optimization, an..." |
| 3. H1 and hierarchy | Partial | H1 "Renew RX" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/national-public-seatinf/

Score 6.0 of 11. Title: "National Public Seatinf - Albert Scott". 13 body words. Inbound links: 3. Screenshots: `project__national-public-seatinf--desktop-1440x900.jpg`, `project__national-public-seatinf--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "National Public Seatinf - Albert Scott" (38 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 103 chars: "Explore how National Public Seating improved Amazon performance with strategic growth and ..." |
| 3. H1 and hierarchy | Partial | H1 "National Public Seating" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 13 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 10 of 10 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/out/

Score 6.0 of 11. Title: "OUT! - Albert Scott". 12 body words. Inbound links: 3. Screenshots: `project__out--desktop-1440x900.jpg`, `project__out--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "OUT! - Albert Scott" (19 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 96 chars: "Case study on OUT brand growth through Amazon strategy, optimization, and performance mark..." |
| 3. H1 and hierarchy | Partial | H1 "OUT!" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 12 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/great-western-foods/

Score 6.0 of 11. Title: "Great Western Foods - Albert Scott". 14 body words. Inbound links: 3. Screenshots: `project__great-western-foods--desktop-1440x900.jpg`, `project__great-western-foods--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Great Western Foods - Albert Scott" (34 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 104 chars: "See how Great Western Foods grew on Amazon through targeted strategies, optimization, and ..." |
| 3. H1 and hierarchy | Partial | H1 "Great Western Cotton Candy" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 11 of 11 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/hyp/

Score 6.0 of 11. Title: "HYP - Albert Scott". 11 body words. Inbound links: 3. Screenshots: `project__hyp--desktop-1440x900.jpg`, `project__hyp--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "HYP - Albert Scott" (18 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 97 chars: "Case study on HYP showcasing brand growth, strategy execution, and performance results on ..." |
| 3. H1 and hierarchy | Partial | H1 "HYP" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 11 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/mannol/

Score 6.0 of 11. Title: "Mannol - Albert Scott". 11 body words. Inbound links: 3. Screenshots: `project__mannol--desktop-1440x900.jpg`, `project__mannol--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Mannol - Albert Scott" (21 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 102 chars: "Learn how Mannol expanded on Amazon with expert strategy, brand management, and marketplac..." |
| 3. H1 and hierarchy | Partial | H1 "Mannol" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 11 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 11 of 11 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/kagi/

Score 6.0 of 11. Title: "Kagi - Albert Scott". 12 body words. Inbound links: 3. Screenshots: `project__kagi--desktop-1440x900.jpg`, `project__kagi--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Kagi - Albert Scott" (19 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 112 chars: "Discover how Kagi achieved Amazon growth through strategic positioning, optimization, and ..." |
| 3. H1 and hierarchy | Partial | H1 "Kagi Chocolate" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 12 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 13 of 13 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/snail-care/

Score 6.0 of 11. Title: "Snail Care - Albert Scott". 14 body words. Inbound links: 3. Screenshots: `project__snail-care--desktop-1440x900.jpg`, `project__snail-care--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Snail Care - Albert Scott" (25 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 120 chars: "Explore how Snail Care achieved Amazon growth through listing optimization, branding, and ..." |
| 3. H1 and hierarchy | Partial | H1 "Snail Care" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/verve-culture/

Score 6.0 of 11. Title: "Verve Culture - Albert Scott". 14 body words. Inbound links: 3. Screenshots: `project__verve-culture--desktop-1440x900.jpg`, `project__verve-culture--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Verve Culture - Albert Scott" (28 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 114 chars: "See how Verve Culture expanded on Amazon with strategic growth, optimized listings, and im..." |
| 3. H1 and hierarchy | Partial | H1 "Verve Culture" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/sunshine-nuts/

Score 6.0 of 11. Title: "Sunshine Nuts - Albert Scott". 12 body words. Inbound links: 3. Screenshots: `project__sunshine-nuts--desktop-1440x900.jpg`, `project__sunshine-nuts--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Sunshine Nuts - Albert Scott" (28 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 117 chars: "Learn how Sunshine Nuts grew on Amazon with improved visibility, strategic marketing, and ..." |
| 3. H1 and hierarchy | Partial | H1 "Sunshine Nuts" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 12 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 11 of 11 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/the-matzo-project/

Score 6.0 of 11. Title: "The Matzo Project - Albert Scott". 13 body words. Inbound links: 3. Screenshots: `project__the-matzo-project--desktop-1440x900.jpg`, `project__the-matzo-project--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "The Matzo Project - Albert Scott" (32 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 117 chars: "Discover how The Matzo Project scaled on Amazon with optimized listings, marketing strateg..." |
| 3. H1 and hierarchy | Partial | H1 "The Matzo Project" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 13 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 11 of 11 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/superior-trading/

Score 6.0 of 11. Title: "Superior Trading - Albert Scott". 10 body words. Inbound links: 2. Screenshots: `project__superior-trading--desktop-1440x900.jpg`, `project__superior-trading--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Superior Trading - Albert Scott" (31 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 123 chars: "See how Superior Trading achieved Amazon growth through strategic optimization, improved l..." |
| 3. H1 and hierarchy | Partial | H1 "Superior Trading" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 10 words of body copy |
| 5. Internal links | Pass | 2 body links out, 2 inbound |
| 6. Image alt text | Fail | 10 of 10 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, ImageObject, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/simple-solution/

Score 6.0 of 11. Title: "Simple Solution - Albert Scott". 13 body words. Inbound links: 3. Screenshots: `project__simple-solution--desktop-1440x900.jpg`, `project__simple-solution--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Simple Solution - Albert Scott" (30 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 155 chars: "Simple Solution pet care project featuring new product photography lifestyle visuals and o..." |
| 3. H1 and hierarchy | Partial | H1 "Simple Solution" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 13 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/nora/

Score 6.0 of 11. Title: "Nora - Albert Scott". 13 body words. Inbound links: 3. Screenshots: `project__nora--desktop-1440x900.jpg`, `project__nora--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Nora - Albert Scott" (19 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 135 chars: "Discover how Albert Scott helped Nora scale on Amazon with optimized operations, improved ..." |
| 3. H1 and hierarchy | Partial | H1 "Nora Seaweed Snacks" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 13 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 11 of 11 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/magmod/

Score 6.0 of 11. Title: "Magmod - Albert Scott". 12 body words. Inbound links: 3. Screenshots: `project__magmod--desktop-1440x900.jpg`, `project__magmod--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Magmod - Albert Scott" (21 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 155 chars: "Magmod lighting accessories project featuring complete graphic optimization updated lifest..." |
| 3. H1 and hierarchy | Partial | H1 "Magmod" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 12 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/vianney/

Score 6.0 of 11. Title: "Vianney - Albert Scott". 11 body words. Inbound links: 3. Screenshots: `project__vianney--desktop-1440x900.jpg`, `project__vianney--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Vianney - Albert Scott" (22 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 153 chars: "Discover how Albert Scott helped Vianney scale on Amazon with optimized logistics, refined..." |
| 3. H1 and hierarchy | Partial | H1 "Vianney" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 11 words of body copy |
| 5. Internal links | Pass | 3 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, ImageObject, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/3835/

Score 6.0 of 11. Title: "Bluestem Botanicals - Albert Scott". 13 body words. Inbound links: 3. Screenshots: `project__3835--desktop-1440x900.jpg`, `project__3835--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Bluestem Botanicals - Albert Scott" (34 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 129 chars: "Bluestem Botanicals got a full graphic refresh - rosy syrup mockups and sleek visuals that b..." |
| 3. H1 and hierarchy | Partial | H1 "Bluestem Botanicals" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 13 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/blue-chill/

Score 6.0 of 11. Title: "Blue Chill - Albert Scott". 10 body words. Inbound links: 2. Screenshots: `project__blue-chill--desktop-1440x900.jpg`, `project__blue-chill--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Blue Chill - Albert Scott" (25 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 120 chars: "Blue Chill’s Amazon visuals got the glow-up - bold apparel mockups and cool, curated product..." |
| 3. H1 and hierarchy | Partial | H1 "Blue Chill" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 10 words of body copy |
| 5. Internal links | Pass | 3 body links out, 2 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/its-just-smart/

Score 6.0 of 11. Title: "It’s Just Smart - Albert Scott". 14 body words. Inbound links: 2. Screenshots: `project__its-just-smart--desktop-1440x900.jpg`, `project__its-just-smart--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "It’s Just Smart - Albert Scott" (30 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 147 chars: "Discover how Albert Scott helped It’s Just Smart boost Amazon performance through optimize..." |
| 3. H1 and hierarchy | Partial | H1 "It’s Just Smart" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 4 body links out, 2 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/human-beanz/

Score 6.0 of 11. Title: "Human Beanz - Albert Scott". 14 body words. Inbound links: 3. Screenshots: `project__human-beanz--desktop-1440x900.jpg`, `project__human-beanz--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Human Beanz - Albert Scott" (26 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 143 chars: "See how Albert Scott elevated Human Beanz supplements with bold branding, optimized graphi..." |
| 3. H1 and hierarchy | Partial | H1 "Human Beanz" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 13 of 13 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/healthy-heist/

Score 6.0 of 11. Title: "Healthy Heist - Albert Scott". 14 body words. Inbound links: 3. Screenshots: `project__healthy-heist--desktop-1440x900.jpg`, `project__healthy-heist--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Healthy Heist - Albert Scott" (28 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 141 chars: "We optimized Healthy Heist’s brand with full graphic design - featuring eye-catching elderbe..." |
| 3. H1 and hierarchy | Partial | H1 "Healthy Heist" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 14 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /project/guylian/

Score 6.0 of 11. Title: "Guylian - Albert Scott". 12 body words. Inbound links: 3. Screenshots: `project__guylian--desktop-1440x900.jpg`, `project__guylian--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Guylian - Albert Scott" (22 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 154 chars: "We redesigned Guylian’s Amazon visuals with full graphic optimization - seashell-inspired mo..." |
| 3. H1 and hierarchy | Partial | H1 "Guylian Chocolates" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 12 words of body copy |
| 5. Internal links | Pass | 4 body links out, 3 inbound |
| 6. Image alt text | Fail | 12 of 12 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, Person, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

### D. Triage pages (test, legacy, duplicate)

#### /home/

Score 7.0 of 11. Title: "Albert Scott - A Full Service Amazon Agency". 943 body words. Inbound links: 0. Screenshots: `home--desktop-1440x900.jpg`, `home--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Albert Scott - A Full Service Amazon Agency" (43 chars) |
| 2. Meta description | Pass | 157 chars: "Albert Scott is a full service Amazon agency supporting mid to large brands grow and succe..." |
| 3. H1 and hierarchy | Fail | 6 H1s; 4 heading(s) before the H1 (H2, H2, H2, H3); 8 level skip(s) |
| 4. Content | Pass | 943 words, 35 paragraphs |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages; 9 generic anchors |
| 6. Image alt text | Fail | 81 of 84 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Pass | CTAs: Contact, CONTACT US, Get A Quote, Let's Talk; form(s): 0; CTA visible in mobile first screen |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /clients/

Score 6.5 of 11. Title: "Clients - Albert Scott". 846 body words. Inbound links: 1. Screenshots: `clients--desktop-1440x900.jpg`, `clients--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Clients - Albert Scott" (22 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 145 chars: "Explore how Albert Scott elevates brands on Amazon - boosting conversions, scaling revenue, ..." |
| 3. H1 and hierarchy | Pass | One H1 "Case Studies", 15 body headings in order |
| 4. Content | Pass | 846 words, 21 paragraphs |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 19 of 28 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, GET A QUOTE TODAY; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section; 4 em dashes in body copy |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /for-amazon-brandsv2/

Score 6.0 of 11. Title: "For Amazon Brandsv2 - Albert Scott". 173 body words. Inbound links: 0. Screenshots: `for-amazon-brandsv2--desktop-1440x900.jpg`, `for-amazon-brandsv2--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "For Amazon Brandsv2 - Albert Scott" (34 chars) |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Partial | 1 level skip(s) |
| 4. Content | Partial | 173 words |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Partial | 6 of 13 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: none; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /for-amazon-brands/

Score 6.0 of 11. Title: "For Amazon Brands - Albert Scott". 173 body words. Inbound links: 0. Screenshots: `for-amazon-brands--desktop-1440x900.jpg`, `for-amazon-brands--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "For Amazon Brands - Albert Scott" (32 chars) |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Partial | 2 level skip(s) |
| 4. Content | Partial | 173 words |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Partial | 6 of 13 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: none; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /retail-management/

Score 6.0 of 11. Title: "Retail Management - Albert Scott". 125 body words. Inbound links: 1. Screenshots: `retail-management--desktop-1440x900.jpg`, `retail-management--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "Retail Management - Albert Scott" (32 chars) |
| 2. Meta description | Partial | 49 chars: "Operations, software and logistics, fully Amazon...." |
| 3. H1 and hierarchy | Partial | 1 level skip(s) |
| 4. Content | Fail | 125 words of body copy |
| 5. Internal links | Partial | 1 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 13 of 14 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Book Appt; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "Our Retail Division is the driving force behind a brand’s Amazon success  -  overseeing every operatio" |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /portfolio/

Score 5.5 of 11. Title: "Portfolio - Albert Scott". 70 body words. Inbound links: 2. Screenshots: `portfolio--desktop-1440x900.jpg`, `portfolio--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Portfolio - Albert Scott" (24 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 144 chars: "Discover Albert Scott’s Amazon portfolio - transforming brands with powerful storefronts, A+..." |
| 3. H1 and hierarchy | Partial | 1 level skip(s) |
| 4. Content | Fail | 70 words of body copy |
| 5. Internal links | Pass | 23 body links out, 2 inbound |
| 6. Image alt text | Fail | 28 of 28 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /hero/

Score 5.5 of 11. Title: "Hero - Albert Scott". 40 body words. Inbound links: 0. Screenshots: `hero--desktop-1440x900.jpg`, `hero--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Hero - Albert Scott" (19 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Pass | One H1 "Dominate Amazon with expert support", 3 body headings in order |
| 4. Content | Fail | 40 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Partial | 4 of 9 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Or Directly Schedule a Meeting Now; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /amazon-management-agency/

Score 5.5 of 11. Title: "FULL SERVICE AMAZON GROWTH AGENCY - Albert Scott". 314 body words. Inbound links: 0. Screenshots: `amazon-management-agency--desktop-1440x900.jpg`, `amazon-management-agency--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Pass | "FULL SERVICE AMAZON GROWTH AGENCY - Albert Scott" (48 chars) |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Partial | 314 words; raw shortcode text visible, placeholder or sample text |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Partial | 5 of 28 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Schedule A Meeting Now; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /sample-page/

Score 5.5 of 11. Title: "Sample Page - Albert Scott". 233 body words. Inbound links: 0. Screenshots: `sample-page--desktop-1440x900.jpg`, `sample-page--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Sample Page - Albert Scott" (26 chars): no descriptive term a buyer would search |
| 2. Meta description | Partial | 300 chars: "This is an example page. It's different from a blog post because it will stay in one place..." |
| 3. H1 and hierarchy | Partial | H1 "Sample Page" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 233 words; placeholder or sample text |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no FAQ or Q&A section. Opening: "This is an example page. It’s different from a blog post because it will stay in one place and will " |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /marketing-division-2/

Score 5.0 of 11. Title: "Marketing Division - Albert Scott". 301 body words. Inbound links: 0. Screenshots: `marketing-division-2--desktop-1440x900.jpg`, `marketing-division-2--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Marketing Division - Albert Scott" (33 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 134 chars: "Drive sales with Albert Scott’s marketing division using Amazon SEO, PPC, and creative str..." |
| 3. H1 and hierarchy | Fail | 1 heading(s) before the H1 (H3); H1 "Marketing Division" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 301 words |
| 5. Internal links | Partial | 1 link(s) to redirecting or broken URLs: /case-studies-2/; 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 44 of 44 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /university/

Score 5.0 of 11. Title: "University - Albert Scott". 148 body words. Inbound links: 0. Screenshots: `university--desktop-1440x900.jpg`, `university--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "University - Albert Scott" (25 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 112 chars: "Access Albert Scott University for expert Amazon resources, guides, and strategies to grow..." |
| 3. H1 and hierarchy | Partial | H1 "University" carries no descriptive term |
| 4. Content | Fail | 148 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Book Appt; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /lets-talk/

Score 5.0 of 11. Title: "Let’s Talk - Albert Scott". 50 body words. Inbound links: 11. Screenshots: `lets-talk--desktop-1440x900.jpg`, `lets-talk--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Let’s Talk - Albert Scott" (25 chars): no descriptive term a buyer would search |
| 2. Meta description | Pass | 147 chars: "Let’s grab some time to chat - whether you're curious about boosting Amazon performance or s..." |
| 3. H1 and hierarchy | Fail | 5 heading(s) before the H1 (H2, H4, H4, H4, H2); H1 "Fill out this form to find out more" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 50 words of body copy |
| 5. Internal links | Pass | 1 body links out, 11 inbound |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Schedule a chat; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /test-modules/

Score 4.5 of 11. Title: "test-modules - Albert Scott". 432 body words. Inbound links: 0. Screenshots: `test-modules--desktop-1440x900.jpg`, `test-modules--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "test-modules - Albert Scott" (27 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Pass | 432 words, 5 paragraphs |
| 5. Internal links | Partial | 2 link(s) to redirecting or broken URLs: /privacy-policy-2/, /marketing-management/; 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 9 of 10 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact, Get My Free Audit, Get a Free Amazon Audit; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | horizontal overflow at 390px; no og:image |

#### /our-management/

Score 4.5 of 11. Title: "Our Management - Albert Scott". 487 body words. Inbound links: 0. Screenshots: `our-management--desktop-1440x900.jpg`, `our-management--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Our Management - Albert Scott" (29 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Our Management" carries no descriptive term |
| 4. Content | Partial | 487 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /our-service/

Score 4.5 of 11. Title: "Our Service - Albert Scott". 286 body words. Inbound links: 0. Screenshots: `our-service--desktop-1440x900.jpg`, `our-service--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Our Service - Albert Scott" (26 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Our Service" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 286 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /overview/

Score 4.5 of 11. Title: "OVERVIEW - Albert Scott". 375 body words. Inbound links: 0. Screenshots: `overview--desktop-1440x900.jpg`, `overview--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "OVERVIEW - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "OVERVIEW" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 375 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | horizontal overflow at 390px; horizontal overflow at 1440px; no og:image |

#### /additional-services/

Score 4.5 of 11. Title: "Additional Services - Albert Scott". 243 body words. Inbound links: 0. Screenshots: `additional-services--desktop-1440x900.jpg`, `additional-services--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Additional Services - Albert Scott" (34 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Additional Services" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 243 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /videos/

Score 4.5 of 11. Title: "Videos - Albert Scott". 489 body words. Inbound links: 0. Screenshots: `videos--desktop-1440x900.jpg`, `videos--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Videos - Albert Scott" (21 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Videos" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 489 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | horizontal overflow at 390px; horizontal overflow at 1440px; no og:image |

#### /niftyone-custom-portal/

Score 4.5 of 11. Title: "NiftyOne Custom Portal - Albert Scott". 276 body words. Inbound links: 0. Screenshots: `niftyone-custom-portal--desktop-1440x900.jpg`, `niftyone-custom-portal--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "NiftyOne Custom Portal - Albert Scott" (37 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "NiftyOne Custom Portal" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 276 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /recent-success/

Score 4.5 of 11. Title: "Recent Success - Albert Scott". 165 body words. Inbound links: 0. Screenshots: `recent-success--desktop-1440x900.jpg`, `recent-success--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Recent Success - Albert Scott" (29 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Recent Success" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 165 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /our-world-wide-team/

Score 4.5 of 11. Title: "Our World-Wide Team - Albert Scott". 173 body words. Inbound links: 0. Screenshots: `our-world-wide-team--desktop-1440x900.jpg`, `our-world-wide-team--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Our World-Wide Team - Albert Scott" (34 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Our World-Wide Team" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 173 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /our-story/

Score 4.5 of 11. Title: "Our Story - Albert Scott". 450 body words. Inbound links: 0. Screenshots: `our-story--desktop-1440x900.jpg`, `our-story--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Our Story - Albert Scott" (24 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Our Story" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 450 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /our-team/

Score 4.5 of 11. Title: "Our Team - Albert Scott". 176 body words. Inbound links: 0. Screenshots: `our-team--desktop-1440x900.jpg`, `our-team--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Our Team - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Our Team" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 176 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | horizontal overflow at 390px; no og:image |

#### /test-page/

Score 4.0 of 11. Title: "test page - Albert Scott". 188 body words. Inbound links: 0. Screenshots: `test-page--desktop-1440x900.jpg`, `test-page--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "test page - Albert Scott" (24 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Partial | 188 words |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /amazon-growth-audit/

Score 4.0 of 11. Title: "Form Ads - Albert Scott". 336 body words. Inbound links: 0. Screenshots: `amazon-growth-audit--desktop-1440x900.jpg`, `amazon-growth-audit--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Form Ads - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1; 1 level skip(s) |
| 4. Content | Partial | 336 words |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 7 of 7 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: none; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /form-ads-test/

Score 3.5 of 11. Title: "Form Ads – TEST - Albert Scott". 4 body words. Inbound links: 0. Screenshots: `form-ads-test--desktop-1440x900.jpg`, `form-ads-test--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Form Ads – TEST - Albert Scott" (30 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Fail | 4 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Partial | 1 of 21 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Fail | no CTA text or form found |
| 10. GEO readability | Fail | no substantive opening paragraph; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /our-location/

Score 3.5 of 11. Title: "Our Location - Albert Scott". 120 body words. Inbound links: 0. Screenshots: `our-location--desktop-1440x900.jpg`, `our-location--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Our Location - Albert Scott" (27 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Fail | 120 words of body copy; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /amazon-growth-audit-v2/

Score 3.0 of 11. Title: "Form Ads v2 - Albert Scott". 0 body words. Inbound links: 0. Screenshots: `amazon-growth-audit-v2--desktop-1440x900.jpg`, `amazon-growth-audit-v2--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Form Ads v2 - Albert Scott" (26 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Fail | 0 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 1 of 1 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Pass | self canonical |
| 9. Conversion path | Fail | no CTA text or form found |
| 10. GEO readability | Fail | no substantive opening paragraph; no meta description for answer engines to quote; no FAQ or Q&A section |
| 11. Cannibalization | Pass | no other crawled page shares this title (topic overlap noted in the roadmap where it exists) |
| 12. Other | Note | no og:image |

#### /thank-you/

Score 3.0 of 11. Title: "Thank you - Albert Scott". 78 body words. Inbound links: 0. Screenshots: `thank-you--desktop-1440x900.jpg`, `thank-you--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Thank you - Albert Scott" (24 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Partial | H1 "Thank you" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 78 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Partial | self canonical; shares title with /thankyou/ |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Fail | duplicate title with /thankyou/ |
| 12. Other | Note | no og:image |

#### /services-2/

Score 3.0 of 11. Title: "Services - Albert Scott". 77 body words. Inbound links: 0. Screenshots: `services-2--desktop-1440x900.jpg`, `services-2--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Services - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Partial | H1 "Services" carries no descriptive term; 1 level skip(s) |
| 4. Content | Fail | 77 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Partial | self canonical; shares title with /services/ |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Fail | duplicate title with /services/ |
| 12. Other | Note | no og:image |

#### /services/

Score 3.0 of 11. Title: "Services - Albert Scott". 211 body words. Inbound links: 0. Screenshots: `services--desktop-1440x900.jpg`, `services--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Services - Albert Scott" (23 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | Meta description contains raw shortcode: "[vc_row css_animation="" row_type="row" use_row_as_full_screen_section..." |
| 3. H1 and hierarchy | Partial | H1 "Services" carries no descriptive term; 1 level skip(s) |
| 4. Content | Partial | 211 words; raw shortcode text visible |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Partial | self canonical; shares title with /services-2/ |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 1; CTA visible in mobile first screen: False |
| 10. GEO readability | Fail | opening paragraph does not state what the page or company is; no FAQ or Q&A section |
| 11. Cannibalization | Fail | duplicate title with /services-2/ |
| 12. Other | Note | horizontal overflow at 390px; horizontal overflow at 1440px; no og:image |

#### /thankyou/

Score 2.5 of 11. Title: "Thank You - Albert Scott". 0 body words. Inbound links: 0. Screenshots: `thankyou--desktop-1440x900.jpg`, `thankyou--mobile-390x844.jpg`.

| Point | Result | Evidence |
|---|---|---|
| 1. Title | Fail | "Thank You - Albert Scott" (24 chars): no descriptive term a buyer would search |
| 2. Meta description | Fail | No meta description |
| 3. H1 and hierarchy | Fail | no H1 |
| 4. Content | Fail | 0 words of body copy |
| 5. Internal links | Partial | 0 inbound internal link(s) from crawled pages |
| 6. Image alt text | Fail | 4 of 4 images have empty alt |
| 7. Schema | Partial | BreadcrumbList, ListItem, Organization, QuantitativeValue, WebPage, WebSite, Organization+ProfessionalService, PostalAddress, OfferCatalog, Offer, Service, ContactPoint; two conflicting Organization nodes sitewide |
| 8. Canonical | Partial | self canonical; shares title with /thank-you/ |
| 9. Conversion path | Partial | CTAs: Contact; form(s): 0; CTA visible in mobile first screen: False |
| 10. GEO readability | Partial | no meta description for answer engines to quote; no FAQ or Q&A section. Opening: "Albert Scott is a complete marketplace account-management partner for brands selling on Amazon." |
| 11. Cannibalization | Fail | duplicate title with /thank-you/ |
| 12. Other | Note | no og:image |

## Part E. Search baseline

WebSearch tool. Positions are the order the tool returned results, not a Google rank tracker. Result counts per query vary from 5 to 10.

| Group | Query | albertscott.com position | Top five as returned | What wins |
|---|---|---|---|---|
| core | full service Amazon agency | absent | myamazonguy.com; canopymanagement.com (best-full-service listicle); harvestgroup.com/amazon/; canopymanagement.com; salesduo.com | Agency homepages and service pages with the phrase in the title (7 of 10); two listicles |
| core | Amazon agency | absent | myamazonguy.com; harvestgroup.com/amazon/; canopymanagement.com (top 10 advertising listicle); novadata.io (best agencies directory); goamify.com | Agency homepages (3) and listicles or directories (3) |
| core | best Amazon agencies | absent | supplykick.com (blog listicle); canopymanagement.com (listicle); thriveagency.com (listicle); clutch.co (directory); novadata.io (directory) | Listicles and directories, 6 of 6; three are agency-owned |
| core | Amazon management agency | absent | darkroomagency.com/services/amazon; palmettodigitalmarketinggroup.com; salesduo.com/full-service-amazon-agency/; salesduo.com (account management agencies listicle); i2oretail.com (listicle) | Half service pages, half listicles. Albert Scott has a page at /amazon-management-agency/ that did not appear. |
| core | Amazon growth agency | absent | newswire.com (Amazon Growth Lab press release); myamazonguy.com; bebolddigital.com; salesduo.com (growth agencies listicle); spectrumbpo.com/amazon-agency/ | Agency homepages whose title contains 'Amazon growth agency' (4), one listicle, one press release. Albert Scott's meta description uses this phrase but its title does not. |
| core | Amazon marketing agency | absent | designrush.com (directory); thriveagency.com (service page); clutch.co (directory); coalitiontechnologies.com; coolnerdsmarketing.com (listicle) | Directories and listicles (5) over service pages (4) |
| service | Amazon advertising agency | absent | inbeat.agency (listicle); within.co (listicle); darkroomagency.com/services/amazon; canopymanagement.com (listicle); aihello.com (listicle) | Listicles (4) and dedicated advertising service pages (3). Maps to /marketing-devision/. |
| service | Amazon PPC management agency | absent | 1digitalagency.com/amazon-ppc-management/; smash.vc (listicle); amazowl.com/amazon-ppc-management/; clearadsagency.com; triviumco.com/services/amazon-ppc-management/ | Dedicated PPC service pages with the phrase in the URL (5 of 7). Albert Scott has no PPC-specific page. |
| service | Amazon DSP agency | absent | nuancedmedia.com/amazon-dsp-agency/; thriveagency.com (DSP service page); smartscout.com (top 10 listicle); data4amazon.com (DSP page); sellerapp.com (DSP page) | Dedicated DSP service pages (5 of 7). Albert Scott has /dsp/ (title 'DSP - Albert Scott', no meta description) which did not appear. |
| service | Amazon listing optimization agency | absent | netpeak.us (service page); eva.guru (guide); salesduo.com (listicle); spectrumbpo.com (service page); i2oretail.com (listicle) | Service pages with the phrase in the title and listicles. Maps to /listing-division/. |
| service | Amazon Vendor Central management agency | absent | data4amazon.com; team4ecom.com; sellermetrics.app; salesduo.com (comparison listicle); amzdudes.com | Dedicated Vendor Central service pages (5 of 7). Maps to /retail-division/, whose title does not contain 'Vendor Central'. |
| service | Amazon 1P vendor agency | absent | myamazonguy.com (vendor services page); data4amazon.com; forceget.com (explainer); sellermetrics.app; cpg.io | Vendor Central service pages and explainers |
| service | Amazon FBA logistics services agency | absent | logisticsplus.com; freightright.com; wise.com (guide); unicargo.com; valleydl.com | 3PL and freight forwarders, not agencies. Maps loosely to /logistics-division/. This query attracts a different buyer; Stage 3 should reframe the logistics angle around 'Amazon agency with logistics' rather than compete with 3PLs. |
| service | Amazon A+ content agency | absent | themediacaptain.com; data4amazon.com; ironcreative.com; salesduo.com (listicle); fndecommerce.com | Dedicated A+ content service pages (5 of 6). Albert Scott has no A+ content page; it is a bullet inside the listing division. |
| local | Amazon agency New York | absent | salesduo.com/amazon-agency/new-york/; ecomranker.com (NYC listicle); growithamazon.com/amazon-agency-new-york/; sermondo.com (NY listicle); amzoptimized.com | City landing pages built for the query (3) and city listicles (3). Albert Scott is in Inwood NY with a /our-location/ page that did not appear. |
| brand | Albert Scott Amazon agency | 8 | zoominfo.com (employee directory); zoominfo.com (company overview); linkedin.com/company/albert-scott-llc; finance.yahoo.com (2024 press release); nombase.com | Third-party profiles and press releases outrank the site for its own name |
| brand | Albert Scott LLC Amazon Inwood NY | absent | finance.yahoo.com; zoominfo.com; linkedin.com; nombase.com; prnewswire.com | albertscott.com absent entirely; data brokers and press release syndication fill the page |
| brand | Who is Albert Scott the Amazon agency? | 8 | zoominfo.com; zoominfo.com; linkedin.com; finance.yahoo.com; nombase.com | Same pattern as the brand query; the tool's summary described Albert Scott accurately using press release language |
| index | site:albertscott.com | absent | wikipedia (noise); wikipedia (noise); wikipedia (noise); albertscott.com/clients/; albertscott.com/ | Of 7 site URLs returned, 4 are legacy or thin pages (/clients/, /our-location/, /amazon-management-agency/, /our-service/) and 1 is a dead URL (/marketing-management/). Only the homepage and /newsroom/ are current primary pages. |
| geo | What are the best full-service Amazon agencies for mid-size brands? | absent | canopymanagement.com (listicle); scoop.market.us (listicle); amzdudes.com (listicle); salesduo.com (listicle); amazongrowthlab.com (listicle) | Listicles 7 of 7. Tool summary named Canopy, Nuanced Media, My Amazon Guy, SalesDuo, SupplyKick. Albert Scott not named. |
| geo | Which Amazon agencies handle both Vendor Central and Seller Central? | absent | myamazonguy.com (hybrid explainer); sarasanalytics.com; sellercentral.amazon.com forum; team4ecom.com; salesduo.com (listicle) | Explainers and listicles. The tool summary named Albert Scott as one of five agencies: 'one of the most established Vendor Central agencies, with their service model explicitly covering both 1P and 3P, and their engagements structured around four models'. This is the only GEO-style prompt where Albert Scott was named. Source appears to be a third-party listicle, not albertscott.com. |
| geo | Amazon agency that also manages logistics and retail operations | absent | supplykick.com (blog); frontrowgroup.com (logistics service page); sprintzeal.com; supplykick.com (supply chain page); supplykick.com (blog) | SupplyKick owns this angle with three URLs. Albert Scott's four-division model (Listing, Marketing, Retail, Logistics) is a direct fit and did not appear. |
| geo | Compare Albert Scott with My Amazon Guy and Canopy Management | 5 | myamazonguy.com (vs Canopy page); riverjournalonline.com; salesduo.com (alternatives post); withalfi.com (Canopy review); albertscott.com | Competitors publish 'vs' and 'alternatives' pages. Albert Scott has none. Tool summary described Albert Scott using homepage copy and named the CEO David Greenblatt. |

Albert Scott appeared in 3 of 24 queries, all brand or comparison queries containing its own name (positions 8, 8, 5). It did not appear for any commercial, service, local or GEO query.

## Part F. Competitor pages captured

Rendered in headless Chromium on 2026-09-03. Full table in `../config/competitors.md`.

| Page | Title | H1 | Words | Schema beyond Organization | FAQ | Pricing | Case studies | sameAs | Images with alt |
|---|---|---|---|---|---|---|---|---|---|
| myamazonguy.com/ | My Amazon Guy: Full-Service Amazon Growth Agency | The Amazon agency that gets your products seen and sold | 4027 | ContactPoint, SearchAction, contactPoint, Brand | True | False | True | 3 | 85 of 86 |
| canopymanagement.com/ | Full Service Amazon Agency / Canopy Management | Your Biggest Months on Amazon, Walmart, and Shopify… are Just a Click Away | 6212 | ReadAction, BreadcrumbList, SearchAction, EntryPoint, PropertyValueSpecification | False | False | True | 0 | 197 of 219 |
| harvestgroup.com/amazon/ | Harvest Group: Full-Service Amazon Agency / Amazon Ad Partner | Amazon | 5739 | Place, PostalAddress, ProfessionalService+Organization, Person, Article | False | False | True | 0 | 96 of 101 |
| salesduo.com/ | Full-Service Amazon Agency & Advertising Partner / SalesDuo | Full-Service Amazon Marketing, Sales & Advertising Agency | 14821 | BreadcrumbList, Service, FAQPage, Question, Answer, AggregateRating | True | True | True | 0 | 359 of 376 |
| www.darkroomagency.com/services/amazon | Amazon Advertising Agency for Ecommerce Brands / Darkroom | Unlock growth with a top Amazon marketing agency | 1438 | ContactPoint, FAQPage, Question, Answer | False | True | True | 3 | 0 of 8 |
| nuancedmedia.com/ | Amazon Marketing & Intelligence Agency / Nuanced Media | We read your Amazon market.Then help you win it. | 2393 |  | False | True | False | 3 | 38 of 58 |
| www.amazongrowthlab.com/ | Amazon Growth Lab / Amazon Marketing Agency | Your Full-Service Amazon Agency | 7870 | Organization+LocalBusiness, PostalAddress, GeoCoordinates, ContactPoint, Person, Quantitat | True | True | True | 4 | 108 of 108 |
| goamify.com/ | Amazon Agency / Leading Amazon Marketing Agency for Brands | Maximize Your Growth With Our Premier Amazon Agency | 1855 | ReadAction, BreadcrumbList, SearchAction, EntryPoint, PropertyValueSpecification | False | True | True | 4 | 19 of 23 |
| salesduo.com/full-service-amazon-agency/ | Full-Service Amazon Account Management Agency / SalesDuo | Amazon Account Management Agency for Profitable, Predictable, Hands-Off eCommerc | 11554 | ProfessionalService, PostalAddress, AggregateRating, Service | True | True | True | 0 | 266 of 275 |
| salesduo.com/amazon-agency/new-york/ | SalesDuo  -  Full Service Amazon Agency in New York | Finally, An Amazon Agency in New York that Delivers Real Results!; Get in Touch | 11194 |  | True | True | True | 0 | 261 of 263 |

## Part G. GEO observations

- Five GEO-style prompts were run through WebSearch (the only allowed surface). Albert Scott was named once, for the Vendor Central plus Seller Central prompt, and the source was a withalfi.com listicle quoting the retail division page, not albertscott.com itself. Details in `../config/geo-watchlist.md`.
- The entity signals on the site conflict: three different one-line descriptions (tagline "E-commerce Management", schema slogan "Amazon. Expertise. Delivered.", meta "full-service Amazon growth agency") and two Organization nodes with different employee counts and no sameAs to LinkedIn or the press coverage that currently outranks the site for its own name.
- Third-party lists that answer engines draw from (Nova, Sermondo, Clutch, Canopy, Ecomranker) do not list Albert Scott. Only withalfi.com does.
- The strongest GEO asset on the site is the four-model explanation on the homepage (Vendor Central, Seller Central, hybrid, distributor) and the Forbes Business Council articles linked from /newsroom/. Neither is marked up or linked from the division pages.

## Verification re-run, 2026-09-03 17:47 UTC

The full Stage 1 crawl, grading, link-status check and 24-query baseline were run a second time the same day to confirm the system is repeatable.

| Check | Run 1 | Run 2 | Difference |
|---|---|---|---|
| Pages crawled, all HTTP 200 | 86 | 86 | none |
| Average score (of 11) | 5.48 | 5.48 | none |
| Pages whose score changed | | | 0 |
| Page facts changed (status, title, meta, canonical, robots, H1, images, alt, schema, overflow, CTA, og:image; word and link counts within tolerance) | | | 0 |
| Internal link targets checked | 142 | 142 | 0 status changes |
| albertscott.com in returned results | 3 of 24 | 3 of 24 | same queries, same positions (8, 8, 5) |
| GEO prompt naming Albert Scott | 1 of 5 | 1 of 5 | same prompt, same wording |

Search result reshuffles between runs, both minor: "Amazon growth agency" dropped the newswire.com press release and added 10xcommerceco.com; "Amazon agency that also manages logistics and retail operations" returned aboutamazon.com first and wearemelody.com instead of two of the supplykick.com URLs. Every other query returned the same domains in the same order. Screenshots from run 2 were not committed because they duplicate run 1.
