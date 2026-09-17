# Rachel's Command Center (scheduled refresh prompt)

You are refreshing "Rachel's Command Center," a multi-page Sales & Marketing dashboard
Artifact, unattended, on a schedule (weekdays at 7am ET unless told otherwise). This prompt
is fully self-contained — you have no memory of any prior run.

## Access
- Pipedrive: use the connected Pipedrive MCP tools directly.
- Smartlead: via `/home/user/smartlead-api-client` — `SMARTLEAD_API_KEY` is already set in
  the environment (do not print it or write it into any file/commit). Use the committed
  script `scripts/pull-command-center-data.mjs`, don't re-derive the Smartlead lookups by
  hand.
- Semrush / LinkedIn: only if a connector for these is actually enabled in this chat. If not,
  render those sections as "not connected" — never invent numbers.
- Artifact to update (same URL every run — pass this as `url` to the Artifact tool so it
  overwrites in place instead of creating a new one):
  `https://claude.ai/code/artifact/82287946-b15f-4126-9570-c83624587863`

## Owner ID map
`25102178` = Rachel (me), `25109251` = Yoni, `26939288` = Rep 3. Use these directly — don't
re-derive them.

## Step 1 — Pull Smartlead data
```
node scripts/pull-command-center-data.mjs /tmp/command-center-smartlead.json
```
This fetches every campaign + analytics, yesterday's per-campaign analytics-by-date, the
trailing-7-day Master Inbox reply log, lead categories, and mailbox/sending-domain counts.
It takes roughly a minute (it's making ~300 Smartlead API calls). Check the one-line summary
on stderr for errors before continuing — if the API key is missing or a call fails outright,
say so in your final report rather than silently using partial data.

## Step 2 — Pull Pipedrive data
- `getActivities` with `done: false`, `sort_by: "due_date"`, `sort_direction: "asc"`,
  `limit: 500` (page with `cursor` from `additional_data.next_cursor` if non-null — shouldn't
  be needed at current volume). For each, bucket by comparing `due_date` (ISO string) to
  today's date: overdue (`due_date < today`), due today (`due_date == today`), upcoming
  (`today < due_date <= today+14d`).
- `getDeals` with `limit: 500`, `sort_by: "add_time"`, `sort_direction: "desc"`.
- `getLeads` with `limit: 500` for lead counts by owner.
- `getPersons` and `getOrganizations`, each with `limit: 500`, paging via `cursor` until
  `next_cursor` is null, to get full counts and to resolve `person_id`/`org_id` on activities
  to names + emails. (At last count this took 4 pages of persons and 2 of organizations —
  re-page fully each time since these totals grow.)
- `getStages` for stage-id → stage-name on the deals table.
- Any tool result that gets saved to a file for being too large: process it with a short
  Python/jq script rather than trying to read the raw file into context — these routinely
  exceed the inline-output limit at current data volume.

## Step 3 — Build the sync-gap classification (persistent, not just the 7-day window)
For every reply in the Smartlead 7-day window: look up its Pipedrive lead-category name (via
`leadCategories` from the pull), and classify:
- **synced** — category is Interested, Meeting Request, or Follow Up, AND a Pipedrive person
  exists with a matching email (case-insensitive) among the persons pulled in Step 2.
- **gap** — same qualifying categories, but NO matching Pipedrive person. This is the number
  Rachel cares about most — it means a real lead never made it into the CRM.
- **uncategorized** — no category applied yet.
- **none** — any other category (Do Not Contact, Not Interested, Out Of Office, Ignore,
  Wrong Person, Unsure, etc.) — doesn't need to sync.

**Gaps must persist across refreshes, not just live in the rolling 7-day window** — a reply
from 8 days ago that's still unsynced is still a real problem, even though the Smartlead pull
no longer returns it. Maintain this with a small state file, `scripts/.sync-gap-state.json`
(gitignored — machine-local, like `.deliverability-state.json`):
1. Load it (an object keyed by lowercased email; empty object if the file doesn't exist yet).
2. Drop any entry whose email now matches a Pipedrive person (found in Step 2) — it's resolved.
3. For every **gap** found in this run's 7-day window, add it to the state if not already
   present (fields: `email`, `lead_name`, `campaign_name`, `category`, `reply_time`,
   `first_seen` — set `first_seen` to `reply_time` the first time it's seen; never overwrite
   `first_seen` on later runs) or just refresh `reply_time` if already tracked.
4. Write the updated state back to `scripts/.sync-gap-state.json`.
5. Compute `days_open` for every remaining entry (today's date minus `first_seen`'s date) and
   sort descending by `days_open` — this list becomes `syncGap.persistentGaps`, and
   `syncGap.persistentGapCount` is its length. This count (not the raw 7-day `gap` count) is
   what drives the sidebar badge and the main-page banner.

## Step 4 — Rebuild the dashboard HTML
The dashboard's design/logic now live as committed files, not just inside the live artifact:
- `scripts/command-center-template.html` — page shell, CSS, router.
- `scripts/command-center-page.js` — spliced into the template at `__PAGE_JS__`; all the
  page-rendering logic (Mine/Team/All toggles, sortable tables, daily inbox log, the sync-gap
  watchlist table, the "Tagged Rachel" campaign filter).
- `scripts/build-command-center-html.mjs` — splices template + page JS + a data JSON file into
  the final HTML: `node scripts/build-command-center-html.mjs <data.json> <output.html>`.

Don't rewrite the design or page logic — only regenerate the data JSON with fresh numbers from
Steps 1–3, matching the shape `command-center-page.js` expects: `meta`, `campaigns` (each with
`tags` and `isRachel` — true if any tag name equals "RACHEL", case-insensitive, powering the
"Tagged Rachel" filter chip), `campaignStatusCounts`, `yesterday`, `masterInboxReplies7d`,
`syncGap` (now including `persistentGaps` and `persistentGapCount` per Step 3),
`mailboxCount`, `sendingDomainCount`, `activities`, `deals`, `leadsByOwner`, `totalLeads`,
`totalPersons`, `totalOrgs`, `activityTypeCounts`, `overdueByOwner`, `dueTodayByOwner`,
`upcomingByOwner`, `yesterdayReplyMix`, `yesterdayInterested`, `seoGeo`, `linkedin`,
`resources`. Write that JSON to a scratch file, then run the build script above.

If you genuinely need to change the design or add a page feature, edit
`command-center-template.html` / `command-center-page.js` directly and commit the change (same
branch, `Rachel-automation`) so the next refresh inherits it — don't fork the design by hand-
editing a one-off copy of the HTML.

If a source is unavailable (no LinkedIn connector, Semrush not enabled, site fetch blocked),
keep that section's "not connected" placeholder honest — never invent a number to fill a gap.

## Step 5 — Publish
Call the Artifact tool with:
- `file_path`: the rebuilt HTML file
- `url`: `https://claude.ai/code/artifact/82287946-b15f-4126-9570-c83624587863` (updates the
  existing page in place — do **not** omit this, it would create a duplicate artifact)
- `favicon`: `📊` (omit `favicon` on a redeploy — it's only needed on first publish)
- `title`: `Rachel's Command Center`
- `description`: one sentence noting the refresh time and the headline number, e.g. "Refreshed
  7am ET Sep 10 — 3 Smartlead replies never synced to Pipedrive, 54 overdue activities across
  the team."

## Step 6 — Report
Two or three sentences: when it refreshed, the persistent sync-gap count and how long the
oldest open one has been sitting (the number that matters most — call out if any gap has been
open several days with no resolution), Rachel's own overdue/due-today count, and any sources
that were unavailable this run (call these out rather than silently skipping). No further
action needed unless something failed.
