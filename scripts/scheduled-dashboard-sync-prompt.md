# Outbound Command Center — hourly dashboard sync (scheduled task prompt)

You are refreshing Albert Scott's "Outbound Command Center" Cowork artifact, unattended, on an
hourly schedule. This prompt is fully self-contained — you have no memory of any prior run.

The artifact aggregates KPIs across every system Albert Scott has already automated —
**Smartlead, Pipedrive, Bluedot, Gmail, and Calendly** — into one dashboard styled to match the
Smartlead/Pipedrive product UI (Albert Scott brand: oxblood `#1D0000` / crimson `#B10548` / pink
`#E51958`, Inter typeface, rounded card system). This repo is the source of truth for the sync
*procedure* (this file); the artifact itself lives on claude.ai and is updated in place by URL —
do not try to move the dashboard's data into the repo, only the instructions for refreshing it.

## Access
- Artifact: `https://claude.ai/code/artifact/439c19b3-6769-49ee-8364-8d57bd02d378` — read it with
  the `Artifact` tool (`action: "read"`), edit a local copy, then republish with
  `action: "publish"` and the **same `url`** so it redeploys in place rather than creating a
  duplicate artifact.
- Pipedrive: connected MCP tools (`getLeads`, `getActivities`, `getDeals`, `getOrganization`,
  `searchOrganization`, etc.) — read-only for this sync, never write.
- Bluedot: connected MCP tools (`list_meetings`, `search_meetings`).
- Gmail: connected MCP tools (`search_threads`) against `yoni@albertscott.com`.
- Google Calendar: connected MCP tools (`list_events`) for the week-ahead view, if the artifact's
  calendar panel is in scope for this run.
- Smartlead: no MCP connector on this account yet. Get the key via Google Drive
  (`search_files` for title contains `'Smartlead API Key'`, then `read_file_content`) — the doc
  markdown-escapes underscores, so strip every backslash before using the key — then call the REST
  API with `WebFetch` (the sandbox proxy blocks `smartlead.ai` for `curl`/Node `fetch`, so
  `WebFetch` is the only path). **If the Drive doc can't be found or read, or Smartlead output
  looks stale/blocked in this session, do not block the rest of the run** — leave the Smartlead
  panel exactly as the "Inbox health refresh" routine (`scripts/` sibling automation, see
  `logs/inbox-health` if present) last left it and say so in your report. Never invent Smartlead
  numbers here; that panel is allowed to lag between the two automations, it is never allowed to
  be guessed.

## Step 1 — Read the current artifact
`Artifact` `action: "read"` on the URL above. Save the returned HTML to a local file and read the
whole thing before editing anything — the page's data model is embedded inline (JS objects/arrays
driving the automation/projects/contacts/inbox/profile views), and a partial edit that doesn't
match the existing shape will break rendering. Keep the CSS, markup structure, and view/nav system
exactly as they are. You are refreshing data, not redesigning.

## Step 2 — Pull this run's live data
Pull only what a connector actually returns — never carry a number forward from a previous run
and never estimate one.

**Pipedrive** (`getLeads` paginated with `start`/`limit` until `more_items_in_collection` is
false; `getActivities` with `done:false`; `getDeals` with `status:"open"`):
- Total leads, how many carry a `next_activity_id`, how many don't, how many have an
  `update_time` older than 30 days, lead adds per month for the trailing months.
- Open activities: total, and a breakdown into overdue (`due_date` before today), due today, due
  this week, due later — verify the four buckets sum to the total before using them anywhere.
  Also break down by activity `type`. List the most-overdue rows (subject, `due_date`, `org_id`).
- Open deal count and total value. Resolve any `org_id` you display into a name via
  `getOrganization` — the dashboard shows account names, never raw numeric ids.

**Bluedot** (`list_meetings`, sorted `desc`): the most recent meetings with title, duration,
whether they're a named client series (`collectionId` present) or an ad-hoc 1:1 (`tenancy:"user"`,
no `collectionId`).

**Gmail** (`search_threads`, query `from:notifications@calendly.com newer_than:30d`): classify
each thread by its subject line — `New Event:` = new booking, `Updated:` = reschedule, a recap
subject (e.g. "meeting recap", "action item") = post-meeting follow-up, anything else
(verification codes, password resets) is Calendly account mail, not a booking signal — exclude it.
For new bookings, break down by the Event Type named in the email body/snippet.

**Smartlead**: see the Access section above — best effort, never invented, never blocking.

## Step 3 — Update the artifact's data in place
Edit only the embedded data (arrays/objects/constants), matching the exact shape the page already
uses for each panel — leave every class name, layout element and script untouched. Update the
"live session" callout block(s) in the Automation view with today's date and what actually changed
since the last run (new leads/activities synced, new exceptions found, anything fixed) — write it
like the existing callouts do: specific record ids and names, not a generic "everything refreshed."
If a panel's upstream data didn't move since last run, say so plainly rather than repeating stale
numbers as if they were fresh.

## Step 4 — Verify before publishing
- Every activity bucket (overdue/today/this week/later) sums to the open-activity total.
- Every number on the page traces to a value a connector actually returned this run (or, for
  Smartlead, is explicitly carried over with that stated).
- The header/"today" date matches the actual run date.
- No JS console errors — if you can render headlessly (Playwright, `executablePath:
  '/opt/pw-browsers/chromium'`, do not run `playwright install`), do a quick check; otherwise
  visually re-read the diff against Step 1's saved copy for anything structurally off.

## Step 5 — Publish
`Artifact` `action: "publish"` with the edited file and the **same `url`** as Step 1 so it
redeploys the existing artifact rather than creating a new one. Keep the `favicon` unchanged.

## Step 6 — Log the run
Append one row to `/home/user/smartlead-api-client/logs/dashboard-sync-log.csv` (create it with a
header row if it doesn't exist yet). Columns, in order:
`timestamp,open_leads_no_activity,activities_overdue,open_deals,calendly_new_bookings_30d,bluedot_meetings_seen,smartlead_panel_status,errors`
- `smartlead_panel_status`: `"refreshed"` / `"carried_over"` / `"unreachable"`
- `errors`: semicolon-joined list of anything that failed (403s, missing Drive doc, connector
  down), or empty

## Step 7 — Report
Two or three sentences: what moved since the last run (overdue count, open-lead-no-activity count,
new Calendly bookings), whether Smartlead refreshed or is carrying over stale data and why, and
any connector failure worth a human's attention. No preamble, no restating these instructions.
