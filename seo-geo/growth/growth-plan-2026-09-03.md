# Growth plan, 2026-09-03 (Stage 3)

What to build, consolidate, and earn so albertscott.com appears for the queries in `../config/keywords.md` and gets named by answer engines. Inputs: the Stage 1 audit, the 24-query baseline, the 10 competitor pages captured, and the third-party lists checked. Every company fact used here comes from albertscott.com (rule 7). No volumes are stated (rule 6). The roadmap (Stage 2) must land first; building new pages on top of the current inventory would add to the duplication problem.

## What the baseline says

- Albert Scott appeared in 3 of 24 queries, and only for queries containing its own name. Competitors win with two content types: a service page whose title states the service, and a "best agencies" comparison article on their own domain. SalesDuo appeared in 12 of 17 commercial queries by having one page per service and one listicle per service line.
- The one GEO prompt where Albert Scott was named (agencies handling both Vendor Central and Seller Central) was sourced from a third-party article quoting the retail division page. The site's own strongest differentiator, the four engagement models and four divisions, is not written anywhere in a form an answer engine can quote in one paragraph.
- For its own name, the site sits at position 8 behind ZoomInfo, LinkedIn and 2024 press releases.

## G1. Fix the entity first (weeks 1 to 2, with roadmap R15 and R17)

One description, used everywhere: schema, meta, the About page opening, LinkedIn. Recommended wording drawn from the homepage: "Albert Scott is a full-service Amazon agency that acts as a complete marketplace account management partner for brands selling on Amazon, across Vendor Central and Seller Central, through four divisions: Listing, Marketing, Retail and Logistics. Based in Inwood, New York." Add sameAs to the LinkedIn company page and the Forbes Business Council author page for David Greenblatt (already linked from /newsroom/). This is the prerequisite for every GEO gain below.

## G2. Service pages that say the service (weeks 2 to 6, with R7 and R11)

Rebuild rather than add. Each page follows the /dsp/ structure, which is the only service page on the site that already works: a definitional H1, an opening sentence that states what the service is, sections for what is included, how it connects to the other divisions, results, and a FAQ with FAQPage schema.

| Query target | Page | What to add, using facts already on the site |
|---|---|---|
| full service Amazon agency, Amazon agency, Amazon growth agency | / | Title change (R7). Move the four engagement models (Vendor Central, Seller Central, hybrid, distributor) higher and write them as one quotable paragraph. Link each division. |
| Amazon management agency, Amazon account management | rebuilt /amazon-management-agency/ | The site already has the URL and it is indexed. Rebuild it as the page for brands looking for full account management: the "How we partner together" models, the four divisions, executive ownership, case studies. |
| Amazon advertising agency, Amazon PPC management agency | /marketing-division/ (renamed) | Retitle. Add a PPC section (Sponsored Products, Sponsored Brands, Sponsored Display are already named on the homepage), link /dsp/ and the TACoS and keyword targeting articles. |
| Amazon DSP agency | /dsp/ | Retitle to include "Amazon DSP agency"; add a meta description; add FAQPage schema to the FAQ that already exists; link it from the homepage and the marketing page (it has 1 inbound link today). |
| Amazon listing optimization agency, Amazon A+ content agency | /listing-division/ plus a new /amazon-a-plus-content/ page | Retitle. The portfolio gallery and 23 projects show A+ modules, Brand Stores and listing images with no text; an A+ content page can hold that work with alt text and captions. |
| Amazon Vendor Central management agency, Amazon 1P vendor agency | /retail-division/ | Retitle to name Vendor Central and Seller Central. The page already states "Seller & Vendor" and channel structure choice; expand into the hybrid and distributor models and link the Forbes article on transitioning from Vendor to Seller Central. |
| Amazon agency with logistics | /logistics-division/ | Retitle. Reframe as an agency that runs logistics, not a 3PL: the query is won by freight forwarders, so the page should compete on "agency plus warehouse" using the Inwood warehouse fact from /our-location/. |

## G3. Comparison and "best agencies" content (weeks 4 to 8)

Every competitor that ranks for "best Amazon agencies" wrote the list themselves. Albert Scott has none. Two articles, published under /blog/ (after R19 fixes the index) and linked from /newsroom/:

1. "How to choose a full-service Amazon agency: 12 questions to ask" with a comparison framework (models covered, 1P and 3P, logistics in-house, executive ownership, retention). Honest, and it names competitors. Target: best Amazon agencies, best full-service Amazon agencies for mid-size brands.
2. "Vendor Central vs Seller Central vs hybrid: which model fits your brand" built on the four models and the existing Forbes article. Target: the Vendor plus Seller GEO prompt that already names Albert Scott.

Add a short "Albert Scott vs" section to /about-us/ rather than separate "vs" pages; the "Compare Albert Scott with..." prompt already returns the homepage at 5.

## G4. Local page (week 6)

"Amazon agency New York" is won by city landing pages and city listicles. Expand /our-location/ into "Amazon Agency in New York: Albert Scott, Inwood NY" using the existing facts (corporate office and main warehouse in Inwood, near JFK Airport; address and phone from schema). Add LocalBusiness to the single Organization node. Link from the footer.

## G5. Third-party lists (weeks 1 to 4, off-site)

| List | Status | Action |
|---|---|---|
| novadata.io best Amazon agencies (119+ agencies, vetted) | Not listed | Email contact@novadata.io with agency name, website, service categories |
| sermondo.com | Not listed | Add the free listing |
| clutch.co Amazon PPC agencies | Not listed | Create a profile and collect verified reviews from the clients already quoted on the homepage (Michel et Augustin, and the two other named testimonial sources) |
| withalfi.com best Vendor Central agencies | Listed second of five | The article says independent verification is limited; a case study page with Vendor Central numbers would give it something to cite |

These lists are what the "best agencies" queries and the GEO prompts return. Presence on them is the fastest route to being named.

## G6. Case studies as the proof layer (weeks 4 to 10, with R12 and R13)

The site has three real case study pages (Atlas Olive Oils, BeYoutiful, Mouthwatchers), the last one noindexed, plus nine case study PDFs linked from pages (Atlas, Flipbelt, Mouthwatchers, Objet D'Art, Great Western, Nora, BeYoutiful, Human Beanz, Roll Comb). Turn each PDF into an HTML case study page with Article schema, the BeYoutiful structure (H1 with the result, metric H3s, narrative), alt text, and a link from the relevant division page. Un-noindex Mouthwatchers once its blog duplicate is merged. This gives the division pages something to link to and gives third-party lists something to verify.

## G7. Brand SERP (weeks 1 to 4)

To move the homepage above ZoomInfo and the press releases for "Albert Scott Amazon agency": the entity fix (G1), a LinkedIn company page description that matches the site, the About page rewritten with a real H1 and the founding story that is currently on the legacy /our-story/ page, and the Newsroom page retitled to "Albert Scott in the News: Forbes and Press Coverage" so it owns the press narrative on the site's own domain.

## What not to do

- Do not add pages before the roadmap's R1 consolidation; the site has 32 pages that should not exist and adding more spreads the same thin authority further.
- Do not compete with 3PLs for "Amazon FBA logistics services"; that buyer wants freight, not an agency.
- Do not state client counts, revenue managed or growth percentages in new copy unless the figure is already published on albertscott.com. Press releases and data brokers carry numbers the site itself does not show; the site is the only allowed source.

## Measurement

Weekly pulse: the 6 core queries plus 2 GEO prompts. Monthly deep dive: all 24 queries, all 7 GEO prompts, re-grade every page touched. Success for this plan is albertscott.com appearing in returned results for at least 6 of the 17 commercial queries and being named in at least 3 of the 7 GEO prompts within three monthly cycles of the roadmap's batch 3 landing.
