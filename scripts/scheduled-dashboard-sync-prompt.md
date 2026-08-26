# Outbound Command Center Dashboard Sync (scheduled task prompt)

You are refreshing Albert Scott's Outbound Command Center dashboard, unattended, on a schedule.
This prompt is fully self-contained — you have no memory of any prior run.

## What you're updating

- **Artifact:** `https://claude.ai/code/artifact/208a1cba-48d9-43a3-bb98-75b6f85ad048` — republish via
  the Artifact tool using this exact `url` (plus `file_path: "command-center.html"`) so it redeploys
  to the same link rather than creating a new one. Do **not** resolve the URL by title via
  `Artifact({action:"list"})` — there are at least two other, unrelated artifacts also titled
  "Outbound Command Center" (a stale pre-rebuild snapshot, and a separate Phase-1 dashboard on its
  own daily-refresh routine sourced from a different repo entirely) — publishing over either of
  those by mistake would break someone else's live link. Use the hardcoded URL above; if it ever
  needs to change, update it here deliberately, don't let a routine run guess it.
- **Repo file:** `command-center.html` in the `yeikkomae-work-mode/albertscott` repo — commit and
  push your changes there too (branch per your standing instructions, or `main` if none given),
  so the Artifact and the repo never drift apart.

Only the `const DATA = {...}` block (search for `/* ===== DATA BLOCK` / `END DATA BLOCK ===== */`)
and its immediately-surrounding cadence text change. Never touch layout, CSS, or the render
functions below the data block — this is a data refresh, not a redesign.

## Access

- **SmartLead:** the `Albertscott_Smartlead` MCP connector if available in your session; otherwise
  the direct REST client at `/home/user/smartlead-api-client` (`src/client.js`). Whichever you use,
  never guess numbers — every figure on the dashboard must trace to an actual API response.
- **Pipedrive:** the connected Pipedrive MCP tools.
- **Gmail (Calendly bookings):** the connected Gmail MCP, searching
  `from:notifications@calendly.com` with subject starting "New Event:" (a reschedule shows
  "Updated:" instead) — same source `scripts/scheduled-inbox-sync-prompt.md` uses. If the Gmail
  account reachable from your session returns no matches, **do not conclude there are no new
  bookings** — it may be scoped to a different inbox than `yoni@albertscott.com`. Say so plainly in
  your report and leave the existing `calendly.bookings` array untouched rather than guessing or
  zeroing it out.
- **HeyReach:** `/home/user/smartlead-api-client/src/heyreach.js`, needs `HEYREACH_API_KEY` (and
  `HEYREACH_ORG_API_KEY` for workspace-level calls) in `.env` — see `.env.example` for where to get
  them. If `.env` doesn't have them (it won't, by default — `.env` is gitignored and this repo is
  cloned fresh per session), **do not fetch or guess** — leave `heyreach` in the DATA block exactly
  as it was and say so in your report.
- **Bluedot:** no MCP connector and no API client exist yet. Before falling back, check whether
  `command-center.html` in the repo already carries newer Bluedot data than what's in the currently
  published Artifact (e.g. because someone updated it by hand, or a browser-based pull happened in
  a prior session) — if the repo's `bluedot` block is more recent, carry that forward; otherwise
  leave the existing `bluedot` block untouched. Never fabricate a meeting or count.
- **AIOSEO:** albertscott.com's own AIOSEO REST API, needs an application password documented in
  `RESOURCES/Tools & API Details/` in the `Client-Management-System` repo (the "sales" app
  password). No client wraps this yet — if you don't have the credential loaded, leave `seo`
  untouched and say so.

Every one of the four sections above (HeyReach, Bluedot, AIOSEO, and Calendly-when-Gmail-comes-up-empty)
degrades the same way: **carry the last known value forward, never zero it out or invent a plausible
number, and call out in your report exactly which sections you could not refresh and why.** A
dashboard that quietly goes stale is fine; one that quietly goes wrong is not.

## Step 1 — Pull SmartLead

- Campaigns: list all campaigns, compute `campaignsTotal` and `statusMix` (ACTIVE / COMPLETED /
  PAUSED / DRAFTED / STOPPED counts), and rebuild the `campaigns` array — one row per **ACTIVE**
  campaign only, as `[name-with-client-prefix-stripped, owner, "Active"]`. Owner is the text before
  the first " - " in the campaign name (e.g. "Rachel - ISM Cologne" → name `ISM Cologne`, owner
  `Rachel`); no prefix → owner `Unlabeled`; a legacy prefix like "John" → keep as-is (dashboard
  shows "John (legacy)" — match that exact label if the campaign is still John's).
- Email accounts: paginate (the API caps each page at 100) until you've seen every account; total
  count is `inboxesTotal`.
- Unread Master Inbox replies: pull with `sortBy: REPLY_TIME_DESC`. `unreadMasterInbox` is the total
  count; `oldestUnreadReply` is the `last_reply_time` of the **last** item in that DESC-sorted list
  (i.e. the oldest of the unread set), not necessarily the oldest reply ever — if `hasMore` is true,
  paginate until you have the true tail.
- Last 7 days: overall stats (sent/opened/replied/bounced) for `start_date` = 7 days before today,
  `end_date` = today.

## Step 2 — Pull Pipedrive

- Overdue activities: `getActivities(done: false, sort_by: due_date, sort_direction: asc, limit: 100)`,
  paginating via `cursor` until you reach a page where every `due_date >= today` (ascending sort
  means overdue items are exhausted as soon as you cross into today's date — you don't need to
  paginate further once that happens). `overdueTotal` = count of all items with `due_date < today`
  across every page. `oldestDate`/`oldestDays` come from the very first page (already sorted
  ascending). `byOwner` and `byType` are group-by counts across the full overdue set.
- Rows for the table: take the 40 oldest overdue activities. Resolve `person_id` → name via
  `getPersons(ids: "...")` (batch, comma-separated, max 100 per call) and `org_id` → name via
  `getOrganizations(ids: "...")`. A null `person_id` renders as `"—"` with an empty org. A person
  with no `org_id` renders their email domain in the org column instead (matches the existing
  Calendly-sourced rows). Row shape: `[due_date, days_overdue, type, subject, lead_name, org_name,
  String(owner_id)]` — `owner_id` stays a string (the render code keys off it as one).
- Owner ID → label mapping is hardcoded in the dashboard's JS (`ownerLabel()`): `26939288` → Yoni,
  `25102178` → "Owner A", `25109251` → "Owner B", anything else → `"#" + id`. Don't duplicate that
  mapping in the DATA block — just pass the raw numeric-string owner_id and let the page resolve it.
  If Eikko has confirmed real names for Owner A / Owner B since this was last true, update the JS
  function itself, not the data.

## Step 3 — Calendly, HeyReach, Bluedot, AIOSEO

Follow the degrade-gracefully rules in **Access** above for each. Only overwrite a section's block
in DATA if you actually pulled fresher data for it this run.

## Step 4 — Update routine bookkeeping

In the `routines` array, update the entry named `outbound-command-center-3h-sync`: set `lastFired`
to this run's timestamp (ISO 8601, UTC) and keep `status: "live"`. Leave every other routine's entry
untouched — this prompt only knows about its own run, not whether the others actually fired; don't
guess at their `lastFired` values.

## Step 5 — Rebuild the DATA block

Set `lastSynced` to this run's timestamp. Replace the `const DATA = {...}` object with the updated
one, keeping the same key structure (`pipedrive`, `smartlead`, `heyreach`, `bluedot`, `calendly`,
`seo`, `automationLog`, `routines`) — `automationLog` is a fixed historical record of the manual QA
pass done 2026-08-25 and is never touched by this routine. Serialize as compact single-line JSON
(matches the file's existing style) so the diff stays reviewable.

## Step 6 — Validate before publishing

- Extract the `<script>` contents and check they still parse (e.g. `node --check`) — a malformed
  DATA object breaks the whole page silently.
- Spot-check that numbers actually changed where you had live access, and stayed identical where
  you didn't (a value that changed with no corresponding pull is a bug, not a coincidence).

## Step 7 — Publish and commit

1. `Artifact({action:"publish", file_path: "command-center.html", url:
   "https://claude.ai/code/artifact/208a1cba-48d9-43a3-bb98-75b6f85ad048", favicon: "📡"})` — same
   `url` and `favicon` every run so it redeploys in place rather than creating a new artifact.
2. Commit `command-center.html` in the `albertscott` repo with a message describing what actually
   changed (which sections refreshed, which carried forward and why, notable deltas like the
   Pipedrive overdue count). Push.

## Step 8 — Report

One-paragraph summary: what refreshed live (with headline deltas — e.g. "Pipedrive overdue: 99,
down from 103"), what carried forward and why (missing credential, no connector, Gmail scope
mismatch, etc.), and any errors encountered. If nothing at all could be pulled live, say that
plainly rather than silently republishing stale data as if it were fresh — a no-op run is fine, a
misleading one is not.
