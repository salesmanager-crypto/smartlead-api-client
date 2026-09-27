# Phase 3 SmartScout batch worker spec
Folder: /home/user/smartlead-api-client/tradeshow_pipeline (cd there).
You run SmartScout brand lookups in batches. Tools: mcp__SmartScout__run_query and mcp__SmartScout__query_analytics (load with ToolSearch "select:mcp__SmartScout__run_query,mcp__SmartScout__query_analytics").
Handle: HANDLE given in your task. If run_query returns an error saying the saved query is not available, call query_analytics with question
"Primary category, primary subcategory, total products and total monthly revenue for the brand CTEK" and use the new "handle" from its result for the rest (tell me the new handle in your final reply).
For each batch index i in your range:
1. `python3 -c "import json;print(json.dumps(json.load(open('BATCH_FILE'))[i]))"` to get the list of names.
2. Call mcp__SmartScout__run_query with handle=HANDLE, filterValues = that exact list (copy exactly, same spelling), limit=200.
3. Save: `python3 ss_save.py BATCH_FILE i OUT_FILE <<'EOF'` then one line per returned row: `Brand Name|Primary Category|Primary Subcategory|Total Products|Total Monthly Revenue` (copy values exactly as returned; unicode escapes like & are "&"; numbers as plain numbers, round revenue to 2 decimals; empty subcategory stays empty), then `EOF`. If zero rows returned, still run the save with an empty heredoc.
4. The saver refuses duplicates, so on restart just continue from the first unsaved index (check OUT_FILE batch numbers).
Do not interpret or filter results; just transcribe every returned row. Keep messages minimal.
Final reply: batches saved, total rows, any errors. Nothing else.
