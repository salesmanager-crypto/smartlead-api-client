from batchlib import *
raw={
"Five Plus Protein":RAW(None,[],[]),
"Fresh Blends":RAW(None,[],[]),
"Heavenly Waffles":RAW(P("Heavenly Waffles","Grocery & Gourmet Food","Pancake & Waffle Mixes",4.14,"",True,"",0.101,0.05,None,15.93,3.86,7,176,4407.27,82747.45),
 S(("Heavenly Waffles",64.684),("MPYRProducts",12.845),("Amazon.com",10.114),("Angels Frequency",5.268),("GrandioseGoods",4.764),("Jodiawala Commodities LLC",1.225)),
 T(("Heavenly Foods Mix, Gluten Free, 18g Protein, 13.5 oz Pouch","B0CYGYFXND",1675.71),("Heavenly Foods Mix, Original Recipe, 14g Protein, 13.5 oz Pouch","B0BX937SH4",928.25),("Heavenly Foods Mix, Legacy Blueberry, 14g Protein, 13.5 oz Pouch","B0CYH3S8R9",702.24),("Heavenly Foods Mix, Original Recipe, 4 lb Pouch","B0DHHFD16S",314.93),("Heavenly Waffles Mix, Chocolate Espresso, 13.5 oz Pouch","B0BX92G1FN",294.52))),
"Gutzy Organic":RAW(None,[],[]),
"Purity Coffee":RAW(P("Purity Coffee","Grocery & Gourmet Food","Ground Coffee",1.5,"PurityCoffee",True,"",0,-0.112,None,54.45,4.36,34,2647,897663.94,12154156.07),
 S(("PurityCoffee",92.178),("MyConnects",7.822)),
 T(("FLOW Original Medium Roast Whole Bean (12oz Bag)","B09T9854DQ",108460),("FLOW Original Medium Roast Whole Bean (5lb Bag)","B09T9FK2MB",106850.7),("FLOW Original Medium Roast Ground (12oz Bag)","B0D67Z89LD",106691),("EASE Low Acid Dark Roast Ground (12oz Bag)","B0D681NCDK",74820),("EASE Low Acid Dark Roast Whole Bean (5lb Bag)","B09T8PKZ55",62301.14))),
"REDMOND":RAW(P("REDMOND","Health & Household","Sports Nutrition Electrolyte Replacement Drinks",2.66,"",True,"",0,-0.069,None,38.69,4.56,211,106946,5865388.48,81031257.32),
 S(("Redmond Life",95.697),("Redmond Minerals",2.284),("CostumeBoom",0.292),("Country Life Natural Foods",0.285),("Whole Foods Market",0.22),("E-Triton LLC",0.16)),
 T(("REDMOND Re-Lyte Sugar Free Electrolyte Powder Drink Mix (Mixed Berry)","B088GJ7VK6",722226.96),("REDMOND Re-Lyte Sugar Free Electrolyte Powder Drink Mix (Lemon Lime)","B088G2F4ZJ",721828.55),("REDMOND Re-Lyte Sugar Free Electrolyte Powder Mix (Strawberry Lemonade)","B097QF7HVH",721625.52),("Redmond Re-Lyte Sugar Free Electrolyte Powder Drink Mix (Watermelon Lime)","B08QV7Q6QX",434559.51),("REDMOND Re-Lyte Sugar Free Electrolyte Powder Drink Mix (Mango)","B097QBZCVK",386270.01))),
"ResBiotic":RAW(P("ResBiotic","Health & Household","Acidophilus Nutritional Supplements",1.8,"ResBiotic",True,"",0,0.009,None,76.95,4.18,10,751,80437.73,671676.85),
 S(("LUMlNlZE",99.661),("resbiotic",0.339)),
 T(("resB Lung Support Probiotic Supplement, 60 Capsules","B09MDJ4GLQ",57138.67),("resB Lung Support Probiotic Supplement, 180 Capsules, 3 Bottles","B0BZJW4GQ1",19508.06),("resG prebeet Prebiotics Drink - 560g, 90 Servings","B0CKZLCVL2",948),("resG prebeet Prebiotics Drink - 180g, 30 Servings","B0CKZJLK5Y",784.2),("resG prebeet Prebiotic Supplement - 30 Stick Packs","B0DPLKR1PP",733.28))),
"Simply Thick":RAW(P("Simply Thick","Health & Household","Daily Living Eating & Drinking Aids",6.62,"SimplyThick, LLC",True,"",0,0.113,None,73.21,4.52,13,9310,814118.49,9568074.48),
 S(("SimplyThick, LLC",68.14),("SimplyMedical",27.433),("Vitamins To Go",4.427)),
 T(("SimplyThick EasyMix | 302 Servings | 55 Fl Oz Bottle with Pump","B07934C3RY",427197.36),("SimplyThick EasyMix | 100 Count of 12g Individual Packets","B079349C6C",125726.92),("SimplyThick EasyMix | 200 Count of 6g Individual Packets","B07934WLC2",91359.12),("SimplyThick EasyMix | 80 Count of 6g Individual Packets","B09KNXTR9W",83829.57),("SimplyThick EasyMix | 92 Servings | 16.9 Fl Oz Bottle with Pump","B08GQDMXPK",60073.65))),
"SPLENDA":RAW(P("Splenda","Grocery & Gourmet Food","Stevia Sugar Substitutes",1.84,"Amazon.com",True,"",0.962,0.054,None,20.89,4.47,196,208964,2074850.52,27069784.92),
 S(("Amazon.com",96.239),("Heartland Food",1.831),("TBC UK",0.444),("FoodserviceDirect Inc.",0.427),("PARTNER STORE USA",0.399),("STRATO HEALTH LIMITED",0.283)),
 T(("SPLENDA Zero Calorie Sweetener, 800 Count Packets","B0BLBJL2D4",372730.6),("SPLENDA Zero Calorie Sweetener, Granulated, Twin Pack Bags, 25.22 Ounce","B0058V22TI",163648.08),("SPLENDA Zero Calorie Sweetener, 2000 Count Packets","B000LRO5O4",125370.81),("SPLENDA Zero Calorie Sweetener, 200 Count Packets","B005IHUYVA",98941.5),("SPLENDA Stevia Zero Calorie Sweetener, 19 oz Jar","B08G5DW3ZZ",81140.22))),
"Standard Process Inc.":RAW(P("Standard Process Inc.","Health & Household","Blended Vitamin & Mineral Supplements",1.18,"Pattern.",True,"",0,0.006,None,53.08,4.62,257,78720,3186033.19,43604271.47),
 S(("Pattern.",93.786),("Tee Distributions",2.979),("Triple T Trade co.",1.165),("Informed Living",0.698),("LEVANI Partners",0.688),("LabX NEW YORK",0.281)),
 T(("Standard Process Zypan, 330 Tablets","B07DP646ZD",130099.2),("Standard Process Ligaplex II, 150 Capsules","B0037MGBPQ",126673.2),("Standard Process Drenamin, 90 Tablets","B0C26JLCQQ",91990.97),("Standard Process Magnesium Lactate, 60 Tablets","B0FP3C8LXZ",87740.64),("Standard Process Tuna Omega-3 Oil, 120 Softgels","B0019FQTHI",63195.26))),
"SunButter":RAW(P("SunButter","Grocery & Gourmet Food","Butter",7.63,"Amazon.com",True,"",0.762,0.108,None,36.86,4.36,35,9023,320726.49,2537146.54),
 S(("Amazon.com",76.173),("Vitamins To Go",15.939),("VitaVerr",2.768),("Whole Foods Market",1.092),("Modernparty",0.992),("FoodserviceDirect Inc.",0.79)),
 T(("SunButter Organic Sunflower Seed Butter, 16 oz","B003PWJFXS",64985.24),("SunButter Original Sunflower Seed Butter, 16 Oz","B000VK84P2",59922.24),("SunButter No Sugar Added Sunflower Seed Butter, 16 Oz, Pack of 6","B00J074W9Y",30373.8),("SunButter Creamy Sunflower Seed Butter, 16 Oz, Pack of 6","B002OK6E6I",28940.85),("SunButter Original Sunflower Seed Butter, 16 Oz, Pack of 6","B001HTIUDC",24915.32))),
"That's it.":RAW(P("That's it.","Grocery & Gourmet Food","Fruit Bars",2.9,"That's it.",False,"",0.002,0.048,None,28.35,4.34,71,35341,1481848.28,19038872.54),
 S(("That's it.",97.183),("OVERTIME WHOLESALE",0.53),("The Bena Group",0.446),("MeltingPoint Shop",0.354),("Thesecondjob",0.266),("Whole Foods Market",0.26)),
 T(("That's it. Mini Fruit Bars, No Sugar Added","B0D1VWMVL7",380551.71),("That's it. Variety Pack 100% Natural Real Fruit Bar, 12 Pack","B01GD5Y3EY",146641.32),("That's it. Large Fruit Bars Variety Pack (20 Pack)","B07VFY3T2S",114904.17),("That's it. Fruit Crunchables Variety Pack (16 Pack)","B0DK8VM92H",110144.9),("That's it. Mini Fruit Bars Gift Pouch (Variety 36 Count)","B0C8C49ZJ3",109262.88))),
"Theralogix":RAW(P("Theralogix","Health & Household","Vitamin B8 (Inositol) Supplements",1.68,"Pattern Products",True,"",0,-0.176,None,87.24,4.49,50,15204,2788946.07,37144561.64),
 S(("Theralogix",99.967),("Pattern Products",0.033)),
 T(("Theralogix Ovasitol Canister","B0CT6LK1JS",804130.36),("Theralogix TheraCran One Cranberry","B06WGSJG33",392555.95),("Theralogix TheraNatal Complete Prenatal Vitamin","B078NVJ47N",277483.35),("Theralogix Ovasitol Packets","B01BT92C24",179351.1),("Theralogix NeoQ10","B01C3FVUVW",145070.13))),
"Thick-It":RAW(P("THICK-IT","Grocery & Gourmet Food","Cooking & Baking Thickeners",5.62,"",True,"",0.836,0.096,None,57.2,4.13,63,17156,278413.57,3726245),
 S(("Amazon.com",83.636),("SimplyMedical",12.108),("Honest Medical",2.021),("IRONMED",0.689),("Engoloids Medical LLC",0.425),("Hey Pharma",0.333)),
 T(("Thick-It Original Food & Beverage Thickener Powder, 36 oz Canister","B0011TUM3E",60263.52),("Thick-It Original Thickener Powder, 36 oz Canister, 2 Pack","B08MXLTZ76",38511),("Thick-It Clear Advantage Mildly Thick Water, 8 oz, 24 Pack","B00DXORLT8",19729.1),("Thick-It Puree Protein Variety Pack, 15 oz, 12 Pack","B08FFPF8VR",19262.72),("Thick-It Original Thickener Powder, 10 oz Canister","B00CMQDPC0",17875.08))),
"Tonnino":RAW(P("Tonnino","Grocery & Gourmet Food","Packaged Tuna Fish",7.21,"Planet Gourmet",True,"",0.119,-0.01,None,40.8,4.42,76,7729,371963.49,4896274.49),
 S(("Planet Gourmet",40.377),("Navistro",14.6),("Amazon.com",11.936),("The Bena Group",5.376),("Royalty Privilege",4.455),("Babil Wholesale",4.02)),
 T(("Tonnino Olive Oil Yellowfin Tuna Fillets, 6.7 oz 6pk","B01FRP21K4",93641.8),("Tonnino Yellowfin Tuna in Olive Oil, Pack of 12 Cans","B07QM9J8VT",45378.76),("Tonnino Spring Water Yellowfin Tuna Fillets, 6.7 oz Pack of Six","B07QN69G3N",32856.3),("Tonnino Yellowfin Tuna in Spring Water, Pack of 12 Cans","B07QM9KD2S",17474.7),("Tonnino Yellowfin Tuna Fillets in Olive Oil, 6.7 OZ","B07Q6PHT5C",17411.46))),
"ZEGO":RAW(P("ZEGO","Grocery & Gourmet Food","Muesli",5.25,"",True,"",0.048,0.199,None,44.84,4.15,16,332,19879.54,224432.2),
 S(("S. Republic",13.98),("TheNewMall",11.829),("Paradine Services",11.761),("ZEGO",8.764),("Judices Corner",8.322),("LuxProdX",7.482)),
 T(("ZEGO Double Protein Raw Oats, 14oz (2 Pack)","B07TXRN6GM",4962.48),("ZEGO Double Protein Raw Oats, 14oz (Single)","B07N8HVLYS",4359.12),("ZEGO Double Protein Raw Oats, Bundle of 5 Bags","B09KSVHKD8",2251.06),("ZEGO Foods Organic Superfood Oatmeal & Muesli (Cinnamon Twist) 13oz","B07TJ24ZX2",2093.22),("ZEGO Foods Organic Superfood Oatmeal & Muesli (Apple Cranberry) 13oz","B07THLL9R4",1969.28))),
"A.T. Storrs":RAW(None,[],[]),
"Advance Wildlife Education":RAW(None,[],[]),
"Adventure Publications":RAW(P("Adventure Publications","Books","Birdwatching Travel Guides",17.89,"Amazon.com",False,"",0.95,-0.357,None,13.41,4.67,352,67058,63917.78,208496.03),
 S(("Amazon.com",95.002),("eGoods365",0.57),("Shakespeare Book House",0.514),("Mom of Three Boys",0.396),("BOOK_DEPOT",0.353),("MyPrepbooks",0.202)),
 T(("Gemstone Tumbling, Cutting, Drilling & Cabochon Making","1591934605",538.4),("Home Winemaking: The Simple Way to Make Delicious Wine","159193947X",501.93),("The Rocky Mountain Plant Guide","1647553253",492.8),("Eat the Weeds: A Forager's Guide","164755179X",441.37),("Mushrooms of the Northeast","1591935911",426.03))),
"Ahead":RAW(P("Ahead","Musical Instruments","Practice Pads & Devices",2.6,"",False,"",0,-0.256,None,97.55,4.51,45,3838,19620.77,369016.14),
 S(("Sweetwater Sound",59.872),("Instrumentpro",16.474),("West Music",10.558),("Sam Ash",7.652),("Y2Play!",1.697),("Alto Music",1.333)),
 T(("Ahead Dial Precision, Screw Drum Tuner (ADD)","B0002E2TVM",5914.09),("Ahead CHAVEZ Tenor Pad Blue","B00OTRKDIE",3299.89),("Ahead S-hoop Chavez Tenor Practice Pad Set","B0CBLC6H9C",1499.95),("Ahead 14 inch SPINAL G Throne","B01K7N5YQO",1409.94),("Ahead 18 inch SPINAL G Throne","B009OLK1AU",1249.95))),
"American Backcountry":RAW(None,[],[]),
"Avalon Meat Candy":RAW(None,[],[]),
"Bigfoot Sock Co.":RAW(None,[],[]),
"Blue Planet Eco-Eyewear":RAW(P("Blue Planet","Sports & Outdoors","Balance Boards",1,"Blue Planet Surf",True,"",0,0.153,None,155.96,4.9,3,215,13102.84,177473.4),[],[]),
"Boardwalk Puzzles":RAW(None,[],[]),
}
FN="Saw that {b} exhibited at FNCE last year."
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
LAUNCH="We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
END="We manage the channel end to end."
emails=[
E(175,"FNCE 2025|Five Plus Protein","Five Plus Protein","Not found; industry-level: storefront exists but no measurable sales in marketplace data","No brand record; sheet: Amazon storefront found (Google only)","Five Plus Protein on Amazon",f"""{H}

{FN.format(b='Five Plus Protein')}

From what we can see, Five Plus Protein has an Amazon storefront, but the listings aren't registering measurable sales in the public marketplace data we look at. That usually means the channel is set up but nobody is running it, and in protein the listings that win are the ones with real content, advertising and review volume behind them.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["no brand record on two attempts (Five Plus Protein, Five Plus); industry-level email"]),
E(176,"FNCE 2025|Fresh Blends","Fresh Blends","Not found; industry-level: one beverage listing, no measurable sales; foodservice brand","No brand record; sheet: single product listing (Wildberry Acai Beverage)","Fresh Blends on Amazon",f"""{H}

{FN.format(b='Fresh Blends')}

Looking at your listings, Fresh Blends shows up on Amazon with a single beverage listing that isn't registering measurable sales in public marketplace data. For a foodservice-first brand that may be deliberate. It also means anyone who tries the product at a venue and searches for it later finds an unmanaged listing rather than a real storefront.

{PROOF} {END}

Is Amazon something you're looking at for the retail side?

Yoni""",conf="not found",qa=["no brand record on two attempts (Fresh Blends, FreshBlends); industry-level email","weaker fit: foodservice beverage brand"]),
E(177,"FNCE 2025|Heavenly Foods","Heavenly Foods","Small footprint (~$4k a month) with a 3.9 rating; a third sold by resellers and Amazon","Heavenly Waffles 64.7%; MPYRProducts 12.8%; Amazon.com 10.1%; monthly rev ~$4.4k; 7 products; 176 reviews; rating 3.86","Heavenly Foods on Amazon",f"""{H}

{FN.format(b='Heavenly Foods')}

Looking at your listings, Heavenly Foods is on Amazon at about $4k a month across seven mixes, with roughly a third of that going through resellers and Amazon itself rather than your account. The rating sits under 4 stars, which is the main thing holding a pancake and waffle mix back on Amazon. The protein angle is a strong one for search, and it isn't showing up in the volume yet.

{CO}

Would it make sense to have a quick conversation?

Yoni""",conf="close",qa=["SmartScout record is under 'Heavenly Waffles' (product line name)"]),
E(178,"FNCE 2025|Keep Moving Inc. - gutzy organic","Gutzy Organic","Not found; industry-level: storefront exists but no measurable sales in marketplace data","No brand record ('Gutzy' record has 0 products); sheet: Gutzy Organic storefront found","Gutzy Organic on Amazon",f"""{H}

{FN.format(b='Gutzy Organic')}

From what we can see, Gutzy Organic has an Amazon storefront, but the listings aren't registering measurable sales in the public marketplace data we look at. Gut health snacks are a category where Amazon search volume is real and growing, so a storefront that isn't being run is mostly handing that demand to whoever ranks.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["combined exhibitor name; queried Gutzy Organic (brand), 'Gutzy' record empty; industry-level email"]),
E(179,"FNCE 2025|Purity Coffee","Purity Coffee","Strong brand-direct position (~92%); month down ~11%; one reseller (MyConnects) on two listings; modest ask","PurityCoffee 92.2%; MyConnects 7.8%; monthly rev ~$898k; 34 products; 2,647 reviews; MoM -11.2%","Purity Coffee on Amazon",f"""{H}

{FN.format(b='Purity Coffee')}

Looking at your listings, Purity Coffee is doing close to $900k a month on Amazon through your own account, which is a strong position. Two things stand out. The month looks to be down about 10%, and a seller called MyConnects is taking close to 8% on two listings. I know you have people on this, so this is more a second set of eyes than a pitch.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni""",qa=["sheet had no seller info; fresh data shows brand direct"]),
E(180,"FNCE 2025|Redmond Real Salt","REDMOND","Very large, brand direct; Re-Lyte carries the top listings, Real Salt not in top five; month down ~7%; narrow ask","Redmond Life 95.7%; Redmond Minerals 2.3%; monthly rev ~$5.9M; 211 products; 107k reviews; MoM -6.9%; top 5 all Re-Lyte","Real Salt versus Re-Lyte on Amazon",f"""{H}

{FN.format(b='Redmond')}

From what we can see, Redmond does close to $6M a month on Amazon through your own accounts, and the Re-Lyte flavors carry it, each doing several hundred thousand a month. Real Salt itself doesn't show up in the top listings, and the month looks to be down about 7%. I know Redmond has an Amazon team. This is a narrow question about the salt line specifically.

{CO}

Open to a 20 minute look at how Real Salt is positioned next to Re-Lyte?

Yoni""",brand_sellers=["Redmond Life","Redmond Minerals"],qa=["sheet Brand (Seller Central) confirmed","very large brand, narrow ask"]),
E(181,"FNCE 2025|Resbiotic Nutrition, Inc.","ResBiotic","Nearly all revenue through a single seller (LUMlNlZE) while the brand's own account sells almost nothing","LUMlNlZE 99.7%; resbiotic 0.3%; monthly rev ~$80k; 10 products; 751 reviews; rating 4.18; resB 60ct ~$57k/mo","Who sells ResBiotic on Amazon",f"""{H}

{FN.format(b='ResBiotic')}

Looking at your listings, ResBiotic is doing about $80k a month on Amazon, and almost all of it runs through a seller called LUMlNlZE, while your own account has a few listings doing almost nothing. If that's a partner you chose, fine. If it isn't, that seller controls the Buy Box, pricing and margin on resB, which is carrying the whole brand on Amazon.

{CO}

Would it make sense to have a quick conversation about who should own the channel?

Yoni""",qa=["sheet third-party (LUMlNlZE) confirmed; LUMlNlZE may be an affiliated account, verify"]),
E(182,"FNCE 2025|SimplyThick","Simply Thick","Brand sells ~68% direct; ~32% through resellers (SimplyMedical 27%) on the same EasyMix listings; growing","SimplyThick, LLC 68.1%; SimplyMedical 27.4%; Vitamins To Go 4.4%; monthly rev ~$814k; 13 products; 9,310 reviews; MoM +11.3%","Reseller share on SimplyThick listings",f"""{H}

{FN.format(b='SimplyThick')}

Looking at your listings, SimplyThick is doing about $800k a month on Amazon and growing, with your own account selling roughly two thirds of it. SimplyMedical takes close to 30% on the same EasyMix listings, and Vitamins To Go a bit more. On a 13 product catalog that's a lot of Buy Box and margin sitting with resellers, and it tends to grow as the listings grow.

{CO}

Would it make sense to have a quick conversation about tightening up the reseller side?

Yoni""",brand_sellers=["SimplyThick, LLC"],qa=["sheet Brand (Seller Central); fresh data shows 32% resellers (Mixed)"]),
E(183,"FNCE 2025|Splenda","SPLENDA","Amazon 1P ~96% (vendor); large brand; narrow ask on advertising and content","Amazon.com 96.2%; Heartland Food 1.8%; monthly rev ~$2.07M; 196 products; 209k reviews; MoM +5.4%","Splenda vendor side on Amazon",f"""{H}

{FN.format(b='Splenda')}

From what we can see, Splenda does about $2M a month on Amazon, nearly all of it sold by Amazon as a vendor, with the 800 count packets alone around $370k. I know Splenda has people on the account. The gap we usually see on vendor-heavy brands is that Amazon controls price and inventory while advertising and content sit in between teams, and that shows up in how the newer stevia and allulose lines rank.

{CO}

Open to a 20 minute look at the vendor side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed","large brand, narrow ask"]),
E(184,"FNCE 2025|Standard Process","Standard Process Inc.","Entire channel runs through Pattern (~94%); brand not the seller; large","Pattern. 93.8%; Tee Distributions 3%; Triple T Trade 1.2%; monthly rev ~$3.19M; 257 products; 79k reviews; MoM +0.6%","Standard Process on Amazon",f"""{H}

{FN.format(b='Standard Process')}

From what we can see, Standard Process does about $3M a month on Amazon, and nearly all of it runs through Pattern rather than a Standard Process account. That's a real model and it clearly moves product. The tradeoff is margin and control, since the seller of record owns pricing, the Buy Box and the customer data, and the month looks flat. I know you have people on this.

{CO}

Open to a 20 minute conversation on how the Pattern arrangement is working versus owning it directly?

Yoni""",qa=["sheet third-party (Pattern.) confirmed","large brand, narrow ask"]),
E(185,"FNCE 2025|SunButter LLC","SunButter","Amazon 1P ~76% (vendor); Vitamins To Go appeared this month at ~16% on one listing; growing","Amazon.com 76.2%; Vitamins To Go 15.9% (new this month); VitaVerr 2.8%; monthly rev ~$321k; 35 products; MoM +10.8%","SunButter listings on Amazon",f"""{H}

{FN.format(b='SunButter')}

Looking at your listings, SunButter is doing about $320k a month on Amazon and growing, with Amazon selling about three quarters of it as a vendor. What stands out is a reseller called Vitamins To Go that showed up this month and is already taking close to 16% on a single listing. On a vendor setup that means someone else is undercutting Amazon on your own product and nobody owns the response.

{CO}

Open to a 20 minute look at the reseller side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed"]),
E(186,"FNCE 2025|That's it. Nutrition","That's it.","Strong brand-direct position (~97%), growing; no brand storefront showing; modest ask","That's it. 97.2%; monthly rev ~$1.48M; 71 products; 35k reviews; MoM +4.8%; mini fruit bars listing ~$380k/mo; storefront false","That's it. on Amazon",f"""{H}

{FN.format(b="That's it.")}

Looking at your listings, That's it. is doing close to $1.5M a month on Amazon through your own account and growing, with the mini fruit bars listing alone around $380k. That's a strong position. The one gap we can see is that no brand storefront shows up in marketplace data, which matters at that scale for ad traffic and for keeping the catalog together. I know you have people on this.

{CO}

Open to a 20 minute look at where the next stretch of growth is?

Yoni""",qa=["sheet sold_by Unknown; fresh data shows brand direct"]),
E(187,"FNCE 2025|Theralogix","Theralogix","Strong brand-direct position, but month down ~18%; Ovasitol carries the channel; second-set-of-eyes ask","Theralogix 99.97%; monthly rev ~$2.79M; 50 products; 15k reviews; MoM -17.6%; Ovasitol canister ~$804k/mo","Theralogix on Amazon",f"""{H}

{FN.format(b='Theralogix')}

Looking at your listings, Theralogix is doing close to $3M a month on Amazon through your own account, with Ovasitol alone around $800k. The month looks to be down close to 18%, which on a catalog this concentrated usually traces to one or two listings and to advertising or ranking on them rather than demand. I know you have people on this, so this is a second set of eyes.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(188,"FNCE 2025|Thick-It/Kent-Precision Foods Group, Inc.","Thick-It","Amazon 1P ~84% (vendor); SimplyMedical ~12%; growing; 4.13 rating","Amazon.com 83.6%; SimplyMedical 12.1%; Honest Medical 2%; monthly rev ~$278k; 63 products; 17k reviews; rating 4.13; MoM +9.6%","Thick-It vendor side on Amazon",f"""{H}

{FN.format(b='Thick-It')}

Looking at your listings, Thick-It is doing about $280k a month on Amazon and growing, with Amazon selling about 84% as a vendor and SimplyMedical taking most of the rest. The rating sits around 4.1, lower than the category leaders, and on a vendor setup content and advertising tend to be the pieces nobody fully owns. That's usually where the gap is.

{CO}

Open to a 20 minute look at the vendor side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed","combined exhibitor name; queried Thick-It"]),
E(189,"FNCE 2025|Tonnino","Tonnino","Sold by distributors and resellers (Planet Gourmet 40%, Navistro 15%, Amazon 12%); no brand account","Planet Gourmet 40.4%; Navistro 14.6%; Amazon.com 11.9%; The Bena Group 5.4%; monthly rev ~$372k; 76 products; MoM -1%","Who sells Tonnino on Amazon",f"""{H}

{FN.format(b='Tonnino')}

Looking at your listings, Tonnino is doing about $370k a month on Amazon, but none of it through a Tonnino account. Planet Gourmet sells about 40%, Navistro and a long tail of resellers most of the rest, and Amazon itself around 12%. For a premium tuna brand, that means price, content and the Buy Box on the olive oil fillets are set by whoever has stock that week.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party (Planet Gourmet) confirmed"]),
E(191,"FNCE 2025|ZEGO","ZEGO","Brand account sells under 10%; a dozen resellers split the rest; small footprint, growing","S. Republic 14%; TheNewMall 11.8%; Paradine Services 11.8%; ZEGO 8.8%; monthly rev ~$20k; 16 products; MoM +19.9%","ZEGO listings on Amazon",f"""{H}

{FN.format(b='ZEGO')}

Looking at your listings, ZEGO is doing about $20k a month on Amazon, but your own account sells under 10% of it. The rest is split across a dozen resellers like S. Republic, TheNewMall and Paradine Services, none of whom are managing content or advertising on the oats and muesli. The month is up, so the demand is there. The brand just isn't the one capturing it.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party (Exo global distribution) confirmed; brand account present at 8.8%"]),
E(192,"Las Vegas Souvenir & Resort Gift Show 2026|A.T. Storrs Ltd.","A.T. Storrs","Not found; industry-level: jewelry brand page exists, no measurable sales in marketplace data","No brand record on two attempts; sheet: A.T. STORRS brand page in Clothing/Jewelry","A.T. Storrs on Amazon",f"""{H}

{LV}

From what we can see, A.T. Storrs has a brand page on Amazon in jewelry, but the listings aren't registering measurable sales in public marketplace data. Souvenir and gift jewelry does well on Amazon when a brand owns the listings and runs them, since shoppers search for the piece they saw in a resort shop long after the trip.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["no brand record on two attempts (A.T. Storrs, A.T. STORRS); industry-level email"]),
E(193,"Las Vegas Souvenir & Resort Gift Show 2026|Advance Wildlife Education","Advance Wildlife Education","Not found; industry-level: one coloring book listing, no measurable sales","No brand record on two attempts; sheet: coloring book listed on Amazon","Advance Wildlife Education on Amazon",f"""{H}

{LV}

Looking at your listings, Advance Wildlife Education shows up on Amazon with a coloring book, but the listing isn't registering measurable sales in public marketplace data. Educational and nature titles for kids are a steady Amazon search, especially from parents and teachers who saw the product at a park or museum shop, and that demand goes to whoever has a managed listing.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["no brand record on two attempts; industry-level email","weaker fit: small publisher"]),
E(194,"Las Vegas Souvenir & Resort Gift Show 2026|AdventureKEEN","Adventure Publications","Publisher; Amazon 1P ~95%; ~350 titles doing ~$64k a month; month down ~36%; narrow ask","Amazon.com 95%; monthly rev ~$64k; 352 products; 67k reviews; MoM -35.7%; top titles ~$500/mo each","AdventureKEEN titles on Amazon",f"""{H}

{LV}

From what we can see, AdventureKEEN has about 350 titles on Amazon under the Adventure Publications imprint doing around $64k a month, nearly all sold by Amazon directly, and the month looks to be down about a third. With that many field guides selling a few hundred dollars each, the lever is usually advertising and A+ content on the backlist rather than new titles.

{CO}

Open to a 20 minute look at the catalog?

Yoni""",conf="close",qa=["SmartScout record is under imprint 'Adventure Publications'","weaker fit: book publisher, Amazon 1P"]),
E(195,"Las Vegas Souvenir & Resort Gift Show 2026|Ahead LLC","Ahead","Wrong match; industry-level: golf headwear brand page, no brand storefront visible","'Ahead' record is a drum accessories brand; sheet: Ahead golf brand page on Amazon","Ahead headwear on Amazon",f"""{H}

{LV}

From what we can see, Ahead's golf headwear shows up on Amazon under a brand page, but we don't see a brand storefront behind it. For a golf shop and resort brand, Amazon is usually where someone goes to rebuy the hat they picked up at a course, and that demand goes to whoever holds the listing that week.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="wrong match",qa=["'Ahead' matched an unrelated drum accessories brand; industry-level email from row info"]),
E(196,"Las Vegas Souvenir & Resort Gift Show 2026|American Backcountry","American Backcountry","Not found; industry-level: storefront exists but no measurable sales in marketplace data","No brand record on two attempts; sheet: Amazon storefront found","American Backcountry on Amazon",f"""{H}

{LV}

From what we can see, American Backcountry has an Amazon storefront, but the listings aren't registering measurable sales in the public marketplace data we look at. Park and destination apparel is a real Amazon category, since people search for the shirt they saw on a trip, and a storefront that isn't being run mostly sends that demand elsewhere.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["no brand record on two attempts; industry-level email"]),
E(197,"Las Vegas Souvenir & Resort Gift Show 2026|Avalon Meat Candy","Avalon Meat Candy","Not found; industry-level: one jerky chips listing, no measurable sales","No brand record on two attempts; sheet: beef jerky chips listed on Amazon","Avalon Meat Candy on Amazon",f"""{H}

{LV}

Looking at your listings, Avalon Meat Candy is on Amazon with a jerky chips listing that isn't registering measurable sales in public marketplace data. Jerky and meat snacks are one of the stronger gift-shop categories on Amazon, since customers reorder after the trip, and it takes content, advertising and reviews on the listing to catch that.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["no brand record on two attempts; industry-level email"]),
E(198,"Las Vegas Souvenir & Resort Gift Show 2026|Bigfoot Sock Co / Sock Harbor","Bigfoot Sock Co.","Not found; industry-level: brand page exists, no measurable sales in marketplace data","No brand record on two attempts; sheet: Bigfoot Sock Co. brand page on Amazon","Bigfoot Sock Co on Amazon",f"""{H}

{LV}

From what we can see, Bigfoot Sock Co has a brand page on Amazon, but the listings aren't registering measurable sales in public marketplace data. Novelty socks are a big Amazon gift category, especially in Q4, and the brands that win there own their listings and run advertising on them rather than relying on the gift-shop customer to find them.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["combined exhibitor name; queried Bigfoot Sock Co. (Sock Harbor not queried)","no brand record on two attempts; industry-level email"]),
E(199,"Las Vegas Souvenir & Resort Gift Show 2026|Blue Planet Eco-Eyewear","Blue Planet Eco-Eyewear","Wrong match; industry-level: eyewear listed, no brand record","'Blue Planet' record is Blue Planet Surf balance boards; sheet: Blue Planet Eco-Eyewear products listed","Blue Planet Eco-Eyewear on Amazon",f"""{H}

{LV}

Looking at your listings, Blue Planet Eco-Eyewear is on Amazon, but the listings aren't registering measurable sales in the public marketplace data we look at. Sunglasses are one of the most searched gift categories on Amazon, and an eco story is a real differentiator there if the content, advertising and reviews are actually built.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="wrong match",qa=["'Blue Planet' matched Blue Planet Surf (balance boards); full name returned empty; industry-level email"]),
E(200,"Las Vegas Souvenir & Resort Gift Show 2026|Boardwalk Puzzles","Boardwalk Puzzles","Not found; industry-level: puzzle listings exist, no measurable sales in marketplace data","No brand record on two attempts; sheet: Boardwalk Puzzles listings and Dowdle storefront page","Boardwalk Puzzles on Amazon",f"""{H}

{LV}

From what we can see, Boardwalk Puzzles has listings on Amazon, but they aren't registering measurable sales in the public marketplace data we look at. Jigsaw puzzles are a strong Amazon category with a big Q4, and destination and city puzzles in particular sell to people who bought one on a trip and want the next.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",conf="not found",qa=["no brand record on two attempts (Boardwalk Puzzles, Boardwalk Puzzle); sheet mentions a Dowdle storefront page, not queried; industry-level email"]),
]
run(raw,emails)
