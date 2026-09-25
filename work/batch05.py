from batchlib import *
raw={
"Honey House Naturals":RAW(P("Honey House Naturals","Beauty & Personal Care","Body Lotions",1.93,"Honey House Naturals",True,"https://www.amazon.com/stores/HoneyHouseNaturals/page/3620B88A-51FC-4F07-A54D-7E48F9B0BF00",0,-0.1,0.006,15.17,4.4,28,2605,7181.39,131677.6),
 S(("Honey House Naturals",48.525),("HeredomUs",40.6),("Leathnu Co.",9.817),("TartBurners and More",0.527),("UneekItems",0.49),("Amazon.com",0.042)),
 T(("Honey House Naturals Hawaiian Bee Bar Beeswax Lotion, 2 Oz","B002SDVHPY",1302),("Honey House Naturals Vanilla Bee Bar, Large, 2 Ounce","B000XVA2EK",1213.38),("Honey House Naturals Lip Butter Gift Set, 5 Piece","B079DXG12M",596.85),("Honey House Naturals Baby Belly Bar Solid Lotion Bar, 1.7 oz","B001BPH6D2",492.71),("Honey House Naturals Lavender Bee Bar, Large, 2 Ounce","B004HZ8ZAG",393))),
"EAGLE CREST":RAW(P("EAGLE CREST","Clothing, Shoes & Jewelry","Men's Baseball Caps",3.15,"",False,"",0,-0.231,-0.48,20.97,4.67,20,4965,6780.14,133305.51),
 S(("Armed Forces Depot",59.396),("Hour Loop",18.497),("Only Good Wholesale",7.593),("Artisan Owl",5.263),("Zentra, LLC",4.315),("AT TEN, LLC",1.74)),
 T(("EAGLE CREST U.S. Air Force Retired Baseball Cap Navy Blue","B00H9H0POS",3057.6),("EAGLE CREST U.S. Air Force Retired Cap, Washed Denim Blue","B010GMLEUG",396.8),("United States Marine Corps Semper Fidelis Challenge Coin","B017O00A4O",353),("Navy Shellback Crossing the Line OD Green Low Profile Cap","B008UK6XS0",318.3),("Operation Desert Storm Veteran Challenge Coin","B007HBMEE0",288.4))),
"Hang Loose Bands":RAW(P("Hang Loose Bands","Clothing, Shoes & Jewelry","Women's Strand Bracelets",0.98,"HangLooseBands",True,"https://www.amazon.com/stores/HangLooseBands/page/1115AAB2-92AC-4D8F-86EE-C14BE6F6160D",0,-0.367,-0.174,9.99,4.45,99,298,5214.78,285188.24),
 S(("HangLooseBands",100)),
 T(("Hang Loose Bands Coastal Malibu Blue Bracelet | 6.5 - Small","B09B15JQKH",239.76),("Hang Loose Bands Fish Skins Brown Trout Bracelet | 7.5 - Medium","B0GGTFLDKN",229.77),("Hang Loose Bands Coastal Pink Sea Turtle Bracelet | 6.5 - Small","B0DFQKTRDL",199.8),("Hang Loose Bands Mountain Tops Bracelet | 6.5 - Small","B0CG7G927C",199.8),("Hang Loose Bands Coastal Navy Blue Bracelet | 7.5 - Medium","B0DFMVFXTR",159.84))),
"L'ovedbaby":RAW(P("L'ovedbaby","Clothing, Shoes & Jewelry","Baby Boys' One-Piece Footies",0.89,"Amazon.com",False,"",0.177,-0.177,-0.637,33.88,4.48,82,2283,5667.01,68912.34),
 S(("Marketplace Valet",82.258),("Amazon.com",17.742)),
 T(("L'ovedbaby Unisex Baby Organic Cotton Snap Footie, Black, 0-3 Months","B077DYGT8Z",3083.34),("L'ovedbaby Baby Girls Organic Snap One Piece Footies, Seafoam, 0-3 Months","B00O0O46AC",350.91),("L'ovedbaby Baby Girls Organic Snap One-Piece Footies, Gray, 3-6 Months","B00I14VMZY",350.91),("L'ovedbaby Baby Girls Organic Snap One-Piece Footies, Mauve, Preemie/NB","B00IIJA5T6",276.99),("L'ovedbaby Baby Girls Organic Snap One-Piece Footies, Seafoam, Preemie/NB","B00O0O41OI",242.97))),
"VINRELLA":RAW(P("VINRELLA","Clothing, Shoes & Jewelry","Stick Umbrellas",1.24,"Vinrella",True,"https://www.amazon.com/stores/Vinrella/page/59B0831D-4888-4B33-A228-AA765A3B2F6D",0,-0.284,-0.255,29.68,4.55,29,1692,4686.05,84492.36),
 S(("Garden Works | Star Kitchen & Home",96.946),("Vinrella",3.054)),
 T(("VINRELLA Rain & Sun Bucket Hat for Women, Red","B07T43RKWQ",560),("VINRELLA Rain & Sun Bucket Hat for Women, Black","B07T5716MV",520),("Rose Labeled Wine Bottle Umbrella","B07HRXJ1X3",335.4),("VINRELLA Wine Bottle Umbrella, Misty Spirits","B01N7TTWGK",279.5),("VINRELLA Wine Bottle Umbrella, Bloom","B08HPMKDGG",251.55))),
"First & Main":RAW(P("First & Main","Toys & Games","Stuffed Animals & Teddy Bears",5,"Amazon.com",False,"",0,0.222,None,22.39,4.7,3,1598,4212.2,42128.24),
 S(("Sunrite Gifts",79.218),("Imperio Nygren",11.827),("Hour Loop",8.873),("The Mulberry Shop",0.082)),
 T(("First & Main 13\" Melancholy Melanie Puppy Dog","B00QSBCZXA",2123.94),("First & Main 10\" Melancholy Mel Puppy Dog","B01F5XEKIO",1941.4),("First & Main 8\" Brown Tender Teddy Bear","B0013FSKM6",146.86))),
"Agoge":RAW(P("Agoge","Health & Household","Sports Nutrition Hemp Protein Powders",1,"",False,"",0,-0.171,None,52.68,4.15,4,41,3041.53,18764.85),
 S(("Agoge Organic Hemp Protein",100)),
 T(("Agoge USDA Organic Hemp Protein Powder, Vanilla, 20 Servings","B0GLH4F7TZ",1052.98),("Agoge USDA Organic Hemp Protein Powder, Matcha, 20 Servings","B0GLH1F3KT",944.79),("Agoge USDA Organic Hemp Protein Powder, Chocolate, 20 Servings","B0GLHF7LP8",765.66),("Agoge USDA Organic Hemp Protein Powder, Unflavored, 20 Servings","B0GLH14369",278.1))),
"The Jonsteen Company":RAW(P("The Jonsteen Company","Patio, Lawn & Garden","Tree Plants & Seeds",0.78,"The Jonsteen Company",True,"",None,-0.017,None,22.64,4.32,9,5182,2747.63,101797.4),
 S(("The Jonsteen Company",80.435),("Japanese Maples and Evergreens",11.916),("Atharva Brands",7.65)),
 T(("Giant Sequoia | Small Tree Seedling | The Jonsteen Company","B00HZR1XQG",1288.99),("Giant Sequoia | Tree Seed Grow Kit | The Jonsteen Company","B019J9KMS2",634.98),("Japanese Maple | Small Tree Seedling | The Jonsteen Company","B00K0NCNNY",327.4),("Bonsai Tree Bundle | Collection of 5 Live Tree Seedlings","B0778VH89S",289.95),("Dawn Redwood | Medium Tree Seedling | The Jonsteen Company","B0CHNB1MCX",161.34))),
"Americaware":RAW(P("Americaware","Kitchen & Dining","Mugs",2.69,"",False,"",0,-0.4,None,20.84,4.7,13,675,2588.55,21739.76),
 S(("Artisan Owl",53.356),("Zentra, LLC",37.411),("AT TEN, LLC",5.685),("Americaware Inc",3.549)),
 T(("Americaware Alaska 18oz. Emblem Coffee Mug","B0163EPOMA",459.48),("Americaware 18oz Big Foot Emblem Mug","B094K4Z7QN",388.74),("Americaware Colorado 22 oz Night Sky Silhouette Mug","B01LZGSZDH",271.74),("Americaware Nashville 18oz. Color Relief Coffee Mug","B01LY5YXG7",261.56),("Americaware Big Foot Beige 18oz Emblem Mug","B0BNP3B44J",214.74))),
"Jacobson Hat Company":RAW(P("Jacobson Hat Company","Clothing, Shoes & Jewelry","Men's Military Accessories",1.4,"",False,"",0,-0.339,None,19.26,4.32,10,3408,2476.37,141714.77),
 S(("Gettysburg Souvenirs & Gifts",37.605),("Arlene's Costumes",29.212),("Atharva Brands",17.195),("Zentra, LLC",5.025),("CostumeVille",4.429),("ExceptionalThings",3.39)),
 T(("100% Wool Civil War Union Kepi Replica Hat S/M","B01BMV9UOC",1015.2),("Statue of Liberty Headband Green","B07XF8RRG7",494.55),("Jacobson Hat Company Men's Tricorne Hat with Snaps, Black","B00BCR8IUO",290.88),("Jacobson Hat Company Chicken Rooster Plush Mask Hat, Red","B014U7DXNO",256.75),("Jacobson Hat Company French Fries Novelty Food Hat, Red","B01IWAQEUO",194.87))),
"Seawag":RAW(P("Seawag","Cell Phones & Accessories","Waterproof Cell Phone Cases",1.17,"",False,"",0,0.128,None,31.02,4.58,12,293,2192.32,18715.06),
 S(("SEAWAG USA",70.598),("Diveland CZ",29.402)),
 T(("SEAWAG Waterproof Pouch for Smartphone Universal Size (Orange White)","B0F1K22DQP",377.58),("SEAWAG Next Waterproof Phone Pouch, 2 Pack Black","B0FHJPW4JT",349.5),("SEAWAG Waterproof Pouch for Smartphone Universal Size (Camouflage)","B0DZ6WH23W",261.12),("SEAWAG Next Waterproof Phone Pouch, 1 Pack Black","B0F1MW6ZLP",249.9),("SEAWAG Next Waterproof Phone Pouch, 2 Pack Black and White","B0FHJYKKVM",244.65))),
"Blossom Bucket":RAW(P("Blossom Bucket","Home & Kitchen","Collectible Figurines",2.83,"Hour Loop",False,"",0,-0.127,None,19.75,4.47,6,3562,1914,105572.77),
 S(("Hour Loop",96.695),("Abundantly Good",3.305)),
 T(("Friend Like Stars Angel with Flowers Resin Tabletop Figurine","B079TJ1QYX",914.5),("B-E-L-I-E-V-E Nativity Resin Christmas Decoration Set of 7 Letters","B00MEHLYY8",287.04),("Friends are A Gift Christmas Angel","B07HCX5SQB",266.22),("Blossom Bucket B-E-L-I-E-V-E Nativity Resin Christmas Decoration Set","B0F272K7MK",236.72),("Blossom Bucket Holy Family with Star","B00FNVKK2O",209.52))),
"Earthview":RAW(P("Earthview","Beauty & Personal Care","Dish Soap",1,"",False,"",0,-0.155,None,101.05,4.41,23,97,1847.58,25846.66),
 S(("Earthview Products Company",100)),
 T(("Earthview Fragrance Free Liquid Dish Soap, 2 Pk/ 24 oz","B086937JYN",395.88),("Earthview Fragrance Free Shampoo & Bodywash, 32 Fl Oz","B0BGJLHGZ1",281.94),("Earthview Fragrance Free Liquid Dish Soap, 128 Fl Oz (1-Gallon)","B01E8582WU",279.88),("Earthview Shampoo Bodywash, 128 Fl Oz, Scent Free","B01E918RLO",190),("Earthview Fragrance Free Liquid Dish Soap, 6 Pk/ 24 oz","B0H35GDWF9",159.9))),
"L W Bristol Classics":RAW(P("L W Bristol Classics","Sports & Outdoors","Trekking Poles",1.92,"Stateline Classics",False,"",0,-0.193,None,15.81,4.67,12,1113,1761.98,24430.76),
 S(("Zentra, LLC",61.863),("Stateline Classics",38.137)),
 T(("Grand Canyon National Park Hiking Stick Medallion","B01MZ0Q75Q",317.4),("Great Smoky Mountains - Bear and Cub - Hiking Stick Medallion","B07VHY8SH9",265.65),("L W Bristol Classics Mount Rushmore Hiking Medallion","B005FSS15S",224.28),("L W Bristol Classics Yellowstone National Park Hiking Stick Medallion","B01MQFJBR4",179.63),("Route 66 - Hiking Stick Medallion","B01MU1LEDT",155.3))),
"Cambrooke":RAW(P("Cambrooke","Health & Household","Branched Chain Amino Acids Nutritional Supplements",2.33,"",False,"",0,3.451,None,208.11,2,3,1,1248.68,14554.25),
 S(("SimplyMedical",95.32),("IRONMED",4.68)),
 T(("Cambrooke Essential Care JR Amino Acid-Based Nutrition Powder (Case of 6, Vanilla)","B0D4KMKFN9",609.56),("Cambrooke Essential Care JR Amino Acid-Based Nutrition Powder (Case of 6, Unflavored)","B0D4KM8JJW",532.28),("Cambrooke Essential Care JR Amino Acid-Based Nutrition Powder (14.1 oz, Unflavored)","B0D4KLV7L9",106.84))),
"Channel Craft":RAW(P("Channel Craft","Arts, Crafts & Sewing","Craft Kits",2.22,"",False,"",0,0.37,None,18.18,4.42,9,846,1129.1,23505.55),
 S(("Fifty & Co",66.801),("Nature's Workshop Plus!",9.383),("BrightStarWholesale",9.106),("Buckeye Nation Sales",4.847),("Heaven of Goods",3.467),("Lange General Store",2.991)),
 T(("Channel Craft, JJ's Pocket Knife, Wood Craft Kit","B004RIJ1IS",858.16),("Channel Craft Campers Knot Tying Game","B01BW2QYEA",97.5),("Channel Craft Canoe Wooden Knife Kit USA Tin Box","B00PX5ZY8U",79.08),("CHANNEL CRAFT Hero Decks - Chicago Cubs - Playing Cards","B000OLNES0",54),("Channel Craft Ring on a String Game","B00FW6P3XQ",40.36))),
"The Handcrafted":RAW(P("The Handcrafted","Toys & Games","Puzzle Boxes",2.25,"",False,"",0,-0.327,None,32.76,4.48,8,781,1032.19,28526.1),
 S(("Cheerful Home",92.642),("Brilliant Store",7.358)),
 T(("Wood Intarsia Bee Puzzle Box, Handcrafted Wooden Secret Compartment Keepsake Box","B00U0JY5KC",297.36),("Flying Eagle - Natural Wood Intarsia Puzzle Box","B002TCZ83Q",197.7),("Butterfly Wooden Puzzle Box, Handcrafted Secret Compartment Keepsake","B00333TS7W",168.2),("Hand-Carved Cat Puzzle Box, Natural Intarsia Wooden Keepsake Box","B00MFVYR5Q",162.75),("Super-Man Superhero Handcrafted Wooden Puzzle Box","B005L3VFI2",143.84))),
"GREENWILL":RAW(P("GREENWILL","Beauty & Personal Care","Bath Soaps",1,"",False,"",0,-0.401,None,24.99,4.3,2,660,939.51,22636.86),
 S(("Greenwill",100)),
 T(("GREENWILL 3 Pounds Organic De-seeded Soap Berries/Soap Nuts + 2 Wash Bags","B00AHTWMXC",599.85),("6 Ounces Greenwill Organic De-seeded Soapberry/Soap Nuts with Wash Bag","B00AHTWN6S",339.66))),
"EnjoyLife Inc":RAW(P("EnjoyLife Inc","Sports & Outdoors","Trick & Novelty Golf Balls",0.92,"EnjoyLife Inc",False,"",0,-0.456,None,13.8,4.71,13,644,902.85,30270.26),
 S(("EnjoyLife Inc",100)),
 T(("EnjoyLife Inc World Collection Globe/International Flags/Earth Golf Ball Gift Set","B000TGN7QE",188.37),("EnjoyLife Inc Basketballs Golf Ball Gift Set","B000S6M0W2",130.41),("EnjoyLife Inc Philadelphia Souvenir Baseball","B00JDS4J7U",91.92),("EnjoyLife Inc Ben Franklin $100 Bill Golf Ball Gift Set","B00OS9LP7Q",86.94),("EnjoyLife Inc Groomsman Wedding Variety Golf Ball Gift Set","B00TQ7VRUU",86.94))),
"Southwest Specialty Food":RAW(P("Southwest Specialty Food","Grocery & Gourmet Food","Hot Sauce",2,"Southwest Specialty Food",False,"",0,0.2,None,9.95,4.6,2,391,851.7,9259.2),
 S(("Southwest Specialty Food",100)),
 T(("Pure Bred Idiot Pure Ground Carolina Reaper Powder","B07RZW8HY6",448.95),("Spontaneous Combustion Habanero Pepper","B000G6XFVO",402.75))),
"Zizo":RAW(P("Zizo","Everything Else","Cell Phone Case & Cover Bundles",1.68,"",True,"",0,0.032,None,28.32,4.23,25,23863,824.27,12498.15),
 S(("wirelessdeals",45.921),("AG DEALS",18.85),("C&M Ecom",14.356),("City-Souvenirs",11.157),("Austin Smart Tech LLC",3.321),("Goody Hunts",3.11)),
 T(("Zizo Bolt Cover - Case for iPhone 11 with Glass Screen Protector & Kickstand (Black)","B07X8RYFZ5",184.9),("ZIZO Bolt Bundle iPhone 13 Case - Black","B09F53FSJW",169.84),("ZIZO Bolt Bundle for iPhone 14 Pro Max Case - Black","B0BBHBC97N",127.75),("ZIZO Bolt Series for Galaxy S21 Plus Case - Blue & Black","B08T5V7ZWC",99.15),("ZIZO USA New York City Broadway Snow Globe","B005F79CJS",91.96))),
"Dry Gulch Gifts":RAW(P("Dry Gulch Gifts","Toys & Games","Assembly & Disentanglement Puzzles",1,"",False,"",0,-0.15,None,24.98,4.6,1,53,674.46,8568.14),
 S(("Lehman's Home and Garden",100)),
 T(("Puzzle: Dry Gulch Horseshoe","B07T7Z5MGL",674.46))),
"Gem Guides Book Co":RAW(P("Gem Guides Book Co","Books","Biology of Fossils",2,"",False,"",0.777,-0.79,None,168.75,4.53,8,1094,570.3,2278.47),
 S(("Amazon.com",77.726),("SPA BOOKS",9.258),("UPICK MARKETING LLC",6.542),("Starbook Store",4.052),("Sunrise Finds",2.422),("NovelDelights",0)),
 T(("Gem Trails of Arizona","1889786470",239.2),("Geodes: Nature's Treasures","1889786322",139.68),("Gem Trails of Southern California","188978625X",89.72),("Rocks, Minerals & Crystals: A Coloring & Collecting Book","188978656X",53.7),("Facet Cutters Handbook","0910652066",48))),
"Lipco":RAW(P("Lipco","Toys & Games","Board Games",1,"",False,"",0,0.23,None,34.66,3.6,1,19,519.9,11242.26),
 S(("Hour Loop",100)),
 T(("Lipco Cabin Decor Moose Cribbage Board, Wood","B0BC6L7CTT",519.9))),
"Little Joys":RAW(P("Little Joys","Health & Household","Children's Vitamins",0.29,"",False,"",0,-0.589,None,35.43,4.33,7,3442,480,75804.89),
 S(("Mosaic Wellness INC",100)),
 T(("Little Joys Omega-3 (DHA) Brain Gummies for Kids 7-12 Years","B0FM3XWXL7",240),("Little Joys DHA Omega 3 Brain Gummies for Toddlers 2-6 Years","B0FM3YZST7",240),("Little Joys Hazelnut Chocolate Spread, 10.58 Oz","B0FJDQ3JHF",0),("Little Joys Chocolate Spread, 26.45 Oz","B0DFWL9G2Z",0),("Little Joys Mixed Nuts Chocolate Spread for Kids, 10.58 Oz","B0G1MVVDF3",0))),
}
FN="Saw that {b} exhibited at FNCE last year."
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
LAUNCH="We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
emails=[
E(100,"Las Vegas Souvenir & Resort Gift Show 2026|Honey House Naturals","Honey House Naturals","Brand's own account sells only ~49%; a reseller (HeredomUs) sells ~41% and is growing; flat year","Honey House Naturals seller 48.5%; HeredomUs 40.6% (MoM +6.9 pts); Leathnu 9.8%; monthly rev ~$7k; 2,605 reviews; 12M MoM +0.6%","Honey House Naturals sellers on Amazon",f"""{H}

{LV}

From what we can see, Honey House Naturals does roughly $7k a month on Amazon, but your own account is only about half of it. A third-party seller, HeredomUs, is taking around 40% and growing, with another reseller behind it. On a catalog with 2,600 reviews and a flat year, that means someone else is winning the Buy Box on your Bee Bars and setting the price.

{CO}

Would it make sense to have a quick conversation?

Yoni"""),
E(101,"Las Vegas Souvenir & Resort Gift Show 2026|Eagle Crest Industries Inc.","EAGLE CREST","No brand account; resellers hold ~100% (Armed Forces Depot 59%, Hour Loop 18%); steep decline","Armed Forces Depot 59.4%; Hour Loop 18.5%; brand direct 0%; monthly rev ~$7k; TTM ~$133k; 12M MoM -48%; 4,965 reviews","Who sells Eagle Crest on Amazon",f"""{H}

{LV}

Looking at your listings, Eagle Crest products do roughly $7k a month on Amazon, down by about half over the last year, and every dollar is sold by third parties, mostly Armed Forces Depot and Hour Loop. We don't see an Eagle Crest account. The Air Force Retired cap alone is close to half the volume, and with nearly 5,000 reviews on the catalog that is a lot of equity in other hands.

{CO}

Would it make sense to talk about taking that back?

Yoni"""),
E(102,"Las Vegas Souvenir & Resort Gift Show 2026|Hang Loose Srl Keep Out Bracelets","Hang Loose Bands","Brand direct; trailing year ~$285k but current run rate ~$5k with very few reviews across 99 listings","Brand direct 100%; monthly rev ~$5k; TTM ~$285k; MoM -37%; 99 products; 298 reviews","Hang Loose Bands on Amazon",f"""{H}

{LV}

From what we can see, Hang Loose Bands did close to $300k on Amazon over the trailing year, sold direct, but the current run rate is around $5k a month and last month was down again by more than a third. The catalog is spread across about 100 listings with under 300 reviews between them, so nothing has the rank to hold on its own once ads or inventory slip.

{CO}

Is it worth a short call to look at what changed?

Yoni""",brand_sellers=["HangLooseBands"],qa=["exhibitor listed as Hang Loose Srl Keep Out Bracelets; matched to Hang Loose Bands brand"]),
E(103,"Las Vegas Souvenir & Resort Gift Show 2026|L'ovedbaby","L'ovedbaby","Sold through a third-party service account (Marketplace Valet 82%) plus Amazon 1P; steep decline","Marketplace Valet 82.3%; Amazon 17.7%; brand direct 0%; monthly rev ~$6k; TTM ~$69k; 12M MoM -64%; 2,283 reviews","L'ovedbaby on Amazon",f"""{H}

{LV}

Looking at your listings, L'ovedbaby does roughly $6k a month on Amazon, down sharply over the last year, with about 80% sold through an account called Marketplace Valet and the rest by Amazon as the vendor. One black footie is half the volume and the other 80 listings barely move. For an organic baby brand with a 4.5 rating, that is a channel nobody is actively building.

{CO}

Would it make sense to have a quick conversation?

Yoni""",qa=["Marketplace Valet is a third-party marketplace service provider; treated as third party per rules"]),
E(104,"Las Vegas Souvenir & Resort Gift Show 2026|Vinrella","VINRELLA","One reseller (Garden Works) sells ~97%; brand's own account ~3%; declining","Garden Works 96.9% on 28 offers; Vinrella seller 3.1%; monthly rev ~$5k; 12M MoM -25%; 1,692 reviews","Who sells Vinrella on Amazon",f"""{H}

{LV}

From what we can see, Vinrella does roughly $5k a month on Amazon and about 97% of it is sold by one account, Garden Works, across 28 of your listings, with your own account on just two. The trend over the last year is down a quarter. The wine bottle umbrella is a gift product that should do well on Amazon in Q4, but right now the listing, the price and the ads are all someone else's call.

{CO}

Would it make sense to talk about taking that back?

Yoni""",qa=["'Garden Works' may be an affiliated company; treated as third party per rules; verify"]),
E(105,"Las Vegas Souvenir & Resort Gift Show 2026|First & Main","First & Main","No brand account; three listings sold entirely by resellers (Sunrite Gifts 79%)","Sunrite Gifts 79.2%; Imperio Nygren 11.8%; Hour Loop 8.9%; brand direct 0%; monthly rev ~$4k; 3 products; 1,598 reviews","First & Main on Amazon",f"""{H}

{LV}

Looking at your listings, First & Main is essentially three plush listings on Amazon doing roughly $4k a month, all sold by third parties, mostly Sunrite Gifts. We don't see a First & Main account, and the Melancholy puppy alone has about 1,600 reviews and a 4.7 rating. That is a brand with a proven product and almost no Amazon channel behind it.

{PROOF} {LAUNCH}

Is Amazon something you're looking at?

Yoni""",qa=["profile pulled via query_analytics after handle renewal"]),
E(106,"FNCE 2025|Agoge","Agoge","Early-stage launch: four listings, ~40 reviews, sub-4.2 rating","Brand direct 100%; monthly rev ~$3k; 4 products; 41 reviews; avg rating 4.15; MoM -17%","Agoge's Amazon launch",f"""{H}

{FN.format(b='Agoge')}

From what we can see, Agoge is doing roughly $3k a month on Amazon across four hemp protein listings, sold direct, with about 40 reviews and an average rating just over 4. That is the very start of a channel. In protein powder the first few hundred reviews, the listing content and the organic and hemp search terms decide whether a brand gets past this stage.

{PROOF} {LAUNCH}

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["Agoge Organic Hemp Protein"]),
E(107,"Las Vegas Souvenir & Resort Gift Show 2026|The Jonsteen Co.","The Jonsteen Company","Mostly brand direct with a strong review base, but small current volume and ~20% leaking to resellers","The Jonsteen Company 80.4%; Japanese Maples and Evergreens 11.9%; Atharva Brands 7.7%; monthly rev ~$2.7k; TTM ~$102k; 5,182 reviews","The Jonsteen Company on Amazon",f"""{H}

{LV}

From what we can see, The Jonsteen Company does roughly $3k a month on Amazon right now, against about $100k over the trailing year, mostly through your own account with about 20% going through two resellers. The Giant Sequoia seedling carries it, and the catalog has more than 5,000 reviews, which is a real asset for nine listings. It looks like the seasonal dip is being ridden out rather than worked.

{CO}

Open to a short call on the off-season plan?

Yoni""",qa=["profile and sellers pulled via query_analytics fallback; 12M growth not returned"]),
E(108,"Las Vegas Souvenir & Resort Gift Show 2026|Americaware, Inc.","Americaware","Resellers (Artisan Owl, Zentra) sell ~90%; brand's own account ~4%; last month down 40%","Artisan Owl 53.4%; Zentra 37.4%; Americaware Inc 3.5%; monthly rev ~$2.6k; MoM -40%; 675 reviews","Who sells Americaware on Amazon",f"""{H}

{LV}

Looking at your listings, Americaware mugs do roughly $2,500 a month on Amazon, and about 90% of that is sold by two resellers, Artisan Owl and Zentra. Your own account is under 5%, and last month was down 40%. Souvenir mugs are a natural gift listing on Amazon, but only if the brand owns the page and keeps the popular designs in stock.

{PROOF} {LAUNCH}

Is Amazon something you're looking at more seriously?

Yoni""",brand_sellers=["Americaware Inc"]),
E(109,"Las Vegas Souvenir & Resort Gift Show 2026|Jacobson Hat Company","Jacobson Hat Company","No brand account; sold entirely by costume and souvenir resellers; trailing year ~$142k vs ~$2.5k now","Gettysburg Souvenirs 37.6%; Arlene's Costumes 29.2%; Atharva Brands 17.2%; brand direct 0%; monthly rev ~$2.5k; TTM ~$142k; 3,408 reviews","Jacobson Hat Company on Amazon",f"""{H}

{LV}

From what we can see, Jacobson Hat Company products did about $140k on Amazon over the trailing year, but every dollar of it is sold by costume and souvenir resellers like Gettysburg Souvenirs and Arlene's Costumes. We don't see a Jacobson account. Right now it is around $2,500 a month heading into the Halloween window, and the Civil War kepi is most of that.

{CO}

Would it make sense to talk about owning that channel yourselves?

Yoni"""),
E(110,"Las Vegas Souvenir & Resort Gift Show 2026|SEAWAG","Seawag","Tiny US footprint; brand's US account ~71% with a European reseller at ~29%","SEAWAG USA 70.6%; Diveland CZ 29.4%; monthly rev ~$2k; 12 products; 293 reviews; avg rating 4.58","Seawag on Amazon US",f"""{H}

{LV}

Looking at your listings, Seawag does roughly $2k a month on Amazon in the US across a dozen pouch listings, with about 30% of that sold by a Czech reseller rather than your US account. Under 300 reviews across the catalog. For a product that sells at every beach and pool gift shop, that is a channel that has barely been started.

{PROOF} {LAUNCH}

Is Amazon something you're looking at for the US?

Yoni""",brand_sellers=["SEAWAG USA"]),
E(111,"Las Vegas Souvenir & Resort Gift Show 2026|Blossom Bucket","Blossom Bucket","Sold almost entirely by one reseller (Hour Loop 97%); no brand account; trailing year ~$106k","Hour Loop 96.7%; brand direct 0%; monthly rev ~$1.9k; TTM ~$106k; 3,562 reviews","Who sells Blossom Bucket on Amazon",f"""{H}

{LV}

From what we can see, Blossom Bucket did about $100k on Amazon over the trailing year, and nearly all of it is sold by one reseller, Hour Loop. We don't see a Blossom Bucket account. The angel figurines and the nativity letters carry it, on a catalog with about 3,500 reviews, and it is heading into Q4 with the pricing and content entirely in a reseller's hands.

{CO}

Would it make sense to talk about taking that back before the holidays?

Yoni"""),
E(112,"Las Vegas Souvenir & Resort Gift Show 2026|Earthview, Inc.","Earthview","Brand direct but tiny: 23 listings, under 100 reviews, high price points","Brand direct 100%; monthly rev ~$1.8k; 23 products; 97 reviews; avg price ~$101","Earthview on Amazon",f"""{H}

{LV}

Looking at your listings, Earthview is on Amazon with about 23 products but doing under $2k a month, sold direct, with fewer than 100 reviews across the whole catalog. Fragrance free and MCS-safe is a real niche that people search for by name, and right now the listings are not built to catch it.

{PROOF} {LAUNCH}

Is Amazon something you're looking at more seriously?

Yoni""",brand_sellers=["Earthview Products Company"]),
E(113,"Las Vegas Souvenir & Resort Gift Show 2026|L. W. Bristol Classics","L W Bristol Classics","Reseller (Zentra) sells ~62% against the brand-side account (Stateline Classics) at ~38%; small","Zentra 61.9%; Stateline Classics 38.1%; monthly rev ~$1.8k; 1,113 reviews; avg rating 4.67","L W Bristol Classics on Amazon",f"""{H}

{LV}

From what we can see, L W Bristol hiking medallions do roughly $2k a month on Amazon, and about 60% of it is sold by a reseller, Zentra, with Stateline Classics on the rest. Both carry the same 11 listings, so they trade the Buy Box back and forth. With over 1,000 reviews and a 4.7 rating, the product is clearly liked, and the channel is just not being run.

{CO}

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["Stateline Classics"],qa=["'Stateline Classics' assumed to be the brand's own account; verify"]),
E(114,"FNCE 2025|Ajinomoto Cambrooke","Cambrooke","Medical foods sold only via a medical reseller; one review at 2 stars; large parent company","SimplyMedical 95.3%; brand direct 0%; monthly rev ~$1.2k; 3 products; 1 review; avg rating 2.0","Cambrooke on Amazon",f"""{H}

{FN.format(b='Ajinomoto Cambrooke')}

Looking at your listings, the Cambrooke Essential Care JR products are on Amazon at about $1,000 a month, sold almost entirely by a medical supply reseller called SimplyMedical, with a single 2 star review across the three listings. That is the whole Amazon presence for the brand as far as we can see, and it is not one Cambrooke controls.

{CO}

Would a 20 minute look at what a brand-owned setup for the medical foods could look like be worth your time?

Yoni""",qa=["large parent (Ajinomoto); SmartScout record covers Essential Care JR only"]),
E(115,"Las Vegas Souvenir & Resort Gift Show 2026|Channel Craft","Channel Craft","No brand account; resellers hold ~100% (Fifty & Co 67%); one craft kit carries the volume","Fifty & Co 66.8%; brand direct 0%; monthly rev ~$1.1k; 9 products; 846 reviews","Channel Craft on Amazon",f"""{H}

{LV}

From what we can see, Channel Craft products do roughly $1,000 a month on Amazon, all through resellers, mostly one account called Fifty & Co, and we don't see a Channel Craft account. JJ's Pocket Knife kit is almost all of it, on nearly 850 reviews across the catalog. Made in USA craft kits are a natural Amazon gift item, and right now nobody is building that.

{PROOF} {LAUNCH}

Is Amazon something you're looking at?

Yoni"""),
E(116,"Las Vegas Souvenir & Resort Gift Show 2026|The Handcrafted","The Handcrafted","Sold entirely by one reseller (Cheerful Home 93%); no brand account; small and declining","Cheerful Home 92.6%; brand direct 0%; monthly rev ~$1k; TTM ~$29k; 8 products; 781 reviews","The Handcrafted puzzle boxes on Amazon",f"""{H}

{LV}

Looking at your listings, The Handcrafted puzzle boxes do roughly $1,000 a month on Amazon, down a third last month, and nearly all of it is sold by an account called Cheerful Home rather than by you. Eight listings, close to 800 reviews, and a product that is exactly what people search for as a gift in Q4, with nobody on the brand side running it.

{PROOF} {LAUNCH}

Is Amazon something you're looking at?

Yoni""",qa=["'Cheerful Home' may be an affiliated account; treated as third party per rules; verify"]),
E(117,"Las Vegas Souvenir & Resort Gift Show 2026|Greenwill Global","GREENWILL","Brand direct with two listings and 660 reviews but under $1k a month and falling","Brand direct 100%; monthly rev ~$940; 2 products; 660 reviews; MoM -40%","Greenwill on Amazon",f"""{H}

{LV}

From what we can see, Greenwill has two soap nut listings on Amazon with about 660 reviews between them, sold direct, but they are doing under $1k a month and last month dropped 40%. Reviews like that on a natural laundry product usually mean the listings once ranked and have since slipped, which is fixable.

{PROOF} {LAUNCH}

Is Amazon something you're looking at more seriously?

Yoni""",brand_sellers=["Greenwill"]),
E(118,"Las Vegas Souvenir & Resort Gift Show 2026|EnjoyLife, Inc.","EnjoyLife Inc","Brand direct, tiny and falling; strong rating on gift golf balls","Brand direct 100%; monthly rev ~$900; TTM ~$30k; MoM -46%; 13 products; 644 reviews; avg rating 4.71","EnjoyLife golf ball gift sets on Amazon",f"""{H}

{LV}

Looking at your listings, EnjoyLife golf ball gift sets do under $1k a month on Amazon, sold direct, down close to half last month, on 13 listings with a 4.7 average rating. That rating on a gift item heading into Q4 is the interesting part. The listings exist, the reviews exist, and it looks like nobody is putting ads or content behind them.

{PROOF} {LAUNCH}

Is Amazon something you're looking at more seriously?

Yoni""",brand_sellers=["EnjoyLife Inc"]),
E(119,"Las Vegas Souvenir & Resort Gift Show 2026|Southwest Specialty Food, Inc.","Southwest Specialty Food","Brand direct, two listings, under $1k a month; catalog barely on Amazon","Brand direct 100%; monthly rev ~$850; 2 products; 391 reviews; avg rating 4.6","Southwest Specialty Food on Amazon",f"""{H}

{LV}

From what we can see, Southwest Specialty Food has two listings on Amazon, the Carolina Reaper powder and the habanero, doing under $1k a month between them, sold direct, with about 400 reviews and a 4.6 rating. Hot sauce and pepper gifts are a big Amazon category in Q4 and the rest of your range isn't there at all.

{PROOF} {LAUNCH}

Is Amazon something you're looking at?

Yoni""",brand_sellers=["Southwest Specialty Food"]),
E(120,"Las Vegas Souvenir & Resort Gift Show 2026|Zizo USA Inc.","Zizo","Huge review base (~24k) but under $1k a month; sold entirely by resellers; catalog abandoned","wirelessdeals 45.9%; AG DEALS 18.9%; C&M Ecom 14.4%; brand direct 0%; monthly rev ~$820; 25 products; 23,863 reviews","Zizo's Amazon catalog",f"""{H}

{LV}

Looking at your listings, Zizo has close to 24,000 reviews on Amazon across about 25 case listings, and it is doing under $1k a month, all through resellers like wirelessdeals and AG DEALS. We don't see a Zizo account. That is a lot of review equity sitting on old iPhone models with nobody carrying it forward to current ones.

{CO}

Would it make sense to have a quick conversation?

Yoni"""),
E(121,"Las Vegas Souvenir & Resort Gift Show 2026|Dry Gulch Gifts","Dry Gulch Gifts","Effectively not on Amazon as a brand: one puzzle sold by a single retailer","Lehman's Home and Garden 100%; 1 product; monthly rev ~$670; 53 reviews","Dry Gulch Gifts on Amazon",f"""{H}

{LV}

From what we can see, Dry Gulch Gifts is on Amazon as a single listing, the horseshoe puzzle, sold by Lehman's rather than by you, at around $700 a month. So the brand is effectively not on Amazon at all, which for a gift line heading into Q4 is either a gap or a choice.

{PROOF} {LAUNCH}

Is Amazon something you're looking at?

Yoni"""),
E(122,"Las Vegas Souvenir & Resort Gift Show 2026|Gem Guides Book Company","Gem Guides Book Co","Small specialty publisher; Amazon 1P ~78%, under $1k a month; weak fit","Amazon 1P 77.7%; monthly rev ~$570; 8 products; 1,094 reviews","Gem Guides titles on Amazon",f"""{H}

{LV}

Looking at Gem Guides titles on Amazon, we see roughly $600 a month across about eight books, mostly sold by Amazon itself, with over 1,000 reviews and a 4.5 rating between them. Gem Trails of Arizona leads. Regional guides like these sell through gift shops, and on Amazon they mostly sit unless someone puts ads and content behind the top titles.

{CO}

Open to a short call on it?

Yoni""",qa=["small book publisher; weaker fit for consumer brand pitch"]),
E(123,"Las Vegas Souvenir & Resort Gift Show 2026|Lipco Group","Lipco","One listing sold by a reseller (Hour Loop); 3.6 rating; effectively not on Amazon","Hour Loop 100%; 1 product; monthly rev ~$520; 19 reviews; avg rating 3.6","Lipco on Amazon",f"""{H}

{LV}

From what we can see, Lipco is on Amazon as a single listing, the moose cribbage board, sold by Hour Loop rather than by you, at around $500 a month with a 3.6 rating on 19 reviews. So the Amazon presence is one product, one reseller, and a rating nobody is managing.

{PROOF} {LAUNCH}

Is Amazon something you're looking at?

Yoni"""),
E(124,"Las Vegas Souvenir & Resort Gift Show 2026|Little Joys","Little Joys","Brand direct via parent (Mosaic Wellness); strong review base but volume has collapsed to under $500 a month","Mosaic Wellness INC 100% (parent company); monthly rev ~$480; TTM ~$76k; MoM -59%; 3,442 reviews; 7 products","Little Joys on Amazon US",f"""{H}

{LV}

Looking at your listings, Little Joys did about $75k on Amazon US over the trailing year, but it is now under $500 a month and dropped close to 60% last month. Two omega-3 gummy listings are all that is moving, and the chocolate spreads show no sales. With nearly 3,500 reviews on the catalog, that is a channel that had traction and lost it.

{CO}

Is it worth a short call to look at what changed?

Yoni""",brand_sellers=["Mosaic Wellness INC"],qa=["Mosaic Wellness is Little Joys' parent company; treated as brand direct"]),
]
run(raw,emails)
