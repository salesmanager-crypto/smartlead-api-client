from batchlib import *
raw={
"Life Extension":RAW(P("Life Extension","Health & Household","Magnesium Mineral Supplements",1.7,"Amazon.com",False,"",0.816,0.027,0.2,31.23,4.5,630,467862,14988387.83,193566295.33),
 S(("Amazon.com",81.628),("Life Extension Buyers Club",8.869),("Peak10 Health LLC",8.511),("RS E.commerce LLC",0.336),("DealsonAmzon",0.285),("Paradine Services",0.196),("Highland Health Foods",0.058),("America Wholesale Inc",0.036),("Slickdeals of America",0.033),("INSAF ENTERPRISES",0.022)),
 T(("Life Extension Neuro-Mag Magnesium L-Threonate, 90 Vegetarian Capsules","B006P536E6",2016213.12),("Life Extension NAD+ Cell Regenerator and Resveratrol Elite, 30 Capsules","B08PMJFLP8",724547.63),("Life Extension Magnesium Glycinate, 90 Capsules","B0DMTV24LR",370728),("Life Extension Super K, Vitamin K1 and K2, 90 Softgels","B07RL1J9BV",364110.72),("Life Extension Ultra Prostate Formula with Saw Palmetto, 60 Softgels","B076S1MKDY",345709.8))),
"Orgain":RAW(P("Orgain","Health & Household","Sports Nutrition Protein Powder Blends",1.56,"Amazon.com",True,"https://www.amazon.com/stores/Orgain/page/23B0D55F-4E42-4EB7-AAD7-235C4F96E4E3",0.997,-0.107,0.153,39.15,4.37,185,305086,15210524.8,198048732.29),
 S(("Amazon.com",99.661),("Whole Foods Market",0.114),("SwiftCreek",0.068),("Carpe Diem Trading, Inc",0.049),("G Dreamer",0.029),("Zerbert",0.021)),
 T(("Orgain Organic Vegan 21g Protein Powder, Vanilla Bean, 2.03 lb","B00J074W7Q",1990031.28),("Orgain Organic Vegan Protein Powder, Creamy Chocolate Fudge, 2.03 lb","B00J074W94",1334561.76),("Orgain Organic Vegan 21g Protein + Superfoods Powder, Vanilla Bean, 2.02lb","B07PXNNFGT",869568.61),("Orgain Hydrolyzed Collagen Peptides Powder, Unflavored, 1lb","B07BL69CD2",810965.65),("Orgain Organic Kids Protein Nutritional Shake, Chocolate, 12 Count","B00BKL4KKY",557423.13))),
"NOW Foods":RAW(P("NOW Foods","Health & Household","Blended Vitamin & Mineral Supplements",3.68,"",True,"https://www.amazon.com/stores/NOW/page/7C89AA39-7209-4289-AA91-6D186B43F3C6",0.606,0.009,0.171,41.46,4.57,1394,790374,8767706.94,122925053.49),
 S(("Amazon.com",60.607),("Highland Health Foods",11.394),("Green Valley Health Market LLC",10.304),("Nutri Catalog",7.112),("Vitamins4Beauty",1.533),("Nature and Herbs",1.178),("eHomeA2Z",1.034),("Best~Naturals",0.803),("gmsupps",0.779),("iHerb",0.718)),
 T(("NOW Supplements, Psyllium Husk Caps 500mg, 200 Veg Caps","B005P0XUAM",500500),("NOW Supplements, Psyllium Husk Caps 500mg, 500 Veg Caps","B0013OW2KS",323329.27),("NOW Supplements, NAC 600 mg with Selenium, 250 Veg Capsules","B0013OUQ3S",318743.25),("Now Foods Magnesium Glycinate, 240 Tablets","B0CB984SHQ",211963.8),("NOW Foods Supplements, Glycine 1,000 mg, 100 Veg Capsules","B002J0RHTQ",194774.44))),
"OWYN Only What You Need":RAW(P("OWYN Only What You Need","Health & Household","Protein Drinks",2.01,"Only What You Need",False,"",0.901,-0.153,-0.065,62.57,4.18,74,23413,2852429.14,37102670.92),
 S(("Amazon.com",90.086),("Alegacy",2.861),("East Coast Fulfillment VA",1.368),("Top shelf Goods",1.26),("lu lu auto shop",0.879),("NES Distribution (WE RECORD SERIAL)",0.692),("KMW Store",0.629),("Whole Foods Market",0.522),("United Airway Supply",0.449),("phoenixrising76",0.229)),
 T(("OWYN 32g Chocolate Flavored Protein Shake, 12 Ct","B08B2J4DKZ",359474.06),("OWYN Dark Chocolate Flavored 20g Protein Shake, 12 Ct","B0764GPB51",344480.29),("OWYN 32g Pro Elite Vanilla Flavored Protein Shake, 12 Ct","B08B7B3CF8",254204.86),("OWYN Chocolate Flavored 30g Protein Powder, 2.96 LB","B0CV87Q4VJ",198541.04),("OWYN Vanilla Flavored 30g Protein Powder, 2.96 LB","B0CV8N9HWF",194865.88))),
"Huel":RAW(P("Huel","Health & Household","Sports Nutrition Protein Powder Blends",1.21,"",True,"https://www.amazon.com/stores/Huel/page/B0885F23-B036-4EEA-8724-D20A8C60E234",0,0.143,0.703,54.66,3.89,76,5169,2638034.5,19066089.45),
 S(("Huel Inc",99.315),("PRIME PHARMA",0.222),("Moon Merch LLC",0.156),("Smart Selections Co.",0.102),("NexxtDay",0.081),("Buckeye City Bargains",0.047),("Carepacked",0.045),("Boulturo",0.023),("AMAZINGFINDS",0.009)),
 T(("Huel Black Edition | Chocolate 40g Vegan Protein Powder","B0BF5STD3J",295510.74),("Huel Black Edition Ready-to-Drink | Meal Replacement Protein Shake","B0FVYFSHQN",194169.69),("Huel Black Edition | Vanilla | 40g Vegan Protein Powder","B085W7MZHR",184049.32),("Huel Black Edition | Chocolate Peanut Butter | 40g Vegan Protein Powder","B0G62ZNV71",180869.85),("Huel Black Edition Ready-to-Drink | Meal Replacement Protein Shake","B0D2DXRXHR",134896.32))),
"Olipop":RAW(P("Olipop","Grocery & Gourmet Food","Soda Soft Drinks",1.84,"WishingUWell",True,"https://www.amazon.com/stores/OLIPOP/page/13DF7D6C-D88B-4C36-AC1E-B8599E9EEB60",0.843,-0.238,0.892,20.48,4.39,113,16875,2441591.9,34430449.29),
 S(("Amazon.com",84.342),("OLIPOP",10.686),("Whole Foods Market",2.365),("Spray and Pray LLC",1.1),("EWill",0.474),("Product Planet Inc",0.346),("Revenue Ecommerce",0.183),("the royal fountain",0.125),("Oasis Snacks",0.122),("Whole Supplies",0.044)),
 T(("OLIPOP 6g Fiber Prebiotic Soda, Vintage Cola, 12 Pack","B0DJN5B63J",183248.68),("OLIPOP Prebiotic Soda, Favorites Variety, 12 Pack","B0DWH3NDP5",179317.19),("OLIPOP Prebiotic Soda, Crisp Apple, 12 Pack","B0FD16JTPQ",168732.2),("OLIPOP Prebiotic Soda, Cream Soda, 12 Pack","B0DJN77TCS",131318.04),("OLIPOP Prebiotic Soda, Classic Grape, 12 Pack","B0DJN7B6HC",126855.12))),
"McGraw-Hill Education":RAW(P("McGraw-Hill Education","Books","Pathology Clinical Chemistry",9.4,"",False,"",0.212,0.246,-0.98,76.6,4.49,4621,612109,2122801.66,6901700.97),
 S(("Amazon.com",21.199),("McGrawHill",7.2),("ColumbusTextbooks",6.722),("Tome Dealers",4.456),("bookhunter188",3.628),("Apex_media",2.341),("textbooks_source",2.124),("doraemoni",1.783),("ayvax",1.514),("RoosterSocks",1.394)),
 T(("First Aid for the USMLE Step 1 2026","1264775784",17703.07),("Principles And Practice of Mechanical Ventilation, Third Edition","0071736263",12317.76),("Atlas of Emergency Medicine, Fifth Edition","1260134946",9205.92),("Tintinalli's Emergency Medicine, 9th Edition","1260019934",8204.4),("Goldfrank's Toxicologic Emergencies, Eleventh Edition","1259859614",8008.2))),
"Perelel":RAW(P("Perelel","Health & Household","Prenatal Vitamins",0.88,"",True,"https://www.amazon.com/stores/Perelel/page/CC2F5569-8B43-4FF7-A1D7-2001CA697B27",0,0.045,4.485,54.44,4.25,24,2233,1838346.66,14171589.92),
 S(("Perelel Health",100)),
 T(("Perelel Conception Fertility Prenatal Vitamins","B0CPKSZJGM",358083.44),("Perelel 2nd Trimester Prenatal Vitamins","B0CSGXY5V5",237566.68),("Perelel 1st Trimester Prenatal Vitamins","B0CSH5PMHQ",236215.2),("Perelel Mom Multi Postnatal Vitamins","B0CPL9CTT8",230045.4),("Perelel 3rd Trimester Prenatal Vitamins","B0CSGZLNY4",176926.36))),
"Microbiome Labs":RAW(P("Microbiome Labs","Health & Household","Probiotic Nutritional Supplements",1.5,"FortressBrand",True,"https://www.amazon.com/stores/MicrobiomeLabs/page/7D152897-8F9E-4787-A2FE-3BE9D1940825",0,-0.085,0.457,68,4.54,34,6959,1836680.8,26851693.84),
 S(("Front Row Group",90.274),("Vital Supplements Supplies",4.034),("upup365",3.362),("Supply Distributor",2.33)),
 T(("Microbiome Labs MegaSporeBiotic Daily Probiotic, 60 Ct","B07TJ4TH8Q",611752.5),("Microbiome Labs Mega SporeBiotic Daily Probiotic, 180 Ct","B08YP9TKVR",340778.55),("Microbiome Labs Mega IgG2000 Capsules, 120 Capsules","B0871XRYQK",118312.66),("Microbiome Labs Mega IgG2000 Gut Health Powder, 2.1 Ounces","B09Z143WS7",107044.11),("Microbiome Labs HU58, Bacillus Subtilis, 60 Ct","B087N2NPM9",84185.36))),
"Kate Farms":RAW(P("Kate Farms","Grocery & Gourmet Food","Meal Replacement Drinks",1.45,"Kate Farms",True,"https://www.amazon.com/stores/KateFarms/page/CACAA8EF-B651-4525-A60D-0B0F21A134AF",0.953,-0.031,0.751,58.25,4.31,67,5886,1471376.91,16952788.59),
 S(("Amazon.com",95.323),("3R ENTERPRISE",2.172),("Kate Farms",1.157),("Food Deals Supply",0.738),("Amazon Resale",0.246),("alt Ltd.",0.159)),
 T(("KATE FARMS Organic High Protein Chocolate Shake, 25g Protein, 12 Pack","B0F712555N",164949.48),("KATE FARMS Organic Plant Based Pediatric 1.2 Sole Source Vanilla, Pack of 12","B07DVZZMRK",119579.46),("KATE FARMS Organic 1.4 High Calorie Shake, Chocolate, 12 Pack","B0BCXBPXDS",78249.36),("KATE FARMS Organic 1.4 High Calorie Shake, Vanilla, 12 Pack","B08F82M84H",78123.64),("KATE FARMS Organic Nutrition Shake, Chocolate, 16g Protein, 12 Pack","B08FNSZP6X",61428.82))),
"Four Sigmatic":RAW(P("Four Sigmatic","Grocery & Gourmet Food","Ground Coffee",2.3,"Amazon.com",False,"",0.618,-0.078,-0.108,35.42,4.28,125,65161,1440770.33,23054352.63),
 S(("Amazon.com",61.838),("Montaukave",23.149),("KOJAT",5.961),("Pantry Provisions",2.966),("GrandioseGoods",2.684),("Super Savings Now",1.087)),
 T(("Four Sigmatic Organic Focus Mushroom Ground Coffee, Dark Roast, 12oz","B0756D1D39",225108),("Four Sigmatic Mushroom Coffee K-Cups, 24 Count","B0883VBNHC",189466.86),("Four Sigmatic Gut Health Organic Ground Coffee, Medium Roast, 12oz","B087YHP3HQ",104122.8),("Four Sigmatic Organic Plant-Based Protein Powder, Creamy Cacao","B08GN81SLF",55919.54),("Four Sigmatic Organic Vegan Protein Powder, Vanilla","B08GNB94B9",54699.84))),
"Lakanto":RAW(P("Lakanto","Grocery & Gourmet Food","Stevia Sugar Substitutes",1.72,"Lakanto",False,"",0.03,-0.076,0.048,41.44,4.26,147,207056,1436990.55,19967626.63),
 S(("Saraya USA (Lakanto)",89.567),("Amazon.com",2.959),("Whole Foods Market",2.817),("HAVE A GREAT DAY!",1.689),("KOJAT",1.051),("ChagaRoot",0.725)),
 T(("Lakanto Classic Monk Fruit Sweetener with Allulose, 3 LB","B0CLBVY6VY",203038.92),("Lakanto Classic Monk Fruit Sweetener with Erythritol, 5 Lb","B098H7XWQ6",184974.03),("Lakanto Classic Monk Fruit Sweetener with Erythritol, 3 lb","B01LDNBAC4",99206.88),("Lakanto Liquid Monk Fruit Extract Drops, Original, 1.76 Fl Oz","B072P5SQMN",92842.92),("Lakanto Classic Monk Fruit Sweetener, 1.76 lb Pack of 3","B09RSSPLK3",49346))),
"Frog Fuel":RAW(P("Frog Fuel","Health & Household","Sports Nutrition Ready to Drink Protein",1,"OP2 Labs",True,"https://www.amazon.com/stores/FrogFuel/page/EA28CE4E-B4B8-4778-82FF-561094E343B9",0,-0.129,0.184,54,4.47,6,7833,1402568,17471408.65),
 S(("OP2 Labs",100)),
 T(("Frog Fuel Power Liquid Protein Shot, 15g Protein, Berry, 24 pk","B010C3MQC4",851520),("Frog Fuel Power Energized Protein Shot, 80mg Caffeine, Berry, 24 pk","B07XGCT1TS",251952),("Frog Fuel Ultra Energy Gel & Pre Workout Shot, 120mg Caffeine, 24 pk","B00I0MLM48",196368),("Frog Fuel Reset Liquid Sleep Supplement Shot, 24 pk","B07L18DT1B",45056),("Frog Fuel Ultra Energy Gel, Caffeine Free, Berry, 24 pk","B00I0MGP2W",45024))),
"Primal Kitchen":RAW(P("Primal Kitchen","Grocery & Gourmet Food","Collagen Supplements",5.56,"",True,"https://www.amazon.com/stores/PrimalKitchen/page/341775E3-9486-4E2A-9753-0A93E82A8146",0.243,-0.029,0.156,23.92,4.22,172,54943,1223704.8,16787887.64),
 S(("Whole Foods Market",32.615),("Primal Blueprint",32.009),("Amazon.com",24.277),("YSSG Deals",2.846),("TheNewMall",1.921),("Apex Circuit",1.08)),
 T(("Primal Kitchen Vanilla Collagen Fuel Drink Mix, 20 Ounces","B07YN3XN7F",77920.02),("Primal Kitchen Mayo made with Avocado Oil, 12 Ounces","B00ZAD36ZS",74482.1),("Primal Kitchen Organic Unsweetened Squeeze Ketchup, 18.5 OZ","B0B18FYSC7",66406.76),("Primal Kitchen Vanilla Collagen Fuel Drink Mix, 14.4 Ounces","B071ZG164V",47977.6),("Primal Kitchen, Buffalo Sauce, 8.5 Ounce","B08HJLD2RH",44697.12))),
"NuGo":RAW(P("NuGo","Health & Household","Sports Nutrition Protein Bars",2.03,"Amazon.com",True,"https://www.amazon.com/stores/NuGoNutrition/page/481E51A5-9207-47DC-B4B0-8E60A512B46D",0.984,-0.005,0.154,35,4.42,100,11283,1196431.27,16105068.48),
 S(("Amazon.com",98.364),("Whole Foods Market",0.894),("TheNewMall",0.18),("We've Got You covered",0.167),("Modernparty",0.144),("The Online Grocery Store",0.127)),
 T(("NuGo Dark, Pretzel w/SS, 12g Vegan Protein Bar, 24 Count","B07V7HKP8N",238908.86),("NuGo Dark, Chocolate Chip, 12g Vegan Protein Bar, 24 Count","B07V5DZ9MX",104982.55),("NuGo Dark, Mint Chocolate Chip, 13g Vegan Protein Bar, 24 CT","B07V4BCFJ4",81682.56),("NuGo Slim, Crunchy Peanut Butter, 16g Vegan Protein Bar, 24 ct","B088JQDW9S",73655.24),("NuGo Slim, Chocolate Mint, 17g Vegan Protein Bar, 24 ct","B088GYH4KF",70812.28))),
"goya":RAW(P("goya","Grocery & Gourmet Food","Mexican Seasonings",2.35,"",True,"https://www.amazon.com/stores/Goya/page/A77AE1AA-DC0C-4085-8C45-F76F342AA2F0",0.642,0.076,-0.013,32.12,4.45,947,190623,1091056.56,14215734.37),
 S(("Amazon.com",64.167),("Authorized Goya Seller",11.875),("HAVE A GREAT DAY!",4.529),("Product Planet Inc",2.595),("Flexi Ventures 26 Years On-Line",2.171),("USTradeEnt",1.512)),
 T(("Goya Foods Chick Peas, Garbanzo Beans, 15.5 Ounce (Pack of 8)","B07TL6CDMX",48574.68),("Goya Black Beans, 15.5 Ounce Pack of 8","B01ALQKTKS",37126.31),("Goya Sazon Seasoning With Azafran 3.52 Ounce (Pack of 3)","B0B94PSYR4",25432.17),("Goya Foods Red Kidney Beans, 15.5 Ounce (Pack of 8)","B078NCN36G",24027.3),("Goya Thai Jasmine Rice 5 lbs","B0047249YA",21991.38))),
"Pendulum":RAW(P("Pendulum","Health & Household","Probiotic Nutritional Supplements",1.14,"Pendulum Therapeutics, Inc.",True,"https://www.amazon.com/stores/Pendulum/page/4FA52738-E3C8-4508-B5E0-CA2D0653EB9F",0,0.002,0.612,88.95,4.19,7,3369,1081696.58,18731493.6),
 S(("Pendulum Therapeutics, Inc.",100)),
 T(("Pendulum Akkermansia Probiotic with Prebiotic Fiber, 30 Capsules","B0B3GF96C3",326528),("Pendulum Metabolic Daily Multi-Strain Probiotic, 30 Capsules","B0BRM7S31J",304209.29),("Pendulum Akkermansia Probiotic, 90 Capsules","B0CGJWF7SN",182514.57),("Pendulum GLP-1 Probiotic, 30 Capsules","B0CY3VZDYP",124873.86),("Pendulum Metabolic Daily with Akkermansia, 90 Servings","B0CGKG1WTN",113930.01))),
"Jones & Bartlett Learning":RAW(P("Jones & Bartlett Learning","Books","Firefighting & Prevention",8.55,"",False,"",0.181,0.673,-0.979,83.81,4.57,869,116651,905662.52,2160626.55),
 S(("itemspopularsonlineaindemand",31.409),("Amazon.com",18.132),("New-Books",6.245),("Tome Dealers",4.508),("studentbargains3",4.41),("textbooks_source",4.058)),
 T(("Ugly's Electrical References, 2026 Edition","1284315754",10956.4),("Emergency Care and Transportation of the Sick and Injured","128432513X",9648.96),("Nancy Caroline's Emergency Care in the Streets","128425674X",9346.26),("Sanders' Paramedic Textbook with Navigate Essentials Access","1284277534",6806.08),("NASM Essentials of Personal Fitness Training","1284200884",5087.61))),
"Jovial":RAW(P("Jovial","Grocery & Gourmet Food","Wheat Flours & Meals",1.77,"Healthy Pantry",False,"",0.046,0.026,0.252,34.53,4.49,171,47734,890670.15,13675512.26),
 S(("LUMlNlZE",60.222),("Whole Foods Market",31.683),("Amazon.com",4.64),("Kenovah Shop",1.252),("SWC 360",1.193),("Super Start Store",0.405)),
 T(("Jovial Organic Einkorn Unbleached All Purpose Flour, 10 Lb","B00K1GFA76",68504.36),("Jovial Organic Einkorn Unbleached All Purpose Flour, 32 Oz","B007SM6NWC",49473.06),("Jovial Organic Einkorn All Purpose Flour, 32 Oz, 5 Pack","B00JS3YX9E",47513.18),("Jovial Organic Einkorn All Purpose Flour, 32 Oz, 2 Pack","B01N3KS5EM",37900.61),("Jovial, Pasta Brown Rice Fusilli Organic, 12 Ounce","B005K0K45Q",31667.35))),
"Hydrapeak":RAW(P("Hydrapeak","Kitchen & Dining","Insulated Food Jars",1.21,"Amazing Deals Online",True,"https://www.amazon.com/stores/HYDRAPEAK/page/0ECE05EB-E2A1-4744-AF86-E913E70AB4A6",0,0.078,0.036,24.52,4.46,613,44292,896008.92,9601555.91),
 S(("Amazing Deals Online",99.365),("Prost Enterprise",0.121),("WHOLESALES",0.12),("Mitchell Great Finds",0.101),("The Grateful Merchant",0.052),("YACSHA Shop",0.036)),
 T(("Hydrapeak 25oz Stainless Steel Vacuum Insulated Food Jar (Black)","B09RNFZRWV",140787.15),("Hydrapeak 25oz Stainless Steel Vacuum Insulated Food Jar (Navy)","B09RP7Q8W1",81894.75),("Hydrapeak 18oz Stainless Steel Vacuum Insulated Food Jar Kids (Navy)","B0BB3KD2JD",55896.3),("Hydrapeak 32oz Stainless Steel Vacuum Insulated Food Jar (Black)","B0CNQ986VR",51502.16),("Hydrapeak 25oz Stainless Steel Vacuum Insulated Food Jar (Ivory)","B0CLY1LWNW",42912.45))),
"Blue 84":RAW(P("Blue 84","Sports & Outdoors","Sports Fan T-Shirts",0.72,"Amazon.com",True,"https://www.amazon.com/stores/Blue84CollegeApparel/page/4709319C-9784-4190-B3EB-1A06B83FB7F5",0.996,0.137,-0.367,50.46,4.55,31040,35109,779757.59,21588074.22),
 S(("Amazon.com",99.629),("Atlantic Coast Promotional",0.248),("MOT LLC",0.046),("JCC Distribution",0.041),("papayaya.store",0.026),("Melodi Books",0.009)),
 T(("Blue 84 Men's Ohio State Buckeyes Tri-Blend T-Shirt Vintage Icon Heather Grey, Large","B08YRV9362",3833.81),("Blue 84 Men's Ohio State Buckeyes Tri-Blend T-Shirt Vintage Icon Heather Grey, X-Large","B08YRV4PW7",3576.3),("Ohio State Buckeyes Tri-Blend T-Shirt Vintage Icon Team Color, Large","B09P2SMQ9T",3487.32),("Blue 84 Men's Maryland Terrapins Crewneck Sweatshirt Cursive Team Color, Small","B08ZJ8SBY4",2599.5),("Blue 84 NCAA Penn State Nittany Lions Mens T Shirt Line Up, X-Large","B08PPFWJSY",2312.34))),
"Fishwife":RAW(P("Fishwife","Grocery & Gourmet Food","Canned & Packaged Sardines",0.93,"",True,"https://www.amazon.com/stores/FishwifeTinnedSeafoodCo/page/A926DD9F-879A-4641-93A0-50E0A5B9D78E",0.221,-0.283,2.089,40.18,4.41,43,3557,776050.17,10540501.16),
 S(("Fishwife Tinned Seafood Co.",56.828),("Amazon.com",22.061),("Whole Foods Market",20.843),("New Life Advisors",0.269),("Natural Nutrient",0)),
 T(("Fishwife Sardine Quad (Lemon & Hot Pepper)","B0CPTGWQCY",91390),("Fishwife Smoked Salmon with Fly (3-Pack)","B0CPT9DZ7P",88162.47),("Fishwife Sardines with Preserved Lemon (1-Pack)","B0BXYN9W4V",56947.65),("Fishwife Albacore Tuna in Olive Oil (1-Pack)","B0CRZ8YBN9",50490.09),("Fishwife Smoked Salmon with Fly (1-Pack)","B0BXYQV5KQ",46847.84))),
"MasterPieces":RAW(P("MasterPieces","Toys & Games","Jigsaw Puzzles",2.4,"MasterPieces, Inc.",True,"https://www.amazon.com/stores/MasterPieces/page/6FFD7CF1-3646-4711-A01A-4ECD04EE4BC5",0.029,-0.009,0.157,18.77,4.58,2664,99008,763197.43,14721414.25),
 S(("MasterPieces, Inc.",86.358),("Amazon.com",2.915),("Angel Seller",2.1),("Toynk Toys",1.376),("Zero Pack",1.165),("First-Class Store",0.749)),
 T(("MasterPieces Puzzle Glue with Wide Plastic Spreader, 2 Pack","B00A8WMDUU",40649.31),("MasterPieces 1000 Piece Jigsaw Puzzle Mom's Pantry","B07CPR6HLD",23650.08),("MasterPieces NFL Gameday Board Game","B0DN24ZBLZ",9437.64),("MasterPieces 1000 Piece Jigsaw Puzzle, National Parks of America","B06XCB5RQX",7472.04),("MasterPieces MLB-Opoly Junior","B0716XXQ2J",6349.7))),
"Lesserevil":RAW(P("Lesserevil","Grocery & Gourmet Food","Popped Popcorn",3.99,"",True,"https://www.amazon.com/stores/LesserEvilSnacks/page/4348D983-90A0-4492-85AF-7A4A04CF2115",0.352,0.026,0.066,23.63,4.31,96,11878,717270.09,10449783.69),
 S(("Whole Foods Market",51.222),("Amazon.com",35.184),("WhyPayMoreOnline",3.859),("supreme7",3.005),("TheNewMall",2.711),("AutoPart Experts",0.465)),
 T(("Lesserevil Organic Real Cheddar Space Balls 10Ct, 6 OZ","B0FRSZS2C3",132075.38),("LESSEREVIL Organic Himalayan Pink Salt Popcorn 10Ct, 4.6 OZ","B0FRSYTMZ5",117733.48),("LesserEvil Himalayan Pink Salt Organic Popcorn, 4.6 Oz, Pack of 3","B09126PS6Y",61231.46),("LesserEvil Himalayan Gold Organic Popcorn, 4.6 Oz, Pack of 3","B0912QKMD2",51202.12),("Lesserevil Organic Himalayan Gold Popcorn 10Ct, 4.6 OZ","B0FRT2HWX7",50590.98))),
"Inis the Energy of the Sea":RAW(P("Inis the Energy of the Sea","Beauty & Personal Care","Men's Cologne",2.23,"",True,"https://www.amazon.com/stores/InistheEnergyoftheSea/page/99133043-9BE8-43E1-B81D-918D81B22741",0,0.002,0.379,25.56,4.75,35,49936,673038.45,10035219.11),
 S(("Inis the Energy of the Sea",100)),
 T(("Inis the Energy of the Sea Cologne for Men and Women, 3.3 fl oz","B000OTZLFG",127855),("Inis Revitalizing Seaweed Body Lotion, 16.9 fl oz","B015QJ7JYE",73929.45),("Inis Reed Diffuser Oil Refill, 3.3 fl oz","B01DEIOSHK",51570),("Inis Cologne for Men and Women, 0.5 fl oz","B00GFPYXWU",43300),("Inis Reed Diffuser Set with Fragrance Oil","B01BIFQO6Y",43282))),
}
FN="Saw that {b} exhibited at FNCE last year."
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
emails=[
E(0,"FNCE 2025|Life Extension","Life Extension","Large brand: Amazon 1P ~82%, third-party reseller Peak10 Health ~8.5% (~$1.3M/mo); narrow reseller angle","Amazon 1P 81.6%; Peak10 Health 8.5% share = ~$1.28M/mo; monthly rev ~$15.0M","Life Extension reseller share on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Life Extension')}

From what we can see, Amazon itself sells about 80% of your volume on the marketplace, and one third-party seller, Peak10 Health, is moving roughly $1.3M a month of your products on its own. That is a lot of pricing and content sitting outside your direct control.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations, and we work in 1P, 3P or hybrid setups.

Open to a 20 minute look at the reseller side specifically?

Yoni""",qa=["very large brand (>$5M/mo), narrow ask used"]),
E(1,"FNCE 2025|Orgain, LLC","Orgain","Large brand: ~100% Amazon 1P, no 3P layer; hybrid angle","Amazon 1P 99.7%; monthly rev ~$15.2M; MoM -10.7%","Orgain's Amazon setup",f"""Hi {{{{first_name}}}},

{FN.format(b='Orgain')}

Looking at your listings, essentially all of Orgain's Amazon revenue, somewhere around $15M a month, runs through Amazon as the vendor. There is no 3P layer underneath it, so pricing, inventory and buying decisions sit entirely with Amazon.

We manage Amazon for brands end to end, and that includes hybrid setups where 1P stays where it works and specific products move to Seller Central for margin or control.

Would a 20 minute conversation on the hybrid option be worth your time?

Yoni""",qa=["very large brand (>$5M/mo), narrow ask used"]),
E(2,"FNCE 2025|NOW Foods","NOW Foods","Large brand: third-party resellers ~39% of Amazon revenue (Highland Health Foods, Green Valley Health Market, Nutri Catalog)","Amazon 1P 60.6%; Highland Health Foods 11.4% + Green Valley 10.3% = ~$1.87M/mo; reseller share ~39%; monthly rev ~$8.8M","NOW Foods third-party sellers on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='NOW Foods')}

From what we can see, roughly 40% of NOW's Amazon revenue is going through third-party sellers rather than Amazon or NOW directly. Highland Health Foods and Green Valley Health Market alone look like about $1.9M a month combined, each on a large chunk of your catalog.

At that size, that is a meaningful piece of pricing, content and Buy Box you don't control.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a 20 minute look at the reseller picture specifically?

Yoni""",qa=["very large brand (>$5M/mo), narrow ask used"]),
E(3,"FNCE 2025|OWYN","OWYN Only What You Need","Amazon 1P ~90% with negative 12-month trend and no storefront flagged","Amazon 1P 90.1%; monthly rev ~$2.85M; 12M MoM growth -6.5%; Has Storefront false","OWYN's Amazon channel",f"""Hi {{{{first_name}}}},

{FN.format(b='OWYN')}

From what we can see, OWYN is doing somewhere around $2.8M a month on Amazon, with about 90% of it going through Amazon as the vendor. We also don't see a brand store attached to the listings, which is unusual at that volume, and the trailing 12 month trend looks slightly negative.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations, and we run 1P, 3P and hybrid setups depending on what the product needs.

Would it make sense to have a quick conversation?

Yoni"""),
E(4,"FNCE 2025|Huel","Huel","Strong growing brand direct; weak review base and sub-4 rating for the volume","Brand direct (Huel Inc) 99.3%; monthly rev ~$2.64M; 12M MoM +70%; 5,169 reviews across 76 products; avg rating 3.89","Huel reviews and ratings on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Huel')}

From what we can see, Huel is doing roughly $2.6M a month on Amazon, all sold direct, and the trailing 12 month trend is strongly up. The one thing that stands out is the review side: about 5,000 reviews across the whole catalog and an average rating under 4 stars, which is low for that volume and will cap conversion as ad spend grows.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Open to a short call on the review and content side?

Yoni"""),
E(5,"FNCE 2025|OLIPOP","Olipop","Amazon 1P ~84% with brand's own 3P account at ~11%; hybrid split angle","Amazon 1P 84.3%; OLIPOP seller 10.7%; monthly rev ~$2.44M","OLIPOP's 1P and 3P split",f"""Hi {{{{first_name}}}},

{FN.format(b='OLIPOP')}

Looking at your listings, OLIPOP is doing roughly $2.4M a month on Amazon, and about 85% of that is Amazon selling as the vendor. Your own seller account is on there too, but only at around 10% of the volume, so the pricing and inventory decisions on the core 12 packs still sit with Amazon.

We manage Amazon for brands end to end, including hybrid 1P/3P setups at the product level, so a brand keeps vendor where it works and takes control where it doesn't.

Would a 20 minute conversation on the hybrid split be worth your time?

Yoni"""),
E(6,"FNCE 2025|McGraw Hill","McGraw-Hill Education","Publisher: ~70% of Amazon revenue via textbook resellers, Amazon 21%, own account 7%","Amazon 21.2%; McGrawHill seller 7.2%; reseller share ~72%; monthly rev ~$2.12M; 4,621 products","McGraw Hill titles on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='McGraw Hill')}

From what we can see, McGraw Hill titles do somewhere around $2M a month on Amazon, but only about a fifth of that goes through Amazon directly and under 10% through your own seller account. The rest, roughly 70%, is textbook resellers like ColumbusTextbooks and Tome Dealers.

Some of that is the used book market and unavoidable. But the new copy Buy Box, pricing and listing content on the top titles is something a publisher can take back.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a short call on it?

Yoni""",qa=["education publisher, weaker fit for consumer brand pitch; reseller share includes used-book sellers"]),
E(7,"FNCE 2025|Perelel","Perelel","Strong growing brand direct; thin review base for the volume","Brand direct (Perelel Health) 100%; monthly rev ~$1.84M; 12M MoM +449%; 2,233 reviews on 24 products","Perelel's next stage on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Perelel')}

From what we can see, Perelel is doing roughly $1.8M a month on Amazon, all sold direct through your own account, and growth over the last year has been steep. What stands out is that the whole catalog sits on about 2,000 reviews, which is thin for that volume and makes every listing more dependent on ad spend than it needs to be.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Is it worth a short call on where the channel goes from here?

Yoni"""),
E(8,"FNCE 2025|Microbiome Labs","Microbiome Labs","Distributor (Front Row Group) sells ~90%; brand not selling direct; distributor-model angle","Front Row Group 90.3%; brand direct 0%; monthly rev ~$1.84M; 12M MoM +46%","Microbiome Labs distributor setup on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Microbiome Labs')}

From what we can see, Microbiome Labs does roughly $1.8M a month on Amazon, and about 90% of it is sold by Front Row Group rather than by the brand or Amazon. That means the listings, pricing and ad spend are most likely running through them, not you.

We work with brands either as the exclusive Amazon distributor or as the team running the brand's own account, covering content, advertising, inventory and operations either way.

Worth comparing what that looks like against the current setup?

Yoni""",qa=["Front Row Group is a known Amazon distributor/agency, treated as third party per rules"]),
E(9,"FNCE 2025|Kate Farms, Inc.","Kate Farms","Amazon 1P ~95%, brand's own account ~1%; hybrid angle","Amazon 1P 95.3%; Kate Farms seller 1.2%; monthly rev ~$1.47M; 12M MoM +75%","Kate Farms 1P exposure on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Kate Farms')}

Looking at your listings, Kate Farms is doing about $1.5M a month on Amazon and roughly 95% of it runs through Amazon as the vendor. Your own seller account is there but only on a handful of offers, so there is no real 3P layer if Amazon cuts a PO or shifts pricing on the shakes.

We manage Amazon for brands end to end, including hybrid 1P/3P setups where the vendor relationship stays and specific products move to Seller Central for control.

Would a 20 minute conversation on the hybrid option be worth your time?

Yoni"""),
E(10,"FNCE 2025|Four Sigmatic","Four Sigmatic","Third-party resellers ~38% (Montaukave 23% and growing) while brand trend is down","Amazon 1P 61.8%; Montaukave 23.1% = ~$331k/mo on 41 offers, MoM +6.4 pts; reseller share ~38%; 12M MoM -10.8%","Four Sigmatic third-party sellers",f"""Hi {{{{first_name}}}},

{FN.format(b='Four Sigmatic')}

From what we can see, close to 40% of Four Sigmatic's Amazon revenue is going through third-party sellers. One of them, Montaukave, looks like roughly $330k a month on about 40 of your listings, and their share is growing month over month while the brand's overall trend is slightly down.

That is pricing, Buy Box and content on your best sellers sitting with someone else.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a 20 minute look at the reseller side?

Yoni"""),
E(11,"FNCE 2025|Lakanto","Lakanto","Brand direct, large review base, flat 12-month trend and down last month; under-worked channel","Brand direct (Saraya USA) 89.6%; monthly rev ~$1.44M; 207k reviews; 12M MoM +4.8%; MoM -7.6%","Lakanto's Amazon trend",f"""Hi {{{{first_name}}}},

{FN.format(b='Lakanto')}

From what we can see, Lakanto does roughly $1.4M a month on Amazon, sold direct, with over 200,000 reviews across the catalog. The trend over the last 12 months is close to flat though, and last month was down, which for a brand with that review base usually means the channel is being maintained rather than pushed.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations. We helped MouthWatchers grow from roughly $40K a month on Amazon to $1M a month, and it wasn't just about increasing ad spend.

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["Saraya USA (Lakanto)"]),
E(12,"FNCE 2025|OP2 Labs","Frog Fuel","Strong brand direct, revenue concentrated in one listing out of six","Brand direct (OP2 Labs) 100%; monthly rev ~$1.40M; 6 products; top ASIN B010C3MQC4 ~$852k/mo","Frog Fuel's concentration on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='OP2 Labs')}

From what we can see, Frog Fuel does roughly $1.4M a month on Amazon off only six listings, all sold direct, and one 24 pack of the Power protein shot is about $850k of that on its own. It works, but it means one listing losing rank or getting hit by a competitor moves the whole business.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Open to a short call on protecting and widening that base?

Yoni""",brand_sellers=["OP2 Labs"]),
E(13,"FNCE 2025|Primal Kitchen","Primal Kitchen","Revenue split three ways (Whole Foods 33%, own Primal Blueprint account 32%, Amazon 1P 24%); fragmented control","Whole Foods Market 32.6%; Primal Blueprint 32.0%; Amazon 1P 24.3%; monthly rev ~$1.22M","Primal Kitchen's three-way Amazon split",f"""Hi {{{{first_name}}}},

{FN.format(b='Primal Kitchen')}

Looking at your listings, Primal Kitchen's Amazon revenue, roughly $1.2M a month, is split three ways: about a third through Whole Foods Market's Amazon storefront, a third through your own Primal Blueprint account, and a quarter through Amazon as the vendor. Three sellers on the same catalog usually means pricing that drifts, ads that compete with each other and content nobody fully owns.

We manage Amazon for brands end to end, including hybrid 1P/3P setups decided at the product level.

Would a 20 minute conversation on cleaning up that split be worth your time?

Yoni""",brand_sellers=["Primal Blueprint"],qa=["Whole Foods Market counted as third party per rules; it is Amazon-owned"]),
E(14,"FNCE 2025|NuGo Nutrition","NuGo","Amazon 1P ~98%, no seller layer; hybrid angle","Amazon 1P 98.4%; monthly rev ~$1.20M; top ASIN NuGo Dark Pretzel 24ct ~$239k/mo","NuGo's 1P exposure on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='NuGo')}

From what we can see, NuGo does roughly $1.2M a month on Amazon and nearly all of it, around 98%, is Amazon selling as the vendor. The NuGo Dark 24 packs carry most of that. There is no seller account underneath, so if Amazon trims a PO or reprices a flavor, there is nothing to catch it.

We manage Amazon for brands end to end, including hybrid setups where 1P stays for the volume SKUs and specific products move to Seller Central for margin and control.

Would a 20 minute conversation on the hybrid option be worth your time?

Yoni"""),
E(15,"FNCE 2025|GOYA FOODS INC. , Goya BetterForYou line","goya","Large catalog with ~24% third-party reseller share; BetterForYou line not visible among top sellers","Amazon 1P 64.2%; Authorized Goya Seller 11.9%; reseller share ~24%; 947 products; monthly rev ~$1.09M","Goya BetterForYou on Amazon",f"""Hi {{{{first_name}}}},

Saw that Goya exhibited at FNCE last year with the BetterForYou line.

Looking at Goya's Amazon listings overall, roughly a quarter of the revenue is going through third-party sellers rather than Amazon or the authorized Goya account, spread across a catalog of about 950 products. The top sellers are still pantry staples like chickpeas and black beans, and we don't see the BetterForYou products anywhere near the top of the catalog.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would a 20 minute look at how BetterForYou could be built out on Amazon be useful?

Yoni""",brand_sellers=["Authorized Goya Seller"],qa=["exhibitor is the BetterForYou line; SmartScout data covers the whole Goya brand"]),
E(16,"FNCE 2025|Pendulum","Pendulum","Strong growing brand direct on seven listings; protect and scale","Brand direct 100%; monthly rev ~$1.08M; 7 products; 12M MoM +61%; avg price ~$89","Pendulum's growth on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Pendulum')}

From what we can see, Pendulum is doing roughly $1.1M a month on Amazon off seven listings, all sold direct, with strong growth over the last year. Akkermansia and Metabolic Daily carry most of it. At that pace the questions become how much of the growth is paid, how you hold the GLP-1 and Akkermansia search terms, and whether Subscribe & Save is doing its job on a $90 product.

We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution.

Open to a short call to compare notes on it?

Yoni"""),
E(17,"FNCE 2025|Jones & Bartlett Learning","Jones & Bartlett Learning","Publisher: ~82% via resellers, largest seller a third party at 31%, no publisher account visible","itemspopularsonlineaindemand 31.4%; Amazon 18.1%; reseller share ~82%; monthly rev ~$906k; 869 products","Jones & Bartlett titles on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Jones & Bartlett Learning')}

From what we can see, Jones & Bartlett titles do somewhere around $900k a month on Amazon, and only about a fifth of that is sold by Amazon itself. The largest single seller of your books on Amazon is a third-party reseller at roughly 30%, and we don't see a Jones & Bartlett seller account in the mix at all.

For a publisher that means the new copy Buy Box, pricing and listing content on your top titles are largely in other hands.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a short call on it?

Yoni""",qa=["education publisher, weaker fit for consumer brand pitch; reseller share includes used-book sellers"]),
E(18,"FNCE 2025|Jovial Foods","Jovial","No brand account; one third-party seller (LUMlNlZE) at ~60%, Whole Foods ~32%","LUMlNlZE 60.2%; Whole Foods Market 31.7%; Amazon 4.6%; brand direct 0%; monthly rev ~$891k","Who is selling Jovial on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='Jovial Foods')}

Looking at your listings, Jovial does roughly $900k a month on Amazon, but we don't see a Jovial seller account anywhere in it. About 60% is sold by a single third-party seller called LUMlNlZE, another 30% or so through Whole Foods Market's Amazon storefront, and Amazon itself is under 5%.

So the einkorn flour and pasta listings, the pricing and the content are effectively being run by a reseller.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would it make sense to have a quick conversation about taking that back?

Yoni"""),
E(19,"Las Vegas Souvenir & Resort Gift Show 2026|HydraPeak","Hydrapeak","Single seller account, big catalog, flat 12-month growth; under-worked catalog","Amazing Deals Online 99.4% (treated as brand's own account); 613 products; 12M MoM +3.6%; monthly rev ~$896k; avg rating 4.46","Hydrapeak's catalog on Amazon",f"""Hi {{{{first_name}}}},

{LV}

From what we can see, Hydrapeak does roughly $900k a month on Amazon, sold through a single seller account, with over 600 listings and a 4.5 average rating. The food jars carry most of it. Growth over the last 12 months looks close to flat though, which with that catalog size usually means a lot of listings are sitting there without ads, content or inventory attention.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Is it worth a short call on getting more out of the catalog?

Yoni""",brand_sellers=["Amazing Deals Online"],qa=["seller 'Amazing Deals Online' (460 offers, 99%) assumed to be Hydrapeak's own account; verify"]),
E(20,"Las Vegas Souvenir & Resort Gift Show 2026|Blue 84/Aksels/Altered Latitudes/Zephyr Headwear","Blue 84","Amazon 1P ~100% across a huge catalog with negative 12-month trend; hybrid angle","Amazon 1P 99.6%; 31,040 products; monthly rev ~$780k; 12M MoM -36.7%","Blue 84's Amazon trend",f"""Hi {{{{first_name}}}},

{LV}

Looking at Blue 84's listings, essentially all of your Amazon revenue, roughly $780k a month, is Amazon selling as the vendor across a catalog of about 30,000 college apparel listings. The trend over the last 12 months looks negative, and with 1P only, the levers to fix that, pricing, ads, content and which SKUs get stocked, mostly sit on Amazon's side.

We manage Amazon for brands end to end, including hybrid 1P/3P setups where specific lines move to Seller Central for control.

Would a 20 minute conversation on the hybrid option be worth your time?

Yoni""",qa=["exhibitor lists multiple brands (Aksels, Altered Latitudes, Zephyr Headwear); only Blue 84 queried"]),
E(21,"FNCE 2025|Fishwife Tinned Seafood Co.","Fishwife","Fast-growing brand with mixed seller base (direct 57%, Amazon 1P 22%, Whole Foods 21%); 1P share rising","Fishwife direct 56.8% (MoM -12.2 pts); Amazon 22.1% (MoM +13.8 pts); Whole Foods 20.8%; monthly rev ~$776k; 12M MoM +209%","Fishwife's Amazon seller mix",f"""Hi {{{{first_name}}}},

{FN.format(b='Fishwife')}

From what we can see, Fishwife is doing roughly $780k a month on Amazon and has grown a lot over the last year. About 55% is through your own account, with the rest split between Amazon as the vendor and Whole Foods Market's Amazon storefront. Amazon's share jumped last month while your direct share dropped, which is worth watching, because once 1P takes the Buy Box on the sardine and salmon packs, the pricing moves with it.

We manage Amazon for brands end to end, including hybrid 1P/3P setups decided at the product level.

Open to a short call on keeping control of that mix?

Yoni"""),
E(22,"Las Vegas Souvenir & Resort Gift Show 2026|MasterPieces Inc.","MasterPieces","Brand direct with a 2,600-listing long tail; top product is puzzle glue; catalog under-merchandised","MasterPieces, Inc. 86.4%; 2,664 products; monthly rev ~$763k; top ASIN puzzle glue ~$41k/mo; avg rating 4.58","MasterPieces catalog on Amazon",f"""Hi {{{{first_name}}}},

{LV}

From what we can see, MasterPieces does roughly $760k a month on Amazon, sold direct, across a catalog of about 2,600 listings with a 4.6 average rating. The top seller is puzzle glue at around $40k a month, and after the first few puzzles the revenue per listing drops off fast. That is a long tail of licensed puzzles and games that mostly isn't being advertised or merchandised.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Is it worth a short call on getting more out of the catalog?

Yoni"""),
E(23,"FNCE 2025|LesserEvil Snacks","Lesserevil","No brand seller account; Whole Foods 51% + Amazon 1P 35%; no 3P layer","Whole Foods Market 51.2%; Amazon 35.2%; brand direct 0%; monthly rev ~$717k","LesserEvil's seller mix on Amazon",f"""Hi {{{{first_name}}}},

{FN.format(b='LesserEvil')}

Looking at your listings, LesserEvil does roughly $700k a month on Amazon, and about half of it is sold through Whole Foods Market's Amazon storefront, with another third through Amazon as the vendor. We don't see a LesserEvil seller account in the mix, so there is no 3P layer for pricing, ads or new launches like the Space Balls 10 count.

We manage Amazon for brands end to end, including hybrid 1P/3P setups where the vendor relationship stays and specific products get a direct seller layer.

Would a 20 minute conversation on that be worth your time?

Yoni"""),
E(24,"Las Vegas Souvenir & Resort Gift Show 2026|Inis the Energy of the Sea","Inis the Energy of the Sea","Strong brand direct with excellent reviews; revenue concentrated in the cologne, rest of line under-scaled","Brand direct 100%; monthly rev ~$673k; 49,936 reviews; avg rating 4.75; cologne 3.3oz ~$128k/mo","Inis beyond the cologne on Amazon",f"""Hi {{{{first_name}}}},

{LV}

From what we can see, Inis is doing roughly $670k a month on Amazon, all sold direct, with about 50,000 reviews and a 4.75 average rating on 35 listings. The cologne carries most of it, and the lotion and diffusers are well behind, which usually means the ads and content are built around one hero rather than the range.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Open to a short call on scaling the rest of the line?

Yoni"""),
]
run(raw,emails)
