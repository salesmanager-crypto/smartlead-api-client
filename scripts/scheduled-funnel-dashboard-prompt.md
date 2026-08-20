# Rachel's Funnel Dashboard (scheduled refresh prompt)

You are refreshing "Rachel's Funnel Dashboard," an Artifact showing how Rachel's prospects
move through Smartlead outreach -> replies -> Pipedrive leads/deals -> Gmail follow-up,
unattended, on a schedule (daily). This prompt is fully self-contained — you have no memory
of any prior run.

## Access
- Pipedrive: use the connected Pipedrive MCP tools directly.
- Smartlead: via `/home/user/smartlead-api-client` — `SMARTLEAD_API_KEY` is already set in the
  environment (do not print it or write it into any file/commit). The committed script
  `scripts/build-funnel-report.mjs` does all Smartlead API calls itself (campaigns named
  "Rachel - ...", per-lead statistics) — don't re-derive that by hand.
- Artifact to update (same URL every run — pass this as `url` to the Artifact tool so it
  overwrites in place instead of creating a new one):
  `https://claude.ai/code/artifact/7261fc65-06df-4839-90d3-5dc53593e177`

## Rachel's identity
- Pipedrive `owner_id`: `25102178`
- Smartlead campaigns: any campaign whose name starts with `"Rachel - "` (the build script
  filters for this itself once it lists campaigns — you don't need to enumerate IDs).
- Gmail: the connected account is `rachel.s@albertscott.com`.

## Step 1 — Compute the window
`range_end` = today (actual current date, not hardcoded). `range_start` = 6 calendar months
before today. Both as `YYYY-MM-DD`.

## Step 2 — Pull Pipedrive data
1. `getLeads({ owner_id: 25102178, limit: 500 })`, paginating with `start`/pagination fields
   until exhausted. Keep every lead (don't pre-filter by date — the build script filters by
   `add_time` itself); each row needs `id`, `person_id`, `add_time`.
2. `getDeals({ owner_id: 25102178, limit: 500, sort_by: "add_time", sort_direction: "desc" })`,
   paginating via `cursor` until `additional_data.next_cursor` is null. Keep `id`, `person_id`,
   `stage_id`, `status`, `value`, `currency`, `add_time`.
3. `getStages({ limit: 500 })` — keep `id`, `name`, `pipeline_id`.
4. `getActivities({ done: false, owner_id: 25102178, limit: 500, sort_by: "due_date",
   sort_direction: "asc" })`, paginating via `cursor`. Count how many have `due_date` strictly
   before today (ISO string comparison) — this is `overdue_activities_count`. You don't need to
   keep the full activity rows, just the count.
5. Collect the unique `person_id`s referenced across the leads and deals from steps 1-2.
   Batch-fetch with `getPersons({ ids: "<comma-separated>", limit: 100 })` in chunks of 100 ids.
   From each person, keep `id`, `name`, `org_id`, and the primary email from `emails[]`
   (fall back to the first email if none is marked primary).
6. Write a JSON file (e.g. `/tmp/rachel-funnel-pipedrive.json`) shaped like:
   ```json
   {
     "range_start": "2026-02-20", "range_end": "2026-08-20", "owner_id": 25102178,
     "persons": [{ "id":123, "name":"...", "email":"...", "org_id":45 }],
     "organizations": [],
     "leads": [{ "id":"uuid", "person_id":123, "add_time":"2026-03-01T00:00:00Z" }],
     "deals": [{ "id":1, "person_id":123, "stage_id":5, "status":"open", "value":1000,
                 "currency":"USD", "add_time":"2026-03-05T00:00:00Z" }],
     "stages": [{ "id":5, "name":"Qualified", "pipeline_id":1 }],
     "overdue_activities_count": 58
   }
   ```

## Step 3 — Pull Gmail data
Gmail's `search_threads` tool matches labels by their **display name in quotes**, not by
label ID (`label:Label_xxx` returns nothing even though the tool's own docs say to use IDs —
confirmed by testing; `label:"Exact Name"` is what actually works).

Run (adjust `after:` to `range_start` in `YYYY/MM/DD` format):
```
after:2026/02/20 (label:"From SmartLead conversations" OR label:"1 Global Brands" OR label:"2 Global Brands" OR label:"3 Global Brands" OR label:"4 Global Brands" OR label:"5 Global Brands" OR label:"6 Global Brands" OR label:"ISM Cologne" OR label:"Pitti Immagine Uomo" OR label:"Modefabriek" OR label:"Solex" OR label:"StackOptimise" OR label:"Trade Show Representatives" OR label:"Home & Gift" OR label:"Reengagement" OR label:"LI Job Posts")
```
with `pageSize: 50`, `view: "THREAD_VIEW_MINIMAL"`, paginating via `pageToken` until it's
absent. If this label set no longer matches Rachel's actual Gmail labels (she renames/adds
campaign labels over time), re-run `list_labels` first and adjust — don't silently drop labels
that clearly still mean "outreach."

For each thread, keep `thread_id` (the `id` field), `subject` (from the first message), and
`messages: [{ from: sender, to: toRecipients, date }]` for every message in the thread.

If this ever exceeds ~500 threads in one run, keep paginating rather than stopping early, but
note the total count in your Step 6 report — that's a real growth signal worth flagging, not
something to hide.

Write a JSON file (e.g. `/tmp/rachel-funnel-gmail.json`) shaped like:
```json
{
  "range_start": "2026-02-20", "range_end": "2026-08-20",
  "my_email": "rachel.s@albertscott.com",
  "threads": [{ "thread_id":"...", "subject":"...",
                "messages": [{ "from":"a@b.com", "to":["rachel.s@albertscott.com"], "date":"2026-03-01T12:00:00Z" }] }]
}
```

## Step 4 — Generate the report
From `/home/user/smartlead-api-client`, run:
```
node scripts/build-funnel-report.mjs /tmp/rachel-funnel-pipedrive.json /tmp/rachel-funnel-gmail.json /tmp/rachel-funnel-dashboard.html "<today's date, e.g. Aug 21, 2026 7:00am ET>"
```
This script pulls Smartlead itself, joins everything, and writes a complete, self-contained
HTML report — don't reimplement its logic. It prints a one-line summary (sent/replied/leads/
deals/followup/unmatched counts) when done; check that it succeeded before continuing.

If `SMARTLEAD_API_KEY` is missing or the script errors, don't invent numbers — publish nothing
and report the failure instead (see Step 6). If Pipedrive or Gmail data is unavailable for this
run but Smartlead succeeded, still generate the report with empty Pipedrive/Gmail arrays (the
script handles missing data gracefully) and flag what's stale in your Step 6 report.

## Step 5 — Publish
Call the Artifact tool with:
- `file_path`: `/tmp/rachel-funnel-dashboard.html`
- `url`: `https://claude.ai/code/artifact/7261fc65-06df-4839-90d3-5dc53593e177` (updates the
  existing page in place — do **not** omit this, it would create a duplicate artifact)
- `favicon`: `🔻`
- `title`: `Rachel's Funnel Dashboard`
- `description`: one sentence noting the refresh time and headline numbers, e.g. "Refreshed
  7am ET Aug 21 — 8,522 sent, 462 replied, 16 became leads, 3 followed up in Gmail."

## Step 6 — Log the run
Append one row to `/home/user/smartlead-api-client/logs/funnel-dashboard-log.csv` (create it
with a header row if it doesn't exist yet). Columns, in order:
`timestamp,range_start,range_end,sent,replied,became_lead,became_deal,followup_sent,unmatched_replies,unmatched_gmail_threads,gmail_threads_total,pipedrive_leads_pulled,pipedrive_deals_pulled,overdue_activities,errors`
- `timestamp`: now, ISO 8601
- `errors`: semicolon-separated list of anything that failed or was stale (empty string if
  nothing went wrong)

## Step 7 — Report
One or two sentences: the headline funnel counts, anything that failed or was stale (missing
API key, Pipedrive/Gmail pull failures, Gmail label list drift — call these out rather than
silently skipping), and the total Gmail thread count if it's grown notably. No further action
needed from anyone unless something failed.
