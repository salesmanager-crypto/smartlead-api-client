# Pipedrive Overdue Activity Alert (scheduled task prompt)

You are sending Yoni's Pipedrive overdue-activity alert, unattended, on a schedule (weekday
mornings). This prompt is self-contained; you have no memory of any prior run. Read-only in
Pipedrive: never change, close or reschedule an activity from this routine.

## What it sends
One email via the Gmail connector to **yoni@albertscott.com**: every open Pipedrive activity
assigned to Yoni (`owner_id` **25109251**) whose due date is before today (America/New_York),
oldest first, grouped into Over 30 days / 8 to 30 days / 1 to 7 days, plus any possible
duplicates (the same contact carrying the same open subject twice). Today's due items are counted
but not listed; the Morning Briefing already covers them.

## Step 0 - Repo
In `/home/user/smartlead-api-client` run `git fetch origin main && git checkout -B main origin/main`
(clone `https://github.com/salesmanager-crypto/smartlead-api-client.git` there first if it isn't
present). All paths below are relative to the repo root.

## Step 1 - Get the data
**If `PIPEDRIVE_API_TOKEN` and `PIPEDRIVE_COMPANY_DOMAIN` are set** (`test -n` only, never print
them), skip to Step 2 and run the script in live mode (no `--activities`).

Otherwise use the Pipedrive connector and save each raw response, unchanged, as a JSON file in your
scratchpad. A large response is saved to a tool-results file by the harness; copy that file.
1. `getActivities` with `owner_id: 25109251`, `done: false`, `limit: 500`, `sort_by: "due_date"`,
   `sort_direction: "asc"` → `activities.json`. If `additional_data.next_cursor` is set, fetch the
   next page with `cursor` and merge the `data` arrays into one `{"data": [...]}` file.
2. From the activities due before today, collect the distinct `person_id` and `org_id` values.
   `getPersons` with `ids` (100 per call, merge pages) → `persons.json`; `getOrganizations` with
   `ids` → `orgs.json`.
3. `getLeads` with `owner_id: 25109251`, `limit: 500` → `leads.json`.
If `getActivities` fails twice, stop: email nothing and report the error (an empty or partial
alert is worse than none).

## Step 2 - Build the email
```
node scripts/pipedrive-overdue-digest.mjs --out <scratchpad>/overdue \
  --activities <scratchpad>/activities.json --persons <scratchpad>/persons.json \
  --orgs <scratchpad>/orgs.json --leads <scratchpad>/leads.json
```
(live mode: `node scripts/pipedrive-overdue-digest.mjs --out <scratchpad>/overdue`)

It prints one JSON line with `overdue`, `dueToday`, `oldestDays`, `byBucket`, `duplicates` and
`subject`, and writes `overdue.html` and `overdue.txt`. If it exits non-zero, stop and report the
error. Never write or edit the email body by hand and never invent a count.

## Step 3 - Send
- `overdue` is 0 and `duplicates` is 0: send nothing.
- Otherwise call Gmail `send_message` with `to: ["yoni@albertscott.com"]`, `subject`: the script's
  `subject` value, `htmlBody`: the full contents of `overdue.html`, `body`: the full contents of
  `overdue.txt`.

## Step 4 - Report
Two lines: overdue count and oldest age, duplicates found, and whether the email was sent (with the
Gmail message id) or skipped and why. No em dashes.
