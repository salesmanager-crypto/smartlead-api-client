# Trade show enrichment run log

Generated 2026-09-25. Input: tradeshow_exhibitors_amazon_check_verified.xlsx, sheet Exhibitors, 1547 rows. Output: tradeshow_FINAL.xlsx (sheets Enriched and SmartLead_Upload). Checkpoint: tradeshow_checkpoint.csv. Cache: smartscout_cache.json.

## Scope and counts per show

| Show | Input rows | In scope | Emails written | Exact | Close | Not found | Wrong match |
|---|---|---|---|---|---|---|---|
| FLIBS 2026 | 704 | 124 | 124 | 50 | 12 | 27 | 35 |
| FNCE 2025 | 289 | 105 | 105 | 97 | 3 | 4 | 1 |
| Las Vegas Souvenir & Resort Gift Show 2026 | 554 | 170 | 170 | 114 | 8 | 39 | 9 |
| Total | 1547 | 399 | 399 | 261 | 23 | 70 | 45 |

Out of scope rows: 1148 (left untouched in Enriched, marked in the Scope column).

## Angle distribution

| Seller type (fresh data) | Rows |
|---|---|
| n/a (not found / wrong match) | 121 |
| Brand direct | 110 |
| Third-party resellers | 81 |
| Mixed | 53 |
| Amazon 1P | 34 |

## Method notes

- Amazon presence was not re-checked for any row. Scope came only from the priority and amazon_presence_summary columns.
- Every in-scope row got a fresh pull of three saved queries (brand profile, top sellers, top products). Results are cached by queried brand name in smartscout_cache.json; repeat brands were reused from cache (Simrad for the Kongsberg row, Teakdecking Systems for the Teak Deck Company row, Solara Suncare for the Solara Labs row).
- Brand name order used for the query: smartscout_brand, else amazon_brand_name, else the store name in amazon_store_url, else the cleaned exhibitor name. Two attempts maximum per row; the second attempt used the exhibitor name or a variant.
- Seller classification from fresh data: Amazon.com counted as 1P; a seller whose name matches the brand counted as brand direct; everything else, including Whole Foods Market and agency accounts such as Pattern, counted as third-party. Where the sheet's amazon_sold_by disagreed with the fresh data, the fresh data was used and the difference is noted in QA_Flags.
- FNCE opener: the template line 'Saw that {{company}} exhibited at FNCE last year.' was written with the real brand name in place of {{company}} so the emails read correctly without a merge field. Las Vegas rows use 'next week', FLIBS rows use 'next month'.
- Tool name is not mentioned in any email. Data is referred to as 'from what we can see' or 'looking at your listings'.
- Saved query handles expired twice (during batch 5 and batch 11). Each time the three handles were renewed with query_analytics and the batch's pulls were rerun. Handles are stored in handles.json.
- Fallbacks: one profile query errored with 'That query couldn't run' (Hooker, batch 11) and one earlier (My Arcade); the retry succeeded for My Arcade, Hooker was treated as not found after the second attempt. Yaza's seller query returned empty, so the seller came from the sheet and is flagged.
- Business plan limits: no brand revenue history, so the 12-month trend uses the average 12-month month-over-month growth field. US marketplace only.
- Word count discipline: emails that measured over 110 body words after the first draft were trimmed and remeasured; those rows carry 'trimmed for length' or a wordcount note in QA_Flags.

## Not found (industry-level email written)

**FLIBS 2026** (27): Vitrifrigo; CMOR Mapping; Salty Dawgs; Sancochos; Scania/Mack Boring & Parts Co.; Axalta Coatings System; Chris-Craft; Colnago USA; Dockside Pros; Dusky Marine, Inc.; Imtra; Inflatable Boat Pro; Jeanneau America; KScott Art & Apparel; LaPorte Products; Life League Gear | Lobster League; Mabru; Novurania of America, Inc.; Ocean Alexander; Rio Life Hats; Seaward Automation; SoFlo Customs / Apocalypse 6x6; Sterling Associates; Tees By Bo; Viking Life Saving Equipment; Wellcraft; Zeelander

**FNCE 2025** (4): Five Plus Protein; Fresh Blends; Keep Moving Inc. - gutzy organic; UP2U

**Las Vegas Souvenir & Resort Gift Show 2026** (39): A.T. Storrs Ltd.; Advance Wildlife Education; American Backcountry; Avalon Meat Candy; Bigfoot Sock Co / Sock Harbor; Boardwalk Puzzles; Conscious Step; Dutch American Import Co., Inc.; END SMALL TALK; Fifth Avenue Manufacturers; Forest Life Creations; Gear Lifestyle Brands (Champion, UA, Gear For Sports, Comfort Wash, Alternative Apparel); Gecko Hawaii; GetAGadget, Inc; Global SWIBCO, Inc.; Glyder LLC; GUIDES CHOICE; LEIGHTWORKS; Pilgrim Imports Inc.; Savvy Sox; Spirit Jersey®; The Landmark Project; Uzzi; Valani Apparel; West Coast Sunglasses, Inc.; Wild Tribute; Wilmot Harvey; YRI Belts; Parks Project; Crazy Apparel Inc.; Desert Sunglass of Scottsdale; Mermaid Soul; Mug Experience; Planet Cotton/ Blue Moon; Please Please Me; Pocket Products, LLC; Prairie Mountain; Tortuga Moon - Cole Apparel; TrendSetterTees, LLC.

## Wrong match (sheet brand mapping did not fit the exhibitor; industry-level email written)

**FLIBS 2026** (35):

- Sea Ray: 'searay' matched guitar picks; 'Sea Ray' variant returned 0 products; industry-level email from row info
- Allied Marine: wrong match: sheet mapped exhibitor to Allied Flag & Frame (unrelated); SS_ numbers are for Allied Flag, not Allied Marine; weaker fit: yacht brokerage and dealer
- Aspen: wrong match: 'Aspen' matched back braces; sheet listing is Aspen cologne; exhibitor is Aspen Power Catamarans; weaker fit: boat builder
- Bertram: wrong match: 'Bertram' matched essential oils; sheet listing is a book; exhibitor is Bertram Yachts; weaker fit: yacht builder
- flite: wrong match: 'Flite' matched FliteBMX; sheet's 'sold by FliteBMX' is the same unrelated company; weaker fit: premium eFoil, dealer-led
- Multiplex GmbH: wrong match: 'Multiplex' matched lab beakers; sheet listing unrelated; exhibitor product line unclear; weaker fit
- Nimbus: wrong match: 'Nimbus' matched a toothbrush brand; sheet store (ZenEssence) is the same unrelated brand; exhibitor is Nimbus Boats; weaker fit: boat builder
- QMI: wrong match: 'QMI' matched fender trim; sheet listing unrelated; weaker fit: OEM supplier
- The Brass Works: wrong match: sheet mapped exhibitor to Brasso (Reckitt) storefront; SS_ numbers are Brasso's; weaker fit: custom marine hardware
- Aqua Nautica USA: no brand record on two attempts; sheet mapped to unrelated Nautica storefront; industry-level email
- AquaVue Tech Co: no brand record on two attempts; sheet mapped to unrelated AQUA-TECH listing; industry-level email
- Bolt Depot: brand record returned 0 products; sheet mapped to unrelated BoltsandNuts.com storefront; industry-level email
- CIRO Marine: wrong match: 'CIRO' matched a motorcycle accessories brand; sheet listing (sold by Gritr) is the same unrelated brand; industry-level email
- CMC Marine Corp: wrong match: 'CMC' matched unrelated T-H Marine parts and piano books; industry-level email; weaker fit: OEM stabilizer manufacturer
- Cody's Fish: no brand record on two attempts; sheet mapped to unrelated Cody Johnson storefront; industry-level email
- Dockmate USA: wrong match: 'Dockmate' record and sheet storefront are an unrelated dock guard brand; exhibitor is the Dockmate wireless docking system; weaker fit: dealer-installed system
- FERRETTI GROUP: no brand record on two attempts; sheet mapped to unrelated Rossano Ferretti listing; industry-level email; weaker fit: yacht builder
- Force-e: no brand record on two attempts; sheet mapped to unrelated Force Factor storefront; industry-level email; weaker fit: dive retailer
- FreedomLift: no brand record on two attempts; sheet mapped to unrelated Freedom Offroad listing; industry-level email; weaker fit: dealer-installed equipment
- Gloria Keg: wrong match: 'GLORIA' matched dollhouse furniture; sheet storefront unrelated; exhibitor product line unclear; industry-level email
- Hooker Pumps: wrong match: 'Hooker' matched Holley exhaust parts; sheet listing unrelated; industry-level email; weaker fit: OEM pump manufacturer
- Island Optics Polarized Sunglasses: wrong match: sheet mapped to Optic Nerve storefront; SS_ numbers are Optic Nerve's; Island Optics not found; industry-level email
- Leak Stop Gun: wrong match: sheet mapped to Leak Saver storefront; SS_ numbers are Leak Saver's; Leak Stop Gun not found; industry-level email
- Merle Wood & Associates: no brand record; sheet mapped to unrelated Merle Norman listing; industry-level email; weaker fit: yacht brokerage
- Ring Power Cox Marine: combined exhibitor name; queried Ring Power and Cox Marine; both empty; sheet mapped to unrelated Ring storefront; weaker fit: dealer
- Seawater Pro: no brand record on two attempts; sheet listing unrelated; industry-level email
- Secured Safety Solutions: wrong match: sheet mapped to Secure Safety Solutions (Personal Safety Corporation) storefront; SS_ numbers are that brand's; industry-level email; exhibitor product line unclear
- Sessa International S.R.L.: wrong match: sheet mapped to Sessa Syrups storefront; SS_ numbers are Sessa Syrups'; Sessa Marine not found; weaker fit: boat builder
- Sharrow Marine: wrong match: 'SHARROW' matched an archery brand; sheet storefront is the same unrelated brand; Sharrow Marine not found; weaker fit: dealer-led premium product
- Spectra Watermakers/Katadyn Desalination: combined exhibitor name; queried SPECTRA (sheet brand) and Spectra Watermakers; Katadyn not queried; wrong match: SPECTRA record and sheet storefront are Spectra Baby; weaker fit: installer-led equipment
- Star Blink Products: no brand record on two attempts; sheet mapped to Amazon-owned Blink storefront; industry-level email; exhibitor product line unclear
- Teak Deck Companay: wrong match: sheet mapped to Teakdecking Systems storefront (different company, row 284); SS_ numbers are Teakdecking Systems'; industry-level email
- Titan Marine Air: wrong match: 'TITAN' record and sheet storefront are a generic unrelated brand; Titan Marine Air not found; weaker fit: installer-led equipment
- Veco USA: wrong match: 'VECO' record and sheet storefront are an unrelated spray bottle brand; Veco USA not found; weaker fit: installer-led equipment
- WATERWAYZ: no brand record on two attempts; sheet listing unrelated; industry-level email; exhibitor product line unclear

**FNCE 2025** (1):

- CommonGround: wrong match: 'Common Ground' matched a shampoo brand; sheet listing is a book; org_type: likely nonprofit or advocacy program, weak fit

**Las Vegas Souvenir & Resort Gift Show 2026** (9):

- Ahead LLC: 'Ahead' matched an unrelated drum accessories brand; industry-level email from row info
- Blue Planet Eco-Eyewear: 'Blue Planet' matched Blue Planet Surf (balance boards); full name returned empty; industry-level email
- Neil Enterprises: wrong match: sheet mapped exhibitor to NeilMed storefront; SS_ numbers are NeilMed's; exhibitor product line assumed from name, verify
- Culver Industries, Inc.: wrong match: 'Culver' record is a glassware brand; sheet storefront (Culver LED) unrelated; exhibitor product line unclear; industry-level email
- DMR Creative: wrong match: 'DMR' record is a bike parts brand; 'DMR Creative' returned empty; sheet seller unknown; industry-level email
- Momentum Comfort Gear: wrong match: 'Momentum' record unrelated; 'Momentum Comfort Gear' returned empty; sheet Amazon (Vendor) not confirmed; industry-level email
- Pacific North Nest Designs: wrong match: sheet mapped exhibitor to NEST New York (home fragrance), unrelated; 'Pacific North Nest' returned empty; industry-level email
- Perrin Sportswear: wrong match: 'PERRIN' record is automotive; sheet listing is a print-on-demand shirt sold by Amazon; industry-level email
- TRAVEL SIZE DEPOT: wrong match: sheet mapped exhibitor to Travel Depot (automotive), unrelated; 'Travel Size Depot' returned empty; industry-level email

## Close matches (verify identity before sending)

- Las Vegas Souvenir & Resort Gift Show 2026 | Liquid Blue/The Mountain -> Liquid Blue: profile query failed on fast path and query_analytics; revenue derived from seller totals; exhibitor also lists The Mountain, not queried; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Blank Tag Co. Stickers -> Blank Tag Co.: profile query returned empty; data from seller and product queries only
- Las Vegas Souvenir & Resort Gift Show 2026 | Bicast Inc. -> Bicast: profile query failed on fast path and query_analytics; sellers empty; treated as effectively not on Amazon
- FLIBS 2026 | Mercury Marine -> MERCURY: mixed record: 'MERCURY' profile includes Mercury Records CDs (MovieMars-CDs); SS_ totals not brand-specific; email uses only marine product listings; 'Mercury Marine' variant returned 1 product; sheet third-party (LEADERS RPM) confirmed
- FLIBS 2026 | Raritan Engineering Co, Inc. -> Raritan: mixed record: 'Raritan' profile is dominated by Raritan Inc KVM switches; SS_ totals not brand-specific; 'Raritan Engineering' variant returned empty; email uses only marine listings; sheet third-party (Homestead Supply) confirmed
- FNCE 2025 | DaVinci Laboratories -> DaVinci: mixed record: 'DAVINCI' profile is dominated by DaVinci Baby cribs; SS_ totals not brand-specific; only the ADK listing is DaVinci Laboratories; sheet third-party (Pattern.) confirmed
- FNCE 2025 | Heavenly Foods -> nan: SmartScout record is under 'Heavenly Waffles' (product line name)
- Las Vegas Souvenir & Resort Gift Show 2026 | AdventureKEEN -> Adventure Publications: SmartScout record is under imprint 'Adventure Publications'; weaker fit: book publisher, Amazon 1P
- FLIBS 2026 | Cummins -> Cummins: record is the whole Cummins consumer catalog (inverters, Onan, Fleetguard); Cummins Marine not separately visible; sheet Amazon (Vendor); fresh data shows Mixed with dealers over half; large company, narrow ask
- FLIBS 2026 | Honda Marine -> Honda: record is all of Honda on Amazon (generators, auto fluids); Honda Marine not separately visible; sheet third-party (G.P.S.) confirmed; very large brand, narrow ask
- FLIBS 2026 | KOAH -> Koah: mixed record: 'Koah' brand on Amazon is mostly Focus Camera's Koah accessory line; SS_ totals not the exhibitor's; email uses only the spearfishing seller data; sheet third-party (Focus Camera) is the unrelated brand's seller
- FLIBS 2026 | Suzuki Marine -> Suzuki: mixed record: 'Suzuki' on Amazon is mostly Suzuki musical instruments; SS_ totals not marine-specific; sheet third-party (Central Florida PowerSports) confirmed for marine listings; large brand, narrow ask
- FLIBS 2026 | Yamaha Marine -> YAMAHA: mixed record: 'YAMAHA' on Amazon is mostly musical instruments; SS_ totals not marine-specific; sheet third-party (Pine Grove Powersports); very large brand, narrow ask
- Las Vegas Souvenir & Resort Gift Show 2026 | Ranger Industries LLC -> Ranger Industries: sheet brand name 'Ranger Pro' is an unrelated herbicide; used 'Ranger Industries' record instead, verify it is the exhibitor; sheet third-party confirmed
- FLIBS 2026 | Bisous -> Bisousweet Confections: verify identity: exhibitor listed as 'Bisous'; sheet and SmartScout record are Bisousweet Confections muffins; may be a different company; sheet third-party (Whole Foods Market)
- FLIBS 2026 | Koenig Polish -> Koenig: record is 'Koenig' (single spray polish listing); verify it is the exhibitor's product; sheet third-party (Alubix) confirmed
- FLIBS 2026 | SIMRAD by Kongsberg -> Simrad: cached Simrad record reflects the Navico recreational brand, not the Kongsberg professional division; sheet sold_by Unknown; fresh data shows Mixed; weaker fit: commercial marine electronics
- FLIBS 2026 | Smith Sport Optics, Inc. -> Smith: 'Smith' record includes unrelated Smith brands (torches, paper); SS_ totals not fully brand-specific; sheet third-party (Pure luxury); fresh data shows Mixed with brand account at 64%; very large brand, narrow ask
- FLIBS 2026 | VETUS Maxwell -> Vetus: combined exhibitor name; queried VETUS (first brand); MAXWELL record is an unrelated foot switch brand; 'Vetus' record includes a few unrelated listings; SS_ totals approximate; sheet third-party (Performance Guarantee) confirmed
- FNCE 2025 | AngelEye Health -> Mt. Angel Vitamins: verify identity: exhibitor listed as AngelEye Health; sheet and SmartScout record are Mt. Angel Vitamins; sheet third-party (Holly Hill Health Foods); fresh data shows Mixed with brand account at 78%
- Las Vegas Souvenir & Resort Gift Show 2026 | Ramatex International -> Ramatex: sheet third-party (SPLG Products); fresh data shows Jetienne as the seller; close match: exhibitor Ramatex International, record Ramatex
- Las Vegas Souvenir & Resort Gift Show 2026 | Tipsy -> TipsyAuthen: verify identity: exhibitor 'Tipsy' at a gift show; Amazon record is the Tipsy audio brand (TipsyAuthen / TipsyAudio) per sheet store URL; sheet Brand (Seller Central) confirmed
- Las Vegas Souvenir & Resort Gift Show 2026 | Topline Products, Inc. -> Topline: verify identity: exhibitor Topline Products, Inc.; Amazon record is TOPLINE TOOLS per sheet store URL; sheet Brand (Seller Central) confirmed; Topline retail Solutions (15%) treated as affiliated, verify

## QA-flagged rows

Rows where QA_Flags contains anything beyond a plain confirmation of the sheet's seller type. All emails passed the final QA pass (word count 60 to 110, no dashes, no exclamation marks, no banned phrases, no unrounded numbers, tool name absent, greeting present, exactly one ask, ends with Yoni, correct opener per show).

307 rows flagged:

- FNCE 2025 | Life Extension [exact]: very large brand (>$5M/mo), narrow ask used
- FNCE 2025 | Orgain, LLC [exact]: very large brand (>$5M/mo), narrow ask used
- FNCE 2025 | NOW Foods [exact]: very large brand (>$5M/mo), narrow ask used
- FNCE 2025 | McGraw Hill [exact]: education publisher, weaker fit for consumer brand pitch; reseller share includes used-book sellers
- FNCE 2025 | Microbiome Labs [exact]: Front Row Group is a known Amazon distributor/agency, treated as third party per rules
- FNCE 2025 | Lakanto [exact]: trimmed for length
- FNCE 2025 | Primal Kitchen [exact]: Whole Foods Market counted as third party per rules; it is Amazon-owned
- FNCE 2025 | GOYA FOODS INC. , Goya BetterForYou line [exact]: exhibitor is the BetterForYou line; SmartScout data covers the whole Goya brand; final QA: opener normalized to standard FNCE line
- FNCE 2025 | Jones & Bartlett Learning [exact]: education publisher, weaker fit for consumer brand pitch; reseller share includes used-book sellers; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | HydraPeak [exact]: seller 'Amazing Deals Online' (460 offers, 99%) assumed to be Hydrapeak's own account; verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Blue 84/Aksels/Altered Latitudes/Zephyr Headwear [exact]: exhibitor lists multiple brands (Aksels, Altered Latitudes, Zephyr Headwear); only Blue 84 queried
- FNCE 2025 | Fishwife Tinned Seafood Co. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | MasterPieces Inc. [exact]: trimmed for length
- FNCE 2025 | Oscar Mayer [exact]: large CPG brand (Kraft Heinz); narrow ask used
- FNCE 2025 | Kiwi Biosciences (FODZYME) [exact]: profile pulled via query_analytics fallback; Amazon 1P % and 12M growth not returned by that query
- Las Vegas Souvenir & Resort Gift Show 2026 | Sourcebooks [exact]: book publisher, weaker fit for consumer brand pitch
- Las Vegas Souvenir & Resort Gift Show 2026 | Logo Brands [exact]: trimmed for length
- FNCE 2025 | Nutricia North America [exact]: SmartScout brand record covers the Pepticate line only, not all Nutricia products
- Las Vegas Souvenir & Resort Gift Show 2026 | Wild Republic / K&M International, Inc. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Ben Kaufman Sales [exact]: trimmed for length
- FNCE 2025 | Lifeway Foods [exact]: SmartScout 'Single Seller Name' shows unrelated Lifeway Christian Resources; ignored; trimmed for length
- FNCE 2025 | Impossible Foods [exact]: products pulled via query_analytics fallback; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | LazyOne [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | The Petting Zoo dba Zoologee [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Safari Ltd. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Gulf Coast Panama Jack [exact]: exhibitor is Gulf Coast Panama Jack (likely licensee); SmartScout data is the Panama Jack brand overall; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Jerzees [exact]: Jerzees is a Fruit of the Loom brand
- Las Vegas Souvenir & Resort Gift Show 2026 | Rhode Island Novelty / Adventure Planet [exact]: exhibitor also lists Adventure Planet; only Rhode Island Novelty queried; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Spoontiques, Inc. [exact]: trimmed for length
- FNCE 2025 | Painterland Sisters [exact]: trimmed for length
- FNCE 2025 | Kibow Biotech LLC [exact]: SmartScout KIBOW brand record also contains two unrelated fire-pit products with $0 revenue; trimmed for length
- FNCE 2025 | Olyra [exact]: trimmed for length
- FNCE 2025 | Kindling Snacks [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | ASOBU [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | American Classics, Inc [exact]: seller '2Bhip' (327 offers, 100%) assumed to be American Classics' own account; verify; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | University Games [exact]: org_type_flag: Likely not a consumer brand (row flag); SmartScout shows a real consumer catalog; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Julie & Joe by Stephen Joseph [exact]: exhibitor is the Julie & Joe line by Stephen Joseph; data covers the Stephen Joseph brand overall
- Las Vegas Souvenir & Resort Gift Show 2026 | American Apparel, LLC. [exact]: American Apparel is a Gildan brand
- FNCE 2025 | General Mills [exact]: very large CPG; SmartScout brand record not representative of the portfolio; seller query failed on both fast path and query_analytics; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | American Needle [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Liquid Blue/The Mountain [close]: profile query failed on fast path and query_analytics; revenue derived from seller totals; exhibitor also lists The Mountain, not queried; trimmed for length
- FNCE 2025 | La Brea Bakery [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Aloe Up Sun & Skin Care Products [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Child To Cherish [exact]: 'Trademark Retail' may be an affiliated company; treated as third party per rules; verify; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Glimmer Wish [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Lavley [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Lavley/Long Sales [exact]: duplicate brand with row 'Lavley' (Long Sales is a rep group); same data, different email; trimmed for length; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Big Skinny Wallets [exact]: trimmed for length
- FNCE 2025 | Mondelez International [exact]: very large CPG; SmartScout brand record not representative of the portfolio
- FNCE 2025 | Gourmend Foods [exact]: profile pulled via query_analytics fallback; Amazon 1P % and 12M growth not returned
- Las Vegas Souvenir & Resort Gift Show 2026 | Ricoma International [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | GeoToys [exact]: seller 'Lidianas' (82 offers, 100%) assumed to be GeoToys' own account; SmartScout single seller field shows 'Zoe's Toys'; verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Wondery Outdoors [exact]: profile monthly revenue ($15.3k) and seller total ($27.6k) disagree; email uses a range
- FNCE 2025 | PepsiCo, Inc. [exact]: very large CPG; SmartScout brand record not representative of the portfolio
- Las Vegas Souvenir & Resort Gift Show 2026 | Xplorer Maps [exact]: 'Buckeye Trading' may be an affiliated company; treated as third party per rules; verify; trimmed for length
- FNCE 2025 | NeuroFiber by Sorridi Therapeutics [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Lantern Press [exact]: org_type_flag: Likely not a consumer brand (row flag); SmartScout shows a consumer catalog
- Las Vegas Souvenir & Resort Gift Show 2026 | THE GEOPROJECT [exact]: 'FoxMarketplace' may be an affiliated company; treated as third party per rules; verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Good Luck Sock [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Bevin Bells [exact]: 'Elbert Mountain' may be an affiliated company; treated as third party per rules; verify
- Las Vegas Souvenir & Resort Gift Show 2026 | E & S Pets [exact]: 'Petasaurus' may be an affiliated company; treated as third party per rules; verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Garvey Products [exact]: B2B supplies brand; SmartScout record includes some Cosco items
- Las Vegas Souvenir & Resort Gift Show 2026 | Boxercraft [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Farcountry Press [exact]: book publisher, weaker fit; org_type_flag: Likely not a consumer brand; trimmed for length
- FNCE 2025 | Mead Johnson Nutrition [exact]: very large company (Reckitt); SmartScout brand record covers metabolic medical foods only
- Las Vegas Souvenir & Resort Gift Show 2026 | Signs 4 Fun, Inc. [exact]: 'Uanna' may be an affiliated company; treated as third party per rules; verify; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Incredible Sunvisor, Inc., The [exact]: 'All Things New Store' may be an affiliated account; treated as third party per rules; verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Eagle Crest Industries Inc. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Hang Loose Srl Keep Out Bracelets [exact]: exhibitor listed as Hang Loose Srl Keep Out Bracelets; matched to Hang Loose Bands brand
- Las Vegas Souvenir & Resort Gift Show 2026 | L'ovedbaby [exact]: Marketplace Valet is a third-party marketplace service provider; treated as third party per rules
- Las Vegas Souvenir & Resort Gift Show 2026 | Vinrella [exact]: 'Garden Works' may be an affiliated company; treated as third party per rules; verify; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | First & Main [exact]: profile pulled via query_analytics after handle renewal; trimmed for length
- FNCE 2025 | Agoge [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | The Jonsteen Co. [exact]: profile and sellers pulled via query_analytics fallback; 12M growth not returned
- Las Vegas Souvenir & Resort Gift Show 2026 | Americaware, Inc. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | SEAWAG [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Earthview, Inc. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | L. W. Bristol Classics [exact]: 'Stateline Classics' assumed to be the brand's own account; verify
- FNCE 2025 | Ajinomoto Cambrooke [exact]: large parent (Ajinomoto); SmartScout record covers Essential Care JR only
- Las Vegas Souvenir & Resort Gift Show 2026 | Channel Craft [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | The Handcrafted [exact]: 'Cheerful Home' may be an affiliated account; treated as third party per rules; verify; trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Greenwill Global [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | EnjoyLife, Inc. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Southwest Specialty Food, Inc. [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Dry Gulch Gifts [exact]: trimmed for length
- Las Vegas Souvenir & Resort Gift Show 2026 | Gem Guides Book Company [exact]: small book publisher; weaker fit for consumer brand pitch
- Las Vegas Souvenir & Resort Gift Show 2026 | Little Joys [exact]: Mosaic Wellness is Little Joys' parent company; treated as brand direct
- FNCE 2025 | Just Made [exact]: profile pulled via query_analytics fallback
- Las Vegas Souvenir & Resort Gift Show 2026 | The Bear Factory [exact]: profile pulled via query_analytics fallback
- Las Vegas Souvenir & Resort Gift Show 2026 | Sona Enterprises [exact]: profile pulled via query_analytics fallback; SmartScout record may be a partial view of the SE catalog
- Las Vegas Souvenir & Resort Gift Show 2026 | ZOOCCHINI / FlapjackKids [exact]: exhibitor also lists FlapjackKids; only Zoocchini queried
- Las Vegas Souvenir & Resort Gift Show 2026 | Blank Tag Co. Stickers [close]: profile query returned empty; data from seller and product queries only
- Las Vegas Souvenir & Resort Gift Show 2026 | RexTooth Studios [exact]: small publisher; weaker fit
- Las Vegas Souvenir & Resort Gift Show 2026 | East View Map Link [exact]: map publisher/distributor; weaker fit
- Las Vegas Souvenir & Resort Gift Show 2026 | Something Wild Inc. [exact]: small publisher; weaker fit; product title not returned, single ASIN
- Las Vegas Souvenir & Resort Gift Show 2026 | Bicast Inc. [close]: profile query failed on fast path and query_analytics; sellers empty; treated as effectively not on Amazon
- FLIBS 2026 | Awlgrip/Interlux/SeaHawk [exact]: exhibitor lists Awlgrip/Interlux/SeaHawk (AkzoNobel brands); only Awlgrip queried; sheet amazon_sold_by = Third-party resellers, confirmed
- FLIBS 2026 | Bluewing Fishing [exact]: sheet amazon_sold_by = Third-party resellers (Uniprime Outdoors); fresh data shows Uniprime as the sole seller on 1,202 offers, treated as brand's own operating account; disagreement noted
- FLIBS 2026 | Cutco Cutlery [exact]: sheet amazon_sold_by = Third-party resellers, confirmed; Cutco is a direct-sales company and may not want Amazon
- FLIBS 2026 | Dometic [exact]: very large brand (>$2M/mo); sheet amazon_sold_by = Unknown; fresh data shows mixed 1P and resellers
- FLIBS 2026 | Fujifilm North America Corporation [exact]: very large brand, narrow ask; sheet third-party (Wiz Distribution) confirmed by fresh data
- FLIBS 2026 | Garmin International [exact]: very large brand, narrow ask; sheet sold_by Unknown; fresh data shows Amazon 1P 57% plus resellers (Mixed)
- FLIBS 2026 | Gtechniq Marine [exact]: sheet says third-party (Harvard Marine); fresh data shows brand account Gtechniq NA at 58% with 42% resellers; trusting fresh (Mixed)
- FLIBS 2026 | Guy Harvey [exact]: NG Labs Apparel is the apparel licensee; treated as brand direct, verify
- FLIBS 2026 | HUK [exact]: sheet Amazon (Vendor) confirmed; large brand, narrow ask
- FLIBS 2026 | Leviton [exact]: sheet Amazon (Vendor) confirmed; very large brand, narrow ask
- FLIBS 2026 | Mercury Marine [close]: mixed record: 'MERCURY' profile includes Mercury Records CDs (MovieMars-CDs); SS_ totals not brand-specific; email uses only marine product listings; 'Mercury Marine' variant returned 1 product; sheet third-party (LEADERS RPM) confirmed
- FLIBS 2026 | Raritan Engineering Co, Inc. [close]: mixed record: 'Raritan' profile is dominated by Raritan Inc KVM switches; SS_ totals not brand-specific; 'Raritan Engineering' variant returned empty; email uses only marine listings; sheet third-party (Homestead Supply) confirmed
- FLIBS 2026 | Sea Foam Sales Co [exact]: sheet says Brand (Seller Central); fresh data shows brand at 25.5% with resellers at ~74%; trusting fresh (Third-party resellers)
- FLIBS 2026 | Sea Ray [wrong match]: 'searay' matched guitar picks; 'Sea Ray' variant returned 0 products; industry-level email from row info
- FLIBS 2026 | SIONYX [exact]: sheet says third-party (Forgot My Souvenirs); fresh data shows brand account at 67% with 33% resellers; trusting fresh (Mixed)
- FLIBS 2026 | SiriusXM [exact]: sheet third-party confirmed; large company, weaker fit (subscription business, hardware via dealers)
- FLIBS 2026 | Vitrifrigo [not found]: profile returned 0 products on two attempts; industry-level email from row info
- FLIBS 2026 | Zero Breeze [exact]: sheet says Brand (Seller Central) sold by Zero Breeze; fresh data shows one listing sold by Max n Company LLC; trusting fresh, partial record (1 product, TTM figure unreliable)
- FNCE 2025 | Banza [exact]: sheet Amazon (Vendor) confirmed; Whole Foods Market counted as third-party per rule but is Amazon-owned; products pulled via query_analytics fallback
- FNCE 2025 | Carlson Laboratories, Inc. [exact]: sheet Brand (Seller Central) confirmed; profile pulled via query_analytics fallback
- FNCE 2025 | Chicken of the Sea [exact]: sheet Amazon (Vendor) confirmed; large brand, narrow ask
- FNCE 2025 | DaVinci Laboratories [close]: mixed record: 'DAVINCI' profile is dominated by DaVinci Baby cribs; SS_ totals not brand-specific; only the ADK listing is DaVinci Laboratories; sheet third-party (Pattern.) confirmed
- FNCE 2025 | Five Plus Protein [not found]: no brand record on two attempts (Five Plus Protein, Five Plus); industry-level email
- FNCE 2025 | Fresh Blends [not found]: no brand record on two attempts (Fresh Blends, FreshBlends); industry-level email; weaker fit: foodservice beverage brand
- FNCE 2025 | Heavenly Foods [close]: SmartScout record is under 'Heavenly Waffles' (product line name)
- FNCE 2025 | Keep Moving Inc. - gutzy organic [not found]: combined exhibitor name; queried Gutzy Organic (brand), 'Gutzy' record empty; industry-level email
- FNCE 2025 | Purity Coffee [exact]: sheet had no seller info; fresh data shows brand direct
- FNCE 2025 | Redmond Real Salt [exact]: sheet Brand (Seller Central) confirmed; very large brand, narrow ask
- FNCE 2025 | Resbiotic Nutrition, Inc. [exact]: sheet third-party (LUMlNlZE) confirmed; LUMlNlZE may be an affiliated account, verify
- FNCE 2025 | SimplyThick [exact]: sheet Brand (Seller Central); fresh data shows 32% resellers (Mixed)
- FNCE 2025 | Splenda [exact]: sheet Amazon (Vendor) confirmed; large brand, narrow ask
- FNCE 2025 | Standard Process [exact]: sheet third-party (Pattern.) confirmed; large brand, narrow ask
- FNCE 2025 | That's it. Nutrition [exact]: sheet sold_by Unknown; fresh data shows brand direct
- FNCE 2025 | Thick-It/Kent-Precision Foods Group, Inc. [exact]: sheet Amazon (Vendor) confirmed; combined exhibitor name; queried Thick-It
- FNCE 2025 | ZEGO [exact]: sheet third-party (Exo global distribution) confirmed; brand account present at 8.8%
- Las Vegas Souvenir & Resort Gift Show 2026 | A.T. Storrs Ltd. [not found]: no brand record on two attempts (A.T. Storrs, A.T. STORRS); industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Advance Wildlife Education [not found]: no brand record on two attempts; industry-level email; weaker fit: small publisher
- Las Vegas Souvenir & Resort Gift Show 2026 | AdventureKEEN [close]: SmartScout record is under imprint 'Adventure Publications'; weaker fit: book publisher, Amazon 1P
- Las Vegas Souvenir & Resort Gift Show 2026 | Ahead LLC [wrong match]: 'Ahead' matched an unrelated drum accessories brand; industry-level email from row info
- Las Vegas Souvenir & Resort Gift Show 2026 | American Backcountry [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Avalon Meat Candy [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Bigfoot Sock Co / Sock Harbor [not found]: combined exhibitor name; queried Bigfoot Sock Co. (Sock Harbor not queried); no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Blue Planet Eco-Eyewear [wrong match]: 'Blue Planet' matched Blue Planet Surf (balance boards); full name returned empty; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Boardwalk Puzzles [not found]: no brand record on two attempts (Boardwalk Puzzles, Boardwalk Puzzle); sheet mentions a Dowdle storefront page, not queried; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Conscious Step [not found]: brand record returned 0 products on two attempts; industry-level email; sheet Brand (Seller Central)
- Las Vegas Souvenir & Resort Gift Show 2026 | Dutch American Import Co., Inc. [not found]: no brand record on two attempts (Dutch American Import Co, Dutch American Imports); industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | END SMALL TALK [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Fifth Avenue Manufacturers [not found]: no brand record on two attempts; industry-level email; weaker fit: souvenir manufacturer, likely wholesale-first
- Las Vegas Souvenir & Resort Gift Show 2026 | Forest Life Creations [not found]: no brand record on two attempts; industry-level email; weaker fit: small handmade maker
- Las Vegas Souvenir & Resort Gift Show 2026 | Gear Lifestyle Brands (Champion, UA, Gear For Sports, Comfort Wash, Alternative Apparel) [not found]: combined exhibitor name; queried Gear For Sports (licensee brand); Champion, UA, Comfort Wash, Alternative Apparel not queried; no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Gecko Hawaii [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | GetAGadget, Inc [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Global SWIBCO, Inc. [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Glyder LLC [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | GUIDES CHOICE [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | LEIGHTWORKS [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | MY ARCADE / dreamGEAR, LLC [exact]: sheet Amazon (Vendor) confirmed; profile pulled on run_query retry; combined exhibitor name; queried My Arcade
- Las Vegas Souvenir & Resort Gift Show 2026 | Pilgrim Imports Inc. [not found]: brand record returned 0 products on two attempts; industry-level email; sheet third-party (Alaskan Connection)
- Las Vegas Souvenir & Resort Gift Show 2026 | Pucker Powder by Creative Concepts [exact]: sheet says third-party (Creative-Concepts); Creative Concepts is the exhibitor's own company, treated as brand direct
- Las Vegas Souvenir & Resort Gift Show 2026 | Savvy Sox [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Spirit Jersey® [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | The Landmark Project [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Uzzi [not found]: brand record returned 0 products on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Valani Apparel [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | West Coast Sunglasses, Inc. [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Wild Tribute [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Wilmot Harvey [not found]: no brand record on two attempts; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | YRI Belts [not found]: no brand record on two attempts; industry-level email
- FLIBS 2026 | Allied Marine [wrong match]: wrong match: sheet mapped exhibitor to Allied Flag & Frame (unrelated); SS_ numbers are for Allied Flag, not Allied Marine; weaker fit: yacht brokerage and dealer
- FLIBS 2026 | Aspen [wrong match]: wrong match: 'Aspen' matched back braces; sheet listing is Aspen cologne; exhibitor is Aspen Power Catamarans; weaker fit: boat builder
- FLIBS 2026 | Bertram [wrong match]: wrong match: 'Bertram' matched essential oils; sheet listing is a book; exhibitor is Bertram Yachts; weaker fit: yacht builder
- FLIBS 2026 | CMOR Mapping [not found]: no brand record on two attempts; industry-level email
- FLIBS 2026 | Cummins [close]: record is the whole Cummins consumer catalog (inverters, Onan, Fleetguard); Cummins Marine not separately visible; sheet Amazon (Vendor); fresh data shows Mixed with dealers over half; large company, narrow ask
- FLIBS 2026 | flite [wrong match]: wrong match: 'Flite' matched FliteBMX; sheet's 'sold by FliteBMX' is the same unrelated company; weaker fit: premium eFoil, dealer-led
- FLIBS 2026 | Honda Marine [close]: record is all of Honda on Amazon (generators, auto fluids); Honda Marine not separately visible; sheet third-party (G.P.S.) confirmed; very large brand, narrow ask
- FLIBS 2026 | KOAH [close]: mixed record: 'Koah' brand on Amazon is mostly Focus Camera's Koah accessory line; SS_ totals not the exhibitor's; email uses only the spearfishing seller data; sheet third-party (Focus Camera) is the unrelated brand's seller
- FLIBS 2026 | KVH Industries [exact]: sheet third-party (The Factory Depot) confirmed; tiny record
- FLIBS 2026 | Multiplex GmbH [wrong match]: wrong match: 'Multiplex' matched lab beakers; sheet listing unrelated; exhibitor product line unclear; weaker fit
- FLIBS 2026 | Nimbus [wrong match]: wrong match: 'Nimbus' matched a toothbrush brand; sheet store (ZenEssence) is the same unrelated brand; exhibitor is Nimbus Boats; weaker fit: boat builder
- FLIBS 2026 | Paddle North [exact]: sheet Brand (Seller Central) confirmed; sheet says brand store, fresh data shows no storefront
- FLIBS 2026 | QMI [wrong match]: wrong match: 'QMI' matched fender trim; sheet listing unrelated; weaker fit: OEM supplier
- FLIBS 2026 | Salty Dawgs [not found]: no brand record on two attempts; industry-level email; sheet sold_by Unknown
- FLIBS 2026 | Sancochos [not found]: no brand record on two attempts; industry-level email; sheet sold_by Unknown; product line unclear
- FLIBS 2026 | Scania/Mack Boring & Parts Co. [not found]: combined exhibitor name; queried SCANIA SWEDEN (sheet brand name) and Scania; no brand record on two attempts; industry-level email; weaker fit: engine distributor
- FLIBS 2026 | Solara [exact]: sheet third-party (JJ Online store); fresh data shows Carbon Beauty at 90%, may be an affiliated account, verify
- FLIBS 2026 | Suzuki Marine [close]: mixed record: 'Suzuki' on Amazon is mostly Suzuki musical instruments; SS_ totals not marine-specific; sheet third-party (Central Florida PowerSports) confirmed for marine listings; large brand, narrow ask
- FLIBS 2026 | Teakdecking Systems [exact]: sheet says brand store; fresh data shows no storefront and Mixed sellers
- FLIBS 2026 | The Brass Works [wrong match]: wrong match: sheet mapped exhibitor to Brasso (Reckitt) storefront; SS_ numbers are Brasso's; weaker fit: custom marine hardware
- FLIBS 2026 | Tommy Bahama [exact]: sheet third-party (Underware House); fresh data shows Amazon 1P 81% (Amazon 1P); very large brand, narrow ask
- FLIBS 2026 | Volvo Penta [exact]: sheet third-party (LEADERS RPM) confirmed; large brand, narrow ask
- FLIBS 2026 | Yamaha Marine [close]: mixed record: 'YAMAHA' on Amazon is mostly musical instruments; SS_ totals not marine-specific; sheet third-party (Pine Grove Powersports); very large brand, narrow ask
- FNCE 2025 | Aonic Inc. [exact]: sheet says brand store; fresh data shows no storefront
- FNCE 2025 | Applegate [exact]: sheet Amazon (Vendor) confirmed; Whole Foods Market counted as third-party per rule but is Amazon-owned; very large brand, narrow ask
- FNCE 2025 | Cargill [exact]: sheet third-party (FoodserviceDirect) confirmed; weaker fit: B2B ingredient company
- FNCE 2025 | CommonGround [wrong match]: wrong match: 'Common Ground' matched a shampoo brand; sheet listing is a book; org_type: likely nonprofit or advocacy program, weak fit
- FNCE 2025 | Daily Crunch Inc. [exact]: sheet Brand (Seller Central); fresh data shows ~40% resellers (Mixed)
- FNCE 2025 | Sunsweet Growers, Inc. [exact]: sheet sold_by Unknown; fresh data shows Mixed with ~69% resellers
- FNCE 2025 | WILDE Brands [exact]: sheet Brand (Seller Central) confirmed; hybrid with Amazon 1P at 16%
- FNCE 2025 | Zesty Z - Perfect Pita Chips [exact]: sheet says brand store; fresh data shows no storefront
- Las Vegas Souvenir & Resort Gift Show 2026 | CoTa Global [exact]: sheet third-party (Mozlly); Mozlly may be an affiliated account, verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Neil Enterprises [wrong match]: wrong match: sheet mapped exhibitor to NeilMed storefront; SS_ numbers are NeilMed's; exhibitor product line assumed from name, verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Parks Project [not found]: brand record returned 0 products on two attempts; industry-level email; sheet third-party (Backcountry)
- Las Vegas Souvenir & Resort Gift Show 2026 | Pennybandz, LLC [exact]: sheet says brand store; fresh data shows no storefront
- Las Vegas Souvenir & Resort Gift Show 2026 | Pillzar LLC [exact]: sheet Brand (Seller Central) confirmed; low rating
- Las Vegas Souvenir & Resort Gift Show 2026 | Pyvot [exact]: sheet third-party (Levinsohn Textile); may be the parent company, verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Ranger Industries LLC [close]: sheet brand name 'Ranger Pro' is an unrelated herbicide; used 'Ranger Industries' record instead, verify it is the exhibitor; sheet third-party confirmed
- FLIBS 2026 | Aqua Nautica USA [wrong match]: no brand record on two attempts; sheet mapped to unrelated Nautica storefront; industry-level email
- FLIBS 2026 | AquaVue Tech Co [wrong match]: no brand record on two attempts; sheet mapped to unrelated AQUA-TECH listing; industry-level email
- FLIBS 2026 | Axalta Coatings System [not found]: no brand record on two attempts; industry-level email; weaker fit: B2B coatings company
- FLIBS 2026 | Bisous [close]: verify identity: exhibitor listed as 'Bisous'; sheet and SmartScout record are Bisousweet Confections muffins; may be a different company; sheet third-party (Whole Foods Market)
- FLIBS 2026 | BLU3 / SeaNXT / JayKay / Lift Foils [exact]: combined exhibitor name; queried BLU3 (first brand); SeaNXT, JayKay, Lift Foils not queried; sheet Brand (Seller Central) confirmed
- FLIBS 2026 | Bolt Depot [wrong match]: brand record returned 0 products; sheet mapped to unrelated BoltsandNuts.com storefront; industry-level email
- FLIBS 2026 | Chris-Craft [not found]: no brand record on two attempts; industry-level email; weaker fit: boat builder
- FLIBS 2026 | CIRO Marine [wrong match]: wrong match: 'CIRO' matched a motorcycle accessories brand; sheet listing (sold by Gritr) is the same unrelated brand; industry-level email
- FLIBS 2026 | CMC Marine Corp [wrong match]: wrong match: 'CMC' matched unrelated T-H Marine parts and piano books; industry-level email; weaker fit: OEM stabilizer manufacturer
- FLIBS 2026 | Cody's Fish [wrong match]: no brand record on two attempts; sheet mapped to unrelated Cody Johnson storefront; industry-level email
- FLIBS 2026 | Colnago USA [not found]: brand record returned 0 active products on two attempts; industry-level email; weaker fit: dealer-led premium brand
- FLIBS 2026 | Dockmate USA [wrong match]: wrong match: 'Dockmate' record and sheet storefront are an unrelated dock guard brand; exhibitor is the Dockmate wireless docking system; weaker fit: dealer-installed system
- FLIBS 2026 | Dockside Pros [not found]: no brand record on two attempts; industry-level email; weaker fit: likely services company
- FLIBS 2026 | Dusky Marine, Inc. [not found]: no brand record on two attempts; industry-level email; weaker fit: boat builder
- FLIBS 2026 | FERRETTI GROUP [wrong match]: no brand record on two attempts; sheet mapped to unrelated Rossano Ferretti listing; industry-level email; weaker fit: yacht builder
- FLIBS 2026 | Force-e [wrong match]: no brand record on two attempts; sheet mapped to unrelated Force Factor storefront; industry-level email; weaker fit: dive retailer
- FLIBS 2026 | FreedomLift [wrong match]: no brand record on two attempts; sheet mapped to unrelated Freedom Offroad listing; industry-level email; weaker fit: dealer-installed equipment
- FLIBS 2026 | Gloria Keg [wrong match]: wrong match: 'GLORIA' matched dollhouse furniture; sheet storefront unrelated; exhibitor product line unclear; industry-level email
- FLIBS 2026 | Hooker Pumps [wrong match]: wrong match: 'Hooker' matched Holley exhaust parts; sheet listing unrelated; industry-level email; weaker fit: OEM pump manufacturer
- FLIBS 2026 | ICOM America [exact]: sheet sold_by Unknown; fresh data shows Third-party resellers
- FLIBS 2026 | Imtra [not found]: brand record returned 0 active products on two attempts; industry-level email; weaker fit: marine distributor
- FLIBS 2026 | Inflatable Boat Pro [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email; weaker fit: likely retailer
- FLIBS 2026 | Island Optics Polarized Sunglasses [wrong match]: wrong match: sheet mapped to Optic Nerve storefront; SS_ numbers are Optic Nerve's; Island Optics not found; industry-level email
- FLIBS 2026 | Jeanneau America [not found]: no brand record on two attempts; industry-level email; weaker fit: boat builder
- FLIBS 2026 | Koenig Polish [close]: record is 'Koenig' (single spray polish listing); verify it is the exhibitor's product; sheet third-party (Alubix) confirmed
- FLIBS 2026 | KScott Art & Apparel [not found]: no brand record on two attempts; industry-level email; sheet third-party (CHAOS Fishing)
- FLIBS 2026 | LaPorte Products [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email; exhibitor product line unclear
- FLIBS 2026 | Leak Stop Gun [wrong match]: wrong match: sheet mapped to Leak Saver storefront; SS_ numbers are Leak Saver's; Leak Stop Gun not found; industry-level email
- FLIBS 2026 | Life League Gear | Lobster League [not found]: combined exhibitor name; queried Life League Gear (first brand) and Lobster League; both empty; industry-level email
- FLIBS 2026 | Lowrance, Simrad, B&G [exact]: combined exhibitor name; queried Lowrance (first brand) and Simrad; B&G not queried; SS_ columns hold Lowrance data; sheet sold_by Unknown; fresh data shows Mixed; very large brand, narrow ask
- FLIBS 2026 | Mabru [not found]: no brand record on two attempts; industry-level email; weaker fit: installer-led equipment
- FLIBS 2026 | Merle Wood & Associates [wrong match]: no brand record; sheet mapped to unrelated Merle Norman listing; industry-level email; weaker fit: yacht brokerage
- FLIBS 2026 | Novurania of America, Inc. [not found]: no brand record on two attempts; industry-level email; weaker fit: boat builder
- FLIBS 2026 | Ocean Alexander [not found]: no brand record on two attempts; sheet brand name 'Ocean' unrelated; industry-level email; weaker fit: yacht builder
- FLIBS 2026 | Ocean-Tamer Inc. [exact]: sheet says brand store; fresh data shows no storefront
- FLIBS 2026 | Ring Power Cox Marine [wrong match]: combined exhibitor name; queried Ring Power and Cox Marine; both empty; sheet mapped to unrelated Ring storefront; weaker fit: dealer
- FLIBS 2026 | Rio Life Hats [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email
- FLIBS 2026 | Seaward Automation [not found]: brand record returned 0 active products on two attempts; industry-level email; weaker fit: B2B automation
- FLIBS 2026 | Seawater Pro [wrong match]: no brand record on two attempts; sheet listing unrelated; industry-level email
- FLIBS 2026 | Secured Safety Solutions [wrong match]: wrong match: sheet mapped to Secure Safety Solutions (Personal Safety Corporation) storefront; SS_ numbers are that brand's; industry-level email; exhibitor product line unclear
- FLIBS 2026 | Sessa International S.R.L. [wrong match]: wrong match: sheet mapped to Sessa Syrups storefront; SS_ numbers are Sessa Syrups'; Sessa Marine not found; weaker fit: boat builder
- FLIBS 2026 | Sharrow Marine [wrong match]: wrong match: 'SHARROW' matched an archery brand; sheet storefront is the same unrelated brand; Sharrow Marine not found; weaker fit: dealer-led premium product
- FLIBS 2026 | Signal Marine [exact]: sheet Brand (Seller Central) confirmed; exhibitor listed as Signal Marine, brand is Sirius Signal
- FLIBS 2026 | Silwy Magnetic Drink & Tableware [exact]: sheet says Amazon (Vendor) with brand store; fresh data shows one reseller listing only; trusting fresh, partial record
- FLIBS 2026 | SIMRAD by Kongsberg [close]: cached Simrad record reflects the Navico recreational brand, not the Kongsberg professional division; sheet sold_by Unknown; fresh data shows Mixed; weaker fit: commercial marine electronics
- FLIBS 2026 | Smith Sport Optics, Inc. [close]: 'Smith' record includes unrelated Smith brands (torches, paper); SS_ totals not fully brand-specific; sheet third-party (Pure luxury); fresh data shows Mixed with brand account at 64%; very large brand, narrow ask
- FLIBS 2026 | SoFlo Customs / Apocalypse 6x6 [not found]: combined exhibitor name; queried SoFlo (first brand); Apocalypse 6x6 not queried; brand record returned 0 products on two attempts; industry-level email; weaker fit: custom vehicle builder
- FLIBS 2026 | Spectra Watermakers/Katadyn Desalination [wrong match]: combined exhibitor name; queried SPECTRA (sheet brand) and Spectra Watermakers; Katadyn not queried; wrong match: SPECTRA record and sheet storefront are Spectra Baby; weaker fit: installer-led equipment
- FLIBS 2026 | Star Blink Products [wrong match]: no brand record on two attempts; sheet mapped to Amazon-owned Blink storefront; industry-level email; exhibitor product line unclear
- FLIBS 2026 | Star Glow & Magic Bling [exact]: sheet Brand (Seller Central) confirmed; exhibitor listed as Star Glow & Magic Bling, brand is Ultra-Glow Super Stars
- FLIBS 2026 | Sterling Associates [not found]: no brand record; sheet listing unrelated; industry-level email; weaker fit: yacht brokerage
- FLIBS 2026 | Teak Deck Companay [wrong match]: wrong match: sheet mapped to Teakdecking Systems storefront (different company, row 284); SS_ numbers are Teakdecking Systems'; industry-level email
- FLIBS 2026 | Tees By Bo [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email
- FLIBS 2026 | TEKTITE SOSeFLARE [exact]: sheet says brand store; fresh data shows no storefront; sheet Brand (Seller Central) confirmed
- FLIBS 2026 | Teledyne FLIR/Raymarine [exact]: combined exhibitor name; queried FLIR (first brand, SS_ columns) and Raymarine (in email); sheet sold_by Unknown; FLIR shows Third-party resellers (partner account), Raymarine dealers; very large brand, narrow ask
- FLIBS 2026 | Titan Marine Air [wrong match]: wrong match: 'TITAN' record and sheet storefront are a generic unrelated brand; Titan Marine Air not found; weaker fit: installer-led equipment
- FLIBS 2026 | Veco USA [wrong match]: wrong match: 'VECO' record and sheet storefront are an unrelated spray bottle brand; Veco USA not found; weaker fit: installer-led equipment
- FLIBS 2026 | VETUS Maxwell [close]: combined exhibitor name; queried VETUS (first brand); MAXWELL record is an unrelated foot switch brand; 'Vetus' record includes a few unrelated listings; SS_ totals approximate; sheet third-party (Performance Guarantee) confirmed
- FLIBS 2026 | Viking Life Saving Equipment [not found]: no brand record on two attempts; industry-level email; weaker fit: commercial safety equipment; sheet third-party (Harvard Marine)
- FLIBS 2026 | WATERWAYZ [wrong match]: no brand record on two attempts; sheet listing unrelated; industry-level email; exhibitor product line unclear
- FLIBS 2026 | Wellcraft [not found]: brand record returned 0 active products on two attempts; industry-level email; weaker fit: boat builder
- FLIBS 2026 | Zeelander [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email; weaker fit: yacht builder
- FNCE 2025 | Amylu Foods [exact]: sheet third-party (Whole Foods Market); Whole Foods counted as third-party per rule but is Amazon-owned (effectively vendor)
- FNCE 2025 | AngelEye Health [close]: verify identity: exhibitor listed as AngelEye Health; sheet and SmartScout record are Mt. Angel Vitamins; sheet third-party (Holly Hill Health Foods); fresh data shows Mixed with brand account at 78%
- FNCE 2025 | Bio-K+ USA [exact]: sheet third-party (SPOTLIGHT 7) confirmed; fresh data shows Mixed with Amazon 1P at 56%
- FNCE 2025 | Brazi Bites [exact]: sheet Amazon (Vendor) confirmed; Whole Foods Market counted as third-party per rule but is Amazon-owned
- FNCE 2025 | Cahokia Rice [exact]: sheet Amazon (Vendor); fresh data shows Mixed with resellers at ~60%
- FNCE 2025 | Cleveland Kitchen [exact]: sheet Amazon (Vendor); fresh data shows Third-party resellers (Eternity Essentials, Whole Foods)
- FNCE 2025 | CON-CRĒT [exact]: sheet third-party (Vireo Systems); Vireo Systems is the parent company, treated as brand direct
- FNCE 2025 | Eggland's Best, Inc. [exact]: sheet third-party (Amazon Now); fresh data shows Amazon 1P 100%; weaker fit: fresh grocery
- FNCE 2025 | Silver Star Nutrition [exact]: verify identity: exhibitor listed as Silver Star Nutrition; sheet and SmartScout record are Sovereign Silver; sheet third-party (LUMlNlZE) confirmed; LUMlNlZE may be an affiliated account, verify; large brand
- FNCE 2025 | Solara Labs [exact]: same brand as FLIBS row 279 (Solara); cached record reused; sheet third-party (JJ Online store); fresh data shows Carbon Beauty at 90%, may be an affiliated account, verify
- FNCE 2025 | Sunnygem LLC [exact]: sheet says brand store; fresh data shows no storefront; sheet Brand (Seller Central) confirmed
- FNCE 2025 | The Wonderful Company [exact]: sheet Amazon (Vendor) confirmed; very large brand, narrow ask
- FNCE 2025 | Tiiga [exact]: sheet says brand store; fresh data shows no storefront; sheet Brand (Seller Central) confirmed
- FNCE 2025 | Tribe Nutrition [exact]: verify identity: exhibitor listed as Tribe Nutrition; sheet and SmartScout record are Alpha Tribe; sheet Brand (Seller Central) confirmed
- FNCE 2025 | UP2U [not found]: no brand record on two attempts; sheet listing is a book; industry-level email; exhibitor product line unclear, weak fit
- FNCE 2025 | VSL#3 / Actial Nutrition, Inc. [exact]: combined exhibitor name; queried VSL #3; sheet says brand store; fresh data shows no storefront; sheet Brand (Seller Central) confirmed
- FNCE 2025 | wildbrine [exact]: sheet third-party (Whole Foods Market) confirmed; Whole Foods counted as third-party per rule but is Amazon-owned
- FNCE 2025 | Yaza [exact]: seller query returned empty; seller taken from sheet (Whole Foods Market); low rating
- Las Vegas Souvenir & Resort Gift Show 2026 | Crazy Apparel Inc. [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Culver Industries, Inc. [wrong match]: wrong match: 'Culver' record is a glassware brand; sheet storefront (Culver LED) unrelated; exhibitor product line unclear; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Desert Sunglass of Scottsdale [not found]: no brand record on two attempts; sheet listing unrelated; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | DMR Creative [wrong match]: wrong match: 'DMR' record is a bike parts brand; 'DMR Creative' returned empty; sheet seller unknown; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Mermaid Soul [not found]: no brand record on two attempts; sheet listing is a book; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Miss Hannah's Gourmet Popcorn [exact]: sheet Brand (Seller Central) confirmed; fresh data shows no storefront flag though sheet found a brand store
- Las Vegas Souvenir & Resort Gift Show 2026 | Momentum Comfort Gear [wrong match]: wrong match: 'Momentum' record unrelated; 'Momentum Comfort Gear' returned empty; sheet Amazon (Vendor) not confirmed; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Mug Experience [not found]: empty brand record on two attempts; sheet third-party (Hour Loop); industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Norty Footwear & Clothing [exact]: sheet third-party (BCClothing) confirmed; BCClothing may be Norty's own account, verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Openers Plus [exact]: sheet Brand (Seller Central) confirmed; exhibitor Openers Plus, brand on Amazon is magic Opener
- Las Vegas Souvenir & Resort Gift Show 2026 | Pacific North Nest Designs [wrong match]: wrong match: sheet mapped exhibitor to NEST New York (home fragrance), unrelated; 'Pacific North Nest' returned empty; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Pearson Ranch Elk & Bison Jerky [exact]: sheet third-party (Tru Inertia) confirmed; Tru Inertia may be an affiliated account, verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Perrin Sportswear [wrong match]: wrong match: 'PERRIN' record is automotive; sheet listing is a print-on-demand shirt sold by Amazon; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Planet Cotton/ Blue Moon [not found]: no brand record on two attempts; sheet mapped to little planet by carter's, unrelated; 'Blue Moon' returned unrelated music record; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Please Please Me [not found]: no brand record on two attempts; sheet listing seller unknown; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Pocket Products, LLC [not found]: no brand record on two attempts; sheet mapped to Pocket AI storefront, likely unrelated; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | Prairie Mountain [not found]: no brand record on two attempts; sheet listing is a print-on-demand shirt; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | R.F.S.J. Inc. [exact]: sheet third-party (Sports Team Accessories) confirmed; may be RFSJ's own account, verify; fresh data shows no storefront flag though sheet found a brand store
- Las Vegas Souvenir & Resort Gift Show 2026 | Ramatex International [close]: sheet third-party (SPLG Products); fresh data shows Jetienne as the seller; close match: exhibitor Ramatex International, record Ramatex
- Las Vegas Souvenir & Resort Gift Show 2026 | Redneck Sunscreen LLC [exact]: sheet Brand (Seller Central) confirmed; fresh data shows no storefront flag though sheet found a brand store
- Las Vegas Souvenir & Resort Gift Show 2026 | Tipsy [close]: verify identity: exhibitor 'Tipsy' at a gift show; Amazon record is the Tipsy audio brand (TipsyAuthen / TipsyAudio) per sheet store URL; sheet Brand (Seller Central) confirmed
- Las Vegas Souvenir & Resort Gift Show 2026 | Topline Products, Inc. [close]: verify identity: exhibitor Topline Products, Inc.; Amazon record is TOPLINE TOOLS per sheet store URL; sheet Brand (Seller Central) confirmed; Topline retail Solutions (15%) treated as affiliated, verify
- Las Vegas Souvenir & Resort Gift Show 2026 | Tortuga Moon - Cole Apparel [not found]: empty brand record on two attempts; sheet mapped to Tortuga Rum Cake storefront, unrelated; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | TRAVEL SIZE DEPOT [wrong match]: wrong match: sheet mapped exhibitor to Travel Depot (automotive), unrelated; 'Travel Size Depot' returned empty; industry-level email
- Las Vegas Souvenir & Resort Gift Show 2026 | TrendSetterTees, LLC. [not found]: no brand record on two attempts; sheet listing is a print-on-demand shirt; industry-level email
