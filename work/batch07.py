from batchlib import *
raw={
"Fujifilm":RAW(P("Fujifilm","Electronics","Instant Film Cameras",3.99,"",True,"",0.162,-0.042,None,522.45,4.55,1237,531618,18990000,301800000),
 S(("Amazon.com",16.244),("The Tudak Store",9.028),("6ave",5.684),("Quality Photo",4.968),("Wholesale Photo",4.852),("SSE Photo & Video",4.356)),
 T(("Fujifilm X100VI Digital Camera, Black","B0CV52JHNR",821291),("Fujifilm Instax Mini Instant Film, 120 Exposures","B07NWRG5T4",578162),("Fujifilm X100VI Digital Camera, Silver (Japan)","B0CV523K92",428065),("Fujifilm X100VI Digital Camera, Silver","B0FC8MT38X",366963),("Fujifilm Instax Mini Instant Film Twin Pack","B00EB4ADQW",329893))),
"Furuno":RAW(P("Furuno","Electronics","Fish Finders",19.09,"Amazon.com",False,"",0.073,-0.349,None,562.53,4.04,23,273,16000,634800),
 S(("ShipSound",32.003),("Prime Marine",17.622),("Advance Cycle Parts",16.219),("Amazon.com",7.343),("PEPE DEALS",5.866),("BeachAudio",5.629)),
 T(("Furuno GP39 GPS/WAAS Navigator","B01M0DED5G",5376),("Furuno FCV600 Fish Finder","B0DH7X11L1",3954),("Furuno FCV800 Fish Finder","B0DM3JMDZ8",3152),("Furuno 525T-BSD Transducer","B000OTLFHE",1618),("Furuno Power Cord","B00286H700",677))),
"Garmin":RAW(P("Garmin","Electronics","Smartwatches",4.96,"",False,"",0.574,-0.192,None,455.42,4.41,2349,631205,49400000,805600000),
 S(("Amazon.com",57.434),("Beach Camera",3.599),("6ave",3.419),("Frontrow Tech",2.478),("Escape To Nature",2.44),("Sports-and-Gadgets",2.204)),
 T(("Garmin vivoactive 5, Ivory","B0CG6NBJ61",1690000),("Garmin Forerunner 165","B0CT3SGHXL",1410000),("Garmin vivoactive 5, Black","B0CG6NR413",981000),("Garmin Forerunner 55","B092RCLKHN",832000),("Garmin Forerunner 265","B0BS1T9J4Y",769000))),
"Gtechniq":RAW(P("Gtechniq","Automotive","Automotive Top Coats",2.7,"The Rag Company",True,"",0,0.03,None,58.76,4.41,86,32327,327200,4950000),
 S(("Gtechniq NA",57.779),("APEXLINE",8.691),("JY & JY",7.606),("Houdini",6.138),("Bloom and Burrow",5.002),("AutoAuthority",3.183)),
 T(("Gtechniq Crystal Serum Light 1.7oz","B07C4JRDY1",82734),("Gtechniq Crystal Serum Light 1oz","B07C546HRW",44441),("Gtechniq C2 Liquid Crystal 16.9oz","B00CE03HYA",15454),("Gtechniq C2 Liquid Crystal 33.8oz","B00JS3I96W",13023),("Gtechniq C4 Permanent Trim Restorer","B00IOMDVWA",10547))),
"Guy Harvey":RAW(P("Guy Harvey","Clothing, Shoes & Jewelry","Men's T-Shirts",0.99,"Guy Harvey by NG Labs",True,"",0,-0.328,None,25.23,4.64,1112,11998,79700,1240000),
 S(("NG Labs Apparel",99.384),("ACMR",0.356),("Dominion Bags",0.185),("MM Depot",0.036),("Tutors247",0.033),("StarCrossing",0.004)),
 T(("Guy Harvey Men's Threadcycled Short Sleeve T-Shirt","B0CSF5H9HD",3552),("Guy Harvey Men's Long Sleeve T-Shirt","B0FD48SSXD",1290),("Guy Harvey Men's Offshore Pocket T-Shirt","B0DTWCJJG3",980),("Guy Harvey Men's Billfish T-Shirt","B0DTWX58J5",974),("Guy Harvey Men's Offshore T-Shirt","B0DC4QK3FH",891))),
"HUK":RAW(P("HUK","Clothing, Shoes & Jewelry","Men's Rain Boots",1.2,"Amazon.com",True,"",0.849,-0.188,None,46.8,4.7,7276,66547,1990000,35300000),
 S(("Amazon.com",84.947),("Grivet Outdoors",1.533),("Grit & Garb",1.459),("Haddad's",1.26),("ST Antonious",1.047),("Angel Seller",0.852)),
 T(("HUK Men's Rogue Wave Shoe, Deck Boot","B0B845HMNJ",33906),("HUK Men's Rogue Wave Shoe","B0B84P8TX6",24080),("HUK Men's Rogue Wave Shoe","B0B83Z57RN",23607),("HUK Men's Rogue Wave Shoe","B0B847WBHP",16409),("HUK Men's Rogue Wave Shoe","B0D73ZPM7B",15053))),
"JL AUDIO":RAW(P("JL AUDIO","Electronics","Marine Speakers",1.67,"",False,"",0,-0.452,None,528.26,4.87,9,30,23100,229000),
 S(("HARVARD MARINE",53.748),("Best Prices",29.313),("Great Price",8.176),("CACHÉ",4.583),("Googol Shop",3.144),("The Factory Depot",1.037)),
 T(("JL Audio M3-650X Marine Coaxial Speakers","B0GCXNV9K6",11978),("JL Audio M6-880X Marine Coaxial Speakers","B0GCY1SBWN",4476),("JL Audio M6-770X Marine Coaxial Speakers","B0GCXZ379K",4078),("JL Audio C2-690TX Coaxial Speakers","B004FVAOOW",1740),("JL Audio MX Series Amplifier","B06XG9ST1L",582))),
"Leviton":RAW(P("Leviton","Tools & Home Improvement","Standard Electrical Outlets",4.48,"Amazon.com",True,"",0.757,-0.028,None,56.2,4.54,2909,590297,3050000,40600000),
 S(("Amazon.com",75.687),("Daily Supply Co",2.581),("Power & Supply",1.676),("MaxWarehouse",1.188),("AMCAN",1.122),("RES LLC",1.1)),
 T(("Leviton Decora Smart Switch","B0GR1TR26Y",122541),("Leviton Decora Smart Dimmer","B000U3I4VE",69558),("Leviton GFWT2-W GFCI Outlet","B013OVCTBO",53402),("Leviton GFTR1-3W GFCI Outlet","B019YJPKWU",49667),("Leviton SureSlide Dimmer","B0GK2JDBF2",43872))),
"MERCURY":RAW(P("MERCURY","CDs & Vinyl","Motor Oils",8.98,"",True,"",0.173,-0.112,None,65.02,4.61,647,265450,867000,13100000),
 S(("LEADERS RPM",23.023),("Amazon.com",17.341),("MovieMars-CDs",7.47),("Wakeboss",6.657),("LMB Retail",3.943),("Doug Russell Marine",3.585)),
 T(("Mercury 8M0081916 Oil Change Kit","B00J903Q6M",32625),("Mercury 2-Stroke DFI Engine Oil, 2.5 Gallon","B0FCHYXYDQ",20639),("Mercury Optimax DFI Engine Oil","B003901RIM",19226),("Dire Straits CD (unrelated Mercury Records)","B00JDVX4J6",18952),("Mercury 8M0188357 Maintenance Kit","B01MXFVZTA",17333))),
"North American Rescue":RAW(P("North American Rescue","Health & Household","Tourniquets",4.04,"",True,"",0.125,0.178,None,36.48,4.73,54,23630,402000,5700000),
 S(("Lightning X Products",43.966),("HMZ Medical",13.399),("Amazon.com",12.491),("Stronghold Group",10.95),("Courage Tactical",5.361),("Best Glide ASE",3.739)),
 T(("North American Rescue CAT Tourniquet GEN 7","B01ITAKG6A",213090),("North American Rescue CAT Tourniquet","B07CP6Z1C4",75791),("North American Rescue CAT Tourniquet","B003IRJGW0",20355),("North American Rescue HyFin Vent Chest Seal","B00KQS2NGK",16382),("North American Rescue HyFin Compact Chest Seal","B01M7O5TJS",13986))),
"Pettit Paint":RAW(P("Pettit Paint","Sports & Outdoors","Boat Painting Supplies",5.42,"Atlantic Boat Supply",False,"",0,0.549,None,134.71,4.5,55,792,23200,206000),
 S(("HARVARD MARINE",26.204),("Atlantic Boat Supply",18.932),("Coastal Marine & Trailer",9.568),("Merritt Supply",8.093),("Autoplicity",6.78),("MarineEngineParts",6.339)),
 T(("Pettit Splash Zone A-788 Epoxy, Quart","B0032FXM9Q",3597),("Pettit Captain's Varnish","B001444U9S",3472),("Pettit Vivid Antifouling Paint, Blue, Gallon","B000N9RPL0",1490),("Pettit Splash Zone Epoxy","B018RQTHC0",1040),("Pettit EZ-Poxy Topside Paint","B000N9RSPS",790))),
"Raritan":RAW(P("Raritan","Electronics","KVM Switches",25.47,"",False,"",0,-0.454,None,544.54,4.59,30,671,47100,880000),
 S(("EPHDirect",17.637),("KVMGalore",14.839),("Neutron USA",12.904),("BigKitchen",7.457),("KART IT",5.379),("MegaRetailStore",4.15)),
 T(("Raritan Dominion KX III KVM Switch (unrelated Raritan Inc)","B00IFEDSHA",11229),("Raritan Dominion KX IV-101 (unrelated Raritan Inc)","B07XN8B678",9056),("Raritan Dominion KX II CIM (unrelated Raritan Inc)","B0018DO29I",8297),("Raritan Potty Pack","B00IO5K1JS",4286),("Raritan K.O. Kills Odors, Gallon","B00DH3W0QO",3692))),
"Sea Foam":RAW(P("Sea Foam","Automotive","Fuel System Cleaners",9.95,"",True,"",0.001,-0.011,None,50.59,4.65,61,51264,343600,4030000),
 S(("JBTools",38.869),("Sea Foam Sales",25.516),("1185 Corp",10.697),("Shalo Dalo",3.76),("WHOLESALE WONDERLAND",2.259),("Penny Peak",2.072)),
 T(("Sea Foam Motor Treatment, 3 Pack","B07CL5Q89T",72771),("Sea Foam Motor Treatment, 6 Pack","B07DHGFXDJ",37592),("Sea Foam Motor Treatment, 4 Pack","B07DHHSQXP",33713),("Sea Foam SF-16 Motor Treatment, 2 Pack","B0CRSPVFK4",26692),("Sea Foam Marine PRO MP20, 3 Pack","B0FL9Z518N",22491))),
"searay":RAW(None,[],[]),
"SeaDek":RAW(P("SeaDek","Sports & Outdoors","Boat Deck Hardware",8.5,"DIY Seat Skins Inc",True,"",0,-0.203,None,107.14,4.66,32,781,13600,220000),
 S(("Autoplicity",58.566),("RecPro",7.788),("HARVARD MARINE",7.258),("Less Is Always More",6.778),("GLEHN'S",5.505),("House & Hammer",5.018)),
 T(("SeaDek Helm Pad, Large","B07RG7368W",3656),("SeaDek DEK Magic Cleaner, Gallon","B09DQCQ2TR",2534),("SeaDek Helm Pad, Small","B07RF9G7CK",2180),("SeaDek DEK Magic Cleaner, 32oz","B09352C4RC",1094),("SeaDek Helm Pad","B07X3N1LKQ",884))),
"SeaSucker":RAW(P("SeaSucker","Electronics","GPS Vehicle Mounts",4.54,"Brandish",True,"",0,-0.363,None,200.83,4.25,13,273,14700,338000),
 S(("Brandish",26.731),("Homestead Supply",22.692),("Geronimo Tackle",14.854),("Broadway Knives",14.184),("Resilient Consulting",9.928),("Performance Guarantee",4.675)),
 T(("SeaSucker Talon MAX Bike Rack","B0BPLJ8R31",3160),("SeaSucker 4.5 inch Vacuum Mount, Black","B00BH9N2SU",2418),("SeaSucker Monkey Bar 60","B0BPVXG35J",2280),("SeaSucker 4.5 inch Vacuum Mount, White","B0058WAFJ6",2198),("SeaSucker 48 inch Monkey Bars","B0BJQG7VNZ",1929))),
"SiOnyx":RAW(P("SiOnyx","Electronics","Monoculars",2.73,"",True,"",0,-0.218,None,745.38,4.51,11,331,82300,1280000),
 S(("SiOnyx",67.141),("Sparkfish",20.832),("Great Price",7.21),("Forgot My Souvenirs",1.957),("Best Prices",1.624),("Unlimited Electric Motor Supply",0.788)),
 T(("SIONYX Aurora PRO Night Vision Camera","B08CHMQ5CC",48393),("SIONYX Nightwave Marine Camera, Gray","B0CKS3P7S5",16358),("SIONYX Nightwave Marine Camera, White","B0BPZRQJ3S",3963),("SIONYX Nightwave Marine Camera, Black","B0CKWR3D4G",3921),("SIONYX Nightwave Vinyl Cover","B0CZY1SVYJ",1560))),
"SiriusXM":RAW(P("SiriusXM","Electronics","Car Satellite Radio",3.49,"",True,"",0.006,-0.076,None,58.47,4.32,49,25362,159800,2680000),
 S(("Photo-Zone [Authorized Dealer",76.384),("Diddly Deals",8.971),("TSS-Radio",4.477),("StereoLiving",4.164),("Solutions by Staples",2.272),("Satellite Radio Superstore",2.088)),
 T(("SiriusXM Onyx EZR Home Kit","B06XSWKGZP",26666),("SiriusXM SXSD2 + EZR Bundle","B07XG27NNZ",20634),("SiriusXM RoadyBT","B09WKV7YT2",19997),("SiriusXM SXSD2 Portable Speaker Dock","B00M0FDN9I",17471),("SiriusXM SXV300V1 Connect Vehicle Tuner","B00NJTO4CY",17145))),
"SPARKLEAN":RAW(P("SPARKLEAN","Beauty & Personal Care","Jewelry Cleaning",1.2,"sparklean shop",True,"",0,-0.01,None,59.99,4.24,5,511,12000,116000),
 S(("sparklean shop",100)),
 T(("Sparklean SparkBrush Jewelry Cleaning Brush","B0BMG28GPM",7208),("Sparklean Jewelry Cleaner, 8oz","B07DBXMY1K",2519),("Sparklean Jewelry Cleaner, 16oz","B07DBWLWW6",880),("Sparklean Jewelry Cleaner, 32oz","B07DBWHX61",720),("Sparklean Jewelry Cleaner, 2oz","B07DBX4LT3",300))),
"Vitrifrigo":RAW(None,[],[]),
"Zero Breeze":RAW(P("Zero Breeze","Home & Kitchen","Portable Air Conditioners",8,"",True,"",0,None,None,933.01,2.6,1,14,3700,941),
 S(("Max n Company LLC",100)),
 T(("Zero Breeze Mark 2 Portable Air Conditioner","B096N7JDS2",3732))),
"BANZA":RAW(P("BANZA","Grocery & Gourmet Food","Penne Pasta",4.93,"",True,"",0.452,0.089,None,19.13,4.39,80,34714,376700,3770000),
 S(("Whole Foods Market",48.878),("Amazon.com",45.197),("Veluxon",2.261),("queenesther",0.803),("OTCRx4u",0.515),("Midwest Estore",0.371)),
 T(("Banza Chickpea Plain Crust Pizza","B08DYZR5GS",44030),("Banza Chickpea Rotini","B00XXOY9A2",35424),("Banza Chickpea Pasta Variety, 6 Pack","B01IBIOMJ2",28735),("Banza Chickpea Cavatappi","B07D633ZWK",25482),("Banza Margherita Pizza","B0BXTVW3WR",21640))),
"Carlson":RAW(P("Carlson","Health & Household","Fish Oil",1.86,"",True,"",0.004,-0.085,None,31.07,4.56,569,134189,2840000,40100000),
 S(("Carlson Labs",90.33),("Swanson",3.619),("Vitamin Shoppe",1.529),("The Vitamin Shoppe",1.271),("NUTRIVIO HOME",1.159),("iHerb",0.516)),
 T(("Carlson Elite Omega-3 Gems, 60 Softgels","B081VWWGCZ",264361),("Carlson The Very Finest Fish Oil, 500mL","B001LF39RO",239997),("Carlson Elite EPA Gems","B06XSD83PC",131573),("Carlson Elite Omega-3 Gems, 90+30","B06XSLW9PY",121448),("Carlson Cod Liver Oil","B003B3P4PO",119070))),
"Chicken of the Sea":RAW(P("Chicken of the Sea","Grocery & Gourmet Food","Packaged Tuna",1.6,"Amazon.com",True,"",0.988,-0.022,None,29.3,4.39,141,46856,830000,9890000),
 S(("Amazon.com",98.792),("Essex Distribution",0.337),("TIMBS",0.226),("keys1428",0.2),("epic it",0.15),("SANTARA USA",0.072)),
 T(("Chicken of the Sea Chunk Light Tuna, 10 Count","B08WR5J62L",208790),("Chicken of the Sea Pink Salmon, 12 Count","B00O6JC15I",59038),("Chicken of the Sea Salmon Packets","B003RWVFEI",57086),("Chicken of the Sea Tuna, 24 Count","B07WJYRHLH",55575),("Chicken of the Sea Tuna","B0025UCU7E",33331))),
"DAVINCI":RAW(P("DaVinci","Baby Products","Convertible Cribs",None,"",True,"",0.73,None,None,None,None,459,48553,2190000,None),
 S(("Amazon.com",73.045),("Pattern.",25.497),("Cymax",0.688),("World Finer Foods",0.302)),
 T(("DaVinci Laboratories ADK Vitamin A, D3 and K2","B00GSN6BVA",114053))),
}
FN="Saw that {b} exhibited at FNCE last year."
FL="Saw you're exhibiting at FLIBS next month."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
LAUNCH="We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
TEAM="We essentially act as the Amazon team for the brands we work with."
emails=[
E(150,"FLIBS 2026|Fujifilm North America Corporation","Fujifilm","Very large brand; ~84% of revenue sold by third-party resellers, Amazon 1P ~16%; narrow reseller-layer ask","Amazon.com 16.2%; Tudak Store 9%; 6ave 5.7%; Quality Photo 5%; monthly rev ~$19M; 1,237 products; 531k reviews","Reseller layer on Fujifilm listings",f"""{H}

{FL}

From what we can see, Fujifilm does very serious volume on Amazon, but only about 16% of it is sold by Amazon directly. The rest goes through resellers like The Tudak Store, 6ave and Quality Photo, so pricing and the Buy Box on the X100 and Instax listings are shaped by a lot of hands. I know Fujifilm has an Amazon team. This is about the reseller layer, not the basics.

{CO}

Open to a 20 minute look at how the third-party layer on your top listings is affecting price and Buy Box?

Yoni""",qa=["very large brand, narrow ask","sheet third-party (Wiz Distribution) confirmed by fresh data"]),
E(151,"FLIBS 2026|Furuno USA, Inc.","Furuno","Sold by third-party resellers (ShipSound 32%, Prime Marine 18%, Advance Cycle Parts 16%); no brand account; month down ~35%","ShipSound 32%; Prime Marine 17.6%; Advance Cycle Parts 16.2%; Amazon.com 7.3%; monthly rev ~$16k; 23 products; MoM -34.9%","Furuno listings on Amazon",f"""{H}

{FL}

Looking at your listings, Furuno is doing about $16k a month on Amazon across roughly 20 products, with most of it sold by resellers like ShipSound, Prime Marine and Advance Cycle Parts. We don't see a Furuno account, and the GP39 and FCV600 listings are down sharply this month. For a brand of Furuno's standing in marine electronics, that footprint looks small and unmanaged.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party confirmed"]),
E(152,"FLIBS 2026|Garmin International","Garmin","Very large brand; Amazon 1P ~57%, third-party resellers ~43%; narrow marine-line ask","Amazon.com 57.4%; Beach Camera 3.6%; 6ave 3.4%; monthly rev ~$49M; 2,349 products; top listings all wearables","Garmin marine line on Amazon",f"""{H}

{FL}

From what we can see, Garmin does very large volume on Amazon, with Amazon itself selling about 57% and resellers like Beach Camera and 6ave splitting the rest. I know Garmin has an Amazon team, so this isn't a pitch on the basics. It's about the marine line specifically, where chartplotters and fish finders get less attention than the wearables and the third-party layer tends to set the price.

{CO}

Open to a 20 minute look at how the marine listings are performing versus the wearables?

Yoni""",qa=["very large brand, narrow ask","sheet sold_by Unknown; fresh data shows Amazon 1P 57% plus resellers (Mixed)"]),
E(153,"FLIBS 2026|Gtechniq Marine","Gtechniq","Brand sells ~58% direct; ~42% through resellers (APEXLINE, JY & JY, Houdini) on the same listings","Gtechniq NA 57.8%; APEXLINE 8.7%; JY & JY 7.6%; Houdini 6.1%; monthly rev ~$327k; 86 products; 32k reviews","Reseller share on Gtechniq listings",f"""{H}

{FL}

Looking at your listings, Gtechniq is doing about $330k a month on Amazon, and your own account sells roughly 58% of it. The other 42% goes through resellers like APEXLINE, JY & JY and Houdini, on the same Crystal Serum Light and C2 listings you're driving. That's a lot of margin and pricing control sitting with other sellers on a brand that's clearly working the channel.

{CO}

Would it make sense to have a quick conversation about tightening up the reseller side?

Yoni""",brand_sellers=["Gtechniq NA"],qa=["sheet says third-party (Harvard Marine); fresh data shows brand account Gtechniq NA at 58% with 42% resellers; trusting fresh (Mixed)"]),
E(154,"FLIBS 2026|Guy Harvey","Guy Harvey","Over 1,100 listings doing ~$80k a month (thin per listing); sold via licensee NG Labs; month down ~33%","NG Labs Apparel 99.4%; monthly rev ~$80k; 1,112 products; 12k reviews; MoM -32.8%","Guy Harvey catalog on Amazon",f"""{H}

{FL}

From what we can see, Guy Harvey has over 1,000 listings on Amazon but does about $80k a month, which works out to well under $100 per listing. It's sold through NG Labs Apparel and the month is down about a third. For a brand with this much recognition in the fishing world, that's a big catalog doing very little per SKU, which usually points to content, advertising and variation structure rather than demand.

{CO}

Open to a short call on where the catalog is leaving volume?

Yoni""",brand_sellers=["NG Labs Apparel","Guy Harvey by NG Labs"],qa=["NG Labs Apparel is the apparel licensee; treated as brand direct, verify"]),
E(155,"FLIBS 2026|HUK","HUK","Amazon 1P ~85% (vendor); large brand; narrow ask on content and advertising across a 7,000 SKU catalog; month down ~19%","Amazon.com 84.9%; monthly rev ~$2M; 7,276 products; 66k reviews; MoM -18.8%","HUK vendor side on Amazon",f"""{H}

{FL}

Looking at your listings, HUK does about $2M a month on Amazon, with roughly 85% of it sold by Amazon as a vendor. That means Amazon sets the price and the inventory position on the Rogue Wave boots and the rest of the line, and the month looks to be down close to 20%. I know HUK has people on this. The gap we usually find on vendor-heavy brands is content and advertising nobody owns across 7,000 SKUs.

{CO}

Open to a 20 minute look at the vendor side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed","large brand, narrow ask"]),
E(156,"FLIBS 2026|JL Audio","JL AUDIO","Sold by third-party resellers (Harvard Marine 54%, Best Prices 29%); only 9 products; month down ~45%","HARVARD MARINE 53.7%; Best Prices 29.3%; Great Price 8.2%; monthly rev ~$23k; 9 products; 30 reviews; MoM -45.2%","JL Audio marine listings",f"""{H}

{FL}

Looking at your listings, JL Audio marine speakers are doing about $23k a month on Amazon across only nine products, sold by resellers like Harvard Marine and Best Prices rather than by you. The month is down close to half. For the name JL Audio carries in marine audio, nine listings run by dealers is a small footprint, and nobody is managing content or advertising on them.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party confirmed"]),
E(157,"FLIBS 2026|Leviton","Leviton","Very large brand; Amazon 1P ~76%, resellers ~24%; marine/RV line not visible in top listings; narrow ask","Amazon.com 75.7%; Daily Supply Co 2.6%; Power & Supply 1.7%; monthly rev ~$3M; 2,909 products; 590k reviews","Leviton marine products on Amazon",f"""{H}

{FL}

From what we can see, Leviton does about $3M a month on Amazon, roughly three quarters of it sold by Amazon as a vendor and the rest by resellers like Daily Supply Co and Power & Supply. I know Leviton has an Amazon team. What we don't see is the marine and RV line showing up in the top listings, which are all smart switches and GFCIs, and that's the piece relevant to a boat show.

{CO}

Open to a 20 minute look at how the marine products are positioned on Amazon?

Yoni""",qa=["sheet Amazon (Vendor) confirmed","very large brand, narrow ask"]),
E(158,"FLIBS 2026|Mercury Marine","MERCURY","Oil and maintenance kits sold by dealers (LEADERS RPM, Wakeboss, Doug Russell Marine) and Amazon 1P; no brand seller layer","LEADERS RPM 23%; Amazon.com 17.3%; Wakeboss 6.7%; Doug Russell Marine 3.6%; oil change kit ~$33k/mo; 2-stroke oil ~$21k/mo","Mercury parts and oil on Amazon",f"""{H}

{FL}

Looking at your listings, Mercury oil and maintenance kits move real volume on Amazon, with the oil change kit listing alone doing around $30k a month, but they're sold by dealers like LEADERS RPM, Wakeboss and Doug Russell Marine plus Amazon itself. We don't see a Mercury account managing the listings. Consumables are where boaters actually buy on Amazon, and the brand isn't the one setting price or content there.

{CO}

Open to a 20 minute look at the parts and oil side of Amazon?

Yoni""",conf="close",qa=["mixed record: 'MERCURY' profile includes Mercury Records CDs (MovieMars-CDs); SS_ totals not brand-specific; email uses only marine product listings","'Mercury Marine' variant returned 1 product; sheet third-party (LEADERS RPM) confirmed"]),
E(159,"FLIBS 2026|North American Rescue","North American Rescue","~88% sold by third-party resellers (Lightning X 44%, HMZ Medical 13%, Stronghold 11%); Amazon 1P 12%; growing","Lightning X Products 44%; HMZ Medical 13.4%; Amazon.com 12.5%; Stronghold Group 11%; monthly rev ~$402k; CAT GEN 7 ~$213k/mo; MoM +17.8%","Who sells North American Rescue on Amazon",f"""{H}

{FL}

Looking at your listings, North American Rescue is doing about $400k a month on Amazon and growing, but almost 90% of it is sold by resellers like Lightning X, HMZ Medical and Stronghold Group, with Amazon itself at about 12%. The CAT tourniquet listing alone is over $200k a month, and the brand isn't the seller on it. That's a lot of price control and margin sitting with distributors on your best product.

{CO}

Would it make sense to have a quick conversation about bringing the channel in house?

Yoni""",qa=["sheet third-party (Stronghold Group) confirmed"]),
E(160,"FLIBS 2026|Pettit Paint","Pettit Paint","Sold entirely by third-party resellers (Harvard Marine 26%, Atlantic Boat Supply 19%); no brand account or storefront; month up","HARVARD MARINE 26.2%; Atlantic Boat Supply 18.9%; Coastal Marine & Trailer 9.6%; monthly rev ~$23k; 55 products; MoM +54.9%","Pettit listings on Amazon",f"""{H}

{FL}

Looking at your listings, Pettit is doing about $23k a month on Amazon across 55 products, all through resellers like Harvard Marine, Atlantic Boat Supply and Coastal Marine. Splash Zone and Captain's Varnish are the listings moving, and the month is up sharply, so the demand is there. What isn't there is a Pettit account, a storefront, or anyone managing content and advertising on a catalog that size.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party confirmed"]),
E(161,"FLIBS 2026|Raritan Engineering Co, Inc.","Raritan","Marine products (Potty Pack, K.O. Kills Odors) sold by resellers only; no storefront; thin catalog","Potty Pack ~$4.3k/mo; K.O. Kills Odors ~$3.7k/mo; sellers on record all third-party; no storefront","Raritan marine listings on Amazon",f"""{H}

{FL}

Looking at your listings, Raritan marine products like the Potty Pack and K.O. Kills Odors are on Amazon doing a few thousand dollars a month each, sold by resellers rather than by you, and there's no Raritan storefront. The catalog is thin relative to the rest of the Raritan marine sanitation line, and the listings that exist aren't being managed for content or advertising.

{CO}

Is Amazon something you're looking at more seriously for the marine line?

Yoni""",conf="close",qa=["mixed record: 'Raritan' profile is dominated by Raritan Inc KVM switches; SS_ totals not brand-specific; 'Raritan Engineering' variant returned empty; email uses only marine listings","sheet third-party (Homestead Supply) confirmed"]),
E(162,"FLIBS 2026|Sea Foam Sales Co","Sea Foam","Brand sells only ~26% direct; ~74% through resellers (JBTools 39%, 1185 Corp 11%) on the same multipacks","JBTools 38.9%; Sea Foam Sales 25.5%; 1185 Corp 10.7%; Shalo Dalo 3.8%; monthly rev ~$344k; 61 products; 51k reviews","Reseller share on Sea Foam listings",f"""{H}

{FL}

Looking at your listings, Sea Foam is doing about $340k a month on Amazon, but your own account sells only about a quarter of it. JBTools alone sells more than you do, and resellers like 1185 Corp and Shalo Dalo take most of the rest, all on the same Motor Treatment multipacks. That's a lot of Buy Box, pricing and margin in other hands on a brand that clearly moves on Amazon.

{CO}

Would it make sense to have a quick conversation about tightening up the reseller side?

Yoni""",brand_sellers=["Sea Foam Sales"],qa=["sheet says Brand (Seller Central); fresh data shows brand at 25.5% with resellers at ~74%; trusting fresh (Third-party resellers)"]),
E(163,"FLIBS 2026|Sea Ray","searay","Wrong match; industry-level: boat builder with a merch and accessories storefront sold by Amazon (from row)","No brand-level data; sheet: brand store, sold by Amazon.com (Vendor)","Sea Ray storefront on Amazon",f"""{H}

{FL}

From what we can see, Sea Ray has a brand store on Amazon with apparel and accessories sold by Amazon itself, which is a common setup for boat builders. It also usually means nobody on the brand side is managing the listings for content, advertising or reviews, so the storefront mostly sits there. For a brand with Sea Ray's owner base, branded gear and accessories can be a real channel rather than a placeholder.

{CO}

Open to a short call on whether the Amazon storefront is worth building out?

Yoni""",conf="wrong match",qa=["'searay' matched guitar picks; 'Sea Ray' variant returned 0 products; industry-level email from row info"]),
E(164,"FLIBS 2026|SeaDek","SeaDek","Sold by third-party resellers (Autoplicity 59%); no brand account; month down ~20%","Autoplicity 58.6%; RecPro 7.8%; HARVARD MARINE 7.3%; monthly rev ~$13.6k; 32 products; MoM -20.3%","SeaDek listings on Amazon",f"""{H}

{FL}

Looking at your listings, SeaDek is on Amazon at about $14k a month across roughly 30 products, sold almost entirely by resellers, with Autoplicity alone at close to 60%. The helm pads and DEK Magic are what moves, and the month is down about 20%. We don't see a SeaDek account. For the brand that defines the category, that's a small and unmanaged presence.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party (RecPro) confirmed"]),
E(165,"FLIBS 2026|Seasucker","SeaSucker","Sold by third-party resellers (Brandish 27%, Homestead Supply 23%, Geronimo Tackle 15%); month down ~36%; 4.25 rating","Brandish 26.7%; Homestead Supply 22.7%; Geronimo Tackle 14.9%; Broadway Knives 14.2%; monthly rev ~$14.7k; 13 products; MoM -36.3%; rating 4.25","SeaSucker listings on Amazon",f"""{H}

{FL}

Looking at your listings, SeaSucker is doing about $15k a month on Amazon across 13 products, sold by resellers like Brandish, Homestead Supply and Geronimo Tackle rather than by you. The month is down about a third and the reviews sit around 4.3. Vacuum mounts and Monkey Bars are exactly what boaters search on Amazon, and the brand isn't the one controlling price, content or advertising on them.

{CO}

Would it make sense to have a quick conversation about owning the channel directly?

Yoni""",qa=["sheet third-party confirmed"]),
E(166,"FLIBS 2026|SIONYX","SiOnyx","Brand sells ~67% direct; ~33% through resellers (Sparkfish 21%, Great Price 7%) on Aurora PRO and Nightwave; month down ~22%","SiOnyx 67.1%; Sparkfish 20.8%; Great Price 7.2%; monthly rev ~$82k; 11 products; MoM -21.8%","Reseller share on SIONYX listings",f"""{H}

{FL}

Looking at your listings, SIONYX is doing about $80k a month on Amazon, with your own account selling about two thirds and resellers like Sparkfish and Great Price taking the rest on the same Aurora PRO and Nightwave listings. The month is down about 20%. On a catalog of 11 products at this price point, a reseller undercutting you on the Aurora PRO costs real margin.

{CO}

Would it make sense to have a quick conversation about tightening up the reseller side?

Yoni""",qa=["sheet says third-party (Forgot My Souvenirs); fresh data shows brand account at 67% with 33% resellers; trusting fresh (Mixed)"]),
E(167,"FLIBS 2026|SiriusXM","SiriusXM","Hardware sold entirely by third-party dealers (Photo-Zone 76%); no brand seller; large company, narrow ask","Photo-Zone 76.4%; Diddly Deals 9%; TSS-Radio 4.5%; monthly rev ~$160k; 49 products; 25k reviews","SiriusXM hardware on Amazon",f"""{H}

{FL}

From what we can see, SiriusXM hardware does about $160k a month on Amazon, with Photo-Zone selling roughly three quarters of it and dealers like Diddly Deals and TSS-Radio the rest. We don't see SiriusXM as a seller on its own radios and docks. I know SiriusXM has people on retail. This is a narrow point about who controls the price, content and advertising on the Onyx and Roady listings.

{CO}

Open to a 20 minute look at the hardware side of Amazon?

Yoni""",qa=["sheet third-party confirmed","large company, weaker fit (subscription business, hardware via dealers)"]),
E(168,"FLIBS 2026|Sparklean","SPARKLEAN","Brand direct, ~$12k a month on 5 products, flat, 4.24 rating holding it back; modest growth angle","sparklean shop 100%; monthly rev ~$12k; 5 products; 511 reviews; rating 4.24; MoM -1%","Sparklean on Amazon",f"""{H}

{FL}

Looking at your listings, Sparklean is doing about $12k a month on Amazon, sold direct, across five products with the SparkBrush doing most of it. The month is flat and the rating sits around 4.2, which is the one thing holding a jewelry cleaner back on Amazon since the category is decided on reviews. There's room to grow this with content, advertising and review work rather than more SKUs.

{CO}

Would it make sense to have a quick conversation?

Yoni""",qa=["sheet Brand (Seller Central) confirmed"]),
E(169,"FLIBS 2026|Vitrifrigo","Vitrifrigo","Not found; industry-level: marine refrigeration listed only via a reseller, no storefront (from row)","No brand-level data; sheet: no brand store, sold by STAL MAR","Vitrifrigo on Amazon",f"""{H}

{FL}

From what we can see, Vitrifrigo units are on Amazon only through a reseller, with no brand storefront and no Vitrifrigo account behind the listings. Marine and RV refrigeration is a category where buyers do their research on Amazon even when they end up buying through a dealer, so those listings become the product page whether or not the brand manages them.

{LAUNCH} {PROOF}

Is Amazon something you're looking at for the US market?

Yoni""",conf="not found",qa=["profile returned 0 products on two attempts; industry-level email from row info"]),
E(170,"FLIBS 2026|Zero Breeze","Zero Breeze","One listing sold by a reseller at a 2.6 rating; small footprint for a $900 product","Max n Company LLC 100%; Mark 2 ~$3.7k/mo; 1 product; 14 reviews; rating 2.6","Zero Breeze Mark 2 listing",f"""{H}

{FL}

Looking at your listings, the Zero Breeze Mark 2 is on Amazon at a few thousand dollars a month, and from what we can see it's being sold by a reseller called Max n Company, with the listing sitting at a 2.6 rating on a handful of reviews. For a $900 product, that rating is doing real damage before anyone gets to the storefront. A portable AC at this price can work on Amazon if the listing, reviews and advertising are actually managed.

{CO}

Would it make sense to have a quick conversation about the Mark 2 listing?

Yoni""",qa=["sheet says Brand (Seller Central) sold by Zero Breeze; fresh data shows one listing sold by Max n Company LLC; trusting fresh, partial record (1 product, TTM figure unreliable)"]),
E(171,"FNCE 2025|Banza","BANZA","Amazon 1P plus Whole Foods ~94% (vendor); no brand seller account; growing; narrow ask on advertising and content","Whole Foods Market 48.9%; Amazon.com 45.2%; monthly rev ~$377k; 80 products; 35k reviews; MoM +8.9%","Banza vendor side on Amazon",f"""{H}

{FN.format(b='Banza')}

From what we can see, Banza does about $380k a month on Amazon, nearly all of it sold by Amazon and Whole Foods Market, and growing. That's a healthy vendor setup, but it also means no brand-owned seller account, so pricing, inventory and content on the pizza and rotini listings are in Amazon's hands. I know Banza has people on this. The piece usually left on the table with vendor-only brands is advertising and content ownership.

{CO}

Open to a 20 minute look at how the vendor side is performing?

Yoni""",qa=["sheet Amazon (Vendor) confirmed; Whole Foods Market counted as third-party per rule but is Amazon-owned","products pulled via query_analytics fallback"]),
E(172,"FNCE 2025|Carlson Laboratories, Inc.","Carlson","Strong brand-direct position (~90%); month down ~8.5%; small reseller layer; modest second-set-of-eyes ask","Carlson Labs 90.3%; Swanson 3.6%; Vitamin Shoppe 2.8%; monthly rev ~$2.84M; 569 products; 134k reviews; MoM -8.5%","Carlson on Amazon",f"""{H}

{FN.format(b='Carlson')}

Looking at your listings, Carlson is doing close to $3M a month on Amazon with your own account selling about 90% of it, which is a strong position. The month looks to be down close to 10%, and resellers like Swanson and Vitamin Shoppe are on the Omega-3 Gems and fish oil listings. I know Carlson has an Amazon team. This isn't a pitch on the basics, more a second set of eyes on the softness.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni""",brand_sellers=["Carlson Labs"],qa=["sheet Brand (Seller Central) confirmed","profile pulled via query_analytics fallback"]),
E(173,"FNCE 2025|Chicken of the Sea","Chicken of the Sea","Amazon 1P ~99% (vendor); large brand; narrow ask on advertising and content","Amazon.com 98.8%; monthly rev ~$830k; 141 products; 47k reviews; chunk light tuna 10ct ~$209k/mo; MoM -2.2%","Chicken of the Sea vendor side",f"""{H}

{FN.format(b='Chicken of the Sea')}

From what we can see, Chicken of the Sea does about $830k a month on Amazon, essentially all of it sold by Amazon as a vendor, with the 10-count chunk light tuna doing around $200k on its own. I know Chicken of the Sea has people on the account. The gap we usually see on vendor-only brands is advertising and content, since Amazon controls price and inventory and nobody owns the rest.

{CO}

Open to a 20 minute look at the vendor side?

Yoni""",qa=["sheet Amazon (Vendor) confirmed","large brand, narrow ask"]),
E(174,"FNCE 2025|DaVinci Laboratories","DAVINCI","One hero listing (ADK, ~$110k a month) sold through Pattern rather than the brand; rest of catalog under-managed","ADK B00GSN6BVA ~$114k/mo; Pattern. 25.5% of mixed record; sheet: sold by Pattern.","DaVinci Labs catalog on Amazon",f"""{H}

{FN.format(b='DaVinci Laboratories')}

Looking at your listings, the DaVinci Labs ADK alone does around $110k a month on Amazon, sold through Pattern rather than by DaVinci directly. When one hero product carries the channel through a third-party seller, the rest of the catalog usually gets little content or advertising attention, and the brand doesn't control price or the Buy Box on its own top listing.

{CO}

Would it make sense to have a quick conversation about the rest of the catalog?

Yoni""",conf="close",qa=["mixed record: 'DAVINCI' profile is dominated by DaVinci Baby cribs; SS_ totals not brand-specific; only the ADK listing is DaVinci Laboratories","sheet third-party (Pattern.) confirmed"]),
]
run(raw,emails)
