from batchlib import *
raw={
"Oscar Mayer":RAW(P("Oscar Mayer","Grocery & Gourmet Food","Bacon",1.03,"",False,"",0.984,0.118,3.116,13.49,4.49,67,132511,666026.47,6603538.7),
 S(("Amazon.com",98.405),("Ever Fresh Market",0.406),("Salutem Solutions",0.37),("FoodserviceDirect Inc.",0.234),("Wholebasket",0.188),("Gourmet Market Pantry",0.078)),
 T(("Oscar Mayer Naturally Hardwood Smoked Bacon, 16 oz Pack","B000Q6U3E6",49463.7),("Oscar Mayer Deli Fresh, Oven Roasted Turkey Breast, 16 oz Family Pack","B00408BEEO",42687.86),("Oscar Mayer Hot Dogs, 10 ct Pack, Classic Weiners","B000RYDFFG",38415.15),("Oscar Mayer Gluten Free Fully Cooked Turkey Bacon, 12 oz","B000R4B8NW",35275.5),("Oscar Mayer Deli Lunch Meat, Bologna, 16 oz Package","B00MCLKC4Y",35224.52))),
"FODZYME":RAW(P("FODZYME","Health & Household","Multi-Enzyme Nutritional Supplements",1,"Kiwi Biosciences",True,"https://www.amazon.com/stores/FODZYMEEnzymesforFODMAPs/page/C40CDEFC-DA1E-4BFA-8CF5-4193E05A9FA3",None,0.013,None,75.99,4.3,2,915,600169.02,6604280.13),
 S(("FODZYME",100)),
 T(("FODZYME On-The-Go Digestive Enzymes, 30 Dose","B0BRHZ429S",308443.41),("FODZYME Home Kit Digestive Enzymes, 60 Dose","B0BSP42YHD",291725.61))),
"Sourcebooks, Inc.":RAW(P("Sourcebooks, Inc.","Books","New Adult & College Romance",10.34,"",False,"",0.858,-0.079,-0.91,19.87,4.45,3839,7647398,555275.87,8934516.38),
 S(("Amazon.com",85.754),("Blackstone_Publishing",1.636),("Raghman Traders Ltd",1.159),("LuminaryBooks",0.684),("Shakespeare Book House",0.339),("Corpus Books",0.289)),
 T(("My Calm Down Book: A Sensory Book to Help Kids Calm Their Bodies","1464221561",12449.92),("The Pumpkin Thief (The Leaf Thief)","146426807X",8698.81),("The Complete Off-Campus Series Set","1464221715",5737.55),("Fiske Guide to Colleges 2027","146426287X",4528.49),("Baby University Complete for Babies Board Book Set","1728232309",3781.18))),
"Logo Brands":RAW(P("Logo Brands","Sports & Outdoors","Sports Fan Canopies",1.59,"",True,"https://www.amazon.com/stores/LogoBrands/page/1902AC74-2F73-4171-91DF-D951F7224D52",0.817,0.117,0.768,46.91,4.49,2690,32841,647126.61,7022579.12),
 S(("Amazon.com",81.737),("My Team Outlet (USA Seller)",3.156),("Vagabond Exchange",2.269),("Yard Inflatables Inc",2.007),("Paragon Trading Post",1.77),("Gadgets Experience",1.65)),
 T(("Logo Brands USA Men's National Soccer 40 oz Tumbler with Handle","B0F64HJJ18",32175.5),("Logo Brands NCAA Tennessee Volunteers 7ft Inflatable Yard Mascot","B0C7J9CL3P",13475.7),("Logo Brands NCAA Alabama Crimson Tide 7ft Inflatable Yard Mascot","B0C7J89X1D",12294),("Logo Brands NCAA LSU Tigers 7ft Inflatable Yard Mascot","B0C7J63Q2Z",10430.42),("Logo Brands NCAA Georgia Bulldogs 7ft Inflatable Yard Mascot","B0CXY8PXCQ",9868.38))),
"NUTRICIA PEPTICATE":RAW(P("NUTRICIA PEPTICATE","Baby Products","Powder Baby Formula",0.67,"Amazon.com",True,"https://www.amazon.com/stores/Pepticate/page/20A8D3F2-7B39-49E6-A9D0-0582931EEC62",1,0.316,1.461,222.48,4.6,3,475,537301.4,5738747.68),
 S(("Amazon.com",100)),
 T(("Pepticate Hypoallergenic Infant Formula 0-12 Months 13.2oz 4 Pack","B0CZ7N9BQH",431731.88),("Pepticate Hypoallergenic Infant Formula 0-12 Months 13.2oz","B0CZ7MV2BC",105569.52),("Pepticate Hypoallergenic Infant Formula, 13.2 Ounce (Pack of 12)","B0HH6WRQKX",0))),
"Wild Republic":RAW(P("Wild Republic","Toys & Games","Stuffed Animals & Teddy Bears",2.71,"Amazon.com",True,"https://www.amazon.com/stores/WildRepublic/page/9244E541-6F8D-417C-863A-E4749C8C23AE",0.564,0.019,-0.23,18.1,4.66,847,382563,515642.37,10760072.55),
 S(("Amazon.com",56.368),("Tuckers Toy Shop",35.432),("Express Shipping",2.203),("First In Kites & Toys",0.944),("VirVentures",0.745),("S.C. Goods",0.568)),
 T(("Wild Republic Huggers Bald Eagle Stuffed Animal - 8\"","B01N1A3BUH",8253.46),("Wild Republic Raccoon Plush, Cuddlekins 8 Inches","B00705X85M",7209),("Wild Republic Huggers Orange Tabby Cat Stuffed Animal - 8\"","B01M158UZA",7112.88),("Wild Republic E-Team X Shark Set Playset, 4-Piece Set","B00TV3NHC0",5614.42),("Wild Republic Rooster Plush, Hug'Ems 7 inches","B07BPPW3BG",5527.8))),
"BEN KAUFMAN SALES CO":RAW(P("BEN KAUFMAN SALES CO","Home & Kitchen","Beach Towels",0.82,"Ben Kaufman Sales",True,"https://www.amazon.com/stores/BENKAUFMANSALESCO/page/7346F583-A6AA-4616-83A4-1231B7678D2D",0,-0.192,-0.166,114.33,4.28,285,51955,469795.65,7308749.86),
 S(("Ben Kaufman Sales",100),("Pattern Direct",0)),
 T(("Kaufman - Soft Oversized Beach Towels in Bulk, Velour Striped (4 Pack)","B00HR9WU1O",89935.01),("Ben Kaufman Terry Cabana Striped Towels - 6 Pack","B00QL6D18K",72016.68),("BEN KAUFMAN SALES CO Terry Beach & Pool Towel - Pack of 4","B00MOIF416",35016.64),("Ben Kaufman Joey Velour Multi-Color Stripe Beach & Pool Towel - 4 Pack","B06XRM37FB",33850.9),("Kaufman - Colorful Racing Striped Beach & Pool Towel - 480 Pack","B0CTWDLJ31",30093))),
"ROBOTIME":RAW(P("ROBOTIME","Toys & Games","Toy Kitchen Sets",0.93,"Robotime Online",True,"https://www.amazon.com/stores/ROBOTIMEBuildingThingstoLife/page/1E67245D-2A0F-40CD-94AB-9BEDB4B11AEC",0.323,-0.06,0.082,54.67,4.5,273,29722,466035.66,14052214.93),
 S(("Global Premier Collections",46.997),("Amazon.com",32.334),("Robotime Online",20.289),("Craftime",0.243),("ivaluemart",0.137)),
 T(("ROBOTIME Wooden Dollhouse with 29 Pcs Furniture, 6 Rooms","B0CZJQNRH4",18921),("ROBOTIME Wooden Play Kitchen Set with Cutting Food","B0CLGBP3SX",17419.2),("ROBOTIME Baby Doll Crib, Wooden Doll Bed (Pink)","B0CPHXVZ6R",10958.63),("ROBOTIME Motorized Wooden Puzzles for Adults - Marble Spaceport","B0CYGLVB4P",10284.84),("ROBOTIME Wooden Dollhouse with 24 Pcs Furniture, Pink","B0CP2BXSSH",9572.16))),
"LifeWay":RAW(P("LifeWay","Grocery & Gourmet Food","Kefir",1.07,"Lifeway Christian Resources",True,"https://www.amazon.com/stores/Lifeway/page/205E0490-6E1B-4B68-B379-9C6071FB17EA",0.585,0.099,2.199,28.94,4.3,46,19200,432452.3,3353493.66),
 S(("Amazon.com",58.478),("Whole Foods Market",40.139),("The Keto Storehouse",0.589),("Eternity Essentials",0.32),("Parthenon Foods",0.244),("Cheese Delicatessen",0.127)),
 T(("Lifeway Organic Low Fat Kefir, Plain, 32 Ounce","B000QJC5KI",59196.48),("Lifeway Low Fat Kefir, Plain, 32 oz","B000QJ7CRE",48444.66),("Lifeway Low Fat Kefir, Strawberry, 32 oz","B00LOAW7U6",46017.95),("Lifeway, Kefir Plain Unsweetened Organic, 32 Fl Oz","B013JL49PI",38548.64),("Lifeway Organic Whole Milk Kefir, Mixed Berry, 32 Fl Oz","B01DF1O088",30968.96))),
"Impossible Foods":RAW(P("Impossible Foods","Grocery & Gourmet Food","Frozen Nuggets & Tenders",1.26,"FoodserviceDirect Inc.",True,"https://www.amazon.com/stores/ImpossibleFoods/page/B6C0D5AD-F789-4FA4-811A-785022183923",0.712,0.485,0.314,16.5,4.57,19,13368,429409.71,3777442.58),
 S(("Amazon.com",71.182),("Whole Foods Market",28.564),("RocketDSD",0.253)),
 T(("Impossible, Frozen Chicken Nuggets Plant Based, 13.5 Ounce","B09C15QWT4",102467.55),("Impossible, Frozen Chicken Patties Plant Based, 13.5 Ounce","B09SKZH9TG",53471.82),("Impossible, Burger Patties Meat from Plants, Frozen, 6 Patti, 24 Ounce","B09C15M76H",47260.88),("Impossible Homestyle Plant Based Meatballs, 14 Ounce","B09DFF96K8",44384.93),("Impossible, Burger Patties Grilled, 21.6 Ounce","B0DLBQ7VGC",37910.07))),
"Lazy One":RAW(P("Lazy One","Clothing, Shoes & Jewelry","Men's Pajama Bottoms",1.5,"LazyOne",True,"https://www.amazon.com/stores/LazyOne/page/1DF90DC5-51D9-41E7-9F4E-96992E42C8CA",0,-0.182,-0.307,28.37,4.69,3195,101490,428153.19,15365981.22),
 S(("LazyOne",99.965),("BA&M Gifts",0.03),("Aneka LLC",0.003),("DECORATORS CHOICE",0.003)),
 T(("Lazy One Wearable Hooded Blanket for Kids (Dinosaur)","B06ZYK56MW",20785.83),("Lazy One Men's Pajama Shorts (Bigfoot, L)","B08VFC3W7S",4683.87),("Lazy One Wearable Hooded Blanket for Kids (Bigfoot)","B0DSLYTW3R",3420.82),("Lazy One Men's Pajama Shorts (Bigfoot, XL)","B08VF9GN6V",2440.89),("Lazy One Men's Pajama Shorts (Bigfoot, M)","B08VF995KY",2396.91))),
"The Petting Zoo":RAW(P("The Petting Zoo","Toys & Games","Stuffed Animals & Teddy Bears",1.72,"The Petting Zoo",True,"https://www.amazon.com/stores/ZoologeebyThePettingZoo/page/1A03C591-CE2F-4DD4-B44E-5D9900831DE0",0,0.076,0.161,18.84,4.72,516,36646,388130.71,7014832.01),
 S(("The Petting Zoo",99.771),("Bayside Emporium LLC",0.229)),
 T(("The Petting Zoo Tiger Stuffed Animal Plushie, Wild Onez, 9 in","B0914T3KNM",13214.52),("The Petting Zoo Floppy Horse Stuffed Animal, Wild Onez, 8 in","B0B5KMJML3",13184.24),("The Petting Zoo Lash'z Giraffe Stuffed Animal Plushie, 12 in","B07PF1NRKW",11014.2),("The Petting Zoo Hedgehog Stuffed Animal Plushie, Babiez, 6 in","B0BTMZQ7V9",10159.83),("The Petting Zoo Lion Stuffed Animal Plushie, Babiez, 6 in","B09X6RX16J",9170.82))),
"Jackson's":RAW(P("Jackson's","Grocery & Gourmet Food","Potato Chips & Crisps",1.72,"Jackson's Food Company",True,"https://www.amazon.com/stores/Jacksons/page/0C3BFA19-2613-4D8B-9093-C64A9BA50A60",0,0.01,0.155,28.88,4.42,61,5657,350385.61,4892355.43),
 S(("Jackson's Food Company",70.305),("Jackson's Naturals",17.056),("The Online Grocery Store",9.674),("Whole Foods Market",1.702),("J&C Global Sourcing LLC",0.668),("TheNewMall",0.456)),
 T(("Jackson's Sweet Potato Kettle Chips, Sea Salt, Avocado Oil (1.5oz, 10ct)","B09Z5W82RD",52785.06),("Jackson's Chips, Sea Salt Avocado Oil Sweet Potato Chips, 5 Ounce","B0CXW7WW79",23996.37),("Jackson's Sweet Potato Kettle Chips Variety Pack (1.5oz, 10ct)","B0DX44ZZW1",23255.76),("Jackson's Classic Potato Kettle Chips, Sea Salt (1.5oz, 10ct)","B0DYRF3ZZZ",18177.18),("Jackson's Sweet Potato Kettle Chips, Sea Salt (7oz, 6ct)","B0DYVT62KY",16699.36))),
"Safari Ltd.":RAW(P("Safari Ltd.","Toys & Games","Kids' Play Animal Figures",1.23,"",True,"https://www.amazon.com/stores/SafariLtd/page/7D6A9C94-16AB-4244-A3BD-820E1B9C9DD6",0.001,0.067,-0.02,14.04,4.58,879,114892,341609.28,6404791.8),
 S(("Safari Ltd.",99.134),("Red Parasol",0.262),("Ozone Toys",0.168),("Draben's Toyland",0.115),("Avalanche Brands",0.108),("Amazon.com",0.069)),
 T(("Safari Ltd. Friendly Fairies Super Toob - 12 Miniature Fairy Figurines","B07BYJTP3Z",5623.55),("Safari Ltd. Continental Army Designer TOOB","B006HEIJ1U",3965.52),("Safari Ltd. Knights and Dragons Toob","B000BNC90A",3959.34),("Safari Ltd. USA Super Toob - 12 American Landmark Figures","B00Q6ZFXVO",3886.38),("Safari Ltd. Around the World Toob - 10 Landmark Figurines","B0081GG6KI",3582.61))),
"Panama Jack":RAW(P("Panama Jack","Beauty & Personal Care","Lip Balms & Moisturizers",1.29,"Panama Jack, Inc.",True,"https://www.amazon.com/stores/PanamaJack/page/2F1C88BF-B629-4776-88CC-C92471EA86F6",0.004,-0.325,0.135,42.4,4.54,292,23912,307341.36,4662122.48),
 S(("Panama Jack, Inc.",99.241),("Amazon.com",0.437),("SWIFTCHOICE",0.25),("bestbrandsupply",0.072),("premier liquidations",0)),
 T(("Panama Jack Sunscreen Lip Balm SPF 45, 4 Pack","B08G5YPWR3",37547.7),("Panama Jack Sunscreen Lip Balm SPF 45, 5 Pack","B0CTVK6SVQ",23331),("Mesh Crown Safari Men's Sun Hat, UPF 50+ (Khaki, Large)","B0BVN83ZVX",10137),("Panama Jack Continuous Spray Sunscreen SPF 15, 5.5 OZ (Pack of 12)","B07SY9W6NX",7386.14),("Panama Jack Sunscreen Lip Balm SPF 45","B0CVMFX8NJ",6084.4))),
"Jerzees":RAW(P("Jerzees","Clothing, Shoes & Jewelry","Men's Polo Shirts",7.24,"",True,"https://www.amazon.com/stores/JERZEES/page/2ABFD786-DD4A-42AF-A748-04069EE84A71",0.627,0.244,-0.328,16.32,4.42,1924,191004,306199.54,8889652.01),
 S(("Amazon.com",62.657),("Grit & Garb",13.791),("officialalldayshirts",9.658),("DEALS BIZARRE",3.213),("kiwisota",2.413),("Midnight Dynamics",1.653)),
 T(("Jerzees Men's NuBlend Fleece Hoodie, Black, Large","B00T7U6QXY",4015.79),("Jerzees Mens Dri-Power Long Sleeve T-Shirt, White, Large","B00O2TEYT8",3856.28),("Jerzees Men's Dri-Power Cotton Blend Long Sleeve Tees, Black, Large","B00T7TXS2W",3740.72),("Jerzees Men's Short Sleeve Polo Shirts, Dri-Power, Black, 5X-Large","B0F1Z5XWDL",3668.36),("Jerzees Men's NuBlend Fleece Hoodie, Black, X-Large","B00T7U6R88",3084.84))),
"Rhode Island Novelty":RAW(P("Rhode Island Novelty","Toys & Games","Gags & Practical Joke Toys",5.03,"",True,"https://www.amazon.com/stores/RhodeIslandNovelty/page/E872043F-F0CF-4D77-B5C0-3C23C236B916",0.054,-0.02,-0.036,16.77,4.11,450,206200,287412.81,4876382.08),
 S(("Libros Judios",25.564),("What America Buys",8.079),("Zack's Edu Castle",6.349),("Discount Party and Novelty",5.614),("Amazon.com",5.424),("HeyGem",5.019)),
 T(("Smile Tooth 2 Minute Sand Timer Assorted Colors (2 Pack)","B0155CENLY",10614.66),("Rhode Island Novelty Deluxe Black Magician Butler Formal Costume Top Hat","B002RHPSYM",9872.55),("Rhode Island Novelty 7 Inch x 8 Inch Hollywood Movie Clapboard","B000IT1EEO",9301.28),("Rhode Island Novelty 15-inch Wide Animal Den Brachiosaurus Plush","B0181QGN46",8732),("Rhode Island Novelty Plastic Jewel Rings, 24 Count Assortment","B00629TPG8",6570.95))),
"Spoontiques":RAW(P("Spoontiques","Patio, Lawn & Garden","Stepping Stones",2.41,"",True,"https://www.amazon.com/stores/Spoontiques/page/02DDC05F-48B6-46FA-B106-84C4C9B764C4",0.669,-0.05,-0.018,22.3,4.6,850,118423,277592.63,6357246.95),
 S(("Amazon.com",66.941),("Hour Loop",17.474),("KART IT",4.192),("Spoontiques",2.577),("ReLIVE Life",1.439),("Plush Puppy To Go",1.306)),
 T(("Spoontiques Snoopy Wind Chime - Outdoor Garden Decor","B0DTPDBH2V",19148.8),("Spoontiques Bronze Angel Stepping Stone","B075MJQNXS",9540.81),("Spoontiques Peanuts Eyeglass Case","B0BY81NV9J",4969.44),("Spoontiques Ruby Slippers Stepping Stone - Wizard of Oz","B008JGUQ2Y",4764.85),("Spoontiques Peanuts 40oz Glitter Acrylic Travel Mug","B0DDL5HWN1",4068.15))),
"Mooala":RAW(P("Mooala","Grocery & Gourmet Food","Almond Milks",3.12,"Mooala Brands",True,"https://www.amazon.com/stores/Mooala/page/042603D4-FA5F-4D14-91FB-385707AAFBA4",0.017,0.023,0.363,31.6,4.12,25,3180,238994.17,3046505.08),
 S(("Mooala Brands",78.519),("K2 Peaks",8.791),("Whole Foods Market",3.814),("DEALZ 4 US INC.",2.822),("FKCGL Goods",1.727),("Amazon.com",1.677)),
 T(("Mooala Organic Simple Almond Milk, 32oz, 6 pack","B0CGJ87VQ3",42020.64),("Mooala Organic Simple Oat Milk, 32oz, 6 pack","B0CGJ7PMBG",33291),("Mooala Organic Simple Almond Milk Vanilla, 32oz, 6 pack","B0DJ1NGY3S",30027.76),("Mooala Organic Original Bananamilk, 32 FL Oz (Pack of 6)","B08BJGTJDG",26317.39),("MOOALA Organic Bananamilk, 48 FZ","B078134TSV",13988.64))),
"Painterland Sisters":RAW(P("Painterland Sisters","Grocery & Gourmet Food","Greek & Icelandic Plain Yogurt",1,"",False,"",0.034,0.244,None,5.39,4.76,7,578,227980.76,700828.09),
 S(("Whole Foods Market",96.574),("Amazon.com",3.426)),
 T(("Painterland Sisters, Yogurt Skyr Plain Organic, 24 Ounce","B0CB1S9X8S",94994.31),("Painterland Sisters, Yogurt Skyr Vanilla Bean Organic, 24 Ounce","B0CC3SXM61",49608.86),("Painterland Sisters, Yogurt Icelandic Style SKYR Strawberry Organic, 5.3 Ounce","B0B5VV53FV",22874.8),("Painterland Sisters, Yogurt Skyr Savannahs Peach Organic, 5.3 Ounce","B0CB1QBC6W",22360.26),("Painterland Sisters, Yogurt Icelandic Style Skyr Vanilla Organic, 5.3 Ounce","B0B5VM8Y4Y",19106))),
"KIBOW":RAW(P("KIBOW","Health & Household","Blended Vitamin & Mineral Supplements",0.5,"Kibow Biotech Official Store",True,"https://www.amazon.com/stores/KibowBiotechInc/page/821C77FA-134B-4313-A794-3D9E5C01B18F",0,0.043,0.904,68.22,4.53,4,2245,227412.4,2363376.08),
 S(("Kibow Biotech Official Store",100),("KIBOW",0)),
 T(("Renadyl Probiotic, 180 Capsules (1 Bottle, 1 Month Supply)","B00WA1VNI0",134728.65),("Renadyl Probiotic, 60 Capsules (1 Bottle, 1 Month Supply)","B004G230Q4",92683.75),("KIBOW 10-Pound Pack Reflective Crushed Fire Glass (unrelated brand sharing name)","B07XCTXTN2",0),("KIBOW Propane Quick Connect Fitting (unrelated brand sharing name)","B07BNX2H5S",0))),
"Olyra":RAW(P("Olyra","Grocery & Gourmet Food","Fruit Bars",0.94,"",True,"https://www.amazon.com/stores/OlyraAncientGreekGrains/page/03C5CD43-12D2-4824-B8C5-FDFE34A02693",0.301,0.06,0.516,23.31,4.16,47,2898,226566.79,3169750.71),
 S(("OLYRA FOODS INC",67.812),("Amazon.com",30.147),("Whole Foods Market",1.619),("LawCorpSales",0.15),("iHerb",0.139),("Dorado General Listings",0.126)),
 T(("Olyra Creme Breakfast Biscuits - Dark Chocolate - Pack of 4","B09MQYB3VD",35443.98),("Olyra Fruit Bars Variety Pack (24)","B0FPRF3K7M",31313.12),("Olyra Organic Vanilla Cream Filled Breakfast Biscuit, 5.3 OZ","B0DNNJJDST",20394.22),("Olyra Sandwich Breakfast Biscuits Dark Chocolate (24)","B08HCYLVBN",18803.03),("Olyra Sandwich Breakfast Biscuits: Vanilla (12)","B0FVG2FX5W",15852.07))),
"Kindling":RAW(P("Kindling","Grocery & Gourmet Food","Pretzels",0.95,"",True,"https://www.amazon.com/stores/Kindling/page/CB426275-2173-419A-AEE7-E9EEFC9887B1",0,-0.281,1.84,27.73,4.18,19,1611,183595.53,3395061.28),
 S(("Kindling Snacks",100)),
 T(("Kindling Protein Pretzels, Variety Pack, 12-Pack Variety","B0DMTSDDTV",88600),("Kindling Protein Pretzels, Sea Salt, 1.06oz Bag, 16-Pack","B0DN3H5XY8",32300),("Kindling Protein Pretzels, Churro, 1.06oz Bag","B0FJKH4XQK",13875),("Kindling Protein Pretzels, Honey Mustard, 1.06oz Bag, 16-Pack","B0DN3JFSY4",13750),("Kindling Protein Pretzels, Dill Pickle, 1.06oz Bag, 16-Pack","B0DN34JK4F",11725))),
"Asobu":RAW(P("Asobu","Kitchen & Dining","Water Bottles",1.29,"Asobu Inc.",True,"https://www.amazon.com/stores/Asobu/page/0DB52FED-F1F2-4E87-B2C6-D7A9D111B63F",0.001,-0.293,0.391,32.59,4.4,257,34182,154433.25,2712725.24),
 S(("Asobu Inc.",92.523),("WeRespectMAP",3.517),("Nalmaga",2.268),("Frontier-Deals",0.845),("Triplenet Pricing INC",0.39),("Most Anything",0.109)),
 T(("asobu Bestie Cow Water Bottle","B0F9WYLJX9",7767.9),("asobu Bestie Water Bottle, Leak Proof","B0CCLMN93C",4355.38),("asobu Bestie Bunny Water Bottle","B0CCLMZ885",4031.91),("asobu Bestie Duck Water Bottle","B0F9X19GFP",4031.91),("asobu Bestie Water Bottle, Leak Proof","B0CP5HM9T3",3994.92))),
"American Classics":RAW(P("American Classics","Clothing, Shoes & Jewelry","Men's Novelty T-Shirts",1.68,"2Bhip",True,"https://www.amazon.com/stores/AmericanClassics/page/0A17B4B1-F129-488B-B23A-8223EF013C2A",0,-0.081,-0.287,29.67,4.63,348,21357,144612.9,2139025.4),
 S(("2Bhip",100)),
 T(("American Classics Def Leppard Hysteria 1988 Tour T Shirt White LG","B07P14CPJY",6159.44),("American Classics Weezer Band Photo Vintage Style Graphic T Shirt MD","B09KYG1NGS",5647.46),("American Classics Def Leppard Pyromania Tour 1983 T Shirt Natural XL","B07G8PKQM9",3256.5),("American Classics Misfits Skull Crossed Arms T Shirt Natural LG","B0C3K5QZG4",3102.45),("American Classics Alice in Chains Rooster Graphic T Shirt Navy Heather LG","B0DMTLG49Y",3023.88))),
}
FN="Saw that {b} exhibited at FNCE last year."
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
H="Hi {{first_name}},"
emails=[
E(25,"FNCE 2025|Oscar Mayer","Oscar Mayer","Amazon 1P ~98%, no brand store flagged; large CPG, narrow content/brand store angle","Amazon 1P 98.4%; monthly rev ~$666k; Has Storefront false; 12M MoM +312%","Oscar Mayer's Amazon brand presence",f"""{H}

{FN.format(b='Oscar Mayer')}

From what we can see, Oscar Mayer does roughly $650k a month on Amazon, essentially all of it through Amazon as the vendor, with bacon, Deli Fresh turkey and hot dogs at the top. Growth over the last year looks strong, but we don't see a brand store on the listings, and with 1P only, content, pricing and which SKUs stay in stock are decided on Amazon's side.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would a 20 minute look at the brand store and content side be worth your time?

Yoni""",qa=["large CPG brand (Kraft Heinz); narrow ask used"]),
E(26,"FNCE 2025|Kiwi Biosciences (FODZYME)","FODZYME","Strong brand direct on two listings; thin review base at a high price point","Brand direct 100%; monthly rev ~$600k; 2 products; 915 reviews; avg price ~$76","FODZYME's two listings on Amazon",f"""{H}

{FN.format(b='Kiwi Biosciences')}

From what we can see, FODZYME is doing roughly $600k a month on Amazon off just two listings, sold direct, at about $75 a unit. That is a strong base for two products. The whole channel sits on under 1,000 reviews though, and at that price point the review count and the content on the page do most of the convincing.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Open to a short call on the review and Subscribe & Save side?

Yoni""",qa=["profile pulled via query_analytics fallback; Amazon 1P % and 12M growth not returned by that query"]),
E(27,"Las Vegas Souvenir & Resort Gift Show 2026|Sourcebooks","Sourcebooks, Inc.","Publisher: Amazon 1P ~86% across 3,800 titles; ads, A+ and gift-season stock sit on the publisher side","Amazon 1P 85.8%; 3,839 products; monthly rev ~$555k; 12M MoM -91%","Sourcebooks gift titles on Amazon",f"""{H}

{LV}

Looking at Sourcebooks titles on Amazon, we see somewhere around $550k a month across roughly 3,800 listings, with about 85% sold by Amazon itself. That is normal for a publisher, but the levers a brand would usually pull, sponsored ads on the top titles, A+ content and keeping gift-driven books like the sensory board books in stock ahead of Q4, sit on the publisher's side, not Amazon's.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a short call on the gift and kids titles specifically?

Yoni""",qa=["book publisher, weaker fit for consumer brand pitch"]),
E(28,"Las Vegas Souvenir & Resort Gift Show 2026|Logo Brands","Logo Brands","Amazon 1P ~82% with ~18% spread across several third-party sellers carrying 100+ listings each","Amazon 1P 81.7%; reseller share ~18% (My Team Outlet 3.2%, Vagabond Exchange 2.3%); 2,690 products; monthly rev ~$647k; 12M MoM +77%","Logo Brands seller mix on Amazon",f"""{H}

{LV}

From what we can see, Logo Brands does roughly $650k a month on Amazon across a catalog of about 2,700 licensed listings, and growth over the last year looks strong. About 80% runs through Amazon as the vendor. The other 20% or so is spread over a handful of third-party sellers like My Team Outlet and Vagabond Exchange, each carrying 100 plus of your listings at their own prices.

We manage Amazon for brands end to end, including hybrid 1P/3P setups and pricing control.

Would a 20 minute look at the seller side be worth your time?

Yoni"""),
E(29,"FNCE 2025|Nutricia North America","NUTRICIA PEPTICATE","Pepticate line: Amazon 1P 100%, two active listings, thin reviews at a $200+ price point","Amazon 1P 100%; monthly rev ~$537k; 3 products (2 active); 475 reviews; avg price ~$222; 12M MoM +146%","Pepticate on Amazon",f"""{H}

{FN.format(b='Nutricia North America')}

Looking at your listings, the Pepticate line is doing roughly $540k a month on Amazon, entirely through Amazon as the vendor, and growing fast over the last year. It is essentially two listings and under 500 reviews, which for a $200 plus hypoallergenic formula is thin, and with 1P only the content, pricing and stock decisions sit with Amazon.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations, in 1P, 3P or hybrid setups.

Would a 20 minute conversation about the medical nutrition range on Amazon make sense?

Yoni""",qa=["SmartScout brand record covers the Pepticate line only, not all Nutricia products"]),
E(30,"Las Vegas Souvenir & Resort Gift Show 2026|Wild Republic / K&M International, Inc.","Wild Republic","One third-party seller (Tuckers Toy Shop) holds ~35%; Amazon 1P ~56%; negative 12-month trend","Tuckers Toy Shop 35.4% on 513 offers; Amazon 1P 56.4%; monthly rev ~$516k; 12M MoM -23%; 382k reviews","Wild Republic reseller share on Amazon",f"""{H}

{LV}

From what we can see, Wild Republic does roughly $500k a month on Amazon, and about 35% of it is sold by one third-party seller, Tuckers Toy Shop, across 500 plus of your listings. Amazon itself is the other 55% or so, and the trend over the last 12 months is down. So a large piece of pricing and Buy Box on a catalog with nearly 400,000 reviews is in a reseller's hands.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a 20 minute look at the seller side?

Yoni"""),
E(31,"Las Vegas Souvenir & Resort Gift Show 2026|Ben Kaufman Sales","BEN KAUFMAN SALES CO","Brand direct, large review base, declining 12-month and last-month trend; under-worked channel","Brand direct 100%; monthly rev ~$470k; 51,955 reviews; 12M MoM -16.6%; MoM -19.2%","Kaufman's Amazon trend",f"""{H}

{LV}

From what we can see, Kaufman does roughly $470k a month on Amazon, all sold direct, with about 50,000 reviews across the towel catalog. The trend over the last 12 months is down though, and last month was down again. With a review base like that, a slide usually comes from ads, content and inventory not being worked hard enough, not from the product.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations. We helped MouthWatchers grow from roughly $40K a month to $1M a month.

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["Ben Kaufman Sales"]),
E(32,"Las Vegas Souvenir & Resort Gift Show 2026|Robotime LLC","ROBOTIME","Third-party seller (Global Premier Collections) holds ~47%; brand's own account only ~20%; Amazon 1P ~32%","Global Premier Collections 47.0% on 116 offers; Amazon 32.3%; Robotime Online 20.3%; monthly rev ~$466k","Who is selling Robotime on Amazon",f"""{H}

{LV}

Looking at your listings, Robotime does roughly $470k a month on Amazon, but your own Robotime Online account is only about 20% of it. Nearly half is sold by a third-party seller, Global Premier Collections, across 100 plus listings, and about a third is Amazon as the vendor. That means three different sellers setting prices on the same dollhouses and kitchen sets.

We manage Amazon for brands end to end, including hybrid 1P/3P setups decided at the product level.

Would a 20 minute conversation on consolidating that be worth your time?

Yoni""",brand_sellers=["Robotime Online"]),
E(33,"FNCE 2025|Lifeway Foods","LifeWay","Refrigerated brand sold only via Amazon 1P and Whole Foods; no brand seller layer","Amazon 1P 58.5%; Whole Foods Market 40.1%; brand direct 0%; monthly rev ~$432k; 12M MoM +220%","Lifeway kefir on Amazon",f"""{H}

{FN.format(b='Lifeway')}

From what we can see, Lifeway kefir does roughly $430k a month on Amazon, split between Amazon as the vendor and Whole Foods Market's Amazon storefront, and growth over the last year has been strong. For a refrigerated product that mix makes sense. What we don't see is a brand layer on top of it, meaning a Lifeway seller account, which is usually where the content and advertising on the 32 oz plain and strawberry get owned.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would a 20 minute look at the content and advertising side be worth your time?

Yoni""",qa=["SmartScout 'Single Seller Name' shows unrelated Lifeway Christian Resources; ignored"]),
E(34,"FNCE 2025|Impossible Foods","Impossible Foods","Frozen brand on Amazon 1P (~71%) and Whole Foods (~29%); vendor-side management angle","Amazon 1P 71.2%; Whole Foods Market 28.6%; 19 products; monthly rev ~$429k; 12M MoM +31%","Impossible Foods vendor side on Amazon",f"""{H}

{FN.format(b='Impossible Foods')}

Looking at your listings, Impossible does roughly $430k a month on Amazon, about 70% through Amazon as the vendor and the rest through Whole Foods Market's Amazon storefront, with the nuggets as the clear leader. Growth over the last year looks solid. With 19 listings and no seller layer, the content, ads and which SKUs Amazon keeps buying are the main things left to manage.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations, and we handle the vendor side too, from forecasting to chargebacks.

Would a 20 minute conversation on the vendor side be worth your time?

Yoni""",qa=["products pulled via query_analytics fallback"]),
E(35,"Las Vegas Souvenir & Resort Gift Show 2026|LazyOne","Lazy One","Brand direct with huge catalog and reviews but declining trend; under-managed catalog","Brand direct 100%; 3,195 products; 101,490 reviews; avg rating 4.69; monthly rev ~$428k; 12M MoM -31%; MoM -18%","LazyOne's Amazon trend",f"""{H}

{LV}

From what we can see, LazyOne does roughly $430k a month on Amazon, sold direct, across about 3,200 listings with over 100,000 reviews and a 4.7 rating. The trend over the last 12 months is down though, and the top seller is the kids hooded blanket rather than the pajamas the brand is known for. That usually means a big catalog running on its own without ads, content or inventory being actively managed.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would it make sense to have a quick conversation before Q4?

Yoni"""),
E(36,"Las Vegas Souvenir & Resort Gift Show 2026|The Petting Zoo dba Zoologee","The Petting Zoo","Steady brand direct with a 500-listing catalog; revenue flattens fast after the top plush","Brand direct 99.8%; 516 products; monthly rev ~$388k; top ASINs ~$9k to $13k/mo; avg rating 4.72; 12M MoM +16%","The Petting Zoo catalog on Amazon",f"""{H}

{LV}

From what we can see, The Petting Zoo does roughly $390k a month on Amazon, all sold direct, across about 500 listings with a 4.7 average rating and steady growth over the last year. The top plush each do around $10k to $13k a month, and it flattens out quickly after that, which is typical for a catalog where only a few listings get ads and content attention.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Open to a short call on getting more out of the catalog ahead of Q4?

Yoni"""),
E(37,"FNCE 2025|Jackson's","Jackson's","Volume shifted between two brand seller accounts last month; a third-party seller picking up ~10%","Jackson's Food Company 70.3% (MoM +70 pts); Jackson's Naturals 17.1% (MoM -79 pts); The Online Grocery Store 9.7%; monthly rev ~$350k","Jackson's seller accounts on Amazon",f"""{H}

{FN.format(b="Jackson's")}

Looking at your listings, Jackson's does roughly $350k a month on Amazon and has grown well over the last year. Two things stand out: the volume moved almost entirely from one Jackson's seller account to another last month, and a third-party seller, The Online Grocery Store, is picking up close to 10% of the sales. Account moves like that are exactly when reviews, rank and Buy Box get lost if the transition isn't managed closely.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["Jackson's Food Company","Jackson's Naturals"]),
E(38,"Las Vegas Souvenir & Resort Gift Show 2026|Safari Ltd.","Safari Ltd.","Brand direct, flat growth, revenue spread thin across ~900 listings with big review base","Brand direct 99.1%; 879 products; 114,892 reviews; monthly rev ~$342k; top ASIN ~$5.6k/mo; 12M MoM -2%","Safari Ltd catalog on Amazon",f"""{H}

{LV}

From what we can see, Safari Ltd does roughly $340k a month on Amazon, sold direct, across nearly 900 listings with over 100,000 reviews. Growth over the last 12 months is flat, and no single listing does more than about $6k a month, so the revenue is spread thin across the whole catalog. That is usually a sign the Toobs and figures are selling on brand recognition rather than on ads, content or any real merchandising.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Is it worth a short call on getting more out of the catalog?

Yoni"""),
E(39,"Las Vegas Souvenir & Resort Gift Show 2026|Gulf Coast Panama Jack","Panama Jack","Brand direct sun care with strong lip balm leaders; sharp seasonal drop last month; off-season plan angle","Brand direct 99.2%; monthly rev ~$307k; MoM -32.5%; 12M MoM +13.5%; top ASIN lip balm 4 pack ~$38k/mo","Panama Jack's off-season on Amazon",f"""{H}

{LV}

From what we can see, Panama Jack does roughly $300k a month on Amazon, sold direct, with the SPF lip balm multipacks as the clear leaders and growth over the last year in the low double digits. Last month was down about a third, which for sun care is the seasonal drop, and it is usually the point where ad budgets and inventory get pulled back too far and the listings lose rank going into the next season.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a short call on the off-season plan?

Yoni""",brand_sellers=["Panama Jack, Inc."],qa=["exhibitor is Gulf Coast Panama Jack (likely licensee); SmartScout data is the Panama Jack brand overall"]),
E(40,"Las Vegas Souvenir & Resort Gift Show 2026|Jerzees","Jerzees","Third-party resellers ~37% (Grit & Garb, officialalldayshirts) with Amazon 1P ~63%; declining trend","Amazon 1P 62.7%; Grit & Garb 13.8%; officialalldayshirts 9.7%; reseller share ~37%; monthly rev ~$306k; 12M MoM -33%; 191k reviews","Jerzees third-party sellers on Amazon",f"""{H}

{LV}

Looking at Jerzees listings on Amazon, roughly $300k a month, about 60% is sold by Amazon as the vendor and close to 40% by third-party sellers like Grit & Garb and officialalldayshirts, each carrying hundreds of your SKUs at their own prices. The trend over the last 12 months is down, and with nearly 200,000 reviews on the catalog that is a lot of brand equity being traded on by resellers.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Open to a 20 minute look at the reseller side?

Yoni""",qa=["Jerzees is a Fruit of the Loom brand"]),
E(41,"Las Vegas Souvenir & Resort Gift Show 2026|Rhode Island Novelty / Adventure Planet","Rhode Island Novelty","No brand seller account; ~95% via third-party resellers (Libros Judios 26%); Amazon 1P ~5%","Libros Judios 25.6%; What America Buys 8.1%; Amazon 5.4%; brand direct 0%; monthly rev ~$287k; 206k reviews","Who is selling Rhode Island Novelty on Amazon",f"""{H}

{LV}

From what we can see, Rhode Island Novelty products do roughly $290k a month on Amazon, but we don't see a Rhode Island Novelty seller account in the mix at all. The biggest seller is a third party called Libros Judios at about a quarter of the volume, followed by a string of other resellers, and Amazon itself is only around 5%. With over 200,000 reviews on the catalog, that is a brand asset being run entirely by other people.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would it make sense to have a quick conversation about taking that back?

Yoni""",qa=["exhibitor also lists Adventure Planet; only Rhode Island Novelty queried"]),
E(42,"Las Vegas Souvenir & Resort Gift Show 2026|Spoontiques, Inc.","Spoontiques","Amazon 1P ~67% plus a reseller (Hour Loop) at ~17%; brand's own account under 3%","Amazon 1P 66.9%; Hour Loop 17.5% on 370 offers; Spoontiques seller 2.6%; reseller share ~30%; monthly rev ~$278k; 118k reviews","Spoontiques seller mix on Amazon",f"""{H}

{LV}

Looking at your listings, Spoontiques does roughly $280k a month on Amazon, about two thirds through Amazon as the vendor, and your own seller account is under 3% of it. A third-party seller, Hour Loop, is carrying close to 20% across 370 of your listings. Growth over the last 12 months is flat.

So on a catalog with nearly 120,000 reviews, pricing and Buy Box on a big slice of the licensed items are decided by Amazon and a reseller, not by you.

We manage Amazon for brands end to end, including hybrid 1P/3P setups decided at the product level.

Open to a 20 minute look at the seller side?

Yoni"""),
E(43,"FNCE 2025|Mooala Brands","Mooala","Growing brand direct with ~20% now leaking to third-party sellers; K2 Peaks jumped to ~9% on one listing","Mooala Brands 78.5%; K2 Peaks 8.8% (MoM +8.8 pts, 1 offer); reseller share ~20%; monthly rev ~$239k; 12M MoM +36%","Mooala third-party sellers on Amazon",f"""{H}

{FN.format(b='Mooala')}

From what we can see, Mooala does roughly $240k a month on Amazon, mostly through your own account, and has grown well over the last year. What stands out is that about 20% of the volume is now going through third-party sellers, and one of them, K2 Peaks, went from nothing to nearly 9% last month on a single listing. That is usually worth looking into before it starts pulling your price down on your own almond milk.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["Mooala Brands"]),
E(44,"FNCE 2025|Painterland Sisters","Painterland Sisters","Sold almost entirely via Whole Foods on Amazon; no brand store, thin reviews; build the brand side","Whole Foods Market 96.6%; Amazon 3.4%; 7 products; 578 reviews; avg rating 4.76; monthly rev ~$228k; Has Storefront false","Painterland Sisters on Amazon",f"""{H}

{FN.format(b='Painterland Sisters')}

Looking at your listings, Painterland Sisters is doing roughly $230k a month on Amazon, nearly all of it through Whole Foods Market's Amazon storefront, with the 24 oz plain skyr on its own at close to $100k. The reviews are excellent, a 4.8 average, but there are under 600 of them across seven listings and we don't see a brand store, so the products are found through Whole Foods rather than through the brand.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would a 20 minute conversation about building the brand side on Amazon be worth your time?

Yoni"""),
E(45,"FNCE 2025|Kibow Biotech LLC","KIBOW","Strong growing brand direct on two Renadyl listings at a high price; Subscribe & Save and content angle","Brand direct 100%; monthly rev ~$227k; Renadyl 180ct ~$135k/mo + 60ct ~$93k/mo; avg price ~$68; 12M MoM +90%","Renadyl on Amazon",f"""{H}

{FN.format(b='Kibow Biotech')}

From what we can see, Renadyl is doing roughly $230k a month on Amazon off two listings, sold direct through your own store, and growth over the last year looks strong. At about $70 a bottle for a monthly supply, the obvious next questions are how much of that is on Subscribe & Save, how the kidney health search terms are being defended, and whether the listing content is doing the clinical story justice.

We help brands build and grow their Amazon business, managing everything from strategy and setup through content, advertising, inventory and day-to-day operations.

Open to a short call to compare notes on it?

Yoni""",brand_sellers=["Kibow Biotech Official Store"],qa=["SmartScout KIBOW brand record also contains two unrelated fire-pit products with $0 revenue"]),
E(46,"FNCE 2025|Olyra","Olyra","Hybrid brand direct (~68%) and Amazon 1P (~30%), growing; weak review base and sub-4.2 rating","OLYRA FOODS INC 67.8%; Amazon 30.1%; 47 products; 2,898 reviews; avg rating 4.16; monthly rev ~$227k; 12M MoM +52%","Olyra reviews and ratings on Amazon",f"""{H}

{FN.format(b='Olyra')}

From what we can see, Olyra does roughly $230k a month on Amazon, about two thirds through your own account and a third through Amazon as the vendor, and growth over the last year looks strong. Running both is the right setup when it's deliberate. The thing I'd look at first is the review side: under 3,000 reviews across 47 listings and an average rating just over 4, which is low for breakfast biscuits and will cap what ads can do.

We manage Amazon for brands end to end, including hybrid 1P/3P setups at the product level.

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["OLYRA FOODS INC"]),
E(47,"FNCE 2025|Kindling Snacks","Kindling","Fast-growing brand direct that dropped ~28% last month; thin reviews and sub-4.2 rating","Brand direct 100%; monthly rev ~$184k; MoM -28%; 12M MoM +184%; 1,611 reviews; avg rating 4.18; variety pack ~$89k/mo","Kindling's next stage on Amazon",f"""{H}

{FN.format(b='Kindling')}

From what we can see, Kindling is doing roughly $180k a month on Amazon, all sold direct, with the variety pack at about half of it, and growth over the last year has been steep. Last month dropped close to 30% though, and the catalog sits on about 1,600 reviews with an average rating just over 4. Fast-growing protein snacks usually hit exactly this point, where ads got it to a level and rank, reviews and inventory have to carry it from here.

We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution.

Open to a short call on it?

Yoni""",brand_sellers=["Kindling Snacks"]),
E(48,"Las Vegas Souvenir & Resort Gift Show 2026|ASOBU","Asobu","Brand direct with a 250-listing catalog spread thin; no hero listing, last month down ~29%","Asobu Inc. 92.5%; 257 products; 34,182 reviews; monthly rev ~$154k; top ASIN ~$7.8k/mo; MoM -29%; 12M MoM +39%","Asobu's hero listings on Amazon",f"""{H}

{LV}

From what we can see, Asobu does roughly $150k a month on Amazon, mostly through your own account, across about 250 listings with 34,000 reviews. The Bestie character bottles lead, but no single listing does more than about $8k a month, and last month was down close to 30%. With that many SKUs, the revenue tends to spread thin unless a few hero listings get real ad and content investment.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Is it worth a short call on where to concentrate ahead of Q4?

Yoni""",brand_sellers=["Asobu Inc."]),
E(49,"Las Vegas Souvenir & Resort Gift Show 2026|American Classics, Inc","American Classics","Single seller account (2Bhip), declining 12-month trend, low revenue per listing on licensed tees","2Bhip 100% (treated as brand's own account); 348 products; monthly rev ~$145k; 12M MoM -29%; top ASINs ~$5k to $6k/mo; avg rating 4.63","American Classics' Amazon trend",f"""{H}

{LV}

From what we can see, American Classics does roughly $145k a month on Amazon through a single seller account, across about 350 band tee listings with a 4.6 average rating. The trend over the last 12 months is down, and the top listings, the Def Leppard and Weezer tees, each do only around $5k to $6k a month. Licensed music apparel on Amazon tends to be won on search and content, and it looks like the catalog is coasting.

We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations.

Would it make sense to have a quick conversation?

Yoni""",brand_sellers=["2Bhip"],qa=["seller '2Bhip' (327 offers, 100%) assumed to be American Classics' own account; verify"]),
]
run(raw,emails)
