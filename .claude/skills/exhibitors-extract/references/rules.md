# Rules: what counts, at each phase

## Phase 1: show data
- Use only what the show page shows. The website is the exhibitor's own link, not the show's URL.
- Take social links only from the exhibitor's own social-media block (`column social-media_container` on MapYourShow), never from share buttons or the show's own accounts.
- Contact names and notes on MapYourShow need a My Show Planner login, so they are not public. Leave them out and say so.
- Dedupe across shows on a normalized name (lowercase, no punctuation, no Inc / LLC / Corp / Co / Ltd / Company) or on the website domain. Keep both booths and both show URLs on the merged row. Don't merge two companies just because they share a parent.

## Phase 2: exhibitor type (exactly one)
- **Brand / Manufacturer**: makes and sells products under its own brand names. This includes factories making parts or accessories (even OEM or private label), chemical and car-care makers, tire makers, performance parts brands, and tool brands sold to consumers or retail.
- **Distributor / Wholesaler**: sells other companies' brands, even if it also owns house brands. Importers, exporters, trading companies, parts warehouses, online parts retailers and buying groups.
- **Service / Software / Media / Association**: SaaS, marketplaces, logistics, finance, agencies, publications, trade associations, government agencies, schools, testing, events and pavilions.
- **Tool & Equipment / Shop Supplier**: capital equipment and supplies sold to repair shops: lifts, alignment, tire changers, paint booths, scan tools, ADAS calibration, A/C machines, shop furniture, and pro-only consumables.
- **Unclear**: too little information to decide.
- Torn between Brand / Manufacturer and Tool & Equipment (hand tools, for example)? Choose Brand / Manufacturer if the products plausibly sell to consumers or through retail.
- Only Brand / Manufacturer goes on to phase 3. The other four types are dropped.

Parent company: fill it only when a source plainly says the exhibitor is owned by, a subsidiary, division or brand of, part of a named group, or acquired by another company, and the source is clearly about this exhibitor. Data-aggregator profiles (Crunchbase, ZoomInfo, PitchBook and similar) don't count on their own. Family-owned, distribution partners and "member of" associations don't count. Blank is the right answer for an independent company.

## Phase 3: brands owned
- A brand counts when the exhibitor sells products under it: its own names, names it lists as its own in the show's Brands section or on its brand pages, and brands the About text says it makes or owns.
- Third-party brands it carries don't count.
- The exhibitor's name, shortened to brand form ("KYB Americas Corporation" becomes "KYB"), is a brand only if products are sold under it.
- List every brand. Use the brand's own spelling. Skip model names unless they are presented as brands.

## Phase 4: exact Amazon store name
- Search `https://www.amazon.com/s?k=<brand>`. Keep results whose title starts with or contains the brand near the start, preferring organic results over sponsored ones. Open up to 3 product pages (`/dp/<ASIN>`).
- Read `#bylineInfo`:
  - "Visit the X Store": the store name is X, Has Amazon Store is yes, and the store URL is the byline link.
  - "Brand: X": the brand field is X and there is no store.
- Record the store name exactly as shown, as plain text: unescape HTML entities ("&amp;" becomes "&"), or SmartScout will miss names like "Smith & Wesson". Never use the search term or the product title.
- Similarity is the best of the store name or brand field against the brand, and against the exhibitor name:
  - verified: 0.85 or more
  - possible: 0.6 or more
  - different brand: below 0.6, meaning a store was found but it belongs to someone else
  - not found: no result title names the brand
- Short brand names (3 letters or fewer once squashed) stay "possible" unless the exhibitor or the seller also matches.
- A store owned by the parent counts. For example, Xtra Seal shows as "31 INCORPORATED", which matches the exhibitor 31 Incorporated, so it is verified through the exhibitor.
- Politeness:
  - Run one worker. Several sessions from one IP get flagged even after the soft check clears.
  - Wait 4 to 8 seconds between brands and 1 to 2.5 seconds between pages.
  - Block images and fonts.
- Robot checks:
  - Soft check (a "Click the button below to continue shopping" page with one button and no puzzle): click the button once and keep the cookies.
  - Image captcha ("Enter the characters you see below"): back off 3, 6, 12 then 30 minutes. Never try to solve it.
  - A robot check is never recorded as a miss.
- Detecting a block: `validatecaptcha`, "enter the characters you see below" or "to discuss automated access to amazon data" in the HTML. The word "captcha" alone also appears on normal pages, so don't use it.

## Phase 5: SmartScout
- Look up by the exact store name, then the Amazon brand field. Only an exact normalized name match counts. Don't try variants: the store name is already the exact name.
- A store that SmartScout doesn't have is "not in SmartScout", and it is still on Amazon.
- Saved query: "Full profile of the brand <X>". Use `run_query` with the handle and `filterValues` of up to 40 names. Handles expire, so get a fresh one from `query_analytics` when `run_query` says it is unavailable.
- Sellers ("Which sellers sell the brand <X> and what is each seller's share of the brand's revenue") and subcategories ("Top 3 subcategories for the brand <X> by the brand's revenue, with the brand's market share and rank in each subcategory") are only for brands you will email.
- Seller type:
  - Amazon 1P: the seller is Amazon.com.
  - Brand direct: the seller is the brand or its owner.
  - Third-party reseller: anyone else.
- Reseller Share % is the total share held by third-party resellers.

## Phase 6: people
- Scope: exhibitors with a verified or possible Amazon store, highest SmartScout revenue first.
- Company first: run `surfe_enrich_companies` on the domain, with externalID set to the exhibitor ID. It returns the LinkedIn company page, employee count, HQ and industry.
- People: run `surfe_search_people` with `company_domains`. Pass the titles with `job_titles`, never with `departments` (that filter fails validation). The search titles are Ecommerce, E-commerce, Amazon, Marketplace, Digital, Marketing, Brand, Sales, National Account, Key Account, Business Development, Channel, Revenue, Commercial and Growth, plus Retail as a last resort.
  - Pass A: US, C-Level / VP / Director / Head.
  - Pass B: US, Manager, for exhibitors with fewer than 5.
  - Pass C: any country, for exhibitors with none.
- Keep only titles matching sales / marketing / e-commerce words.
- Drop:
  - CEO, founder, owner, chairman, board, president (vice president is kept), and the other chiefs (CFO, COO, CTO, CIO, etc.).
  - Junior and support roles: intern, assistant, coordinator, specialist, rep, associate (associate director is kept), analyst, admin, customer service, support.
  - Technical, finance and operations roles: engineer, designer, IT and data roles, HR, accounting, purchasing, buyer, supply chain, logistics, quality, inside sales, territory.
  - Former staff, and surnames shown as an initial only.
- Rank:
  - Country: US first.
  - Seniority: chief marketing / revenue / commercial, then VP, then head / director, then manager.
  - Function: e-commerce / Amazon / digital, then marketing / brand, then sales.
  - Keep the top 5.
- Surfe search quota: the API caps how many people a search may return per window. On this account only about 1 to 5 people per call get through before `PUBLIC_API_PEOPLE_SEARCH_QUOTA_EXCEEDED`, and the allowance refills slowly. One chunk of 40 companies used about 155 results before the cap hit. A single slow agent (one domain per call, limit about 8, 60 seconds between calls, 180 seconds after a quota error) found about 150 people in 70 minutes, so plan on roughly 2 people a minute.
  - Run one search agent at a time, with small limits (`people_per_company` 5, about 5 to 10 per call).
  - Retry after 60 seconds.
  - Use public LinkedIn search results from earlier work as a second source, under the same title filter, with Surfe rows winning on duplicates.
  - Check credits with `surfe_get_credits`; `totalSearch` is not the same as this quota.

## Phase 7: emails
- Use `surfe_enrich_people` with first name, last name, LinkedIn URL, company domain and externalID = `<exhibitor id>|<linkedin url>`. Request email only and no mobile, then poll `surfe_get_enrichment_status`.
- Spend credits by Amazon status (verified, then possible), then by revenue.
- Never guess, construct or pattern-fill an email.
- Credits are charged when Surfe runs the enrichment, not when results are saved. Write the results to disk as soon as the status is complete, and never stop an enrichment agent midway: the credits are spent either way. If one is stopped, fetch the results with `surfe_get_enrichment_status` and the enrichment ID instead of enriching again.

## Phase 8: custom emails (my-writing-style, cold mode)
- 40 to 70 words between "Hi {first_name}," and "Yoni".
- One line each:
  - the show and booth
  - an Amazon fact
  - what Albert Scott does, as functions
  - an optional proof point
  - one question as the ask, with the calendar link on its own line if the ask is a call
- Amazon facts come from the data only:
  - the store name
  - revenue rounded and phrased as "from what we can see": under $5k is not cited, under $100k goes to the nearest $5k, under $1M to the nearest $50k, up to $3M to the nearest $0.1M, and above $3M (a whole-brand figure for a big company) is not cited
  - resellers holding most of the sales
  - the top subcategory
- Never name the data tool, and never cite an exact figure.
- Proof points (only these): a brand from no Amazon presence to a $1M+ annual run rate within six months; MouthWatchers from about $40K a month to $1M a month.
- Match the angle to the role:
  - e-commerce: channel control and growth
  - marketing: content, the store and how the brand shows up
  - sales: resellers, 1P / 3P and channel control
- People at the same company get different emails.
- Banned:
  - em and en dashes, exclamation marks, emojis, bullets
  - "I'd love to" / "would love", "hope this email finds you well", leverage, synergy, unlock, touch base, circle back, "quick question"
  - invented facts, discounts, pilots or trials
  - any claim that Yoni will be at the show unless he says so
- Subject: plain, under 60 characters, no dashes.

## Phase 9: master sheet
- One tab, one row per person, sorted by Amazon status, then revenue, then exhibitor, then priority.
- An in-scope exhibitor with no people gets one row with Row Status explaining why: Amazon check not run yet, Not on Amazon, People search pending, No people found in Surfe, Email pending, Custom email pending, No email from Surfe, or Ready.
- Google Sheets:
  - Writes are limited to about 6 per minute, so send large blocks starting at the top-left cell.
  - Values are parsed like typed input, so write numbers as plain numbers.
  - Read back the row count and a sample of cells after writing.
