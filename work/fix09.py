from helpers import update_rows
LV="Saw you're exhibiting at the Las Vegas Souvenir & Resort Gift Show next week."
FN="Saw that {b} exhibited at FNCE last year."
H="Hi {{first_name}},"
CO="We manage Amazon for brands end to end, including strategy, content, advertising, inventory and operations."
PROOF="We recently helped a brand go from no Amazon presence to a $1M+ annual run rate within six months."
END="We manage the channel end to end."
LVS="Las Vegas Souvenir & Resort Gift Show 2026|"
FNS="FNCE 2025|"
def m(opener,body,co,ask): return f"{H}\n\n{opener}\n\n{body}\n\n{co}\n\n{ask}\n\nYoni"
fixes={
FNS+"Cleveland Kitchen":dict(Email=m(FN.format(b="Cleveland Kitchen"),
"Looking at your listings, Cleveland Kitchen is doing about $84k a month on Amazon, up several times on the year, but the brand isn't the seller on any of it. Whole Foods Market sells about a third, and a reseller called Eternity Essentials appeared this month and is already near 60% on the beet kraut. For a refrigerated product, that's a cold-chain risk as much as a pricing one.",
CO,"Would it make sense to have a quick conversation about the reseller side?")),
FNS+"CON-CRĒT":dict(Email=m(FN.format(b="CON-CRET"),
"Looking at your listings, CON-CRET is doing about $1.2M a month on Amazon through the Vireo Systems account and growing fast, with the capsules carrying more than a third of it. That's a strong position in a category where creatine HCl is getting a lot of new search. I know you have people on this, so this isn't a pitch on the basics. It's about the next stretch as the flavored powders come up.",
CO,"Open to a 20 minute look at the next stretch of growth?")),
LVS+"Crazy Apparel Inc.":dict(Email=m(LV,
"From what we can see, Crazy Apparel doesn't have a brand presence on Amazon, and the only listing tied to the name is an unrelated novelty shirt. Resort apparel gets searched by name on Amazon by people who bought a piece on a trip, and a storefront with a few well-built listings is a small way to catch that before the holidays.",
f"{PROOF} {END}","Is Amazon something you're looking at more seriously?")),
LVS+"Crossroads Designs, LLC":dict(Email=m(LV,
"Looking at your listings, Crossroads candles are on Amazon at about $19k a month across roughly 60 listings, all sold by resellers like Hour Loop and JBTools rather than a Crossroads account, with no brand storefront. The Buttered Maple Syrup scent carries it, with 4,600 reviews behind the catalog. Candles are one of the biggest Q4 gift searches on Amazon, and the brand isn't the one selling them.",
CO,"Would it make sense to have a quick conversation about owning the channel before Q4?")),
LVS+"Desert Sunglass of Scottsdale":dict(Email=m(LV,
"From what we can see, Desert Sunglass of Scottsdale doesn't have a brand presence on Amazon, and the only listing tied to the name is an unrelated novelty shirt. Sunglasses are one of the most searched gift categories on Amazon, and a resort sunglass line with a storefront and a few well-built listings can catch people who bought a pair on a trip.",
f"{PROOF} {END}","Is Amazon something you're looking at more seriously?")),
}
update_rows(fixes)
from helpers import status
print(status())
