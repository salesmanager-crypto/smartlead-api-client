# Issue tracker

One line per issue. Tick the box when the fix is live and verified on the page. Same rows as `issue-tracker.csv` (open that in Excel or Google Sheets) and `issue-tracker.xlsx`. Priority: P1 configuration and quick copy, P2 page work, P3 cleanup. Roadmap ref points to `../roadmap/roadmap-2026-09-03.md` or the growth plan; "new" means found while building this tracker. Built 2026-09-03 from the Stage 1 evidence.


## General

- [ ] **AS-001 Duplicate company schema** (P1, site-wide)  
  What is happening: Every page carries two separate Organization blocks in JSON-LD. The AIOSEO one says the company is "E-commerce Management" with 5 to 10 employees. The custom one says ProfessionalService, 30 employees, with address, phone and a service catalog. They use different IDs so search and AI engines see two conflicting companies.  
  Fix: Keep one Organization block (the custom one has the useful detail). Set one employee count and one description that matches the homepage meta description. Turn off the AIOSEO Organization output or make the custom block the only source.  
  Ref: R15
- [ ] **AS-002 No sameAs links in schema** (P1, site-wide)  
  What is happening: The Organization schema does not link to any other profile (LinkedIn, Forbes author page, press). Engines cannot confirm that the LinkedIn page and the press releases that outrank the site are the same company.  
  Fix: Add sameAs to the single Organization block: LinkedIn company page URL and the Forbes Business Council author URL already linked from /newsroom/.  
  Ref: R15
- [ ] **AS-003 No og:image on any page** (P1, site-wide)  
  What is happening: 86 of 86 pages have no og:image tag. When a page is shared in chat, social or shown as an AI citation, no preview image is available.  
  Fix: Set a default social image in AIOSEO (Social Networks settings) and a specific image for the homepage and division pages.  
  Ref: R17
- [ ] **AS-004 Company described three different ways** (P1, site-wide)  
  What is happening: Tagline says "E-commerce Management", schema slogan says "Amazon. Expertise. Delivered.", homepage meta says "full-service Amazon growth agency". Engines trying to answer "what is Albert Scott" get three answers.  
  Fix: Pick one description and use it in the WordPress tagline, the schema description, the homepage meta description and the About page opening.  
  Ref: G1
- [ ] **AS-005 Junk archive pages are indexable and in the sitemap** (P1, site-wide)  
  What is happening: 7 category archives, 2 tag archives, 10 project_category archives and the /project/ archive are listed in the sitemap and return 200 with no noindex. Each holds 1 to 3 items. They dilute the index with near-empty pages.  
  Fix: In AIOSEO: set categories, tags and project_category to noindex and exclude them from the sitemap. Redirect /project/ to /listings-portfolio-gallery/.  
  Ref: R4
- [ ] **AS-006 Author archives are indexable** (P1, site-wide)  
  What is happening: /blog/author/albertllc/ and /blog/author/hannah-kaufman/ return 200 and are indexable. The REST API also exposes two more accounts (7121525_u8r6t1, hashsalacop) with author URLs.  
  Fix: Set author archives to noindex in AIOSEO. Ask the site admin to confirm the two unfamiliar accounts are legitimate.  
  Ref: R4
- [ ] **AS-007 /blog/ returns 404** (P1, site-wide)  
  What is happening: All 13 posts live under /blog/ but /blog/ itself is a 404. There is no blog index page, so once category archives are noindexed the posts lose their crawl path.  
  Fix: Create a blog index at /blog/ listing all articles, or 301 /blog/ to /newsroom/ and list the articles there.  
  Ref: R19
- [ ] **AS-008 Dead URLs still indexed or linked** (P1, site-wide)  
  What is happening: /marketing-management/ is a 404 but still appears for a site: search. /privacy-policy-2/ is a 404 linked from /test-modules/.  
  Fix: 301 /marketing-management/ to the marketing division page. 301 /privacy-policy-2/ to /privacy-policy/.  
  Ref: R5
- [ ] **AS-009 Redirect links in navigation blocks** (P1, site-wide)  
  What is happening: The homepage divisions section links /listing-division-2/, /marketing-division/ and /logistics-division-2/, which all 301. Four pages link /case-studies-2/, which 301s to /case-studies/. The homepage reaches its own service pages only through redirects.  
  Fix: Edit the homepage divisions block and the case study CTAs to point at the live URLs.  
  Ref: R2

## Homepage

- [ ] **AS-010 Homepage stats not in the HTML** (P1, /)  
  What is happening: The five metrics (30+ Marketplace Experts, 90+ Client Retention, 10+ Years, 100M+ Managed Revenue, 50+ Clients) are Divi number counters. The values live only in a data-number-value attribute and are written into the page by JavaScript after load. In the raw HTML that crawlers and answer engines read, the number text is empty.  
  Fix: Replace the counter modules with plain text modules that contain the number, or add the same figures as a sentence in the body copy ("30+ marketplace experts, 90%+ client retention...") so they exist without JavaScript.  
  Ref: new

## General

- [ ] **AS-011 Image alt text missing site-wide** (P2, site-wide)  
  What is happening: 1,504 of 1,601 images have alt="". 63 pages have no alt on any image. Client logos, portfolio work, icons and the site logo are all unlabeled, so none of the portfolio work is visible to image search or screen readers.  
  Fix: Add alt text in the Media Library for every image, starting with the homepage, the four division pages, /dsp/, /case-studies/ and the portfolio gallery. Pattern: client logos "[Brand] logo"; portfolio "[Brand] Amazon A+ module designed by Albert Scott".  
  Ref: R10
- [ ] **AS-012 32 test, legacy and duplicate pages are live** (P2, site-wide)  
  What is happening: A third of the indexable site is old homepages, 2019-era service pages showing raw [vc_row] shortcode, test pages, form tests and duplicate thank-you and services pages. 33 pages have no internal links pointing to them at all.  
  Fix: Redirect or delete each page per the disposition list (rows below marked Triage).  
  Ref: R1
- [ ] **AS-013 No FAQ schema anywhere** (P2, site-wide)  
  What is happening: No page has FAQPage schema even where FAQ text exists (/dsp/, /albert-scott-university/). Competitor service pages (SalesDuo, Darkroom, Amazon Growth Lab) carry FAQPage and Service schema.  
  Fix: Add FAQPage schema to existing FAQs via AIOSEO schema settings; add Service schema on each division page; add Article schema on case study pages.  
  Ref: R16
- [ ] **AS-014 Em dashes in body copy** (P3, site-wide)  
  What is happening: 83 em dashes across 18 pages. House style rule: no em dashes.  
  Fix: Replace with a comma, period or colon as each page is rewritten.  
  Ref: R14
- [ ] **AS-015 WordPress and plugin versions exposed** (P3, site-wide)  
  What is happening: Meta generator tags reveal WordPress 7.1, AIOSEO Pro 5.0.1 and Site Kit 1.186.0.  
  Fix: Remove generator tags (a one-line function in the theme or a security plugin setting). Low SEO impact, hygiene only.  
  Ref: new
- [ ] **AS-016 Cookie banner covers the mobile CTA area** (P3, site-wide)  
  What is happening: On a 390px screen the cookie banner covers roughly the bottom fifth of the viewport until accepted.  
  Fix: Reduce banner height on mobile or move it to a compact top bar.  
  Ref: new

## Homepage

- [ ] **AS-017 Title does not say what the page is** (P1, /)  
  What is happening: Current title tag: "Home - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Full-Service Amazon Agency for Vendor and Seller Central Brands: Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-018 Testimonials and names set as headings** (P2, /)  
  What is happening: Customer quotes and attributions are rendered as H2, H3 and H4 tags (on the homepage the same three names appear as H4 nine times because the carousel clones them).  
  Fix: Use blockquote and paragraph tags for testimonials; keep headings for section titles.  
  Ref: R9
- [ ] **AS-019 Images without alt text** (P2, /)  
  What is happening: 236 of 236 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-020 Links to redirecting or dead URLs** (P1, /)  
  What is happening: Links target: /listing-division-2/, /logistics-division-2/, /case-studies-2/, /marketing-division/.  
  Fix: Point each link at the live URL.  
  Ref: R2
- [ ] **AS-021 Competes with old copies of itself** (P1, /)  
  What is happening: /home/ (old homepage, title "Albert Scott - A Full Service Amazon Agency"), /amazon-management-agency/ ("FULL SERVICE AMAZON GROWTH AGENCY"), /for-amazon-brands/ and /for-amazon-brandsv2/ are all live and indexable with the same positioning.  
  Fix: Redirect /home/ to /. Rebuild /amazon-management-agency/ as a distinct account management page or redirect it. Noindex the ad landing pages.  
  Ref: R1
- [ ] **AS-022 Four engagement models are not quotable** (P2, /)  
  What is happening: The homepage explains Vendor Central, Seller Central, hybrid and distributor models across several sections. The one AI answer that named Albert Scott quoted a third-party summary of this, not the site.  
  Fix: Write the four models as one short paragraph near the top of the page and repeat it on /retail-division/. Add it to the About page.  
  Ref: G2

## About page

- [ ] **AS-023 Title does not say what the page is** (P1, /about-us/)  
  What is happening: Current title tag: "About Us - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "About Albert Scott, Amazon Agency in Inwood, New York". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-024 No H1** (P2, /about-us/)  
  What is happening: The page has no H1 heading, so the main topic is not declared to crawlers.  
  Fix: Set the page headline as an H1 (About: "About Albert Scott"; Contact: "Contact Albert Scott"; Gallery: "Amazon Listing and A+ Content Portfolio").  
  Ref: R9
- [ ] **AS-025 Images without alt text** (P2, /about-us/)  
  What is happening: 93 of 93 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-026 Body copy links to almost nothing** (P2, /about-us/)  
  What is happening: 2 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-027 No call to action in the first mobile screen** (P2, /about-us/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-028 Horizontal scroll on mobile** (P2, /about-us/)  
  What is happening: Rendered at 390px the page is wider than the screen, so it scrolls sideways.  
  Fix: Find the element wider than the viewport (usually a fixed-width image, table or gallery row) and set max-width 100%.  
  Ref: R6
- [ ] **AS-029 Horizontal scroll on desktop** (P2, /about-us/)  
  What is happening: Rendered at 1440px the page is wider than the viewport.  
  Fix: Same fix as mobile: constrain the overflowing element.  
  Ref: R6

## Listing division page

- [ ] **AS-030 Heading before the H1** (P2, /listing-division/)  
  What is happening: "Albert Scott Divisions" is an H3 placed above the H1 "Listing Division". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-031 Service page is short** (P2, /listing-division/)  
  What is happening: About 451 words. The DSP page (1,396 words) shows the depth the division pages need.  
  Fix: Expand to at least 900 words: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-032 Images without alt text** (P2, /listing-division/)  
  What is happening: 19 of 21 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-033 Body copy links to almost nothing** (P2, /listing-division/)  
  What is happening: 2 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-034 No call to action in the first mobile screen** (P2, /listing-division/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## Marketing division page

- [ ] **AS-035 Title does not say what the page is** (P1, /marketing-devision/)  
  What is happening: Current title tag: "Marketing Devision - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Amazon Advertising Agency: Sponsored Ads and DSP Managed by Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-036 Slug, title and breadcrumb misspell "Division" as "Devision"** (P1, /marketing-devision/)  
  What is happening: The URL is /marketing-devision/, the title is "Marketing Devision - Albert Scott" and the AIOSEO breadcrumb schema names the page "Marketing Devision". The correctly spelled /marketing-division/ exists only as a redirect to the misspelled page.  
  Fix: Rename the slug to /marketing-division/, let WordPress 301 the old slug, and remove the existing reverse redirect. Fix the SEO title and breadcrumb title at the same time.  
  Ref: R3
- [ ] **AS-037 No meta description** (P1, /marketing-devision/)  
  What is happening: The page has no meta description, so search results and answer engines pick their own snippet from the page.  
  Fix: Write a 120 to 155 character description in AIOSEO stating what the page offers and for whom, using claims already on the page.  
  Ref: R8
- [ ] **AS-038 Heading before the H1** (P2, /marketing-devision/)  
  What is happening: "Albert Scott Divisions" is an H3 placed above the H1 "Marketing Division". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-039 H1 carries no descriptive term** (P2, /marketing-devision/)  
  What is happening: H1 is "Marketing Division". A slogan or a label, not a statement of the service.  
  Fix: Rewrite the H1 to name the service and the audience, for example "Full-Service Amazon Agency for Vendor and Seller Central Brands", keeping the slogan as a subheading.  
  Ref: R9
- [ ] **AS-040 Testimonials and names set as headings** (P2, /marketing-devision/)  
  What is happening: Customer quotes and attributions are rendered as H2, H3 and H4 tags (on the homepage the same three names appear as H4 nine times because the carousel clones them).  
  Fix: Use blockquote and paragraph tags for testimonials; keep headings for section titles.  
  Ref: R9
- [ ] **AS-041 Images without alt text** (P2, /marketing-devision/)  
  What is happening: 42 of 44 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-042 Links to redirecting or dead URLs** (P1, /marketing-devision/)  
  What is happening: Links target: /case-studies-2/.  
  Fix: Point each link at the live URL.  
  Ref: R2
- [ ] **AS-043 No call to action in the first mobile screen** (P2, /marketing-devision/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-044 Duplicate page /marketing-division-2/ is live** (P1, /marketing-devision/)  
  What is happening: A second marketing division page exists at /marketing-division-2/ with its own title and meta description (405 words), indexable.  
  Fix: 301 /marketing-division-2/ to the marketing division page.  
  Ref: R1

## Retail division page

- [ ] **AS-045 Heading before the H1** (P2, /retail-division/)  
  What is happening: "Albert Scott Divisions" is an H3 placed above the H1 "Retail Division". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-046 Service page is short** (P2, /retail-division/)  
  What is happening: About 378 words. The DSP page (1,396 words) shows the depth the division pages need.  
  Fix: Expand to at least 900 words: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-047 Images without alt text** (P2, /retail-division/)  
  What is happening: 19 of 19 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-048 Body copy links to almost nothing** (P2, /retail-division/)  
  What is happening: 1 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-049 No call to action in the first mobile screen** (P2, /retail-division/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## Logistics division page

- [ ] **AS-050 Heading before the H1** (P2, /logistics-division/)  
  What is happening: "Albert Scott Divisions" is an H3 placed above the H1 "Logistics Division". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-051 Thin content** (P2, /logistics-division/)  
  What is happening: About 336 words of body copy. Competitor service pages that rank run 1,400 to 14,800 words.  
  Fix: Expand to at least 900 words using the /dsp/ page structure: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-052 Images without alt text** (P2, /logistics-division/)  
  What is happening: 10 of 10 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-053 Body copy links to almost nothing** (P2, /logistics-division/)  
  What is happening: 1 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-054 No call to action in the first mobile screen** (P2, /logistics-division/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## DSP page

- [ ] **AS-055 Title does not say what the page is** (P1, /dsp/)  
  What is happening: Current title tag: "DSP - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Amazon DSP Management Agency: Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-056 No meta description** (P1, /dsp/)  
  What is happening: The page has no meta description, so search results and answer engines pick their own snippet from the page.  
  Fix: Write a 120 to 155 character description in AIOSEO stating what the page offers and for whom, using claims already on the page.  
  Ref: R8
- [ ] **AS-057 Images without alt text** (P2, /dsp/)  
  What is happening: 175 of 175 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-058 Almost no internal links point here** (P2, /dsp/)  
  What is happening: 1 inbound link(s) from other pages. The page is reachable mainly via the sitemap.  
  Fix: Link to it from the homepage divisions section, the relevant division page and the related articles.  
  Ref: R18
- [ ] **AS-059 Body copy links to almost nothing** (P2, /dsp/)  
  What is happening: 1 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-060 No call to action in the first mobile screen** (P2, /dsp/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-061 FAQ text has no FAQ schema** (P2, /dsp/)  
  What is happening: The page has a FAQ section but no FAQPage markup.  
  Fix: Add FAQPage schema via AIOSEO for the existing questions.  
  Ref: R16

## Case studies page

- [ ] **AS-062 Title does not say what the page is** (P1, /case-studies/)  
  What is happening: Current title tag: "Case Studies - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Amazon Growth Case Studies: Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-063 Thin content** (P2, /case-studies/)  
  What is happening: About 276 words of body copy. Competitor service pages that rank run 1,400 to 14,800 words.  
  Fix: Expand to at least 900 words using the /dsp/ page structure: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-064 Images without alt text** (P2, /case-studies/)  
  What is happening: 7 of 7 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-065 No call to action in the first mobile screen** (P2, /case-studies/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-066 H1 says "General Case Studies"** (P2, /case-studies/)  
  What is happening: The H1 is a category label; the page holds three case studies and links nine PDFs from other pages.  
  Fix: H1 "Amazon Growth Case Studies". List every case study, including the nine that exist only as PDFs.  
  Ref: G6

## Case study: BeYoutiful

- [ ] **AS-067 Title does not say what the page is** (P1, /case-studies/beyoutiful/)  
  What is happening: Current title tag: "From $0 to $1M+ in Year 1 - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "[Service] for Amazon Brands: Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-068 No meta description** (P1, /case-studies/beyoutiful/)  
  What is happening: The page has no meta description, so search results and answer engines pick their own snippet from the page.  
  Fix: Write a 120 to 155 character description in AIOSEO stating what the page offers and for whom, using claims already on the page.  
  Ref: R8
- [ ] **AS-069 Heading before the H1** (P2, /case-studies/beyoutiful/)  
  What is happening: "CASE STUDY: BEYOUTIFUL" is an H4 placed above the H1 "From $0 to $1M+ in Year 1: Launching a New Skincare Brand on Amazon". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-070 Images without alt text** (P2, /case-studies/beyoutiful/)  
  What is happening: 10 of 13 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-071 Almost no internal links point here** (P2, /case-studies/beyoutiful/)  
  What is happening: 1 inbound link(s) from other pages. The page is reachable mainly via the sitemap.  
  Fix: Link to it from the homepage divisions section, the relevant division page and the related articles.  
  Ref: R18
- [ ] **AS-072 Body copy links to almost nothing** (P2, /case-studies/beyoutiful/)  
  What is happening: 2 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-073 No call to action in the first mobile screen** (P2, /case-studies/beyoutiful/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## Case study: Atlas Olive Oils

- [ ] **AS-074 Title does not say what the page is** (P1, /case-studies/atlas-olive-oils/)  
  What is happening: Current title tag: "Atlas Olive Oils - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "[Service] for Amazon Brands: Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-075 No meta description** (P1, /case-studies/atlas-olive-oils/)  
  What is happening: The page has no meta description, so search results and answer engines pick their own snippet from the page.  
  Fix: Write a 120 to 155 character description in AIOSEO stating what the page offers and for whom, using claims already on the page.  
  Ref: R8
- [ ] **AS-076 Heading before the H1** (P2, /case-studies/atlas-olive-oils/)  
  What is happening: "Case Study: Atlas Olive Oils" is an H4 placed above the H1 "Atlas Olive Oil: The Best Selling Olive Oil on Amazon". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-077 Images without alt text** (P2, /case-studies/atlas-olive-oils/)  
  What is happening: 11 of 13 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-078 Almost no internal links point here** (P2, /case-studies/atlas-olive-oils/)  
  What is happening: 1 inbound link(s) from other pages. The page is reachable mainly via the sitemap.  
  Fix: Link to it from the homepage divisions section, the relevant division page and the related articles.  
  Ref: R18
- [ ] **AS-079 Body copy links to almost nothing** (P2, /case-studies/atlas-olive-oils/)  
  What is happening: 2 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-080 No call to action in the first mobile screen** (P2, /case-studies/atlas-olive-oils/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## Case study: Mouthwatchers

- [ ] **AS-081 Heading before the H1** (P2, /case-studies/mouthwatchers/)  
  What is happening: "Case Study: Mouthwatchers" is an H4 placed above the H1 "Mouthwatchers: Unlocking Growth in a Commodity Category". Eyebrow labels styled as headings break the document outline.  
  Fix: Change the eyebrow label to a paragraph with a CSS class; keep the H1 first.  
  Ref: R9
- [ ] **AS-082 H1 carries no descriptive term** (P2, /case-studies/mouthwatchers/)  
  What is happening: H1 is "Mouthwatchers: Unlocking Growth in a Commodity Category". A slogan or a label, not a statement of the service.  
  Fix: Rewrite the H1 to name the service and the audience, for example "Full-Service Amazon Agency for Vendor and Seller Central Brands", keeping the slogan as a subheading.  
  Ref: R9
- [ ] **AS-083 Images without alt text** (P2, /case-studies/mouthwatchers/)  
  What is happening: 11 of 12 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-084 Almost no internal links point here** (P2, /case-studies/mouthwatchers/)  
  What is happening: 1 inbound link(s) from other pages. The page is reachable mainly via the sitemap.  
  Fix: Link to it from the homepage divisions section, the relevant division page and the related articles.  
  Ref: R18
- [ ] **AS-085 Body copy links to almost nothing** (P2, /case-studies/mouthwatchers/)  
  What is happening: 2 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-086 Page is noindexed** (P2, /case-studies/mouthwatchers/)  
  What is happening: meta robots is "noindex, nofollow" and the page is excluded from the sitemap, yet it has the best title and description of the three case studies. A duplicate blog post /blog/mouthwatchers/ is indexed instead.  
  Fix: Merge /blog/mouthwatchers/ into this page, 301 the post, then remove the noindex.  
  Ref: R12
- [ ] **AS-087 No call to action in the first mobile screen** (P2, /case-studies/mouthwatchers/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## Portfolio gallery page

- [ ] **AS-088 No H1** (P2, /listings-portfolio-gallery/)  
  What is happening: The page has no H1 heading, so the main topic is not declared to crawlers.  
  Fix: Set the page headline as an H1 (About: "About Albert Scott"; Contact: "Contact Albert Scott"; Gallery: "Amazon Listing and A+ Content Portfolio").  
  Ref: R9
- [ ] **AS-089 Thin content** (P2, /listings-portfolio-gallery/)  
  What is happening: About 229 words of body copy. Competitor service pages that rank run 1,400 to 14,800 words.  
  Fix: Expand to at least 900 words using the /dsp/ page structure: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-090 Images without alt text** (P2, /listings-portfolio-gallery/)  
  What is happening: 219 of 219 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-091 Links to redirecting or dead URLs** (P1, /listings-portfolio-gallery/)  
  What is happening: Links target: /case-studies-2/.  
  Fix: Point each link at the live URL.  
  Ref: R2
- [ ] **AS-092 No call to action in the first mobile screen** (P2, /listings-portfolio-gallery/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-093 Horizontal scroll on mobile** (P2, /listings-portfolio-gallery/)  
  What is happening: Rendered at 390px the page is wider than the screen, so it scrolls sideways.  
  Fix: Find the element wider than the viewport (usually a fixed-width image, table or gallery row) and set max-width 100%.  
  Ref: R6
- [ ] **AS-094 Gallery links go to image files** (P2, /listings-portfolio-gallery/)  
  What is happening: 52 body links point at raw .png and .jpg files under /wp-content/uploads/ rather than pages. The work has no captions or text.  
  Fix: Link gallery tiles to project or case study pages with text, or add captions and alt text to each tile.  
  Ref: R13

## Newsroom page

- [ ] **AS-095 Title does not say what the page is** (P1, /newsroom/)  
  What is happening: Current title tag: "Newsroom - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Albert Scott in the News: Forbes and Press Coverage". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-096 H1 carries no descriptive term** (P2, /newsroom/)  
  What is happening: H1 is "Newsroom". A slogan or a label, not a statement of the service.  
  Fix: Rewrite the H1 to name the service and the audience, for example "Full-Service Amazon Agency for Vendor and Seller Central Brands", keeping the slogan as a subheading.  
  Ref: R9
- [ ] **AS-097 Images without alt text** (P2, /newsroom/)  
  What is happening: 5 of 5 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-098 No call to action in the first mobile screen** (P2, /newsroom/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-099 Press coverage is off-site only** (P3, /newsroom/)  
  What is happening: The Forbes Business Council articles are linked but not summarized, and the page title does not claim the coverage.  
  Fix: Retitle to claim the coverage, add a two-line summary per article, and link the relevant division page from each summary.  
  Ref: G7

## University page

- [ ] **AS-100 Title does not say what the page is** (P1, /albert-scott-university/)  
  What is happening: Current title tag: "Albert Scott University - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Albert Scott University: Amazon Guides and Resources". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-101 H1 carries no descriptive term** (P2, /albert-scott-university/)  
  What is happening: H1 is "Albert Scott University". A slogan or a label, not a statement of the service.  
  Fix: Rewrite the H1 to name the service and the audience, for example "Full-Service Amazon Agency for Vendor and Seller Central Brands", keeping the slogan as a subheading.  
  Ref: R9
- [ ] **AS-102 Thin content** (P2, /albert-scott-university/)  
  What is happening: About 176 words of body copy. Competitor service pages that rank run 1,400 to 14,800 words.  
  Fix: Expand to at least 900 words using the /dsp/ page structure: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-103 Images without alt text** (P2, /albert-scott-university/)  
  What is happening: 4 of 4 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-104 No call to action in the first mobile screen** (P2, /albert-scott-university/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-105 Duplicate /university/ page** (P2, /albert-scott-university/)  
  What is happening: /university/ (148 words) duplicates this page.  
  Fix: 301 /university/ to /albert-scott-university/.  
  Ref: R1

## Contact page

- [ ] **AS-106 Title does not say what the page is** (P1, /contact-us/)  
  What is happening: Current title tag: "Contact Us - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Contact Albert Scott, Amazon Agency in New York". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-107 H1 carries no descriptive term** (P2, /contact-us/)  
  What is happening: H1 is "Get in Touch". A slogan or a label, not a statement of the service.  
  Fix: Rewrite the H1 to name the service and the audience, for example "Full-Service Amazon Agency for Vendor and Seller Central Brands", keeping the slogan as a subheading.  
  Ref: R9
- [ ] **AS-108 Images without alt text** (P2, /contact-us/)  
  What is happening: 6 of 6 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-109 Body copy links to almost nothing** (P2, /contact-us/)  
  What is happening: 1 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-110 No call to action in the first mobile screen** (P2, /contact-us/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-111 Three contact pages** (P2, /contact-us/)  
  What is happening: /contact-us/ (54 words), /book-a-call/ (68 words, orphan) and /lets-talk/ (50 words) all do the same job.  
  Fix: Keep /contact-us/ with an H1, the address and phone already in schema, 150+ words and the booking embed. 301 the other two (or noindex /book-a-call/ if the embed must stay separate).  
  Ref: R20

## Book a call page

- [ ] **AS-112 Title does not say what the page is** (P1, /book-a-call/)  
  What is happening: Current title tag: "Book a Call - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "[Service] for Amazon Brands: Albert Scott". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-113 No meta description** (P1, /book-a-call/)  
  What is happening: The page has no meta description, so search results and answer engines pick their own snippet from the page.  
  Fix: Write a 120 to 155 character description in AIOSEO stating what the page offers and for whom, using claims already on the page.  
  Ref: R8
- [ ] **AS-114 No H1** (P2, /book-a-call/)  
  What is happening: The page has no H1 heading, so the main topic is not declared to crawlers.  
  Fix: Set the page headline as an H1 (About: "About Albert Scott"; Contact: "Contact Albert Scott"; Gallery: "Amazon Listing and A+ Content Portfolio").  
  Ref: R9
- [ ] **AS-115 Images without alt text** (P2, /book-a-call/)  
  What is happening: 2 of 2 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-116 Almost no internal links point here** (P2, /book-a-call/)  
  What is happening: 0 inbound link(s) from other pages. The page is reachable mainly via the sitemap.  
  Fix: Link to it from the homepage divisions section, the relevant division page and the related articles.  
  Ref: R18
- [ ] **AS-117 Body copy links to almost nothing** (P2, /book-a-call/)  
  What is happening: 1 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-118 No call to action in the first mobile screen** (P2, /book-a-call/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20

## Location page

- [ ] **AS-119 Title does not say what the page is** (P1, /our-location/)  
  What is happening: Current title tag: "Our Location - Albert Scott". It carries no term a buyer would search for, so the page cannot appear for service queries and the og:title (which copies it) is equally blank.  
  Fix: Change the SEO title in AIOSEO to: "Amazon Agency in New York: Albert Scott, Inwood NY". Keep it under 65 characters where possible.  
  Ref: R7
- [ ] **AS-120 No meta description** (P1, /our-location/)  
  What is happening: The page has no meta description, so search results and answer engines pick their own snippet from the page.  
  Fix: Write a 120 to 155 character description in AIOSEO stating what the page offers and for whom, using claims already on the page.  
  Ref: R8
- [ ] **AS-121 No H1** (P2, /our-location/)  
  What is happening: The page has no H1 heading, so the main topic is not declared to crawlers.  
  Fix: Set the page headline as an H1 (About: "About Albert Scott"; Contact: "Contact Albert Scott"; Gallery: "Amazon Listing and A+ Content Portfolio").  
  Ref: R9
- [ ] **AS-122 Thin content** (P2, /our-location/)  
  What is happening: About 120 words of body copy. Competitor service pages that rank run 1,400 to 14,800 words.  
  Fix: Expand to at least 900 words using the /dsp/ page structure: definition, what is included, how it connects to the other divisions, results, FAQ.  
  Ref: R11
- [ ] **AS-123 Images without alt text** (P2, /our-location/)  
  What is happening: 4 of 4 images have empty alt attributes.  
  Fix: Add descriptive alt text to every image in the Media Library.  
  Ref: R10
- [ ] **AS-124 Almost no internal links point here** (P2, /our-location/)  
  What is happening: 0 inbound link(s) from other pages. The page is reachable mainly via the sitemap.  
  Fix: Link to it from the homepage divisions section, the relevant division page and the related articles.  
  Ref: R18
- [ ] **AS-125 Body copy links to almost nothing** (P2, /our-location/)  
  What is happening: 1 link(s) in the body beyond nav and footer. Related case studies, articles and sibling divisions are not linked.  
  Fix: Add contextual links: division pages link their case studies, related articles and /dsp/; the homepage links all four divisions and /dsp/ directly.  
  Ref: R18
- [ ] **AS-126 No call to action in the first mobile screen** (P2, /our-location/)  
  What is happening: On a 390px screen the only CTA above the fold is the Contact button, which sits inside the hamburger menu. The homepage is the only page with a visible button ("GET MY FREE AUDIT").  
  Fix: Add a visible button under the H1 on every primary page (Book a call, Get my free audit) that is present on mobile without opening the menu.  
  Ref: R20
- [ ] **AS-127 Location page is thin and orphaned** (P2, /our-location/)  
  What is happening: 120 words, no H1, no meta description, no inbound links. The Inwood NY office and warehouse fact only appears here. "Amazon agency New York" is won by city pages.  
  Fix: Expand into a New York agency page (office and warehouse near JFK, address, phone, what the warehouse does) or 301 to /about-us/.  
  Ref: G4

## Blog posts

- [ ] **AS-128 Eight brand write-ups duplicate case studies and projects** (P2, /blog/mouthwatchers/, /blog/tabanero/, /blog/yumvs/, /blog/atlas-olive-oil-spray/, /blog/objet-dart/, /blog/rae-dunn/, /blog/jose-gourmet/, /blog/73-originals/)  
  What is happening: These posts are 61 to 139 words each and repeat what the project and case study pages show. Four have no inbound links.  
  Fix: Merge each into its case study or project page and 301 the post. Keep the five real articles.  
  Ref: R12
- [ ] **AS-129 Articles are not linked from service pages** (P2, 5 articles)  
  What is happening: The TACoS, DSP, keyword targeting, Subscribe and Save and logistics articles are the best-scoring pages on the site (7.5 to 8.0) but no division page links to them.  
  Fix: Link each article from the matching division page and from /newsroom/ or the new /blog/ index.  
  Ref: R18

## Portfolio projects

- [ ] **AS-130 Project pages are image galleries with no text** (P2, 23 pages under /project/)  
  What is happening: Each project page has 10 to 14 words ("Project Scope: Full Graphic Optimization"), no meta description, no alt text and one inbound link from the gallery. They carry nothing an engine can index.  
  Fix: Either write 150 to 300 words per project (brand, category, what was built, which division) with alt text on every image, or noindex all 23 and keep them as gallery items.  
  Ref: R13
- [ ] **AS-131 Slug typo "seatinf"** (P3, /project/national-public-seatinf/)  
  What is happening: The project slug misspells "seating".  
  Fix: Rename the slug and let WordPress redirect.  
  Ref: R13

## Triage (legacy, test, duplicate)

- [ ] **AS-132 Old homepage still live** (P2, /home/)  
  What is happening: Title "Albert Scott - A Full Service Amazon Agency", 6 H1s, 1,053 words, indexable. Competes with /.  
  Fix: 301 to /  
  Ref: R1
- [ ] **AS-133 Legacy landing page, title in caps** (P2, /amazon-management-agency/)  
  What is happening: "FULL SERVICE AMAZON GROWTH AGENCY", 425 words, no H1, shortcode in body, indexed by search.  
  Fix: Rebuild as the account management page (growth plan G2) or 301 to /  
  Ref: R1
- [ ] **AS-134 Two ad landing pages indexable** (P2, /for-amazon-brands/ and /for-amazon-brandsv2/)  
  What is happening: 205 and 208 words, v2 duplicates v1, no inbound links.  
  Fix: Noindex both if still used for ads; otherwise 301 to /  
  Ref: R1
- [ ] **AS-135 Form test pages indexable** (P2, /amazon-growth-audit/, /amazon-growth-audit-v2/, /form-ads-test/)  
  What is happening: Titles "Form Ads", "Form Ads v2", "Form Ads - TEST"; 0 to 363 words.  
  Fix: Noindex the live one; delete the tests  
  Ref: R1
- [ ] **AS-136 Five legacy services pages** (P2, /services/, /services-2/, /our-service/, /additional-services/, /overview/)  
  What is happening: 2019 to 2022 pages with raw [vc_row] shortcode in body and meta description; duplicate titles "Services".  
  Fix: 301 all five to /  
  Ref: R1
- [ ] **AS-137 Duplicate marketing page** (P2, /marketing-division-2/)  
  What is happening: 405 words, indexable, own meta description.  
  Fix: 301 to the marketing division page  
  Ref: R1
- [ ] **AS-138 Duplicate retail page** (P2, /retail-management/)  
  What is happening: 125 words, 1 inbound link.  
  Fix: 301 to /retail-division/  
  Ref: R1
- [ ] **AS-139 Duplicate university page** (P2, /university/)  
  What is happening: 148 words.  
  Fix: 301 to /albert-scott-university/  
  Ref: R1
- [ ] **AS-140 Legacy portfolio pages** (P2, /portfolio/, /recent-success/, /videos/)  
  What is happening: 70 to 300 words, shortcode leaks on two.  
  Fix: 301 to /listings-portfolio-gallery/  
  Ref: R1
- [ ] **AS-141 Legacy about pages** (P2, /our-story/, /our-team/, /our-management/, /our-world-wide-team/, /niftyone-custom-portal/)  
  What is happening: 2018 to 2020 pages with shortcode leaks; /our-story/ holds the founding story that /about-us/ lacks.  
  Fix: Move the founding story into /about-us/, then 301 all five to /about-us/  
  Ref: R1
- [ ] **AS-142 Legacy clients page** (P2, /clients/)  
  What is happening: Indexed by search; logo wall with no alt text.  
  Fix: 301 to /case-studies/ or rebuild with alt text  
  Ref: R1
- [ ] **AS-143 Duplicate contact pages** (P2, /lets-talk/, /book-a-call/)  
  What is happening: 50 and 68 words; /book-a-call/ is an orphan with no H1 or meta.  
  Fix: 301 to /contact-us/ (keep one noindexed booking page if the embed is needed)  
  Ref: R1
- [ ] **AS-144 Two thank-you pages, both indexable** (P2, /thankyou/ and /thank-you/)  
  What is happening: Duplicate titles; 102 and 180 words.  
  Fix: 301 /thankyou/ to /thank-you/; noindex /thank-you/  
  Ref: R1
- [ ] **AS-145 Test and sample pages live** (P2, /test-page/, /test-modules/, /hero/, /sample-page/)  
  What is happening: Includes the WordPress default Sample Page and a test page linking two 404s.  
  Fix: Delete (410)  
  Ref: R1

## Junk URLs

- [ ] **AS-146 Indexable, in sitemap** (P1, 7 category archives)  
  What is happening: 1 to 3 posts each.  
  Fix: Noindex, remove from sitemap  
  Ref: R4
- [ ] **AS-147 Indexable, in sitemap** (P1, 2 tag archives)  
  What is happening: 1 post each.  
  Fix: Noindex, remove from sitemap, delete the tags  
  Ref: R4
- [ ] **AS-148 Indexable, in sitemap, under /blog/ prefix** (P1, 10 project_category archives)  
  What is happening: 389 words sampled.  
  Fix: Noindex, remove from sitemap  
  Ref: R4
- [ ] **AS-149 Indexable, in sitemap, no meta** (P1, /project/ archive)  
  What is happening: 562 words.  
  Fix: 301 to /listings-portfolio-gallery/  
  Ref: R4
- [ ] **AS-150 Indexable** (P1, 4 author archives)  
  What is happening: Two unfamiliar account slugs exposed.  
  Fix: Noindex; verify accounts  
  Ref: R4
- [ ] **AS-151 Already redirect to file** (P1, Attachment pages (1,075))  
  What is happening: Two sampled, both 301.  
  Fix: No action; re-sample monthly  
  Ref: R4
