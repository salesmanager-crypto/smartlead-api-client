# Phase 3 brand discovery spec (workers)
Folder: /home/user/smartlead-api-client/tradeshow_pipeline. Input: phase3_work/brands_chunk_<N>.csv, one row per in-scope exhibitor (Exhibitor Key).
Columns: Exhibitor Key, Exhibitor Name, Exhibitor Type, Shows, Categories, About, Website, Site Title, Site Description, Site Text, Brand Page URL, Brand Page Text, Brand Page Logos (image alt texts from the brand page), Parent Company, SmartScout Name Hit (the exhibitor name matched a SmartScout brand: "<brand> | <category> > <subcategory> | products N | monthly revenue $X", else blank).

Task: list every brand the exhibitor OWNS, using only the text in the row (never memory, no web tools).
Rules:
- A brand is a name printed on the exhibitor's products (product line / label / trademark). Collections or product-line names inside one brand (e.g. "Coastal Collection") are NOT separate brands unless the text calls them brands.
- The exhibitor name (or its short form, e.g. "Hooker Furnishings" -> "Hooker Furniture") is a brand only if products carry it: evidence = Site Title/Description/About describe "our products"/"<name> products", the company is a Brand / Manufacturer selling under its name, or SmartScout Name Hit fits the product type. For a Brand / Manufacturer with no contrary evidence, the exhibitor name IS a brand (Brand Source = "exhibitor name").
- Distributor / Wholesaler: list only house / private / exclusive brands it owns ("our brands", "exclusive brand", "proprietary"). Third-party brands it distributes ("we carry", "authorized dealer for", "we represent") are NOT listed. If it owns none, write one row with Brand blank and Notes = "Distributor; no owned brands found in text".
- Unclear with no text at all: one row with Brand = exhibitor name short form, Brand Source = "exhibitor name (unverified)", Notes = "No site or description; name checked as brand".
- If the text lists 15 owned brands, list 15. Use the brand's own spelling. Strip legal suffixes (Inc, LLC).
- Brand Source = "brand page <url>" / "site text" / "show About" / "exhibitor name" / "exhibitor name (unverified)" / "parent brand list".
- Also give up to 2 Search Variants for Amazon lookup when useful (e.g. "Arc'teryx" -> "Arcteryx"; "ClassicFlame" vs "Classic Flame"; drop words like "Home", "USA", "Furniture" only if that is how the brand is written on products). Blank if none.
Output: phase3_work/brands_out_<N>.csv, columns EXACTLY:
Exhibitor Key, Brand, Brand Source, Search Variants, Notes
(one row per brand; Search Variants joined by " ; "). Write with Python csv module, append + flush every 25 to 50 exhibitors; read input in slices with pandas. On start skip Exhibitor Keys already in the output. No em dashes. Helper/temp filenames must include "b<N>".
Final reply: exhibitors done, brand rows written, exhibitors with 0 brands. Nothing else.
