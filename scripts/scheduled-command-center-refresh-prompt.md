# Yoni Sales & Marketing Command Center refresh (scheduled task prompt)

You are refreshing Yoni's Sales & Marketing Command Center dashboard, unattended, on a schedule
(daily, 8:00 am Eastern). This prompt is fully self-contained; you have no memory of prior runs.

## What you're updating

- **Artifact:** `https://claude.ai/code/artifact/e803bcae-9873-490a-8b87-f1e352bc7597`. Republish
  with the Artifact tool using this exact `url` and `file_path: "dashboards/yoni-command-center.html"`
  so it redeploys to the same link. Do **not** resolve the URL by title via `Artifact({action:"list"})`;
  there are other artifacts with similar names. Use the hardcoded URL.
- **Repo file:** `dashboards/yoni-command-center.html` in this repo (`salesmanager-crypto/smartlead-api-client`).
  Commit and push the refreshed file on `main` so the artifact and the repo never drift.

Only the `DATA BLOCK` inside the page's `<script>` changes on a refresh (`/* ===== DATA BLOCK` to
`END DATA BLOCK ===== */`). The scripts below rewrite it for you. Never edit layout, CSS, or the
render functions on a scheduled run; this is a data refresh, not a redesign.

## Access

- **SmartLead:** `SMARTLEAD_API_KEY` from the environment (or `.env`). If it is missing, stop and
  report that; do not guess numbers.
- **HeyReach:** `HEYREACH_API_KEY` from the environment (or `.env`). If missing, skip step 2; the
  build script carries the previous `LINKEDIN` block forward and says so.
- **Pipedrive:** `PIPEDRIVE_API_TOKEN` from the environment (or `.env`) drives
  `dashboards/pull/pull-pipedrive.mjs`, which needs no connector. If the token is missing but the
  Pipedrive MCP connector is available, use the connector as described in step 3b. If neither is
  available, stop and report that; the overdue list and the sync check cannot be built without
  Pipedrive.

Every figure on the dashboard must trace to an API response from this run or be carried forward
from the previous page with a note in your report. Never invent a plausible number.

## Step 1: SmartLead

```
node dashboards/pull/pull-smartlead.mjs
```

Writes `dashboards/pull/out/smartlead-pull.json` (all campaigns with all-time analytics, yesterday's
sends per campaign, every inbox, the trailing 7 days of Master Inbox replies with categories).
Takes 2 to 3 minutes. If it exits non-zero, stop and report the error.

## Step 2: HeyReach

```
node dashboards/pull/pull-heyreach.mjs
```

Writes `dashboards/pull/out/heyreach-pull.json`. Skip if the key is missing.

## Step 3a: Pipedrive over REST (preferred)

```
node dashboards/pull/pull-pipedrive.mjs
```

Writes every file step 3b describes under `dashboards/pull/out/pipedrive/`. If it succeeds, skip 3b.

## Step 3b: Pipedrive over the connector (fallback when there is no API token)

Save each raw connector response as a JSON file under `dashboards/pull/out/pipedrive/`. Large
responses are saved by the harness to a tool-results file; copy that file to the path below rather
than retyping anything. Every file is the raw `{success, data, additional_data}` object.

1. `getActivities(done: false, sort_by: "due_date", sort_direction: "asc", limit: 500)` →
   `activities-1.json`; if `additional_data.next_cursor` is set, keep paging with `cursor` into
   `activities-2.json`, `activities-3.json`, ... until the cursor is null.
2. `getDeals(status: "open", limit: 100)` → `deals-open.json`; `getDeals(status: "won", limit: 100)`
   → `deals-won.json`; `getDeals(status: "lost", limit: 100)` → `deals-lost.json`.
3. `getStages()` → `stages.json`.
4. `getLeads(limit: 500)` → `leads-1.json`; page with `start` if it returns 500.
5. `getPersons(limit: 500, sort_by: "id", sort_direction: "desc")` → `persons-1.json`, then page with
   `cursor` into `persons-2.json`, ... until the cursor is null. Every page matters: the sync check
   matches reply emails against every person on file.
6. `getOrganizations(limit: 500, sort_by: "id", sort_direction: "desc")` → `orgs-1.json`, `orgs-2.json`, ...

## Step 4: Build and apply

```
node dashboards/pull/build-constants.mjs
node dashboards/pull/apply-constants.mjs
```

`build-constants` prints a summary line (campaign count, inbox-log rows, sync gaps, overdue, deals,
persons, orgs, warnings). Sanity-check it: campaigns in the high 100s, persons in the thousands,
overdue not zero. A warning means a section was carried forward; say so in the report.
`apply-constants` rewrites the DATA BLOCK and runs `node --check` on the page script. If either
exits non-zero, stop and report; do not publish a broken page.

## Step 5: Publish and commit

1. `Artifact({action:"publish", file_path:"dashboards/yoni-command-center.html",
   url:"https://claude.ai/code/artifact/e803bcae-9873-490a-8b87-f1e352bc7597"})`. Do not pass a
   favicon (keeps the existing one).
2. Commit `dashboards/yoni-command-center.html` with a message that names the date and the
   headline deltas (overdue count, sync gaps, replies yesterday). Do not commit anything under
   `dashboards/pull/out/`; it is gitignored. Push to `main`.

## Step 6: Report

One paragraph: the data date, overdue follow-ups (and change vs. the previous page's OVERDUE
length, which you can read from the git diff), replies yesterday and how many are uncategorized,
and the number of **Sync missing** rows today with the lead names and campaigns. If any section was
carried forward or any step failed, say exactly which and why. A no-op run is fine; a misleading one
is not.
