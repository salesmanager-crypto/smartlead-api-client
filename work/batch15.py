from batchlib import *
NF=RAW(None,[],[])
c=load_cache()
raw={
"Buoy":RAW(P("Buoy","Health & Household","Sports Nutrition Electrolyte Replacement Drinks",2.88,"",True,"https://www.amazon.com/stores/Buoy/page/FA6EB318-3931-4ED0-A27B-5B9EAD8596A2",0,0.035,0.038,50.65,4.1,8,1945,298082.34,4976056.11),
 S(("Buoy Hydration",88.086),("Summit Essentials Co.",8.835),("WELLNESSWAY",1.656),("V Choices",1.424)),
 T(("Buoy Electrolyte Drops, 120 Servings, Unflavored 3 Pack","B07NP5SY6Y",195798.98),("Buoy Rescue Electrolyte Drops, 60 Servings","B0H4LFW6YL",42028.25),("Buoy Digestion Electrolyte Drops, 120 Servings","B0GGLLXLG5",17130.55),("Buoy Electrolyte Drops Variety Pack (160 Servings)","B0DKQ54NZX",15014.82),("Buoy Brain Health Electrolyte Drops, 120 Servings","B0GKVKS8JF",8539.09))),
"Cahokia":RAW(P("Cahokia","Grocery & Gourmet Food","Dried White Rice",10,"",False,"",0.398,0.534,1.709,14.86,4.3,2,85,1965.94,18057.11),
 S(("Amazon.com",39.806),("Navistro",20.524),("Love 4 One LLC",19.762),("Elev8d Deals",6.304),("DANCO CAPITAL",6.145),("Dreamostore",4.003)),
 T(("Cahokia High Protein White Rice","B078C553WR",1287.9),("Cahokia High Protein Brown Rice","B078C58GRC",678.04))),
"Cleveland Kitchen":RAW(P("Cleveland Kitchen","Grocery & Gourmet Food","Canned & Jarred Sauerkraut",0.63,"",True,"https://www.amazon.com/stores/ClevelandKitchen/page/7A2813AB-1565-4D39-AF8E-746150A1EB8B",0.055,0.106,3.458,20.84,4.4,8,1936,84001.59,772400.06),
 S(("Eternity Essentials",59.453),("Whole Foods Market",35.009),("Amazon.com",5.538),("FoodserviceDirect Inc.",0)),
 T(("Cleveland Kitchen Beet Red Kraut, 16 oz","B019EG7L3E",28269.9),("Cleveland Kitchen Classic Kimchi, 16 oz","B098PVNV18",24950.4),("Cleveland Kitchen Kimchi Pickle Chips, 16 oz","B0CKJ8C6SW",16192.32),("Cleveland Kitchen Classic Kraut, 16 oz","B019773QEI",9647.25),("Cleveland Kitchen Roasted Garlic Kraut, 16 oz","B019773QCK",4941.72))),
"CON-CRET":RAW(P("CON-CRET","Health & Household","Creatine Nutritional Supplements",1.41,"",True,"https://www.amazon.com/stores/CON-CR%C4%92T%C2%AE/page/3F97182A-BBE0-4E54-8F55-25C9E1B99F23",0.001,0.035,0.843,35.67,4.49,27,5541,1214245.29,14157149.8),
 S(("Vireo Systems INC",99.667),("Paradine Services",0.277),("Amazon.com",0.055)),
 T(("CON-CRET Creatine HCl Capsules, 90 Count","B0BKCVLYGX",450659.73),("CON-CRET Creatine HCl Powder, Unflavored, 100 Servings","B0CQ8V7NXS",152859.03),("CON-CRET Creatine HCl Powder, Pineapple, 100 Servings","B0CQ8XWFWL",89820.05),("CON-CRET Creatine HCl Powder, Raspberry, 100 Servings","B0CQ8X9CZV",89820.05),("CON-CRET Creatine HCl Powder, Lemon Lime, 100 Servings","B0CQ8XG21K",89580.13))),
"drink wholesome":RAW(P("drink wholesome","Grocery & Gourmet Food","Protein Drinks",0.88,"Drink Wholesome",True,"https://www.amazon.com/stores/drinkwholesome/page/7A8459AF-4EC8-4C29-A33F-EA6D6260C90F",0,0.029,0.402,69.55,4.58,17,318,69404.19,1222902.21),
 S(("Drink Wholesome",100)),
 T(("drink wholesome Vanilla Egg White Protein Powder","B0CZS4QYBV",24356.52),("drink wholesome Chocolate Egg White Protein Powder","B0CZS4V65R",8818.74),("drink wholesome Unflavored Egg White Protein Powder","B0CZS4VDJR",8678.76),("drink wholesome Vanilla Collagen Protein Powder","B0CYM5RDKD",6439.08),("Drink Wholesome Vanilla Meal Replacement Powder","B0CZS1HX2D",3319.68))),
"Egglands Best":RAW(P("Egglands Best","Grocery & Gourmet Food","Whole Eggs",0.5,"",False,"",1,-0.035,None,18.02,4.7,4,10487,59363.64,335674.95),
 S(("Amazon.com",100)),
 T(("Eggland's Best Large Cage Free Brown Eggs, 1 dozen","B00A445BW4",36835.26),("Eggland's Best Large Organic Brown Eggs, 12 count","B00AR7HCMK",19817),("Eggland's Best Large Eggs, 18 ct","B005MS7C74",2711.38),("Eggland's Best 17% Layer Crumbles Chicken Food, 40 lbs","B07XPBSSYS",0))),
"Equip":RAW(P("Equip","Health & Household","Sports Nutrition Protein Powder Blends",1.19,"EquipFoods",True,"https://www.amazon.com/stores/EquipFoods/page/06E91FD9-9518-4FFD-A1CF-43F8594C4615",0.001,-0.196,0.383,55.41,4.44,72,6026,2163609.73,27220111.86),
 S(("EquipFoods",99.693),("ChefsKiss",0.131),("Denovo Brands",0.079),("Amazon.com",0.067),("MarketingSpot",0.028),("Thee-store",0.001)),
 T(("Equip Prime Chocolate Protein Powder, 30 Scoops","B013MRPPL6",556158.2),("Equip Foods Prime Protein Powder, Vanilla, 30 Servings","B01M2Y1NN8",417798.55),("Equip Foods Prime Protein Powder, Unflavored, 30 Servings","B0B41YX3VR",200978.44),("Equip Prime Vanilla Protein Powder, 30 Scoops","B0FXXCG2XH",132852.46),("Equip Foods Grass Fed Collagen Powder, Unflavored, 30 Servings","B071SH212S",131415.79))),
"Red Plate Foods":RAW(P("Red Plate Foods","Grocery & Gourmet Food","Granola",6.83,"Amazon.com",False,"",0,0.087,-0.051,49.67,4.85,6,37,7238.51,87014.63),
 S(("Everyday Supply Co.",45.453),("KeHE Distributors, LLC",21.799),("Everyday Goods Inc.",15.862),("TheNewMall",15.727),("UnbeatableSale Local",0.634),("USTradeEnt",0.525)),
 T(("Red Plate Foods Golden Vanilla Granola, 11 Ounce (Pack of 6)","B0BLHSCMMV",2485),("Red Plate Foods Cinnamon Granola, 11 Ounce (Pack of 6)","B0BLHRYM9Q",1952.34),("Red Plate Foods Dark Chocolate Granola, 11 Ounce (Pack of 6)","B0BLHR76HW",1854.02),("Red Plate Foods Gourmet Granola, 6 bags 12 oz (Cinnamon)","B08S24TDWX",352.73),("Red Plate Foods Gourmet Granola, 6 bags 12 oz (Vanilla)","B08S19C61T",305.4))),
"Sovereign Silver":RAW(P("Sovereign Silver","Health & Household","Colloidal Silver Mineral Supplements",2.1,"ZQUARED",True,"https://www.amazon.com/stores/SovereignSilver/page/68EBCCEF-EE76-447A-9518-C89A3B1564F7",0,-0.056,0.135,29.15,4.6,30,76853,956318.27,14176096.51),
 S(("LUMlNlZE",98.305),("The Brky Guy",0.909),("Glutenfree4U",0.516),("HealthZone",0.187),("S. Republic",0.062),("Amazon.com",0.021)),
 T(("Sovereign Silver Immune Support, Colloidal Silver, 4 fl oz","B000OA6Z6O",167728.03),("Sovereign Silver Immune Support, Colloidal Silver, 8 fl oz","B00XQF5SXU",159517.11),("Sovereign Silver Immune Support, Colloidal Silver, 16 fl oz","B00GEF1DXI",146082.11),("Sovereign Silver Sinus Relief Nasal Spray, 2 fl oz","B0C5Y1ZVKB",76419.22),("Sovereign Silver Immune Support, Colloidal Silver, 32 fl oz","B00OTZK0Z2",76154.28))),
"SOLARA SUNCARE":c["SOLARA SUNCARE"],
"Step One Foods":RAW(P("Step One Foods","Health & Household","Sports Nutrition Bars",0.6,"Step One Foods",True,"https://www.amazon.com/stores/StepOneFoods/page/0A019713-F8E4-4F89-A432-8F95D9F4C5B8",0,-0.01,0.142,46.94,4.08,5,921,39121.1,1045604.46),
 S(("Step One Foods",100)),
 T(("Step One Foods Apple Cinnamon Bars (12 Pack)","B0C1CMW8JZ",15479.1),("Step One Foods Dark Chocolate Walnut Bars (24 Pack)","B0F679RR8Q",13404.5),("Step One Foods Lemon Almond Bar (12 Pack)","B0CSZDTNTW",10237.5),("Step One Foods Anytime Sprinkle (12 Pack)","B0BVRPYBQK",0),("Step One Foods Anytime Sprinkle (12 Pack)","B0DW4FG85G",0))),
"Sunnygem California":RAW(P("Sunnygem California","Grocery & Gourmet Food","Almond Oils",2,"",False,"",0,0.106,-0.49,22.99,4.4,1,100,1885.18,24278.06),
 S(("Sunnygem Almond Oil",100)),
 T(("Sunnygem California Almond Oil Cold Pressed Food Grade, 16.9 oz","B0BPWXR53L",1885.18))),
"Wonderful Pistachios":RAW(P("Wonderful Pistachios","Grocery & Gourmet Food","Pistachio Nuts",3.29,"Amazon.com",True,"https://www.amazon.com/stores/Wonderful/page/144617BC-5B1A-497F-A256-CB8FC5E710B2",0.99,0.221,-0.119,36.99,4.67,117,261286,2712289.5,33717351.44),
 S(("Amazon.com",99.01),("FoodserviceDirect Inc.",0.324),("Whole Foods Market",0.198),("Cool Sea",0.129),("Buck Island Trading",0.077),("HealthandOutdoors",0.075)),
 T(("Wonderful Pistachios No Shells, 3 Flavors Variety Pack of 9","B08DX4JCKQ",407080.8),("Wonderful Pistachios No Shells, Roasted & Salted, 24 Ounce Bag","B004HZFASG",353972.98),("Wonderful Pistachios No Shells, Roasted & Salted, 0.75 Ounce (Pack of 14)","B07TCW23N9",295268.4),("Wonderful Pistachios In Shell, Roasted & Salted, 48 Ounce","B07PBKZZ51",257833.2),("Wonderful Pistachios No Shells, Roasted & Salted, 0.75 Oz (Pack of 9)","B07XSKK6Z4",194622.96))),
"Tiiga":RAW(P("Tiiga","Health & Household","Sports Nutrition Electrolyte Replacement Drinks",0.2,"",False,"",0,-0.128,0.308,28.49,3.9,10,37,1079.84,17505.19),
 S(("Tiiga",100)),
 T(("Tiiga Gut Health & Hydration Drink Mix, Watermelon, 30 Servings","B0D9H8VHCW",680),("Tiiga Gut Health Prebiotic Fiber & Baobab Drink Mix (Lemon Lime)","B08SM9Q3P9",399.84),("Tiiga Baobab Boost Organic Baobab (30)","B0FYRQS14Q",0),("Tiiga Baobab Boost Organic Baobab Fruit Prebiotic Fiber","B0FYK1XTP5",0),("Tiiga Gut Health Drink Mix (Tropical Bliss)","B08CWZHWNR",0))),
"Tosi":RAW(P("Tosi","Grocery & Gourmet Food","Nut Bars",2.61,"Tosi Snacks",True,"https://www.amazon.com/stores/Tosi/page/21B228BC-2326-4D9C-B9C9-A9FED76361B3",0.01,0.315,0.347,23.76,4.31,36,909,53675.03,803473.94),
 S(("Tosi Snacks",90.792),("Everyday Goods Inc.",5.37),("Franzy Boy Goods",1.07),("Amazon.com",0.974),("Modernparty",0.888),("USTradeEnt",0.424)),
 T(("Tosi Nut Bars, Almond Blueberry, 12-Pack","B07P86LP93",5448),("Tosi Nut Bars, Cashew Coconut, 12-Pack","B07VYVH8HG",5424),("Tosi Nut Bars, Almond Dark Choco, 12-Pack","B09J6RG9WP",5328),("Tosi Organic SuperBites, Variety, 8-Pack","B099FK6P91",4637.68),("Tosi Crunchy Meal Nut Bars, Almond Blueberry, 12-Pack","B07VYVCZ2L",3776.92))),
"Alpha Tribe":RAW(P("Alpha Tribe","Health & Household","Blended Vitamin & Mineral Supplements",0.4,"",True,"https://www.amazon.com/stores/AlphaTribe/page/FE01C1E0-17BD-47F3-9646-2200B02DB0A8",0,-0.338,2.793,90.93,4.34,5,982,34158.24,1435116.93),
 S(("AlphaTribe",100)),
 T(("Alpha Tribe Multivitamin for Men with Sea Moss, Black Seed Oil, Ashwagandha","B0DKNJBC9C",17827.94),("Alpha Tribe Multivitamin for Men with Sea Moss, Black Seed Oil, Ashwagandha","B0CV641R7Z",16330.3),("Alpha Tribe Test Protocol (120 Count Pack of 1)","B0CTVN1WFY",0),("Alpha Tribe Test Protocol (Pack of 2)","B0F45SLFCQ",0),("Alpha Tribe Test Protocol (Pack of 3)","B0F45ST163",0))),
"Up2U":NF,
"VSL #3":RAW(P("VSL #3","Health & Household","Acidophilus Nutritional Supplements",1.33,"",False,"",0,-0.153,0.465,161.12,4.63,6,3595,505520.95,8227053.15),
 S(("VSL#3",100)),
 T(("VSL #3 High-Potency Probiotic Medical Food","B083STQVBP",248805),("VSL #3 High-Potency Probiotic Medical Food","B07WX1LVHL",141880.35),("VSL #3 High-Potency Probiotic Medical Food","B0BWHB72DH",41287.1),("VSL #3 High-Potency Probiotic Medical Food","B0BWHJ1JS1",33660.9),("VSL #3 High-Potency Probiotic Medical Food","B083WNY2TF",22045.1))),
"Wildbrine":RAW(P("Wildbrine","Grocery & Gourmet Food","Canned & Jarred Sauerkraut",1.75,"Amazon.com",False,"",0,1.035,2.001,19.28,4.03,8,4716,100747.93,1223437.88),
 S(("Whole Foods Market",91.53),("Royalty Privilege",3.632),("Eternity Essentials",2.186),("Big-Foot",1.497),("AKYS",0.677),("Mugatu",0.477)),
 T(("Wildbrine Organic Green Sauerkraut 18 oz Jar","B075M96F77",39442.65),("Wildbrine Kimchi 18 oz Jar","B01CRLP1U8",28779),("Wildbrine Mediterranean Fermented Chickpea Salad 20 oz Jar","B07G4XNC45",12530.7),("Wildbrine Organic Red Beet & Cabbage Sauerkraut 18 oz Jar","B01MEEJDXR",10284.56),("Wildbrine Organic Dill & Garlic Sauerkraut 18 oz Jar","B00GFPW8PE",8551.41))),
"Yaza":RAW(P("Yaza","Grocery & Gourmet Food","Refrigerated Cheese Dips & Spreads",0.5,"",True,"https://www.amazon.com/stores/Yaza/page/9F60B7ED-24D5-4443-AA9E-1C2083FAD181",0,0.074,10.627,7.56,3.55,2,127,27614.44,141062.16),
 [],
 T(("Yaza, Labneh Plain, 12 Ounce","B0CSLLDL42",17138.4),("Yaza, Labneh Zaatar And Olive Oil, 12 Ounce","B0CSLB4ZML",10476.04))),
"Backroad Country":RAW(P("Backroad Country","Grocery & Gourmet Food","Licorice Candy",1.74,"",True,"https://www.amazon.com/stores/BackroadCountry/page/BDDC3BDE-88B6-4D28-93BE-5B6EFBE98B24",0,-0.01,0.098,15.61,4.08,50,5322,54762.72,782573.85),
 S(("ChristianStore2011",53.474),("Myers Distribution",37.315),("Panorama Goods Hub",2.526),("Spring Mount Supply",1.992),("Sellet-Ohio",1.275),("Shop Avaaya",0.925)),
 T(("Backroad Country Old Fashioned Classic Black Licorice Twists, 16 OZ (Pack of 2)","B09SGLC6VZ",9030.7),("Backroad Country Old Fashioned Classic Black Licorice Twists, 16 OZ","B07MWBGFSF",8850.36),("Backroad Country Pickled Cured Pork Hocks in a Jar, 12 oz","B019ZGOGZ4",6114.96),("Backroad Country Old Fashioned Green Apple Twists, 16 OZ","B07N1R8NR3",4913.48),("Backroad Country Old Fashioned Red Twists, 16 OZ","B00BLBMUIM",4759.36))),
"Crazy Apparel":NF,
"CROSSROADS ORIGINAL DESIGNS":RAW(P("CROSSROADS ORIGINAL DESIGNS","Home & Kitchen","Jar Candles",2.54,"",False,"",0,0.234,0.192,40.61,4.28,59,4605,19261.67,376851.91),
 S(("Hour Loop",43.86),("JBTools",12.992),("Top Logistics & Marketing",8.84),("ArtsiHome",6.459),("E SHOPPE",6.427),("Casablanca Goods LLC",4.249)),
 T(("Crossroads Buttered Maple Syrup Scented 2-Wick Candle, 26 Ounce","B009ACFT0K",5156),("Crossroads Candle 16 Ounce Jar Candle, Buttered Maple Syrup","B00I213R68",2210.1),("Crossroads Maple Pumpkin Donut Scented 2-Wick Candle, 26 oz","B0794BCKSN",1708.2),("Crossroads Buttered Maple Syrup Scented 4-Wick Candle, 96 Ounce","B076PP6MNN",1329.86),("Crossroads Buttered Maple Syrup Scented 4-Wick Candle, 64 Ounce","B00NEZYYNC",895.2))),
"Culver":RAW(P("Culver","Kitchen & Dining","Old Fashioned Glasses",0.88,"LaPrima Shops",True,"https://www.amazon.com/stores/Culver/page/2B31068F-F1CD-49BF-AE8D-9EC9D3637EC8",0,-0.054,-0.22,36.05,4.54,16,2225,9007.04,188762.03),[],[]),
"Desert Sunglass":NF,
}
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
FN="Saw that {b} exhibited at FNCE last year."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
END="We manage the channel end to end."
KL="Las Vegas Souvenir & Resort Gift Show 2026|"; KN="FNCE 2025|"
ASK_NF="Is Amazon something you're looking at more seriously?"
def nf(row,key,q,angle,points,subject,body,qa,opener,ask=ASK_NF,conf="not found"):
    return E(row,key,q,angle,points,subject,f"""{H}

{opener}

{body}

{PROOF} {END}

{ask}

Yoni""",conf=conf,qa=qa)
emails=[
E(1060,KN+"Buoy Hydration","Buoy","Strong brand-direct position (~$298k a month); one reseller (Summit Essentials) appeared this month at ~9%; 4.1 rating; flat","Buoy Hydration 88.1%; Summit Essentials Co. 8.8% (new this month); WELLNESSWAY 1.7%; monthly rev ~$298k; 8 products; 1,945 reviews; rating 4.1; 3-pack drops ~$196k/mo","Buoy on Amazon",f"""{H}

{FN.format(b='Buoy')}

Looking at your listings, Buoy is doing about $300k a month on Amazon through your own account, with the unflavored 3-pack carrying two thirds of it. Two things stand out. A reseller called Summit Essentials showed up this month and is already at close to 9% on one listing, and the rating sits at 4.1, which for electrolytes is where taste complaints cap conversion. I know you have people on this.

{CO}

Open to a 20 minute look at the reseller and rating side?

Yoni""",brand_sellers=["Buoy Hydration"],qa=["sheet Brand (Seller Central) confirmed"]),
E(1062,KN+"Cahokia Rice","Cahokia","Barely on Amazon: two rice listings doing ~$2k a month, split between Amazon 1P and a handful of resellers; no storefront; growing fast from a tiny base","Amazon.com 39.8%; Navistro 20.5%; Love 4 One 19.8%; monthly rev ~$2k; 2 products; 85 reviews; rating 4.3; 12M MoM +171%","Cahokia Rice on Amazon",f"""{H}

{FN.format(b='Cahokia')}

Looking at your listings, Cahokia has two rice listings on Amazon doing about $2k a month combined, with Amazon selling some of it as a vendor and resellers like Navistro and Love 4 One the rest. There's no brand storefront and under 100 reviews. High-protein rice is a search with real demand and almost no branded competition on Amazon, which is a rare position for a small brand.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",qa=["sheet Amazon (Vendor); fresh data shows Mixed with resellers at ~60%"]),
E(1072,KN+"Cleveland Kitchen","Cleveland Kitchen","Sold through Whole Foods and a reseller (Eternity Essentials ~59%) rather than the brand; ~$84k a month, up several times on the year","Eternity Essentials 59.5% (new this month); Whole Foods Market 35%; Amazon.com 5.5%; monthly rev ~$84k; 8 products; 1,936 reviews; rating 4.4; 12M MoM +346%","Who sells Cleveland Kitchen on Amazon",f"""{H}

{FN.format(b='Cleveland Kitchen')}

Looking at your listings, Cleveland Kitchen is doing about $84k a month on Amazon, up several times on the year, but the brand isn't the seller on any of it. Whole Foods Market sells about a third, and a reseller called Eternity Essentials appeared this month and is already at close to 60% on the beet kraut listing. For a refrigerated product, a reseller you don't control is a cold-chain risk as much as a pricing one.

{CO}

Would it make sense to have a quick conversation about the reseller side?

Yoni""",qa=["sheet Amazon (Vendor); fresh data shows Third-party resellers (Eternity Essentials, Whole Foods)"]),
E(1076,KN+"CON-CRĒT","CON-CRET","Strong brand-direct position through Vireo Systems (~$1.2M a month), up ~84% on the year; modest ask","Vireo Systems INC 99.7%; monthly rev ~$1.21M; 27 products; 5,541 reviews; rating 4.49; MoM +3.5%; 12M MoM +84%; capsules ~$451k/mo","CON-CRET on Amazon",f"""{H}

{FN.format(b='CON-CRET')}

Looking at your listings, CON-CRET is doing about $1.2M a month on Amazon through the Vireo Systems account and growing fast, with the capsules carrying more than a third of it. That's a strong position in a category where creatine HCl is getting a lot of new search. I know you have people on this, so this isn't a pitch on the basics. It's more about what the next stretch looks like as the flavored powders come up.

{CO}

Open to a 20 minute look at where the next stretch of growth is?

Yoni""",brand_sellers=["Vireo Systems INC"],qa=["sheet third-party (Vireo Systems); Vireo Systems is the parent company, treated as brand direct"]),
E(1092,KN+"Drink Wholesome","drink wholesome","Brand direct at ~$69k a month, up ~40% on the year, but only 318 reviews across 17 listings at a $70 price point","Drink Wholesome 100%; monthly rev ~$69k; 17 products; 318 reviews; rating 4.58; MoM +2.9%; 12M MoM +40%; vanilla egg white ~$24k/mo","drink wholesome on Amazon",f"""{H}

{FN.format(b='Drink Wholesome')}

Looking at your listings, drink wholesome is doing about $69k a month on Amazon through your own account and up about 40% on the year, with the vanilla egg white protein carrying it. What stands out is the review count: about 300 across 17 listings for a $70 product, which is the main thing keeping conversion and rank from matching the growth. That's the piece to build going into next year.

{CO}

Would it make sense to have a quick conversation about growing the channel?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(1098,KN+"Eggland's Best, Inc.","Egglands Best","Amazon 1P only (Amazon Fresh eggs); ~$59k a month on four listings; no storefront; narrow ask","Amazon.com 100%; monthly rev ~$59k; 4 products; 10,487 reviews; rating 4.7; MoM -3.5%","Eggland's Best on Amazon",f"""{H}

{FN.format(b="Eggland's Best")}

From what we can see, Eggland's Best does about $59k a month on Amazon, all of it sold by Amazon itself through grocery delivery on a handful of egg listings, with no brand storefront and nothing on the shelf-stable side. I know Eggland's Best has people on retail. This is a narrow point about whether the brand should own its Amazon presence rather than leaving it entirely to Amazon Fresh.

{CO}

Open to a 20 minute conversation about the Amazon side?

Yoni""",qa=["sheet third-party (Amazon Now); fresh data shows Amazon 1P 100%","weaker fit: fresh grocery"]),
E(1103,KN+"Equip","Equip","Very strong brand-direct position (~$2.2M a month), up ~38% on the year, month down ~20%; modest second-set-of-eyes ask","EquipFoods 99.7%; monthly rev ~$2.16M; 72 products; 6,026 reviews; rating 4.44; MoM -19.6%; 12M MoM +38%; Prime chocolate ~$556k/mo","Equip on Amazon",f"""{H}

{FN.format(b='Equip')}

Looking at your listings, Equip is doing about $2.2M a month on Amazon through your own account, up close to 40% on the year, with the Prime beef protein in chocolate and vanilla carrying most of it. The month looks to be down about 20%, which on a catalog this concentrated usually traces to one or two listings. I know you have an Amazon team, so this is a second set of eyes rather than a pitch.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni""",brand_sellers=["EquipFoods"],qa=["sheet Brand (Seller Central) confirmed"]),
E(1171,KN+"Red Plate Foods","Red Plate Foods","Sold entirely by distributors and resellers (Everyday Supply 45%, KeHE 22%); ~$7k a month; no brand account or storefront; 37 reviews at 4.85","Everyday Supply Co. 45.5%; KeHE Distributors 21.8%; Everyday Goods 15.9%; TheNewMall 15.7%; monthly rev ~$7.2k; 6 products; 37 reviews; rating 4.85","Who sells Red Plate Foods on Amazon",f"""{H}

{FN.format(b='Red Plate Foods')}

Looking at your listings, Red Plate Foods granola is on Amazon at about $7k a month, all sold by distributors and resellers like Everyday Supply, KeHE and TheNewMall rather than a Red Plate account, with no brand storefront. The reviews are excellent, 4.85 across the catalog, but there are fewer than 40 of them. Nut-free granola is a real search on Amazon, and the brand isn't the one answering it.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party (AmeriStyle) confirmed"]),
E(1175,KN+"Silver Star Nutrition","Sovereign Silver","Nearly all revenue (~$956k a month) runs through a single seller (LUMlNlZE) rather than a brand account; identity of exhibitor unverified","LUMlNlZE 98.3%; The Brky Guy 0.9%; monthly rev ~$956k; 30 products; 76,853 reviews; rating 4.6; MoM -5.6%; 12M MoM +13.5%","Who sells Sovereign Silver on Amazon",f"""{H}

{FN.format(b='Sovereign Silver')}

Looking at your listings, Sovereign Silver does close to $1M a month on Amazon, and nearly all of it runs through a seller called LUMlNlZE rather than a brand account. If that's a partner you chose, fine. If it isn't, that seller controls the Buy Box, pricing and the customer data on a brand with 77,000 reviews, and the month looks to be down about 6%. I know you have people on this.

{CO}

Open to a 20 minute conversation about who should own the channel?

Yoni""",qa=["verify identity: exhibitor listed as Silver Star Nutrition; sheet and SmartScout record are Sovereign Silver","sheet third-party (LUMlNlZE) confirmed; LUMlNlZE may be an affiliated account, verify","large brand"]),
E(1178,KN+"Solara Labs","SOLARA SUNCARE","Nearly all revenue through one seller (Carbon Beauty ~90%); 3.8 rating; month down ~40% after summer; same brand as FLIBS row 279","Cached Solara Suncare record: Carbon Beauty 89.8%; JJ Online store 3.6%; monthly rev ~$37k; 16 products; 748 reviews; rating 3.79; MoM -40%; 12M MoM +18%","Solara Suncare on Amazon",f"""{H}

{FN.format(b='Solara Suncare')}

Looking at your listings, Solara Suncare is doing about $37k a month on Amazon, almost all of it through a seller called Carbon Beauty rather than a Solara account, with a few small resellers on the same listings. If Carbon Beauty is your partner, fine. What stands out either way is a 3.8 rating across the catalog, which for a premium sunscreen is the thing capping conversion, and the off-season is when that gets fixed.

{CO}

Would it make sense to have a quick conversation before next season?

Yoni""",qa=["same brand as FLIBS row 279 (Solara); cached record reused","sheet third-party (JJ Online store); fresh data shows Carbon Beauty at 90%, may be an affiliated account, verify"]),
E(1183,KN+"Step One Foods","Step One Foods","Brand direct at ~$39k a month on three selling listings; 4.08 rating; flat month, up ~14% on the year","Step One Foods 100%; monthly rev ~$39k; 5 products; 921 reviews; rating 4.08; MoM -1%; 12M MoM +14%","Step One Foods on Amazon",f"""{H}

{FN.format(b='Step One Foods')}

Looking at your listings, Step One Foods is doing about $39k a month on Amazon through your own account, spread across three bar listings, with the sprinkle products not moving at all. The rating sits just above 4, which for a clinically positioned product is lower than it should be and is the main thing capping conversion. The clinical story is a real differentiator in a crowded bar category if the listings tell it.

{CO}

Would it make sense to have a quick conversation about growing the channel?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(1184,KN+"Sunnygem LLC","Sunnygem California","One almond oil listing doing ~$1.9k a month, sold direct, down ~49% on the year; no storefront","Sunnygem Almond Oil 100%; monthly rev ~$1.9k; TTM ~$24k; 1 product; 100 reviews; rating 4.4; 12M MoM -49%","Sunnygem on Amazon",f"""{H}

{FN.format(b='Sunnygem')}

Looking at your listings, Sunnygem has one almond oil listing on Amazon doing about $2k a month, sold direct, with 100 reviews at a 4.4 average and the year down by about half. There's no brand storefront and nothing else from the catalog is listed. Almond oil is a steady Amazon search across cooking and skincare, and one listing left to drift isn't a channel.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",qa=["sheet says brand store; fresh data shows no storefront","sheet Brand (Seller Central) confirmed"]),
E(1193,KN+"The Wonderful Company","Wonderful Pistachios","Very large; Amazon 1P ~99% (vendor); 117 listings; down ~12% on the year; narrow ask","Amazon.com 99%; monthly rev ~$2.71M; 117 products; 261,286 reviews; rating 4.67; MoM +22%; 12M MoM -12%","Wonderful vendor side on Amazon",f"""{H}

{FN.format(b='Wonderful Pistachios')}

From what we can see, Wonderful Pistachios does about $2.7M a month on Amazon, essentially all of it sold by Amazon as a vendor, with the no-shell variety packs carrying the top listings and the year down about 12%. I know Wonderful has an Amazon team. This is a narrow point about the vendor setup, where Amazon controls price and stock and the advertising and content across 117 listings tend to sit between teams.

{CO}

Open to a 20 minute look at the vendor side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed","very large brand, narrow ask"]),
E(1194,KN+"Tiiga","Tiiga","Barely on Amazon: two listings selling ~$1k a month, sold direct, 37 reviews at a 3.9 rating; no storefront showing","Tiiga 100%; monthly rev ~$1.1k; 10 products; 37 reviews; rating 3.9; MoM -13%; storefront false","Tiiga on Amazon",f"""{H}

{FN.format(b='Tiiga')}

Looking at your listings, Tiiga is on Amazon at about $1k a month, sold direct, with two of ten listings selling and under 40 reviews at a 3.9 average. Gut health hydration is a category where Amazon search is doing real work right now, and a listing set this thin isn't in the conversation. The rating is the first thing to fix, then content and advertising.

{PROOF} {END}

Is Amazon something you're looking at more seriously?

Yoni""",qa=["sheet says brand store; fresh data shows no storefront","sheet Brand (Seller Central) confirmed"]),
E(1199,KN+"Tosi Snacks","Tosi","Brand sells ~91% direct at ~$54k a month, growing; small reseller layer (Everyday Goods 5%); 36 listings averaging low volume each","Tosi Snacks 90.8%; Everyday Goods 5.4%; Amazon.com 1%; monthly rev ~$54k; 36 products; 909 reviews; rating 4.31; MoM +31.5%; 12M MoM +35%","Tosi on Amazon",f"""{H}

{FN.format(b='Tosi')}

Looking at your listings, Tosi is doing about $54k a month on Amazon through your own account and growing, spread fairly evenly across the nut bar 12-packs with no single hero listing. That's a healthy base. With 36 listings and about 900 reviews across all of them, the catalog is wide but thin on social proof, and consolidating around a few winners with advertising behind them is usually what moves a brand at this stage.

{CO}

Would it make sense to have a quick conversation about the next stretch?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(1200,KN+"Tribe Nutrition","Alpha Tribe","Brand direct at ~$34k a month, up several times on the year but down ~34% this month; two multivitamin listings carry it; identity of exhibitor unverified","AlphaTribe 100%; monthly rev ~$34k; 5 products; 982 reviews; rating 4.34; MoM -34%; 12M MoM +279%","Alpha Tribe on Amazon",f"""{H}

{FN.format(b='Alpha Tribe')}

Looking at your listings, Alpha Tribe is doing about $34k a month on Amazon through your own account, up several times on the year, with the two men's multivitamin listings carrying all of it and the Test Protocol line not moving. The month looks to be down about a third. When a brand rides two listings that hard, a dip like that is usually ranking or advertising on one of them, and it's fixable.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni""",qa=["verify identity: exhibitor listed as Tribe Nutrition; sheet and SmartScout record are Alpha Tribe","sheet Brand (Seller Central) confirmed"]),
nf(1207,KN+"UP2U","Up2U","Not found; sheet listing is a book ISBN; exhibitor product line unclear","No brand record on two attempts (Up2U, UP2U); sheet listing is a book","UP2U on Amazon",
"From what we can see, UP2U doesn't have a brand presence on Amazon, and the only listing tied to the name is a book. If UP2U is a program or service rather than a product, Amazon isn't relevant and this note can be ignored. If there's a product side, that's where public marketplace data would start to matter.",
["no brand record on two attempts; sheet listing is a book; industry-level email","exhibitor product line unclear, weak fit"],FN.format(b='UP2U'),ask="Is there a product side to UP2U where Amazon comes up?"),
E(1213,KN+"VSL#3 / Actial Nutrition, Inc.","VSL #3","Brand direct at ~$506k a month on six listings, up ~47% on the year, month down ~15%; no storefront showing; modest ask","VSL#3 100%; monthly rev ~$506k; 6 products; 3,595 reviews; rating 4.63; MoM -15%; 12M MoM +47%; storefront false","VSL#3 on Amazon",f"""{H}

{FN.format(b='VSL#3')}

Looking at your listings, VSL#3 is doing about $500k a month on Amazon through your own account across six listings, up close to 50% on the year, with the month down about 15%. One thing stands out: no brand storefront shows up in marketplace data, which at this scale matters for ad traffic and for keeping a medical food positioned properly. I know you have people on this.

{CO}

Open to a 20 minute look at where the next stretch of growth is?

Yoni""",qa=["combined exhibitor name; queried VSL #3","sheet says brand store; fresh data shows no storefront","sheet Brand (Seller Central) confirmed"]),
E(1215,KN+"wildbrine","Wildbrine","Sold through Whole Foods Market (~92%) and small resellers; no brand account or storefront; up strongly on the year; 4.03 rating","Whole Foods Market 91.5%; Royalty Privilege 3.6%; Eternity Essentials 2.2%; monthly rev ~$101k; 8 products; 4,716 reviews; rating 4.03; MoM +104%; 12M MoM +200%","wildbrine on Amazon",f"""{H}

{FN.format(b='wildbrine')}

Looking at your listings, wildbrine is doing about $100k a month on Amazon, up sharply on the year, with Whole Foods Market as the seller on more than 90% and a few small resellers on the rest. There's no brand account or storefront, and the rating sits around 4.0, which on refrigerated kraut and kimchi usually traces to shipping and temperature complaints. That's a content and packaging problem more than a product one.

{CO}

Open to a 20 minute look at the rating and content side?

Yoni""",qa=["sheet third-party (Whole Foods Market) confirmed; Whole Foods counted as third-party per rule but is Amazon-owned"]),
E(1217,KN+"Yaza","Yaza","Two labneh listings doing ~$28k a month through Whole Foods Market; 3.55 rating on 127 reviews; up sharply on the year","Sheet: sold by Whole Foods Market; monthly rev ~$28k; 2 products; 127 reviews; rating 3.55; MoM +7%; 12M MoM +1,063%","Yaza on Amazon",f"""{H}

{FN.format(b='Yaza')}

Looking at your listings, Yaza has two labneh listings on Amazon doing about $28k a month, sold through Whole Foods Market rather than a brand account, and the growth on the year is dramatic. What stands out is a 3.55 rating on about 130 reviews. For a refrigerated dairy product that usually traces to how it arrives rather than how it tastes, and it caps everything the growth could become.

{CO}

Would it make sense to have a quick conversation about the rating?

Yoni""",qa=["seller query returned empty; seller taken from sheet (Whole Foods Market)","low rating"]),
E(1277,KL+"Country Fresh Food & Confections, Inc.","Backroad Country","Sold entirely by resellers (ChristianStore2011 53%, Myers Distribution 37%); ~$55k a month across 50 listings; no brand account","ChristianStore2011 53.5%; Myers Distribution 37.3%; Panorama Goods Hub 2.5%; monthly rev ~$55k; 50 products; 5,322 reviews; rating 4.08; 12M MoM +10%","Who sells Backroad Country on Amazon",f"""{H}

{LV}

Looking at your listings, Backroad Country is doing about $55k a month on Amazon across 50 listings, with the black licorice twists carrying it, and none of it runs through a Country Fresh account. ChristianStore2011 sells about half, Myers Distribution most of the rest. For a candy brand heading into Q4, that means price, content and the Buy Box on your best sellers are set by whoever has stock.

{CO}

Would it make sense to have a quick conversation about owning the channel before Q4?

Yoni""",qa=["sheet third-party (ChristianStore2011) confirmed"]),
nf(1278,KL+"Crazy Apparel Inc.","Crazy Apparel","Not found; sheet listing is an unrelated print-on-demand shirt; industry-level email","No brand record on two attempts (Crazy Apparel, Crazy Apparel Inc); sheet listing is a novelty shirt sold by Amazon","Crazy Apparel on Amazon",
"From what we can see, Crazy Apparel doesn't have a brand presence on Amazon, and the only listing tied to the name is an unrelated novelty shirt. Resort and souvenir apparel gets searched by name on Amazon by the people who bought a piece on a trip, and a storefront with a few well-built listings is a small way to catch that going into the holidays.",
["no brand record on two attempts; sheet listing unrelated; industry-level email"],LV),
E(1281,KL+"Crossroads Designs, LLC","CROSSROADS ORIGINAL DESIGNS","Sold entirely by resellers (Hour Loop 44%, JBTools 13%, ArtsiHome 6%); ~$19k a month across 59 candle listings; no brand account or storefront","Hour Loop 43.9%; JBTools 13%; Top Logistics 8.8%; ArtsiHome 6.5%; monthly rev ~$19k; 59 products; 4,605 reviews; rating 4.28; MoM +23%","Who sells Crossroads candles on Amazon",f"""{H}

{LV}

Looking at your listings, Crossroads candles are on Amazon at about $19k a month across roughly 60 listings, all sold by resellers like Hour Loop, JBTools and ArtsiHome rather than a Crossroads account, and there's no brand storefront. The Buttered Maple Syrup scent carries it, with 4,600 reviews behind the catalog. Candles are one of the biggest Q4 gift searches on Amazon, and the brand isn't the one selling them.

{CO}

Would it make sense to have a quick conversation about owning the channel before Q4?

Yoni""",qa=["sheet third-party (Hour Loop) confirmed"]),
nf(1283,KL+"Culver Industries, Inc.","Culver","Wrong match; 'Culver' on Amazon is a glassware brand sold by LaPrima Shops; sheet mapped to an unrelated LED storefront; industry-level email","'Culver' record (~$9k/mo, glassware) and sheet storefront (Culver LED) are both unrelated; 'Culver Industries' returned empty","Culver Industries on Amazon",
"From what we can see, Culver Industries doesn't have a brand presence on Amazon, and searches for the name land on an unrelated glassware brand and an unrelated lighting storefront. For a gift-show exhibitor, Amazon is where the people who saw you go to look afterward, and right now there's nothing built under the name to catch that.",
["wrong match: 'Culver' record is a glassware brand; sheet storefront (Culver LED) unrelated; exhibitor product line unclear","industry-level email"],LV,conf="wrong match"),
nf(1288,KL+"Desert Sunglass of Scottsdale","Desert Sunglass","Not found; sheet listing is an unrelated novelty shirt; industry-level email","No brand record on two attempts; sheet listing is a print-on-demand shirt sold by Amazon","Desert Sunglass on Amazon",
"From what we can see, Desert Sunglass of Scottsdale doesn't have a brand presence on Amazon, and the only listing tied to the name is an unrelated novelty shirt. Sunglasses are one of the most searched gift categories on Amazon, and a resort sunglass line with a storefront and a few well-built listings can catch the people who bought a pair on a trip and want another.",
["no brand record on two attempts; sheet listing unrelated; industry-level email"],LV),
]
run(raw,emails)
