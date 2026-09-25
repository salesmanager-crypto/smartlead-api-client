from batchlib import *
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
LVS+"Channel Craft":dict(Email=m(LV,
"From what we can see, Channel Craft products do roughly $1,000 a month on Amazon, all through resellers, mostly one account called Fifty & Co, with no Channel Craft account. JJ's Pocket Knife kit is almost all of it. Made in USA craft kits are a natural Amazon gift item, and nobody is building that.",
f"{PROOF} {END}","Is Amazon something you're looking at?")),
FNS+"Cleveland Kitchen":dict(Email=m(FN.format(b="Cleveland Kitchen"),
"Looking at your listings, Cleveland Kitchen is doing about $84k a month on Amazon, up several times on the year, but the brand isn't the seller on any of it. Whole Foods Market sells about a third, and a reseller called Eternity Essentials appeared this month and is already near 60% on the beet kraut. For a refrigerated product, a reseller you don't control is a cold-chain risk as much as a pricing one.",
CO,"Would it make sense to have a quick conversation about the reseller side?")),
FNS+"CON-CRĒT":dict(Email=m(FN.format(b="CON-CRET"),
"Looking at your listings, CON-CRET is doing about $1.2M a month on Amazon through the Vireo Systems account and growing fast, with the capsules carrying more than a third of it. That's a strong position in a category where creatine HCl is getting a lot of new search. I know you have people on this, so this isn't a pitch on the basics. It's about what the next stretch looks like as the flavored powders come up.",
CO,"Open to a 20 minute look at the next stretch of growth?")),
FNS+"Equip":dict(Email=m(FN.format(b="Equip"),
"Looking at your listings, Equip is doing about $2.2M a month on Amazon through your own account, up close to 40% on the year, with the Prime beef protein in chocolate and vanilla carrying most of it. The month looks to be down about 20%, which on a catalog this concentrated usually traces to one or two listings. I know you have an Amazon team, so this is a second set of eyes.",
CO,"Open to a 20 minute look at where the dip is coming from?")),
FNS+"Solara Labs":dict(Email=m(FN.format(b="Solara Suncare"),
"Looking at your listings, Solara Suncare is doing about $37k a month on Amazon, almost all through a seller called Carbon Beauty rather than a Solara account, with a few small resellers on the same listings. If Carbon Beauty is your partner, fine. What stands out either way is a 3.8 rating across the catalog, which for a premium sunscreen is what caps conversion, and the off-season is when that gets fixed.",
CO,"Would it make sense to have a quick conversation before next season?")),
FNS+"Step One Foods":dict(Email=m(FN.format(b="Step One Foods"),
"Looking at your listings, Step One Foods is doing about $39k a month on Amazon through your own account, spread across three bar listings, with the sprinkle products not moving at all. The rating sits just above 4, which for a clinically positioned product is lower than it should be and is what caps conversion. The clinical story is a real differentiator in a crowded bar category if the listings tell it.",
CO,"Would it make sense to have a quick conversation about growing the channel?")),
FNS+"Tosi Snacks":dict(Email=m(FN.format(b="Tosi"),
"Looking at your listings, Tosi is doing about $54k a month on Amazon through your own account and growing, spread fairly evenly across the nut bar 12-packs with no single hero listing. That's a healthy base. With 36 listings and about 900 reviews across all of them, the catalog is wide but thin on social proof, and consolidating around a few winners with advertising behind them is usually what moves a brand at this stage.",
CO,"Would it make sense to have a quick conversation?")),
FNS+"Tribe Nutrition":dict(Email=m(FN.format(b="Alpha Tribe"),
"Looking at your listings, Alpha Tribe is doing about $34k a month on Amazon through your own account, up several times on the year, with the two men's multivitamin listings carrying all of it and the Test Protocol line not moving. The month looks to be down about a third. When a brand rides two listings that hard, a dip like that is usually ranking or advertising on one of them, and it's fixable.",
CO,"Open to a 20 minute look at the dip?")),
LVS+"Country Fresh Food & Confections, Inc.":dict(Email=m(LV,
"Looking at your listings, Backroad Country is doing about $55k a month on Amazon across 50 listings, with the black licorice twists carrying it, and none of it runs through a Country Fresh account. ChristianStore2011 sells about half, Myers Distribution most of the rest. For a candy brand heading into Q4, that means price, content and the Buy Box are set by whoever has stock.",
CO,"Would it make sense to have a quick conversation about owning the channel before Q4?")),
LVS+"Crazy Apparel Inc.":dict(Email=m(LV,
"From what we can see, Crazy Apparel doesn't have a brand presence on Amazon, and the only listing tied to the name is an unrelated novelty shirt. Resort and souvenir apparel gets searched by name on Amazon by people who bought a piece on a trip, and a storefront with a few well-built listings is a small way to catch that before the holidays.",
f"{PROOF} {END}","Is Amazon something you're looking at more seriously?")),
LVS+"Crossroads Designs, LLC":dict(Email=m(LV,
"Looking at your listings, Crossroads candles are on Amazon at about $19k a month across roughly 60 listings, all sold by resellers like Hour Loop, JBTools and ArtsiHome rather than a Crossroads account, with no brand storefront. The Buttered Maple Syrup scent carries it, with 4,600 reviews behind the catalog. Candles are one of the biggest Q4 gift searches on Amazon, and the brand isn't the one selling them.",
CO,"Would it make sense to have a quick conversation about owning the channel before Q4?")),
LVS+"Desert Sunglass of Scottsdale":dict(Email=m(LV,
"From what we can see, Desert Sunglass of Scottsdale doesn't have a brand presence on Amazon, and the only listing tied to the name is an unrelated novelty shirt. Sunglasses are one of the most searched gift categories on Amazon, and a resort sunglass line with a storefront and a few well-built listings can catch people who bought a pair on a trip and want another.",
f"{PROOF} {END}","Is Amazon something you're looking at more seriously?")),
}
update_rows(fixes)
