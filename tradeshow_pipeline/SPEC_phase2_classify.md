# Phase 2 classification spec (workers)
Folder: /home/user/smartlead-api-client/tradeshow_pipeline. Input: phase2_work/classify_chunk_<N>.csv. One row per exhibitor (Exhibitor Key).
Input columns: Exhibitor Key, Exhibitor Name, Shows, Categories, About (trimmed), Website, Site Title, Site Description, Site Text (home + about page, trimmed), Parent Snippets (sentences from the site mentioning "division of / subsidiary of / owned by / acquired by / part of"), Site Copyright, Search Info (what a web search said they sell, when the show had no site).

For EACH row decide, using ONLY the text given (never memory):
1. Exhibitor Type, exactly one of:
   - Brand / Manufacturer: makes or designs products sold under its own name or its own brands (includes importers selling their own label, designers, artisans with a product line sold wholesale, furniture/lighting makers, jewelry manufacturers, gear makers, publishers of their own comics/games/toys, food/beverage/beauty brands).
   - Distributor / Wholesaler: mainly sells other companies' brands to retailers (may also own house brands).
   - Retailer / Reseller: sells to consumers at the show or online, mostly others' products (comic shops, collectible resellers, booths selling assorted merch, ski shops).
   - Artist / Individual: an individual artist, author, creator or cosplayer rather than a company.
   - Service / Software / Media / Association: services, software, payment/POS, marketing, publications, media, trade associations, shipping, staffing, consulting, show organizers, charities, government, schools.
   - Equipment / Supplier: sells to businesses, not consumers: fixtures, displays, packaging, raw materials, components, machinery, coffee roasting/espresso equipment for shops, salon equipment, private-label manufacturers selling only to other brands, B2B parts suppliers.
   - Unclear: not enough information to tell.
   Tie-breaks: a company that sells its own branded products to consumers or retailers is Brand / Manufacturer even if it also distributes. Private label / contract manufacturers that make products for other brands (White Label Expo) = Equipment / Supplier unless they also sell their own brand. Automotive aftermarket parts brands sold to consumers (PRI, SEMA-style) = Brand / Manufacturer; pure machine-shop/tooling/industrial suppliers = Equipment / Supplier. Media companies that also sell branded merchandise/products (e.g. comic publishers, toy companies at NYCC) = Brand / Manufacturer.
2. Type Reason: 5 to 15 words citing the evidence ("About: designs and manufactures ski goggles", "Categories: POS software").
3. Parent Company / Parent Domain / Parent Source: fill ONLY when the given text plainly states the exhibitor is owned by, a division/subsidiary/brand of, or part of another named company (Parent Snippets, About, Site Text, or a name like "X by Y Company" together with a shared website). Parent Source = where it was stated ("site about page", "show About text", "exhibitor name + shared website", "search result"). Parent Domain only if given in the text. A copyright line alone is NOT enough; if the copyright names a clearly different company put "Site copyright: <name>" in Notes instead. Blank is the right answer for independents.
4. Notes: only if something is worth flagging (e.g. site unreachable and About empty so type is a guess from the name).

Output: phase2_work/classify_out_<N>.csv, columns EXACTLY:
Exhibitor Key, Exhibitor Type, Type Reason, Parent Company, Parent Domain, Parent Source, Notes
Write with Python csv module, append and flush after every batch of rows you decide (do batches of 25 to 50; read the input in slices with pandas so you never need the whole file in context). On start skip keys already in the output (resume). No em dashes. Print "phase 2 classify chunk N: X of Y" every 100 rows.
Final reply: counts by type and number of parents found. Nothing else.
