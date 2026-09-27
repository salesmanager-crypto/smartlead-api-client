# Phase 2 domain search spec (workers)
Folder: /home/user/smartlead-api-client/tradeshow_pipeline. Input: phase2_work/search_chunk_<N>.csv (exhibitors whose show page had no company website, or only a social link).
For EACH row, in order:
1. Use the WebSearch tool: `<Exhibitor Name> official site`. If the name is generic or ambiguous, add one context term from Categories / Shows / City (e.g. `"Blue Ridge Candle" candles official site`). At most 2 searches per row.
2. Accept a Domain only if a result is clearly THIS company's own website (name matches, product type fits the show/category, location fits when given). Never accept marketplaces (amazon, etsy, ebay, faire, walmart), directories (yelp, bbb, zoominfo, dnb, opencorporates, mapyourshow, show sites), or social sites (facebook, instagram, linkedin, tiktok, linktr.ee). A Shopify/Wix/Square site on the company's own domain is fine. If only a social profile exists, Domain blank, Notes = "Only social profile found: <url>".
3. Domain = bare domain (e.g. acme.com). Domain Confidence = "found by search" or "not found".
4. Parent Company / Parent Source only if a search result states it plainly (e.g. "a division of X", "acquired by X"). Do NOT do an extra search for parent. Never from memory.
5. What They Sell = 3 to 10 words from the result snippet (blank if not found).
6. Company LinkedIn = linkedin.com/company/... URL only if it appears in the results for this company (do not search for it).
Output: append one row per input row to phase2_work/search_out_<N>.csv immediately after each row (open in append mode, flush), columns EXACTLY:
Exhibitor Key, Exhibitor Name, Domain, Domain Confidence, Domain Evidence, What They Sell, Parent Company, Parent Source, Company LinkedIn, Notes
- Domain Evidence = the result URL used + a few words why it matches.
- Notes required when Domain is blank (e.g. "No company site in results; only Etsy shop" / "Name too generic; no confident match").
- Use Python csv module for writing (proper quoting). No em dashes anywhere.
On start, if search_out_<N>.csv exists, skip keys already in it (resume). Keep your own messages short; the file is the record.
Every 50 rows print a line: "phase 2 search chunk N: X of Y, Z not found".
Final reply: rows done, found, not found, parents found. Nothing else.
