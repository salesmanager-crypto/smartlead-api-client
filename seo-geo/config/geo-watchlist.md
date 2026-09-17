# GEO watchlist

Generative engine optimization: whether AI answer engines name Albert Scott when asked about Amazon agencies, and what they say. Only WebSearch, WebFetch, and the headless browser are used to observe this (rule 1). Nothing is asserted about how a given engine ranks.

Status: first run 2026-09-03 through WebSearch (the only allowed observation surface). Five prompts run. Albert Scott was named for one.

## Entity facts an answer engine can read today (from the live site, 2026-09-03)

Two JSON-LD Organization blocks are present on every page checked:

- AIOSEO block: `@id` `/#organization`, name "Albert Scott", description "E-commerce Management", numberOfEmployees 5 to 10.
- Custom block: `@id` `/#org`, types Organization and ProfessionalService, slogan "Amazon. Expertise. Delivered.", telephone, email, postal address in Inwood NY, areaServed United States, North America, Global, numberOfEmployees 30, a knowsAbout list and an OfferCatalog of services.

The two blocks disagree on employee count and description and use different identifiers. No `sameAs` links to LinkedIn or other profiles were found in either block. This is the first GEO fix candidate.

## Prompts to run each week (pick two)

1. "What are the best full-service Amazon agencies for mid-size brands?"
2. "Which Amazon agencies handle both Vendor Central and Seller Central?"
3. "Who is Albert Scott, the Amazon agency?"
4. "Best Amazon DSP agencies"
5. "Amazon agency in New York"

## Prompts to run monthly (all of the above plus)

6. "Compare Albert Scott with My Amazon Guy and Canopy Management"
7. "Amazon agency that also manages logistics and retail operations"

## Recording format

| Date | Prompt | Engine or search surface observed | Albert Scott named? | What was said | Source cited |
|---|---|---|---|---|---|
| 2026-09-03 | What are the best full-service Amazon agencies for mid-size brands? | WebSearch result summary | No | Named Canopy, Nuanced Media, My Amazon Guy, SalesDuo, SupplyKick | 7 listicles, 3 of them agency-owned |
| 2026-09-03 | Which Amazon agencies handle both Vendor Central and Seller Central? | WebSearch result summary | Yes, 4th of 5 | "one of the most established Vendor Central agencies, with their service model explicitly covering both 1P and 3P, and their engagements structured around four models" | withalfi.com listicle (albertscott.com itself not cited) |
| 2026-09-03 | Who is Albert Scott the Amazon agency? | WebSearch result summary | Yes (brand query) | "full-service Amazon agency that aids mid to large brands... across both Vendor Central and Seller Central... based in Inwood, NY" | prnewswire.com and zoominfo.com language; homepage at result 8 |
| 2026-09-03 | Amazon agency that also manages logistics and retail operations | WebSearch result summary | No | Generic description; supplykick.com held 3 of 8 results | supplykick.com |
| 2026-09-03 | Compare Albert Scott with My Amazon Guy and Canopy Management | WebSearch result summary | Yes | Used homepage copy and named CEO David Greenblatt as "a recognized thought leader" | albertscott.com homepage at result 5; competitors' "vs" pages above it |
