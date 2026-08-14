# Campaign Analytics Report (scheduled task prompt)

You are running Albert Scott's recurring Smartlead campaign analytics report, unattended,
on a schedule. This prompt is fully self-contained — you have no memory of any prior run.

## Access
- SmartLead: direct REST API via `/home/user/smartlead-api-client` (`src/client.js` / `src/cli.js`).
  Base URL and API key load from `/home/user/smartlead-api-client/.env`. Company account.
- Report engine: `scripts/campaign-analytics-report.mjs` + `scripts/build-analytics-dashboard.mjs`
  in that same repo.

## Step 1 — Generate the report
From `/home/user/smartlead-api-client`, run:
```
node scripts/campaign-analytics-report.mjs --since=2026-07-01 --end=<today, YYYY-MM-DD>
```
- `--since` is the campaign-creation cutoff (only campaigns created on/after this date are
  included) — keep it at `2026-07-01` unless the user has told you to move it.
- `--end` defaults to today if omitted; pass it explicitly for a reproducible run.
- Add `--status=ACTIVE` if the user only wants currently-active campaigns that run; default
  is all statuses (so paused/completed campaigns from the window still show up).
- The script prints a text summary to stderr and writes a JSON report to
  `scripts/output/<start>_<end>-campaign-report.json`.

## Step 2 — Build the dashboard
```
node scripts/build-analytics-dashboard.mjs scripts/output/<start>_<end>-campaign-report.json
```
This writes a self-contained HTML file next to the JSON (same name, `.html`).

## Step 3 — Publish
Load the `artifact-design` skill's guidance is already baked into the generated page — just
call the `Artifact` tool on the resulting `.html` file to publish/update the dashboard. If a
prior run already published one for this recurring report, republish to the **same URL**
(pass its `url`) rather than creating a new artifact each time — find the URL via
`Artifact({action: "list"})` if it isn't already in context, or ask the user for it once and
remember it in this prompt file going forward.

## Step 4 — Report
One-paragraph summary in your reply: date range covered, total sent/open/click/reply/bounce
rates, number of campaigns flagged critical/warning, number of repeat non-openers and chronic
bouncers found, and the artifact link. If any campaign fetch or lead-statistics fetch failed
(check stderr for "failed:" lines), say so explicitly rather than silently reporting partial
data as complete.

## Step 5 — Act on the obvious ones (only if the user has pre-authorized this)
Do **not** block domains, pause leads, or pause campaigns automatically unless the user has
explicitly told you, in a prior turn or in this prompt's future revisions, that this report
run should also take action. By default this is a read-only reporting run — surface the
flagged leads/campaigns and let the user decide.

## Cadence notes
This prompt is designed to be fired weekly (e.g. Monday mornings) via a Routine bound to a
fresh session each time. If the user asks to change cadence, thresholds, or the `--since`
cutoff, edit this file — don't just change it verbally for one run and lose the change.
