from batchlib import *
NF=RAW(None,[],[])
raw={
"Salty Dawg":NF,"Sancocho":NF,"SCANIA SWEDEN":NF,
"SOLARA SUNCARE":RAW(P("Solara Suncare","Beauty & Personal Care","Facial Sunscreens",1.13,"",True,"https://www.amazon.com/stores/SolaraSuncare/page/98ED9EFA-96A6-4985-B9AD-53B4C8891C86",0,-0.404,0.182,33.8,3.79,16,748,37305.51,481438.33),
 S(("Carbon Beauty",89.822),("JJ Online store",3.639),("Mint Blossoms",2.947),("Tech P. Horizon",2.073),("V Choices",1.23),("Coastal Co. Goods",0.289)),
 T(("Solara Suncare Go! Daily Defense Soothing Face Sunscreen (1.7 fl oz)","B0BG6ZRYMC",9119.95),("Solara Suncare Guardian Angel Super Peptide Sunscreen Milk (1 fl oz)","B0D9L1XLPZ",8149.72),("Solara Suncare Go! Mineral Defense SPORT Body Sunscreen (5 fl oz)","B0DBM6C2S8",3658.17),("Solara Suncare Good Karma Dry Oil Mineral Sunscreen (3.4 fl oz)","B0DGH2X4H8",3024),("Solara Suncare Go! Vacation Glow Tinted Mineral Sunscreen (1.7 fl oz)","B0BGDFC8H6",2499))),
"Sunchill":RAW(P("Sunchill","Toys & Games","Pool Rafts & Inflatable Ride-ons",0.5,"",False,"",0,-0.6,None,99,4.8,2,30,2574,30927.04),
 S(("Sunchill",100)),
 T(("Sunchill SunChair Inflatable Float Chair, Mint","B0H4FZ5S4S",2574),("Sunchill SunChair Inflatable Float Chair","B0G15S4QG5",0))),
"SUZUKI":RAW(P("Suzuki","Musical Instruments","Melodicas",1.95,"",True,"https://www.amazon.com/stores/Suzuki/page/EFCEC546-45B9-4CDE-A967-8C31CEB44B2B",0.16,-0.158,-0.149,256.47,4.43,96,3433,39023.71,646874.96),
 S(("Briskdrop",22.482),("Amazon.com",15.966),("Sweetwater Sound",10.732),("Central Florida PowerSports",9.358),("Craft and Sound Hub",8.206),("Cyclemax",5.014)),
 T(("Suzuki HB-250 Two Octave Tone Chime Set (unrelated Suzuki instruments)","B00LIUCL0I",7199.94),("Suzuki M-37C Alto Melodion (unrelated)","B000XYFBMK",5487.44),("Suzuki Marine 990A0-01E81-01Q ECSTAR Hypoid Gear Oil SAE 90","B07XF7LFYR",4814.22),("Suzuki PRO-37V3 Pro Alto Melodion (unrelated)","B07MMRF1H1",4756.09),("Suzuki Omnichord Gig Bag (unrelated)","B0CVV3NZC1",2315.68))),
"Teakdecking Systems":RAW(P("Teakdecking Systems","Sports & Outdoors","Boat Tools",1.75,"",False,"",0,0.745,-0.379,45.22,4.36,8,206,6393.25,57582.16),
 S(("TeakDecking Systems",59.715),("Merritt Supply",37.82),("IPC-STORE",1.452),("Fiberglass Supply Depot",1.013)),
 T(("Teakdecking Systems (TDS) Reefing Hook, Caulk Removal Tool, 8.5in","B08KQK38JP",3300.79),("TDS SIS440 Marine Caulk Sausage 20oz, Black","B01E8M0T88",597.74),("TDS Seam Sander Kit","B0GHPY6WG4",552.93),("TDS SIS440 Marine Caulk Sausage 20oz, Gray","B0GHBJG866",501.03),("TDS SIS 440 Teak Deck Caulk Cartridge 10.3oz, White","B00CFN1MNE",442.82))),
"Brasso":RAW(P("Brasso","Health & Household","Household Cleaning Metal Polishes",2.92,"",True,"https://www.amazon.com/stores/ReckittHomeandHygiene/page/4B57FD6D-B4F6-4934-9D2A-6001162DABB9",0.838,-0.092,0.074,23.15,4.44,12,31503,121387.91,1511488.48),[],[]),
"Tommy Bahama":RAW(P("Tommy Bahama","Sports & Outdoors","Camping Chairs",0.78,"",True,"https://www.amazon.com/stores/TommyBahama/page/A00B18A4-3CA1-4FA6-984C-6288D4B16718",0.812,-0.241,-0.048,71.99,4.45,1323,80018,1332947.42,21440151.75),
 S(("Amazon.com",81.16),("Underware House",5.024),("IMLDESIGNS",2.316),("AR DISCOUNTS",2.149),("ATLANTIC B&G",1.702),("New depot",1.477)),
 T(("Tommy Bahama 5-Position Classic Lay Flat Folding Backpack Beach Chair, Navy","B07YH2LB9R",85863.83),("Tommy Bahama 4-Position Easy-Out Backpack Beach Chair, 2-Pack","B0CWWC57G8",68412.56),("Tommy Bahama 4-Position Hi-Boy Beach Chair, Blue Palms, 2-Pack","B0CWVWQ6YS",59645.63),("Tommy Bahama 5-Position Classic Lay Flat Backpack Beach Chair, Red White Blue","B07YH3W49D",46581.7),("Tommy Bahama 4-Position Hi-Boy Beach Chair, Logo Stripe, 2-Pack","B0CWVXND5F",43185.56))),
"Volvo Penta":RAW(P("Volvo Penta","Automotive","Gear Oils",4.2,"",False,"",0,-0.255,-0.322,96.82,4.68,45,4644,67660.31,663184.58),
 S(("LEADERS RPM",73.207),("Doug Russell Marine",7.746),("Power Mower Sales USA",5.109),("MarineEngineParts",1.562),("Avalon Online",1.419),("Stär67",1.326)),
 T(("Volvo Penta Gear Oil Synthetic 75W 90 1-Gallon","B001VMLF82",6646.94),("Volvo Penta OEM Water Pump Impeller Kit 21700445","B016WPZ4OI",6231.6),("Volvo Penta OEM 10W-40 Full Synthetic Engine Oil 21681795","B0761Y5ZZF",5253.04),("Volvo Penta Gear Oil Synthetic 75W 90 1-Quart","B001VMCUKE",4010.28),("Volvo Penta OEM Synthetic Engine Oil 10w-40 Quart, Pack of 5","B00KRO0UO0",3875.89))),
"YAMAHA":RAW(P("YAMAHA","Musical Instruments","Home Digital Pianos",4.04,"",False,"",0.437,-0.03,0.091,475.93,4.54,2093,287738,11310667.32,160728860.64),
 S(("Amazon.com",43.688),("Sweetwater Sound",10.435),("WORLD WIDE STEREO",4.555),("FocusProAudio",2.481),("K-Wind Instruments Pro",2.221),("ECOMADE ARENA",2.013)),
 T(("YAMAHA P71 88-Key Digital Piano (unrelated to marine)","B01LY8OUQW",488689.14),("Yamaha P145BT Digital Piano (unrelated)","B0F9H3SHFJ",331054.53),("Yamaha YFL-222 Flute (unrelated)","B01DD4MIPY",222471),("Yamaha P225 Digital Piano (unrelated)","B0CBN7HYKB",187402.38),("Yamaha P-143 Digital Piano Bundle (unrelated)","B0FMCGPCR4",169317.51))),
"AONIC":RAW(P("AONIC","Health & Household","Sports Nutrition Ready to Drink Protein",1.14,"",False,"",0,-0.235,None,41.58,4.07,7,236,14303.7,224517.13),
 S(("Aonic",100)),
 T(("Aonic Fuel Protein Shake, Smooth Vanilla, 11 fl oz (Pack 12)","B0G5RWLK1W",11263.5),("AONIC Build Creatine, Fruit Punch, 30 Sticks","B0FXJMK2ZW",1009.05),("AONIC Build Creatine, Unflavored, 30 Sticks","B0FXJGJ13F",911.43),("AONIC Flow Blood Pressure Support, 90ct","B0FXFDJKV2",839.79),("AONIC GLP-1 Companion Supplement, 90 Caps","B0GKDFHFQP",279.93))),
"Applegate":RAW(P("Applegate","Grocery & Gourmet Food","Frozen Nuggets & Tenders",1.07,"Applegate Brands",True,"https://www.amazon.com/stores/Applegate/page/B23ECBD8-F79D-474B-B96B-7FB048C4E8E0",0.502,0.039,0.907,12.68,4.38,86,153471,4155657.53,40736470.77),
 S(("Amazon.com",50.16),("Whole Foods Market",49.12),("Basil Grocery LLC",0.71),("Entrepreneurs 1901",0.01)),
 T(("APPLEGATE NATURALS Chicken & Maple Breakfast Sausage Patties, 16 OZ","B0BWPJ54BV",194723.4),("APPLEGATE NATURALS Chicken & Maple Breakfast Sausage Links, 16 OZ","B0DQXZ1G9H",190985.84),("APPLEGATE ORGANICS Oven Roasted Turkey Breast, 6oz","B00I2VLK2Q",188200.32),("APPLEGATE Naturals Gluten-Free Breaded Chicken Breast Tenders","B09LG1CSNR",152285.28),("Applegate Farms Chicken Nugget Gluten Free Value Pack, 16 Ounce","B07PXG3WSF",144505.65))),
"Cargill":RAW(P("Cargill","Grocery & Gourmet Food","Salt & Salt Substitutes",5.38,"",False,"",0,0.039,1.044,71.23,4.71,8,109,10909.33,144345.84),
 S(("FoodserviceDirect Inc.",46.044),("Homegoods Shop",29.705),("CountryMax Stores",8.451),("Lovinio",4.759),("Healthy_Goods",3.982),("Triplenet Pricing INC",2.588)),
 T(("Cargill Salt Diamond Crystal Pellet 50Lb","B001CECONY",3546),("Cargill Purified Untreated Sea Salt, 50 Pound","B00N37ZENU",2722.5),("Cargill Golden Nature Pasteurized Whole Liquid Eggs, 2 lb (Pack of 12)","B00B048LWE",1904.85),("Cargill Pretzel Salt Coarse Topping, 25 Lb","B003XDCZTU",1634.58),("Cargill Loyall Life Large Breed Dog Food 40 Pounds","B0D2RRHFFK",449.76))),
"Common Ground":RAW(P("COMMON GROUND","Beauty & Personal Care","Shampoo & Conditioner Sets",0.94,"Organics Buddy",True,"https://www.amazon.com/stores/CommonGround/page/D7D811AF-29C1-4D63-BECA-AB68C33FC2FB",0,0.264,-0.067,25.14,4.37,18,955,14102.73,216195.68),[],[]),
"Daily Crunch":RAW(P("Daily Crunch","Grocery & Gourmet Food","Almonds",1.88,"",True,"https://www.amazon.com/stores/DailyCrunchSnacks/page/9758E082-E4B4-43F4-8ADF-C775B8C58660",0.018,-0.207,0.756,24.93,4.18,43,872,42298.46,604689.35),
 S(("Daily Crunch Snacks",58.268),("NEEXMARKET",19.231),("GrandioseGoods",9.742),("Truly-deal",4.515),("Exquisites Market",2.314),("Amazon.com",1.763)),
 T(("Daily Crunch Sprouted Almonds & Pepitas, Dill Pickle, 4oz","B0D4648758",12465),("Daily Crunch Sprouted Almonds & Pepitas, Dill Pickle, 4oz, 2 Pack","B0CCW986BC",3402.73),("Daily Crunch Sprouted Nuts & Seeds, Mediterranean Medley, 2 Pack","B0GHDMSBNN",3387.74),("Daily Crunch Sprouted Almonds, Mini Variety Pack, 24 Pack","B0H852SBFM",2973.81),("Daily Crunch Sprouted Cashews & Edamame, Sweet & Spicy Sichuan, 4oz","B0D8LKGD7K",2873.64))),
"Sunsweet":RAW(P("Sunsweet","Grocery & Gourmet Food","Dried Prunes",3.87,"",False,"",0,-0.019,0.333,32.85,4.5,76,16465,290814.2,3461757.28),
 S(("Sunsweet Growers",30.756),("RLP Marketing LLC",11.255),("Next Day Shipping Store",10.846),("Product Planet Inc",7.458),("ShippedFast",6.237),("1st & Fast",3.221)),
 T(("Sunsweet Gold Label Ones Individually Wrapped Prunes 6.0 Ounces (Pack of 2)","B007AN8OZ8",34241),("Sunsweet Pitted Prunes Bundle, 16 oz Canister & Recipe Book","B0BKT93D8H",25693.47),("Sunsweet Prune Juice, 32 Ounce (Pack of 2)","B0F787TQNP",24130.4),("Sunsweet Prune Juice, Pack of 8 Cans, 7.5 oz","B0F7HVZ2RB",23481.54),("Sunsweet Amazin Prune Juice, 6x4 Pack, 7.5oz","B0CTTFZ5P2",20114.01))),
"Supergut":RAW(P("Supergut","Health & Household","Dietary Fiber Nutritional Supplements",1.38,"Supergut Official",True,"https://www.amazon.com/stores/Supergut/page/7835B9CC-DE35-45A3-86C5-86C004395689",0,-0.208,0.427,32.75,4.22,21,2601,432469.99,7822920.58),
 S(("Supergut Official",85.639),("Abundita",3.268),("Scissors Plus",3.053),("DIGITAL MART",1.899),("The Brand Collective",1.868),("supreme7",1.827)),
 T(("Supergut GLP1 Daily Support (20 Servings)","B0DRWLTRHB",96499.24),("Supergut GLP1 Daily Support, Blood Orange (18 Servings)","B0F8LKTQTX",55725.5),("Supergut GLP1 Daily Support, Raspberry Lemon, 18 Servings","B0F8LRV2QK",48891.62),("Supergut Foundational Daily Fiber Powder, Unflavored, 20 Servings","B0FM164X5M",48716.58),("Supergut GLP1 Daily Support, Variety Pack (15 Servings)","B0F8LG2MWM",47000.94))),
"Wilde Chips":RAW(P("Wilde Chips","Health & Household","Sports Nutrition Chips & Crisps Snacks",3.46,"Wilde Chips",True,"https://www.amazon.com/stores/WildeChips/page/062E9906-FE44-4F8E-ADDD-B1A9931EBA31",0.165,-0.016,0.36,33.33,4.32,46,11523,749653.08,12703103.88),
 S(("Wilde Chips",79.541),("Amazon.com",16.471),("Whole Foods Market",0.703),("SANTARA USA",0.62),("O.A.C MegaStore LLC",0.407),("Everyday Goods Inc.",0.261)),
 T(("WILDE Protein Chips Variety Pack, 1.34 oz Bags, Pack of 12","B0B9WDZ7K9",284924.48),("WILDE Chicken & Waffles Protein Chips, Pack of 12","B0F3DPZ3QP",73599.55),("WILDE Protein Chips Variety Pack, Pack of 12","B0FNB1BP64",70144.51),("WILDE Himalayan Pink Salt Protein Chips, Pack of 12","B0H8W7PCPF",64386.11),("Wilde Brands Sea Salt & Vinegar Protein Chips, 4 OZ","B0BFKD24CF",42086.4))),
"Zesty Z":RAW(P("Zesty Z","Grocery & Gourmet Food","Pita Chips & Crisps",0.27,"",False,"",0,0.309,None,29.33,4.29,11,433,2950.77,7412.98),
 S(("Zesty Z",100)),
 T(("Zesty Z 5g Fiber Pita Chips, Parmesan Garlic","B0CWJGVYZM",1631.32),("Zesty Z 5g Fiber Pita Chips, Parmesan Garlic","B0CYZMYHXH",1319.45),("Zesty Z 5g Fiber Pita Chips, Sea Salt","B0GQHNK9V9",0),("Zesty Z Fiber Pita Chip Variety, Pack of 8","B0GH91Z3RH",0),("Zesty Z High Fiber Pita Chip, Parmesan Garlic, Pack of 8","B0GH8YH9BY",0))),
"CoTa Global":RAW(P("CoTa Global","Toys & Games","Children's Swim Rings",2.09,"Mozlly",True,"https://www.amazon.com/stores/CoTaGlobal/page/B720A69A-0838-4CE5-8C79-B786CA48AECC",0,-0.286,-0.056,27.9,4.4,45,4317,11614.36,209709.83),
 S(("Mozlly",99.772),("Lunch money",0.209),("Ranger trading",0.019)),
 T(("CoTa Global Inflatable Pool Float Tube Confetti, Rose Gold","B07C2NC31C",1694.94),("CoTa Global Neptune Nautical Wooden Jewelry Box, 6.5 Inch","B076HBY4BQ",1462.86),("CoTa Global Alexander Wooden Barrel Wine Rack, 18 Bottles","B08DHR424B",799.95),("CoTa Global Sloth Snow Globe, 45 mm","B096X6WCT4",390.77),("CoTa Global Inflatable Pool Float Tube Confetti 36 Inches (Pack of 2)","B0HB25JQ2N",351.78))),
"NeilMed":RAW(P("NeilMed","Health & Household","Sinus Medicine",4.4,"Amazon.com",True,"https://www.amazon.com/stores/NeilMedPharmaceuticals/page/3FBD35CC-E591-42D8-B3B5-BB420454C4E4",0.79,-0.027,-0.147,18.86,4.5,103,174386,2115209.46,26962200.68),[],[]),
"OLD GUYS RULE":RAW(P("OLD GUYS RULE","Clothing, Shoes & Jewelry","Men's Novelty T-Shirts",0.9,"Old Guys Rule",True,"https://www.amazon.com/stores/OldGuysRule/page/895FE4DF-71BE-4A3C-B9F6-285A1A15FC9A",0,-0.077,-0.551,27.44,4.8,10,452,2004.55,46526.51),
 S(("Old Guys Rule",100)),
 T(("OLD GUYS RULE Men's Graphic T-Shirt, On Permanent Vacation (Heather Indigo, 3X-Large)","B0160CNHCO",454.5),("OLD GUYS RULE Men's Graphic T-Shirt, On Permanent Vacation (Heather Indigo, XX-Large)","B0160CNFPI",359.4),("OLD GUYS RULE Men's Graphic T-Shirt, On Permanent Vacation (Heather Indigo, Medium)","B0160CNAVM",324.32),("OLD GUYS RULE Men's Graphic T-Shirt, On Permanent Vacation (Heather Indigo, X-Large)","B0160CNE1I",289.5),("Old Guys Rule Men's Graphic T-Shirt, Respect the Rust (Dark Heather, XX-Large)","B088QSQWTL",215.64))),
"Parks Project":RAW(P("Parks Project","Sports & Outdoors","Women's Hiking & Outdoor Recreation Fleece Jackets",None,"",False,"",0,None,None,None,None,0,0,0,0),[],[]),
"Pennington Bear Company":RAW(P("Pennington Bear Company","Toys & Games","Stuffed Animals & Teddy Bears",2,"",True,"https://www.amazon.com/stores/PenningtonBearCompany/page/32BCE87C-4AB1-4885-A9FF-46761E703F9E",0,0.3,-0.2,20.49,4.8,1,1352,3544.77,64316.03),
 S(("Atharva Brands",100)),
 T(("Pennington Bear Company The Original Sock Monkey, Hand-Knit, 20 inch","B07GBJKMZ1",3544.77))),
}
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
FL="Saw you're exhibiting at FLIBS next month."
FN="Saw that {b} exhibited at FNCE last year."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
END="We manage the channel end to end."
KL="Las Vegas Souvenir & Resort Gift Show 2026|"; KF="FLIBS 2026|"; KN="FNCE 2025|"
ASK_NF="Is Amazon something you're looking at more seriously?"
def nf(row,key,q,angle,points,subject,body,qa,opener,ask=ASK_NF,conf="not found"):
    return E(row,key,q,angle,points,subject,f"""{H}

{opener}

{body}

{PROOF} {END}

{ask}

Yoni""",conf=conf,qa=qa)
emails=[
nf(270,KF+"Salty Dawgs","Salty Dawg","Not found; industry-level: one listing, seller not shown, no measurable sales","No brand record on two attempts (Salty Dawg, Salty Dawgs); sheet: single listing, seller not shown","Salty Dawgs on Amazon",
"Looking at your listings, Salty Dawgs shows up on Amazon with a single listing that isn't registering measurable sales in public marketplace data, and we don't see a brand storefront. Boat show brands get searched by name on Amazon long after the show, and a lone listing without content, advertising or reviews behind it doesn't catch that.",
["no brand record on two attempts; industry-level email","sheet sold_by Unknown"],FL),
nf(271,KF+"Sancochos","Sancocho","Not found; industry-level: one listing, seller not shown, no measurable sales","No brand record on two attempts (Sancocho, Sancochos); sheet: single listing, seller not shown","Sancochos on Amazon",
"Looking at your listings, Sancochos shows up on Amazon with a single listing that isn't registering measurable sales in public marketplace data, and we don't see a brand storefront. For a brand exhibiting at a show like FLIBS, Amazon is usually where the people who saw you go to look afterward, and right now there's nothing built to catch that.",
["no brand record on two attempts; industry-level email","sheet sold_by Unknown; product line unclear"],FL),
nf(272,KF+"Scania/Mack Boring & Parts Co.","SCANIA SWEDEN","Not found; industry-level: one listing sold by Amazon, no brand presence; engine distributor, weak fit","No brand record on two attempts (SCANIA SWEDEN, Scania); sheet: single listing sold by Amazon.com","Scania marine parts on Amazon",
"From what we can see, Scania has a single listing on Amazon sold by Amazon itself, no brand storefront, and nothing registering measurable sales in public marketplace data. For a marine engine line sold through Mack Boring and dealers that's expected. Where Amazon tends to matter for engine brands is filters, service kits and consumables that owners search for by part number.",
["combined exhibitor name; queried SCANIA SWEDEN (sheet brand name) and Scania","no brand record on two attempts; industry-level email","weaker fit: engine distributor"],FL,ask="Is Amazon something you're looking at for the parts side?"),
E(279,KF+"Solara","SOLARA SUNCARE","Nearly all revenue through one seller (Carbon Beauty ~90%); 3.8 rating; month down ~40% after summer","Carbon Beauty 89.8%; JJ Online store 3.6%; Mint Blossoms 2.9%; monthly rev ~$37k; 16 products; 748 reviews; rating 3.79; MoM -40%; 12M MoM +18%","Solara Suncare on Amazon",f"""{H}

{FL}

Looking at your listings, Solara Suncare is doing about $37k a month on Amazon, almost all of it through a seller called Carbon Beauty rather than a Solara account, with a few small resellers on the same listings. If Carbon Beauty is your partner, fine. What stands out either way is a 3.8 rating across the catalog, which for a premium sunscreen is the thing capping conversion, and the off-season is when that gets fixed.

{CO}

Would it make sense to have a quick conversation before next season?

Yoni""",qa=["sheet third-party (JJ Online store); fresh data shows Carbon Beauty at 90%, may be an affiliated account, verify"]),
E(281,KF+"Sunchill","Sunchill","Tiny footprint: two listings, ~$2.6k a month, 30 reviews, no storefront; sold direct; season ending","Sunchill 100%; monthly rev ~$2.6k; TTM ~$31k; 2 products; 30 reviews; rating 4.8; MoM -60%","Sunchill on Amazon",f"""{H}

{FL}

Looking at your listings, the Sunchill SunChair is on Amazon with two listings, sold direct, doing a few thousand dollars a month on about 30 reviews at a 4.8 average, and no brand storefront. The product clearly lands with the people who find it. Almost nobody does, and the off-season is when the content, reviews and advertising get built so next spring starts from a different place.

{CO}

Would it make sense to have a quick conversation before next season?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(282,KF+"Suzuki Marine","SUZUKI","Marine parts sold by dealers (Central Florida PowerSports, Cyclemax); the Suzuki name on Amazon is dominated by the instrument line; narrow ask","Mixed record: Briskdrop 22.5%; Amazon.com 16%; Sweetwater 10.7%; Central Florida PowerSports 9.4%; Cyclemax 5%; ECSTAR gear oil ~$4.8k/mo","Suzuki Marine parts on Amazon",f"""{H}

{FL}

From what we can see, Suzuki Marine parts and oil show up on Amazon through dealers like Central Florida PowerSports and Cyclemax rather than a Suzuki account, and the Suzuki name on Amazon is mostly the instrument line, so anyone searching lands on melodicas before outboard parts. I know Suzuki has people on this. It's a narrow point about the ECSTAR oil and service parts boaters search for by name.

{CO}

Open to a 20 minute look at the marine parts side of Amazon?

Yoni""",conf="close",qa=["mixed record: 'Suzuki' on Amazon is mostly Suzuki musical instruments; SS_ totals not marine-specific","sheet third-party (Central Florida PowerSports) confirmed for marine listings","large brand, narrow ask"]),
E(284,KF+"Teakdecking Systems","Teakdecking Systems","Brand sells ~60% direct; Merritt Supply ~38% on the same listings; small footprint (~$6k a month); no storefront","TeakDecking Systems 59.7%; Merritt Supply 37.8%; monthly rev ~$6.4k; 8 products; 206 reviews; MoM +75%; 12M MoM -38%; storefront false","Teakdecking Systems on Amazon",f"""{H}

{FL}

Looking at your listings, Teakdecking Systems is on Amazon at about $6k a month across eight listings, with your own account selling about 60% and Merritt Supply most of the rest on the same caulk and reefing hook listings. There's no brand storefront. Teak caulk is a repeat purchase owners search for by name, so this is a small channel with a reseller taking a big slice of it.

{CO}

Would it make sense to have a quick conversation about owning the channel fully?

Yoni""",brand_sellers=["TeakDecking Systems"],qa=["sheet says brand store; fresh data shows no storefront and Mixed sellers"]),
nf(286,KF+"The Brass Works","Brasso","Wrong match; brass hardware maker matched to Brasso (Reckitt) in the sheet; industry-level email","'Brasso' record is Reckitt metal polish (~$121k/mo), not the exhibitor; no data for The Brass Works","The Brass Works on Amazon",
"From what we can see, The Brass Works doesn't have a brand presence on Amazon, and the listings that come up under a similar name belong to a polish brand. For a custom marine hardware maker that's understandable. Where Amazon tends to come up for brands like yours is standard fittings and replacement parts that owners search for by name, and right now nothing under The Brass Works answers that.",
["wrong match: sheet mapped exhibitor to Brasso (Reckitt) storefront; SS_ numbers are Brasso's","weaker fit: custom marine hardware"],FL,conf="wrong match"),
E(287,KF+"Tommy Bahama","Tommy Bahama","Very large; Amazon 1P ~81%; licensed beach chairs carry the top listings; month down ~24%; narrow ask on the apparel side","Amazon.com 81.2%; Underware House 5%; IMLDESIGNS 2.3%; monthly rev ~$1.33M; 1,323 products; 80k reviews; MoM -24%; 12M MoM -5%","Tommy Bahama on Amazon",f"""{H}

{FL}

From what we can see, Tommy Bahama does about $1.3M a month on Amazon, roughly 80% of it sold by Amazon as a vendor, and the beach chairs carry the top listings while the apparel that defines the brand barely shows up there. The month looks to be down close to a quarter. I know Tommy Bahama has an Amazon team. This is a narrow point about the apparel side and the third-party layer on it.

{CO}

Open to a 20 minute look at how the apparel is positioned on Amazon?

Yoni""",qa=["sheet third-party (Underware House); fresh data shows Amazon 1P 81% (Amazon 1P)","very large brand, narrow ask"]),
E(289,KF+"Volvo Penta","Volvo Penta","Parts and oil sold entirely by dealers (LEADERS RPM 73%, Doug Russell Marine 8%); no brand account or storefront; down ~26% month and ~32% on the year","LEADERS RPM 73.2%; Doug Russell Marine 7.7%; Power Mower Sales 5.1%; monthly rev ~$68k; 45 products; 4,644 reviews; MoM -25.5%; 12M MoM -32%","Volvo Penta parts on Amazon",f"""{H}

{FL}

Looking at your listings, Volvo Penta oil, impellers and service parts do about $68k a month on Amazon, with LEADERS RPM selling close to three quarters of it and other dealers the rest. There's no Volvo Penta account or storefront, and the trend is down on both the month and the year. I know Volvo Penta has people on this. It's a narrow point about who controls the price, content and Buy Box on parts owners search for by number.

{CO}

Open to a 20 minute look at the parts side of Amazon?

Yoni""",qa=["sheet third-party (LEADERS RPM) confirmed","large brand, narrow ask"]),
E(292,KF+"Yamaha Marine","YAMAHA","Yamaha on Amazon is dominated by the instrument line; marine parts sold by powersports dealers; no marine brand account; narrow ask","Mixed record: Amazon.com 43.7%; Sweetwater 10.4%; WORLD WIDE STEREO 4.6%; top listings all pianos; sheet: sold by Pine Grove Powersports","Yamaha Marine parts on Amazon",f"""{H}

{FL}

From what we can see, the Yamaha name on Amazon is almost entirely the instrument business, and the marine parts and oil that boaters search for sit underneath it, sold by powersports dealers like Pine Grove rather than a Yamaha Marine account. I know Yamaha has an Amazon team. This is a narrow point about the outboard parts, Yamalube and service kits, and who controls price and content on those listings.

{CO}

Open to a 20 minute look at the marine parts side of Amazon?

Yoni""",conf="close",qa=["mixed record: 'YAMAHA' on Amazon is mostly musical instruments; SS_ totals not marine-specific","sheet third-party (Pine Grove Powersports)","very large brand, narrow ask"]),
E(294,KN+"Aonic Inc.","AONIC","Small footprint (~$14k a month) carried by one protein shake listing; sold direct; 4.07 rating; month down ~24%; no storefront showing","Aonic 100%; monthly rev ~$14k; 7 products; 236 reviews; rating 4.07; MoM -23.5%; protein shake ~$11k/mo; storefront false","Aonic on Amazon",f"""{H}

{FN.format(b='Aonic')}

Looking at your listings, Aonic is on Amazon at about $14k a month, sold direct, with the vanilla protein shake doing nearly all of it and the creatine and supplement lines a few hundred dollars each. The month looks to be down close to a quarter and the rating sits just above 4. Ready-to-drink protein is a big, ad-driven category on Amazon, and this looks like a catalog running without much behind it.

{CO}

Would it make sense to have a quick conversation?

Yoni""",qa=["sheet says brand store; fresh data shows no storefront"]),
E(295,KN+"Applegate","Applegate","Very large; Amazon 1P and Whole Foods ~99% (vendor); growing strongly on the year; narrow ask on advertising and content","Amazon.com 50.2%; Whole Foods Market 49.1%; monthly rev ~$4.16M; 86 products; 153k reviews; MoM +3.9%; 12M MoM +91%","Applegate vendor side on Amazon",f"""{H}

{FN.format(b='Applegate')}

From what we can see, Applegate does about $4M a month on Amazon, split almost evenly between Amazon and Whole Foods Market as the sellers, and the year has been strong. That's a vendor setup working well. The piece usually left on the table with vendor-only brands is advertising and content ownership across the catalog, since Amazon controls price and stock. I know Applegate has people on this.

{CO}

Open to a 20 minute look at the vendor side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed; Whole Foods Market counted as third-party per rule but is Amazon-owned","very large brand, narrow ask"]),
E(297,KN+"Cargill","Cargill","Bulk salt and ingredients sold by distributors (FoodserviceDirect 46%, Homegoods Shop 30%); tiny Amazon slice for a giant; weak fit, narrow ask","FoodserviceDirect 46%; Homegoods Shop 29.7%; CountryMax 8.5%; monthly rev ~$11k; 8 products; 109 reviews; 12M MoM +104%","Cargill consumer listings on Amazon",f"""{H}

{FN.format(b='Cargill')}

From what we can see, the Cargill name on Amazon is a handful of bulk salt, liquid egg and pet food listings doing about $11k a month, all sold by distributors like FoodserviceDirect rather than a Cargill account. For a company Cargill's size that's clearly not a priority channel, and it may never be. Where it does come up is consumer-facing brands and ingredients that home bakers and small operators search for by name.

{CO}

Is there a consumer-facing line where Amazon is on the roadmap?

Yoni""",qa=["sheet third-party (FoodserviceDirect) confirmed","weaker fit: B2B ingredient company"]),
nf(299,KN+"CommonGround","Common Ground","Wrong match; advocacy organization matched to an unrelated personal care brand; likely non-product exhibitor","'COMMON GROUND' record is a shampoo brand (~$14k/mo, Organics Buddy); sheet listing is a book ISBN; exhibitor appears to be an advocacy program","CommonGround on Amazon",
"From what we can see, CommonGround doesn't have a product presence on Amazon, and the listings that come up under the name belong to an unrelated personal care brand. If CommonGround is purely an advocacy program, Amazon isn't relevant and this note can be ignored. If there's a product or publishing side to it, that's where the marketplace data would matter.",
["wrong match: 'Common Ground' matched a shampoo brand; sheet listing is a book","org_type: likely nonprofit or advocacy program, weak fit"],FN.format(b='CommonGround'),conf="wrong match",ask="Is there a product side to CommonGround where Amazon comes up?"),
E(300,KN+"Daily Crunch Inc.","Daily Crunch","Brand sells ~58% direct; ~40% through resellers (NEEXMARKET 19%, GrandioseGoods 10%) on the same listings; month down ~21% after a strong year","Daily Crunch Snacks 58.3%; NEEXMARKET 19.2%; GrandioseGoods 9.7%; Truly-deal 4.5%; monthly rev ~$42k; 43 products; MoM -20.7%; 12M MoM +76%","Reseller share on Daily Crunch listings",f"""{H}

{FN.format(b='Daily Crunch')}

Looking at your listings, Daily Crunch is doing about $42k a month on Amazon, with your own account selling under 60% of it and resellers like NEEXMARKET and GrandioseGoods taking most of the rest on the same dill pickle almonds listing that carries the brand. The year has been strong and the month is down about 20%. That's usually a sign the reseller layer is starting to set price and win the Buy Box.

{CO}

Would it make sense to have a quick conversation about tightening up the reseller side?

Yoni""",brand_sellers=["Daily Crunch Snacks"],qa=["sheet Brand (Seller Central); fresh data shows ~40% resellers (Mixed)"]),
E(309,KN+"Sunsweet Growers, Inc.","Sunsweet","Brand account sells ~31%; ~69% through resellers (RLP Marketing 11%, Next Day Shipping 11%, Product Planet 7%); no storefront","Sunsweet Growers 30.8%; RLP Marketing 11.3%; Next Day Shipping Store 10.8%; Product Planet 7.5%; ShippedFast 6.2%; monthly rev ~$291k; 76 products; 16k reviews; 12M MoM +33%; storefront false","Who sells Sunsweet on Amazon",f"""{H}

{FN.format(b='Sunsweet')}

Looking at your listings, Sunsweet does about $290k a month on Amazon, but your own account sells under a third of it. The rest is spread across resellers like RLP Marketing, Next Day Shipping Store and Product Planet on the same prune and juice listings, and there's no brand storefront. For a brand that owns its category the way Sunsweet does, that's a lot of Buy Box, pricing and margin sitting with other sellers.

{CO}

Would it make sense to have a quick conversation about tightening up the reseller side?

Yoni""",brand_sellers=["Sunsweet Growers"],qa=["sheet sold_by Unknown; fresh data shows Mixed with ~69% resellers"]),
E(310,KN+"Supergut","Supergut","Strong brand-direct position (~86%) after a big year, but month down ~21% and a dozen small resellers appearing on the GLP-1 listings","Supergut Official 85.6%; Abundita 3.3%; Scissors Plus 3.1%; DIGITAL MART 1.9%; monthly rev ~$432k; 21 products; 2,601 reviews; rating 4.22; MoM -20.8%; 12M MoM +43%","Supergut on Amazon",f"""{H}

{FN.format(b='Supergut')}

Looking at your listings, Supergut is doing about $430k a month on Amazon through your own account after a strong year, with the GLP-1 daily support line carrying it. Two things stand out. The month looks to be down about 20%, and a dozen small resellers have started showing up on the same listings, which usually means someone is sourcing product to undercut you. I know you have people on this.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(313,KN+"WILDE Brands","Wilde Chips","Strong position: ~$750k a month, brand direct ~80%, Amazon 1P ~16%, up on the year; modest ask","Wilde Chips 79.5%; Amazon.com 16.5%; monthly rev ~$750k; 46 products; 11,523 reviews; MoM -1.6%; 12M MoM +36%; variety pack ~$285k/mo","WILDE on Amazon",f"""{H}

{FN.format(b='WILDE')}

Looking at your listings, WILDE is doing about $750k a month on Amazon, mostly through your own account with Amazon selling the rest as a vendor, and the year has been strong. The variety pack carries close to 40% of it. I know you have an Amazon team, so this isn't a pitch on the basics. It's more about what the next stretch looks like when one listing is doing that much of the work.

{CO}

Open to a 20 minute look at where the next stretch of growth is?

Yoni""",qa=["sheet Brand (Seller Central) confirmed; hybrid with Amazon 1P at 16%"]),
E(314,KN+"Zesty Z - Perfect Pita Chips","Zesty Z","Small footprint: two listings selling ~$3k a month, sold direct, no storefront; growing; 433 reviews","Zesty Z 100%; monthly rev ~$3k; 11 products; 433 reviews; rating 4.29; MoM +31%; storefront false","Zesty Z on Amazon",f"""{H}

{FN.format(b='Zesty Z')}

Looking at your listings, Zesty Z is on Amazon at a few thousand dollars a month, sold direct, with the parmesan garlic fiber pita chips doing all of it and the newer listings not moving yet. It's growing and there are over 400 reviews, so the product lands. There's no brand storefront, and high-fiber snacks are a category where Amazon search is doing real work right now.

{CO}

Would it make sense to have a quick conversation?

Yoni""",qa=["sheet says brand store; fresh data shows no storefront"]),
E(318,KL+"CoTa Global","CoTa Global","Sold entirely through Mozlly rather than a CoTa account; ~$12k a month across 45 listings; month down ~29%","Mozlly 99.8%; monthly rev ~$11.6k; 45 products; 4,317 reviews; rating 4.4; MoM -28.6%","CoTa Global on Amazon",f"""{H}

{LV}

Looking at your listings, CoTa Global is on Amazon at about $12k a month across 45 products, all sold through a seller called Mozlly rather than a CoTa account, and the month is down close to 30%. If Mozlly is your own operation, fine. Either way the numbers say a catalog of gift and novelty items with over 4,000 reviews is doing a few hundred dollars per listing going into Q4.

{CO}

Would it make sense to have a quick conversation before Q4?

Yoni""",qa=["sheet third-party (Mozlly); Mozlly may be an affiliated account, verify"]),
nf(329,KL+"Neil Enterprises","NeilMed","Wrong match; souvenir and photo products company matched to NeilMed in the sheet; industry-level email","'NeilMed' record is a sinus care brand (~$2.1M/mo), not the exhibitor; no data for Neil Enterprises","Neil Enterprises on Amazon",
"From what we can see, Neil Enterprises doesn't have a brand presence on Amazon, and the listings that come up under a similar name belong to an unrelated health brand. Souvenir photo frames and keepsakes are a steady Amazon search from visitors after the trip, and that demand goes to whoever has a managed listing under a name people can find.",
["wrong match: sheet mapped exhibitor to NeilMed storefront; SS_ numbers are NeilMed's","exhibitor product line assumed from name, verify"],LV,conf="wrong match"),
E(330,KL+"Old Guys Rule","OLD GUYS RULE","Tiny footprint for a well-known brand: ten listings, ~$2k a month, sold direct, down ~55% on the year","Old Guys Rule 100%; monthly rev ~$2k; TTM ~$47k; 10 products; 452 reviews; rating 4.8; 12M MoM -55%","Old Guys Rule on Amazon",f"""{H}

{LV}

Looking at your listings, Old Guys Rule is on Amazon with ten tee listings doing about $2k a month, sold direct, and the trend on the year is down by more than half. The reviews are excellent, 4.8 across the board. For a brand with this much name recognition and a Father's Day and holiday gift profile, that's a channel that has been left to drift going into Q4.

{CO}

Would it make sense to have a quick conversation before Q4?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
nf(332,KL+"Parks Project","Parks Project","Not found; industry-level: listings sold by Backcountry, no brand account or storefront","Record exists with 0 active products; sheet: no brand store, sold by Backcountry","Parks Project on Amazon",
"Looking at your listings, Parks Project shows up on Amazon through Backcountry rather than a brand account, with no storefront, and the listings aren't registering measurable sales in public marketplace data. National park apparel is a large Amazon search, especially around gifting, and a brand with your following is leaving that to a retailer.",
["brand record returned 0 products on two attempts; industry-level email","sheet third-party (Backcountry)"],LV),
E(335,KL+"Pennington Bear Company","Pennington Bear Company","One listing (sock monkey) doing ~$3.5k a month, sold by a reseller (Atharva Brands) rather than the brand; 1,352 reviews","Atharva Brands 100%; monthly rev ~$3.5k; TTM ~$64k; 1 product; 1,352 reviews; rating 4.8; MoM +30%","Pennington Bear on Amazon",f"""{H}

{LV}

Looking at your listings, Pennington Bear Company has one product on Amazon, the sock monkey, doing a few thousand dollars a month with over 1,300 reviews at a 4.8 average, and it's sold by a reseller called Atharva Brands rather than by you. That's a proven listing the brand doesn't control, and the rest of the catalog isn't on Amazon at all going into the season that matters for plush.

{CO}

Would it make sense to have a quick conversation before Q4?

Yoni""",qa=["sheet third-party (Atharva Brands) confirmed"]),
]
run(raw,emails)
