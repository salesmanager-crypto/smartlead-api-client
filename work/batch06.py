from batchlib import *
raw={
"JUST MADE":RAW(P("JUST MADE","Grocery & Gourmet Food","Fruit Juice Beverages",0.33,"",False,"",None,0,None,27.99,4.8,3,42,449.9,8773.53),
 S(("Just Made Foods",100)),
 T(("JUST MADE JUICE Pineapple Ginger Juice, 11.8 FZ","B0CPQ95VYB",449.9),("JUST MADE JUICE Mango Moringa Juice, 11.8 FZ","B07QDPBZDW",0),("JUST MADE | JUST TOWELS Disposable Face Towel, 60 Count","B09ZLXNNDS",0))),
"Joe Blow":RAW(P("Joe Blow","Automotive","Automotive Interior Safety Products",2.63,"",False,"",0,-1,None,26.1,4.75,8,865,428.79,4679.05),
 S(("SR1 Performance USA",75.121),("Zentra, LLC",12.3),("CycleServe Store",8.976),("TIS CA",3.603),("GoodSpeedUSA",0)),
 T(("Joe Blow GM Chevy Truck Dealer Scene 67-72 Adult T-Shirt, X-Large","B01B0WUHDG",374.85),("Joe Blow T's Chevy Chevelle, Camaro, Nova & Impala Muscle Car T-Shirt, XX-Large","B01KYN12S6",27.99),("Chevy Chevelle, Camaro, Nova & Impala Muscle Car T-Shirt, X-Large","B01KYN10JC",25.95),("Joe Blow GM Chevy Truck Dealer Scene 67-72 Adult T-Shirt, Medium","B01B0WUNB2",0),("Joe Blow T's Chevy Muscle Car T-Shirt, Small","B01LEF3Z74",0))),
"Capsmith":RAW(P("Capsmith","Sports & Outdoors","Sports Fan Skullies & Beanies",3.33,"",False,"",0,0.781,None,18.93,4.53,3,259,418.02,18548.79),
 S(("Zentra, LLC",57.241),("Vagabond Joes 2",26.929),("Lunch money",15.829)),
 T(("Blue Officially Licensed US USN Navy Eagle Embroidered Beanie","B0784GVM26",216.3),("Danbanna Deluxe Black Orange Just Ride Eagle Head Wrap Cap","B07FBM2G6W",122.16),("Capsmith Black Gold US USMC Marines Licensed Cuff Watch Cap Beanie","B074W6VBX9",79.56))),
"The Bear Factory":RAW(P("The Bear Factory","Toys & Games","Stuffed Animal Clothing",0.67,"",False,"",0,0.454,-0.364,15.18,4.57,3,275,321.12,18994.44),
 S(("GetHyped USA",66.231),("ZTRONWARD",33.769),("The Zoo Factory",0)),
 T(("Construction Worker with Hard Hat Outfit Teddy Bear Clothes by Bear Factory","B00OVJ0GW8",321.12),("Blue Jean Shorts Teddy Bear Clothes Fit 14\" - 18\"","B007RHLYWC",0),("The Bear Factory Cowboy Outfit for 15 Thru 19 inch Animals & Dolls","B005DLFNCQ",0))),
"Sona Enterprises":RAW(P("Sona Enterprises","Tools & Home Improvement","Pin Punches",3,"",False,"",0,None,None,17.47,4.1,2,333,244.58,2142.77),
 S(("Buy Sharp Eye",100)),
 T(("SE 18-Piece Drive Pin Punch Set - ST3018","B000ZEABGO",181.65),("SE Drive Pin Punches - Set of 4 Pcs - ST1023I","B00C1MEANI",62.93))),
"Green Tree Jewelry":RAW(P("Green Tree Jewelry","Toys & Games","Women's Drop & Dangle Earrings",2,"",False,"",0,None,None,15.84,4.6,1,118,205.92,4252.52),
 S(("Zentra, LLC",50.471),("Artisan Owl",49.529)),
 T(("Puerto Rican Flag Earrings","B08SQQJ49S",205.92))),
"Whitney Howard Designs":RAW(P("Whitney Howard Designs","Home & Kitchen","Decorative Hanging Ornaments",2.07,"",False,"",0,None,None,17.32,4.43,15,155,169.91,7168.93),
 S(("Whitney Howard Designs",94.621),("Hour Loop",5.379)),
 T(("Whitney Howard Designs Memorial Ornament, Double Sided Pewter","B0FVGK6979",79.96),("Whitney Howard Designs Music Christmas Ornament","B07XYH2PYW",59.97),("Whitney Howard Designs Forever in My Heart Pet Sympathy Gift","B0B1GRQ7G6",14.99),("Whitney Howard Designs in Loving Memory Pet Memorial Gift","B0B1FQZGJF",14.99),("Whitney Howard Designs Peace on Earth Christmas Ornament","B07J3RV4X8",0))),
"ZOOCCHINI":RAW(P("ZOOCCHINI","Health & Household","Baby Boys' Leggings",1.06,"Listr",False,"",0,-0.718,None,21.48,4.39,18,513,130.71,13345.45),
 S(("Zoocchini",100)),
 T(("ZOOCCHINI Toddler 3-Pack Potty Training Pants, Ocean Friends, 3T-4T","B016L7LRVG",32.99),("ZOOCCHINI Grip+Easy Comfort Crawler Legging & Socks Set (12-18 Months, Bosley the Bear)","B07H7BSSTR",19.99),("ZOOCCHINI Baby/Toddler Crawling Pants, 6-12 Months, Sherman The Shark","B0777RZ8G6",19.99),("ZOOCCHINI Baby/Toddler Crawling Pants, 12-18 Months, Allie The Alicorn","B0777RCHTY",19.99),("ZOOCCHINI Baby/Toddler Crawling Pants, 12-18 Months, Fiona The Fawn","B07H7CK5JM",19.99))),
"Blank Tag Co.":RAW({"Brand Name":"Blank Tag Co.","Primary Category":"Office Products","Primary Subcategory":"Kids' Stickers","Total Monthly Revenue":74.97,"Total Products":1,"_note":"profile query returned empty; fields from seller and product queries"},
 S(("Blank Tag, LLC.",100)),
 T(("Strawberry Shortcake 5-Pack Sticker Bundle - Waterproof Stickers","B0DSXVNW2L",74.97))),
"Rextooth Studios":RAW(P("Rextooth Studios","Books","Children's Comics & Graphic Novels",4,"",False,"",0,-1,None,19.95,4.6,1,26,59.85,159.6),
 S(("Rextooth Studios",100)),
 T(("End of the Ice Age","159152220X",59.85))),
"East View Map Link":RAW(P("East View Map Link","Electronics","Fishing Charts & Maps",1,"",False,"",0,0,None,24.48,5,1,2,48.96,3038.91),
 S(("East View Map Link",100)),
 T(("NOAA Chart 25641 Virgin Islands by East View Geospatial","B011W87NE4",48.96))),
"Squire Boone Village":RAW(P("Squire Boone Village","Toys & Games","Kids' Play Dinosaur & Prehistoric Creature Figures",1,"",False,"",0,-0.102,None,3.9,3.83,3,124,46.8,2995.09),
 S(("ToyWiz",95.726),("CJ Linked Inc",4.274)),
 T(("Squire Boone Village Junior Megasaur Mystery Egg","B08K711GG3",46.8),("Childrens Orange Construction Lighted Miner Hard Hat","B00B7LVU5U",0),("Childrens Construction Lighted Miner Hard Hat Bright Blue","B00LPTPCJY",0))),
"Little Critterz":RAW(P("Little Critterz","Home & Kitchen","Collectible Figurines",2,"",False,"",0,None,None,12.99,4.8,1,58,38.97,77.94),
 S(("Little Critterz",100)),
 T(("Little Critterz Tuxedo Kitten Porcelain Figurine Chessie","B00689GCI6",38.97))),
"Something Wild":RAW(P("Something Wild","Books","Children's Zoo Books",1,"",False,"",1,None,None,10.97,5,1,23,32.91,228.86),
 S(("Amazon.com",100)),
 T(("Something Wild children's zoo book (single title)","",32.91))),
"Bicast":RAW({"Brand Name":"Bicast","Primary Category":"Office Products","Primary Subcategory":"Wall Calendars","Total Monthly Revenue":0,"Total Products":3,"_note":"profile query failed twice; sellers empty; products show 2024 calendars with $0 revenue"},
 [],
 T(("2024 Outer Banks 14 Month Calendar (12 x 12)","B0CCPNHK7T",0),("2024 Outer Banks 14 Month Calendar (8 x 10)","B0CCPP1883",0),("2024 Williamsburg, Jamestown & Yorktown 14 Month Calendar","B0CCPLYPQP",0))),
"Spin Copter":RAW(P("Spin Copter","Industrial & Scientific","Unmanned Aerial Vehicles (UAVs)",0,"",False,"",0,None,None,30.87,4.5,1,11,0,50.02),
 S(("Rojay Party",0)),
 T(("LED Spincopter (5)","B07QP7YG8S",0))),
"Sunlight Art":RAW(P("Sunlight Art","Patio, Lawn & Garden","Garden Suncatchers",1,"",False,"",0,None,None,12.75,4.5,1,2,0,0),
 S(("The Performers Collection",0)),
 T(("Sunlight Art Two Blue and Black Hummingbirds Suncatcher Window Panel","B0C9WGL2N6",0))),
"TELL INDUSTRIES":RAW(P("TELL INDUSTRIES","Arts, Crafts & Sewing","Craft & Sewing Supplies Storage",0,"Tell Industries LLC",False,"",0,None,None,34.99,4.5,2,27,0,0),
 [],
 T(("TELL INDUSTRIES 129 oz Hexagon Wide Mouth Plastic Storage Container with Lid (1)","B0CCK4582F",0),("TELL INDUSTRIES 129 oz Hexagon Plastic Storage Container with Lid (4)","B0CCK565PD",0))),
"Awlgrip":RAW(P("Awlgrip","Sports & Outdoors","Boat Painting Supplies",8.38,"",False,"",0,-0.215,None,80.69,4.62,21,505,18945.24,252116.84),
 S(("Merritt Supply",52.071),("Boats & More",39.799),("Atlantic Boat Supply",5.337),("Autoplicity",1.399),("Island Marine",0.74),("HARVARD MARINE",0.543)),
 T(("Awlgrip Awlcat #3 Brush Top Coat Converter, Pint","B000N9O9NM",2966.25),("Awlgrip 545 Epoxy Primer Converter Gallon","B000N9RLUU",1909.7),("Awlgrip Awlcare Polymer Sealer, 1/2 Gallon","B002IZHHA6",1815.75),("Awlgrip Awlcat #3 Brush Top Coat Converter, 1/2 Gallon","B002IZHGIO",1559.94),("Awlgrip AWLWASH Wash Down Concentrate","B000N9RL2S",1505.94))),
"BLUEWING":RAW(P("BLUEWING","Sports & Outdoors","Fishing Sinkers & Weights",1.18,"Uniprime Outdoors",True,"",0,0.029,None,65.24,4.62,1213,4754,366672.36,3647641.29),
 S(("Uniprime Outdoors",100)),
 T(("BLUEWING 2-Pack V4 Upgraded Sunshade Support Pole for Fishing Boats","B0G38F5BCJ",12643.8),("BLUEWING Hollow Spectra Threading Splicing Needles Kit 23pcs","B0F8QD4GXL",6239.52),("BLUEWING 12ft Heavy Duty Carbon Fiber Fishing Gaff","B0CQC5RDYM",4499.91),("BLUEWING Monofilament Fishing Line 80 lbs 500 Yards","B0BKFXXKK5",4417.79),("BLUEWING 10ft Heavy Duty Carbon Fiber Fishing Gaff","B0CQCH9G2G",3601.62))),
"BOTE":RAW(P("BOTE","Sports & Outdoors","Stand-Up Paddleboards",0.66,"BOTE",False,"",0,-0.578,None,459.83,4.44,169,1375,258322.38,3509115.17),
 S(("BOTE",100)),
 T(("BOTE WULF Aero 11'4\" Inflatable Paddle Board","B0GL9NRVBZ",34779.5),("BOTE WULF Aero 10'4\" Inflatable Paddle Board","B0GL9NGWXN",32255.6),("BOTE Hangout Sling Chair 1-Pack","B0DY8993GD",22161),("BOTE Breeze Aero 11'6\" Inflatable Paddle Board","B0GWC91GDS",19603.92),("BOTE Breeze Aero 11'6\" Inflatable Paddle Board","B0GWCKF4DF",19601.68))),
"Crazy Creek Products":RAW(P("Crazy Creek Products","Sports & Outdoors","Camping Chairs",0.81,"",True,"",0.002,0.005,None,76.42,4.4,37,1402,166685.99,1959018.2),
 S(("Crazy Creek Products",99.773),("Amazon.com",0.227)),
 T(("Crazy Creek HEX 2.0 Original Chair, Olive/Slate","B09FB1MXV7",30778),("Crazy Creek The Chair","B0D47XC7F2",24587.65),("Crazy Creek HEX 2.0 Original Chair, Copper/Slate","B07CV96G3V",16997.85),("Crazy Creek HEX 2.0 LongBack Chair","B09TWMTBKD",11033.1),("Crazy Creek The Chair (variant)","B0D47V832M",11012.75))),
"Cutco":RAW(P("Cutco","Kitchen & Dining","Dinner Knives",5.92,"",False,"",0,-0.132,None,215.26,4.72,37,6448,112700.26,1918297.76),
 S(("GJA Family Enterprise LLC",18.914),("ReSellItRight",11.263),("buy Again",8.672),("iValueCookware",7.444),("N&J Trading co.",7.13),("New Leaf SG",6.986)),
 T(("CUTCO Model 1759 Table Knife","B00HK4LWOM",11522.42),("CUTCO Model 1721 Trimmer","B009X55UYE",10786.68),("CUTCO Super Shears/Scissors #77","B07JDWBPPQ",10078.97),("Cutco 4720 4\" Gourmet Paring Knife","B07T95TSX1",9621.6),("Cutco 19 Pc Kitchen Knife Set Cherry Wood Stand","B08FMTRFLW",9595.04))),
"Datrex":RAW(P("Datrex","Tools & Home Improvement","Home Emergency Survival Kits",5.06,"",False,"",0.007,0.101,None,77.6,4.42,17,9317,64557.5,527897.62),
 S(("Better service stores",36.797),("Kaizen8",25.625),("FHS Retail",13.091),("My Merchant",6.637),("Poolweb",5.061),("LFS Marine & Outdoor",2.935)),
 T(("Datrex Emergency Water Packet 4.227 oz (18 Packs)","B0134DAXJ2",16307.64),("Datrex Emergency Survival Water Pouch (Pack of 64)","B00ANY4EXM",14488.76),("Datrex Emergency Water Packet (24 Packs)","B0134DAXM4",11069.52),("Datrex Emergency Water Packet (12 packets)","B001CS53E2",6062.85),("Datrex DX024RD Life Ring w/Tape, Orange, 24","B08WRC1CVL",4853.64))),
"Dometic":RAW(P("Dometic","Automotive","RV Air Conditioners",6.36,"",True,"",0.341,-0.202,None,171.34,4.33,455,61403,2190724.57,20877698.14),
 S(("Amazon.com",34.131),("Global Climate Alliance",18.847),("CWDS",17.973),("Autoplicity",4.84),("Parts Via",2.939),("Legendary RV Parts",2.572)),
 T(("Dometic Model 410 Complete RV Toilet, White","B0BZH4HQN2",254457.92),("Dometic FreshJet 3 Series 15K BTU RV Rooftop Air Conditioner","B0BGYXRMFM",189154.24),("Dometic CFX5 95L Dual Zone Electric Cooler","B0DVLZYX4R",130989),("Dometic CFX5 75L Dual Zone Electric Cooler","B0DVM1HDV6",117481),("Dometic CFX5 55L Electric Cooler with Ice Maker","B0DVLZL61N",95611.88))),
}
FN="Saw that {b} exhibited at FNCE last year."
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
FL="Saw you're exhibiting at FLIBS next month."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
LAUNCH="We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
emails=[
E(125,"FNCE 2025|Just Made","JUST MADE","Barely on Amazon: one juice listing selling, under $500 a month, sold direct","Brand direct 100%; monthly rev ~$450; 1 active ASIN; 42 reviews; avg rating 4.8","Just Made on Amazon",f"""{H}

{FN.format(b='Just Made')}

From what we can see, Just Made is on Amazon with one juice listing actually selling, the pineapple ginger, at under $500 a month, sold direct, with about 40 reviews and a 4.8 rating. So the channel is essentially a placeholder right now, which for a cold-pressed juice brand may be deliberate, but it is also where shelf-stable and multipack products in your category do real volume.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",brand_sellers=["Just Made Foods"],qa=["profile pulled via query_analytics fallback"]),
E(126,"Las Vegas Souvenir & Resort Gift Show 2026|Joe Blow T's, Inc.","Joe Blow","Barely on Amazon; sold by resellers (SR1 Performance 75%); one tee listing moving","SR1 Performance USA 75.1%; brand direct 0%; monthly rev ~$430; 865 reviews; avg rating 4.75","Joe Blow T's on Amazon",f"""{H}

{LV}

Looking at your listings, Joe Blow T's are on Amazon at under $500 a month, sold by resellers like SR1 Performance rather than by you, with one Chevy truck tee doing nearly all of it. The reviews are strong, about 850 at a 4.75 average, so the demand is real. The channel just isn't built or owned.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(127,"Las Vegas Souvenir & Resort Gift Show 2026|Capsmith Inc","Capsmith","Barely on Amazon; sold entirely by resellers; trailing year ~$19k vs ~$400 now","Zentra 57.2%; Vagabond Joes 26.9%; brand direct 0%; monthly rev ~$420; TTM ~$18.5k; 259 reviews","Capsmith on Amazon",f"""{H}

{LV}

From what we can see, Capsmith licensed military beanies did about $18k on Amazon over the trailing year, all through resellers like Zentra and Vagabond Joes, and are now down to a few hundred dollars a month. We don't see a Capsmith account. Licensed Navy and Marines caps are exactly what sells on Amazon around the holidays if someone owns the listings.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(128,"Las Vegas Souvenir & Resort Gift Show 2026|The Bear Factory","The Bear Factory","Barely on Amazon; sold by resellers (GetHyped USA 66%); trailing year ~$19k vs ~$300 now","GetHyped USA 66.2%; ZTRONWARD 33.8%; brand direct 0%; monthly rev ~$320; TTM ~$19k; 275 reviews","The Bear Factory on Amazon",f"""{H}

{LV}

Looking at your listings, The Bear Factory outfits did close to $20k on Amazon over the trailing year but are down to a few hundred dollars a month now, all sold by resellers like GetHyped USA. We don't see a Bear Factory account. Build-a-bear clothes are a steady Amazon search, and the brand is not the one answering it.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",qa=["profile pulled via query_analytics fallback"]),
E(129,"Las Vegas Souvenir & Resort Gift Show 2026|Sona Enterprises","Sona Enterprises","Barely on Amazon; two SE tool listings sold by a reseller; small","Buy Sharp Eye 100%; brand direct 0%; monthly rev ~$245; 2 products; 333 reviews","Sona Enterprises on Amazon",f"""{H}

{LV}

From what we can see, the Sona Enterprises listings on Amazon come down to two SE pin punch sets doing a few hundred dollars a month, sold by a reseller called Buy Sharp Eye rather than by you. There are over 300 reviews between them, so people find and buy them. There is just no brand behind the listings on Amazon.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",qa=["profile pulled via query_analytics fallback; SmartScout record may be a partial view of the SE catalog"]),
E(130,"Las Vegas Souvenir & Resort Gift Show 2026|Green Tree Jewelry","Green Tree Jewelry","Effectively not on Amazon: one earring listing sold by two resellers","Zentra 50.5%; Artisan Owl 49.5%; brand direct 0%; 1 product; monthly rev ~$200; 118 reviews","Green Tree Jewelry on Amazon",f"""{H}

{LV}

Looking at your listings, Green Tree Jewelry is on Amazon as a single pair of Puerto Rican flag earrings, sold by two resellers, doing about $200 a month. That is the whole presence for a brand with a full wooden jewelry line. For gift and souvenir jewelry, Amazon is usually the biggest single shelf a brand can get onto.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(131,"Las Vegas Souvenir & Resort Gift Show 2026|Whitney Howard Designs","Whitney Howard Designs","Brand direct, 15 listings, under $200 a month; channel never built","Brand direct 94.6%; monthly rev ~$170; 15 products; 155 reviews; avg rating 4.43","Whitney Howard Designs on Amazon",f"""{H}

{LV}

From what we can see, Whitney Howard Designs has about 15 ornament and memorial gift listings on Amazon, sold direct, doing under $200 a month between them with around 150 reviews. Memorial and pet sympathy gifts are a search people make year round, and Christmas ornaments are about to peak, so the listings exist at the right moment without anything pushing them.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at more seriously?

Yoni"""),
E(132,"Las Vegas Souvenir & Resort Gift Show 2026|ZOOCCHINI / FlapjackKids","ZOOCCHINI","Brand direct but collapsed: trailing year ~$13k, now ~$130 a month across 18 listings","Brand direct 100%; monthly rev ~$130; TTM ~$13k; MoM -72%; 18 products; 513 reviews","Zoocchini on Amazon",f"""{H}

{LV}

Looking at your listings, Zoocchini did about $13k on Amazon over the trailing year, sold direct, and is now at just over $100 a month across 18 listings, with last month down more than 70%. There are over 500 reviews on the catalog, so the crawler pants and training pants had traction once. It looks like the channel has been left to drift.

{CO}

Would it make sense to have a quick conversation?

Yoni""",qa=["exhibitor also lists FlapjackKids; only Zoocchini queried"]),
E(133,"Las Vegas Souvenir & Resort Gift Show 2026|Blank Tag Co. Stickers","Blank Tag Co.","Effectively not on Amazon: one sticker bundle, under $100 a month, sold direct","Blank Tag, LLC. 100%; 1 product; monthly rev ~$75","Blank Tag Co. on Amazon",f"""{H}

{LV}

From what we can see, Blank Tag Co. is on Amazon as a single Strawberry Shortcake sticker bundle doing under $100 a month, sold direct. That is the whole presence, and licensed waterproof stickers for water bottles and laptops are one of the more searched gift items on Amazon, so the catalog is not really there yet.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",conf="close",brand_sellers=["Blank Tag, LLC."],qa=["profile query returned empty; data from seller and product queries only"]),
E(134,"Las Vegas Souvenir & Resort Gift Show 2026|RexTooth Studios","Rextooth Studios","Effectively not on Amazon: one book, a few copies a month","Brand direct 100%; 1 product; monthly rev ~$60; 26 reviews","Rextooth Studios on Amazon",f"""{H}

{LV}

Looking at your listings, Rextooth Studios is on Amazon as one title, End of the Ice Age, selling a few copies a month with a 4.6 rating. So the rest of the dinosaur comics and books are not on the biggest bookshelf in the country. That is worth a conversation on its own, whether or not the answer is to build it out.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",qa=["small publisher; weaker fit"]),
E(135,"Las Vegas Souvenir & Resort Gift Show 2026|East View Map Link","East View Map Link","Effectively not on Amazon: one chart listing, a couple of sales a month","Brand direct 100%; 1 product; monthly rev ~$50; 2 reviews","East View Map Link on Amazon",f"""{H}

{LV}

From what we can see, East View Map Link is on Amazon as a single NOAA chart listing selling a couple of copies a month. For a map and chart catalog of your size, that means the Amazon channel is essentially untouched, and printed charts and regional maps are a steady search on Amazon for boaters and travelers.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",qa=["map publisher/distributor; weaker fit"]),
E(136,"Las Vegas Souvenir & Resort Gift Show 2026|Squire Boone Village","Squire Boone Village","Effectively not on Amazon: one mystery egg listing sold by a reseller (ToyWiz)","ToyWiz 95.7%; brand direct 0%; 3 products; monthly rev ~$47; 124 reviews","Squire Boone Village on Amazon",f"""{H}

{LV}

Looking at your listings, Squire Boone Village products are on Amazon as a couple of listings, mainly the dinosaur mystery egg, sold by a reseller called ToyWiz, at under $50 a month. So the brand is effectively not on Amazon, and the souvenir toy and gemstone items you make are exactly what people search for as gifts and party favors there.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(137,"Las Vegas Souvenir & Resort Gift Show 2026|Little Critterz","Little Critterz","Effectively not on Amazon: one porcelain figurine listing, a few sales a month","Brand direct 100%; 1 product; monthly rev ~$40; 58 reviews; avg rating 4.8","Little Critterz on Amazon",f"""{H}

{LV}

From what we can see, Little Critterz is on Amazon as a single kitten figurine listing, sold direct, doing a few sales a month with a 4.8 rating on about 60 reviews. That is the entire presence for a collectible figurine line, in a category where collectors search by animal and buy several at a time.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(138,"Las Vegas Souvenir & Resort Gift Show 2026|Something Wild Inc.","Something Wild","Effectively not on Amazon: one children's book sold by Amazon, a few copies a month","Amazon 1P 100%; 1 product; monthly rev ~$33; 23 reviews","Something Wild on Amazon",f"""{H}

{LV}

Looking at your listings, Something Wild is on Amazon as one children's zoo book sold by Amazon itself, moving a few copies a month with a 5 star average on about 20 reviews. The rest of the range is not there. For a kids' book and gift publisher, that is the biggest channel in the country left almost entirely unused.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",qa=["small publisher; weaker fit; product title not returned, single ASIN"]),
E(139,"Las Vegas Souvenir & Resort Gift Show 2026|Bicast Inc.","Bicast","Effectively not on Amazon: only out-of-date 2024 calendars listed with no sales","3 products (2024 calendars); monthly rev $0; no active sellers; profile query failed twice","Bicast calendars on Amazon",f"""{H}

{LV}

From what we can see, the only Bicast listings on Amazon are 2024 Outer Banks and Williamsburg calendars with no sales and no active seller. So the brand is not on Amazon in any real sense, and regional calendars are a Q4 gift item people do search for by place name.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni""",conf="close",qa=["profile query failed on fast path and query_analytics; sellers empty; treated as effectively not on Amazon"]),
E(140,"Las Vegas Souvenir & Resort Gift Show 2026|Spin Copter","Spin Copter","Effectively not on Amazon: one listing, no sales, held by a party-supply reseller","Rojay Party (no revenue); 1 product; monthly rev $0; 11 reviews","Spin Copter on Amazon",f"""{H}

{LV}

Looking at your listings, Spin Copter is on Amazon as a single LED spincopter listing with no sales this month, held by a party-supply reseller rather than by you. Light-up flying toys are a strong Amazon impulse buy, especially in Q4, and right now the brand isn't in that market at all.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(141,"Las Vegas Souvenir & Resort Gift Show 2026|SUNLIGHT ART LLC","Sunlight Art","Effectively not on Amazon: one suncatcher listing, no sales, held by a reseller","The Performers Collection (no revenue); 1 product; monthly rev $0; 2 reviews","Sunlight Art on Amazon",f"""{H}

{LV}

From what we can see, Sunlight Art is on Amazon as one hummingbird suncatcher listing with no sales, held by a reseller called The Performers Collection rather than by you. So the brand is effectively not on Amazon, and window art and suncatchers are a steady gift search there.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at?

Yoni"""),
E(142,"Las Vegas Souvenir & Resort Gift Show 2026|Tell Industries","TELL INDUSTRIES","Effectively not on Amazon: two container listings with no sales","Tell Industries LLC (no active sales); 2 products; monthly rev $0; 27 reviews","Tell Industries on Amazon",f"""{H}

{LV}

Looking at your listings, Tell Industries has two hexagon storage container listings on Amazon with no sales this month and about 27 reviews between them. So the brand is on Amazon in name only. Clear storage jars are a big, searched category there, and it looks like the listings were set up and left.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at more seriously?

Yoni""",brand_sellers=["Tell Industries LLC"]),
E(143,"FLIBS 2026|Awlgrip/Interlux/SeaHawk","Awlgrip","Sold entirely by marine supply resellers (Merritt Supply 52%, Boats & More 40%); no brand account; large parent","Merritt Supply 52.1%; Boats & More 39.8%; brand direct 0%; monthly rev ~$19k; TTM ~$252k; 505 reviews; MoM -21.5%","Awlgrip on Amazon",f"""{H}

{FL}

From what we can see, Awlgrip products do roughly $19k a month on Amazon, and all of it is sold by marine distributors, mostly Merritt Supply and Boats & More, with no Awlgrip account in the mix. The converters and Awlcare lead. That is consistent with what we saw on the listings directly. For a brand at Awlgrip's level, the pricing, content and Buy Box on Amazon are entirely in distributor hands.

{CO}

Would a 20 minute look at the Amazon side of the marine coatings be worth your time?

Yoni""",qa=["exhibitor lists Awlgrip/Interlux/SeaHawk (AkzoNobel brands); only Awlgrip queried; sheet amazon_sold_by = Third-party resellers, confirmed"]),
E(144,"FLIBS 2026|Bluewing Fishing","BLUEWING","Large catalog sold through a single account (Uniprime Outdoors) with a thin review base for the volume","Uniprime Outdoors 100% on 1,202 offers (treated as brand's own account); monthly rev ~$367k; TTM ~$3.6M; 1,213 products; 4,754 reviews; avg rating 4.62","Bluewing's review base on Amazon",f"""{H}

{FL}

From what we can see, Bluewing does roughly $370k a month on Amazon through a single seller account across about 1,200 listings, with a 4.6 average rating. That is a serious channel. The thing that stands out is the review base: under 5,000 reviews across all of it, so most listings are running on a handful each, which makes the catalog more dependent on ads than it should be at that size.

{CO}

Open to a short call on the review and content side?

Yoni""",brand_sellers=["Uniprime Outdoors"],qa=["sheet amazon_sold_by = Third-party resellers (Uniprime Outdoors); fresh data shows Uniprime as the sole seller on 1,202 offers, treated as brand's own operating account; disagreement noted"]),
E(145,"FLIBS 2026|BOTE","BOTE","Strong brand direct with a sharp seasonal drop; thin reviews for the price point","Brand direct 100%; monthly rev ~$258k; TTM ~$3.5M; MoM -58%; 169 products; 1,375 reviews; avg price ~$460","BOTE's off-season on Amazon",f"""{H}

{FL}

Looking at your listings, BOTE does roughly $260k a month on Amazon, all sold direct, against a trailing year around $3.5M. Last month was down close to 60% with the season. At a $450 average price the catalog sits on under 1,400 reviews, and the off-season is usually when rank gets lost and has to be bought back in spring.

{CO}

Open to a short call on the off-season plan?

Yoni""",qa=["sheet amazon_sold_by = Brand (Seller Central), confirmed"]),
E(146,"FLIBS 2026|Crazy Creek Products","Crazy Creek Products","Strong brand direct, flat month, concentrated in two chair listings; scale angle","Brand direct 99.8%; monthly rev ~$167k; TTM ~$2.0M; 37 products; 1,402 reviews; top two ASINs ~$55k/mo combined","Crazy Creek on Amazon",f"""{H}

{FL}

From what we can see, Crazy Creek does roughly $165k a month on Amazon, sold direct, with the HEX 2.0 and The Chair carrying about a third of it between two listings. Growth is flat month to month, and the catalog sits on about 1,400 reviews, which for $2M a year is thin and keeps the ads working harder than they need to.

{CO}

Would it make sense to have a quick conversation about the next stage?

Yoni""",qa=["sheet amazon_sold_by = Brand (Seller Central), confirmed"]),
E(147,"FLIBS 2026|Cutco Cutlery","Cutco","Direct-sales brand whose Amazon volume (~$113k/mo) is entirely unauthorized resellers","GJA Family Enterprise 18.9%; ReSellItRight 11.3%; buy Again 8.7%; brand direct 0%; monthly rev ~$113k; TTM ~$1.9M; 6,448 reviews","Who sells Cutco on Amazon",f"""{H}

{FL}

From what we can see, Cutco does roughly $110k a month on Amazon, close to $2M over the trailing year, and every dollar is sold by third parties, six or more resellers like GJA Family Enterprise and ReSellItRight, with no Cutco account. That matches what we saw on the listings directly. So the pricing, the content and the reviews on the table knives and shears are being built by people you don't control.

{CO}

Would a 20 minute conversation about what a brand-owned Amazon channel could look like be worth your time?

Yoni""",qa=["sheet amazon_sold_by = Third-party resellers, confirmed; Cutco is a direct-sales company and may not want Amazon"]),
E(148,"FLIBS 2026|DATREX","Datrex","Sold entirely through resellers (Better service stores 37%, Kaizen8 26%); no brand account","Better service stores 36.8%; Kaizen8 25.6%; FHS Retail 13.1%; brand direct 0%; monthly rev ~$65k; 9,317 reviews","Who sells Datrex on Amazon",f"""{H}

{FL}

Looking at your listings, Datrex does roughly $65k a month on Amazon, mostly the emergency water packets, and all of it is sold by resellers like Better service stores and Kaizen8, with no Datrex account. That matches what we saw directly. With over 9,000 reviews on the catalog, that is a brand asset where the price and the page are set by whoever has stock that month.

{CO}

Would it make sense to talk about taking that back?

Yoni""",qa=["sheet amazon_sold_by = Third-party resellers, confirmed"]),
E(149,"FLIBS 2026|Dometic","Dometic","Very large brand: Amazon 1P ~34% with resellers (Global Climate Alliance, CWDS) at ~60%+; narrow reseller-share angle","Amazon 1P 34.1%; Global Climate Alliance 18.8%; CWDS 18.0%; reseller share ~66%; monthly rev ~$2.19M; TTM ~$20.9M; MoM -20%","Dometic reseller share on Amazon",f"""{H}

{FL}

From what we can see, Dometic does roughly $2.2M a month on Amazon, and only about a third of it is Amazon as the vendor. Close to 40% is two resellers, Global Climate Alliance and CWDS, with another dozen behind them. Last month was down about 20%. I know Dometic has an Amazon team, so this is a narrow point: that reseller share is where pricing and content drift.

{CO}

Would a 20 minute look at the reseller side be worth your time?

Yoni""",qa=["very large brand (>$2M/mo); sheet amazon_sold_by = Unknown; fresh data shows mixed 1P and resellers"]),
]
run(raw,emails)
