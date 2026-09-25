from helpers import *
H="Hi {{first_name}},"
FL="Saw you're exhibiting at FLIBS next month."
FN="Saw that {b} exhibited at FNCE last year."
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
LAUNCH="We help brands launch, manage and grow on Amazon, supporting the full channel from strategy through execution."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
fx={}
fx["FLIBS 2026|Fujifilm North America Corporation"]=dict(Email=f"""{H}

{FL}

From what we can see, Fujifilm does very serious volume on Amazon, but only about 16% of it is sold by Amazon directly. The rest goes through resellers like The Tudak Store, 6ave and Quality Photo, so pricing and the Buy Box on the X100 and Instax listings are shaped by a lot of hands. I know Fujifilm has an Amazon team. This is about the reseller layer, not the basics.

{CO}

Open to a 20 minute look at the third-party layer on your top listings?

Yoni
""")
fx["FLIBS 2026|Leviton"]=dict(Email=f"""{H}

{FL}

From what we can see, Leviton does about $3M a month on Amazon, roughly three quarters of it sold by Amazon as a vendor and the rest by resellers like Daily Supply Co and Power & Supply. I know Leviton has an Amazon team. What we don't see is the marine and RV line in the top listings, which are all smart switches and GFCIs, and that's the piece relevant to a boat show.

{CO}

Open to a 20 minute look at how the marine products are positioned?

Yoni
""")
fx["FLIBS 2026|Vitrifrigo"]=dict(Email=f"""{H}

{FL}

From what we can see, Vitrifrigo units are on Amazon only through a reseller, with no brand storefront and no Vitrifrigo account behind the listings. Marine and RV refrigeration is a category where buyers research on Amazon even when they buy through a dealer, so those listings become the product page whether or not the brand manages them.

{PROOF} We manage the channel end to end.

Is Amazon something you're looking at for the US market?

Yoni
""")
fx["FLIBS 2026|Zero Breeze"]=dict(Email=f"""{H}

{FL}

Looking at your listings, the Zero Breeze Mark 2 is on Amazon at a few thousand dollars a month, and from what we can see it's sold by a reseller called Max n Company, with the listing sitting at a 2.6 rating on a handful of reviews. For a $900 product, that rating does real damage before anyone reaches the storefront. It can work on Amazon if the listing, reviews and advertising are actually managed.

{CO}

Would it make sense to have a quick conversation about the Mark 2 listing?

Yoni
""")
fx["FNCE 2025|Banza"]=dict(Email=f"""{H}

{FN.format(b='Banza')}

From what we can see, Banza does about $380k a month on Amazon, nearly all of it sold by Amazon and Whole Foods Market, and growing. That's a healthy vendor setup, but it also means no brand-owned seller account, so pricing, inventory and content on the pizza and rotini listings sit with Amazon. I know Banza has people on this. The piece usually left on the table with vendor-only brands is advertising and content ownership.

{CO}

Open to a 20 minute look at the vendor side?

Yoni
""")
fx["FNCE 2025|Carlson Laboratories, Inc."]=dict(Email=f"""{H}

{FN.format(b='Carlson')}

Looking at your listings, Carlson is doing close to $3M a month on Amazon with your own account selling about 90% of it, which is a strong position. The month looks to be down close to 10%, and resellers like Swanson and Vitamin Shoppe are on the Omega-3 Gems and fish oil listings. I know Carlson has an Amazon team. This is more a second set of eyes on the softness.

{CO}

Open to a 20 minute look at where the dip is coming from?

Yoni
""")
update_rows(fx)
print(status())
