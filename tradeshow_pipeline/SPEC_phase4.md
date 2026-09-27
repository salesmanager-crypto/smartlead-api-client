# Phase 4 SmartScout worker spec
Folder: /home/user/smartlead-api-client/tradeshow_pipeline (cd there). Tools: load with ToolSearch "select:mcp__SmartScout__run_query,mcp__SmartScout__query_analytics".
Transcribe results exactly (unicode escapes like & = "&", ' = "'"); numbers as plain numbers (revenue rounded to 2 decimals); empty values stay empty. Keep messages minimal. Never interpret or filter rows.

## Mode PROFILE (batches from phase4_work/profile_batches.json)
HANDLE_PROFILE = qh_4-XqemdjuIWN (fallback question if the handle errors: "Full profile of the brand CTEK"; use the new handle).
For each batch index i in your range:
1. `python3 -c "import json;print(json.dumps(json.load(open('phase4_work/profile_batches.json'))[i]))"`
2. run_query(handle=HANDLE_PROFILE, filterValues=<that list exactly>, limit=200)
3. `python3 p4_save.py profile i OUT_FILE <<'EOF'` + one line per returned row with 15 pipe-separated fields in this order:
   Brand Name|Primary Category|Primary Subcategory|Total Monthly Revenue|Trailing 12-Month Revenue|Total Products|Total Reviews|Average Rating|Average Price|Average Sellers|Has Storefront|Average Amazon Revenue %|Average MoM Growth|Has Single Seller|Single Seller Name
   + `EOF`. (Has Storefront / Has Single Seller as true/false.) If the saver prints BAD FIELD COUNT, fix the line and re-run.

## Mode BRAND (per brand, list from phase4_work/rev_brands.json, slice [START:END])
HANDLE_SELLERS = qh_TxoS1SN9FuFm (fallback question: "Which sellers sell the brand CTEK and what is each seller's share of the brand's revenue")
HANDLE_SUBCATS = qh_ni-LUmPq7eUo (fallback question: "Top 3 subcategories for the brand CTEK by the brand's revenue, with the brand's market share and rank in each subcategory")
Get your list: `python3 -c "import json;print(json.dumps(json.load(open('phase4_work/rev_brands.json'))[START:END]))"`. For each brand:
1. run_query(handle=HANDLE_SELLERS, filterValues=[brand], limit=5)
2. run_query(handle=HANDLE_SUBCATS, filterValues=[brand], limit=3)
3. `python3 p4_save.py brand "<brand>" OUT_FILE <<'EOF'` then `SELLERS`, one line per seller row: Seller Name|Number of Offers|Brand Revenue Estimate|Estimated Brand Share|Month Over Month Change ; then `SUBCATS`, one line per subcat row: Sub Category Context|Marketshare|Revenue|Subcategory Rank ; then `EOF`.
   Replace any "|" inside a seller name with "/". If the saver prints BAD LINE, fix and re-run. The saver skips brands already saved, so on restart continue from the first unsaved brand.
Final reply: items saved, errors, any new handles. Nothing else.
