# Rachel's Overdue Desk (scheduled refresh prompt)

You are refreshing "Rachel's Overdue Desk," an Artifact report of Rachel's overdue Pipedrive
activities cross-checked against Smartlead, unattended, on a schedule (9am and 4pm ET daily).
This prompt is fully self-contained — you have no memory of any prior run.

## Access
- Pipedrive: use the connected Pipedrive MCP tools directly.
- Smartlead: via `/home/user/smartlead-api-client` — `SMARTLEAD_API_KEY` is already set in the
  environment (do not print it or write it into any file/commit). Use the committed script
  `scripts/build-overdue-report.mjs`, don't re-derive the Smartlead lookup or HTML by hand.
- Artifact to update (same URL every run — pass this as `url` to the Artifact tool so it
  overwrites in place instead of creating a new one):
  `https://claude.ai/code/artifact/8a2280a3-ca6e-4abb-ac1f-cba0c7d76e75`

## Rachel's Pipedrive identity
Rachel's Pipedrive `owner_id` is `25102178` (confirmed via a note's `user.email ==
"rachel.s@albertscott.com"` with `is_you: true`). Use this directly — don't re-derive it.

## Step 1 — Pull Rachel's open activities
`getActivities` with `done: false`, `owner_id: 25102178`, `sort_by: "due_date"`,
`sort_direction: "asc"`, `limit: 500`. If `additional_data.next_cursor` is non-null, page through
with `cursor` until it's null.

Filter to activities whose `due_date` is strictly before **today** (compare as ISO date strings,
e.g. `"2026-08-19" < "2026-08-20"`). Use the actual current date, not a hardcoded one.

## Step 2 — Resolve contacts and companies
Collect the unique non-null `org_id`s and `person_id`s across the filtered activities.
Batch-fetch with `getOrganizations({ ids: "<comma-separated>", limit: 100 })` and
`getPersons({ ids: "<comma-separated>", limit: 100 })` — chunk into groups of 100 ids if there are
more than 100 of either. From each person record take `name` and the primary `emails[].value`;
from each org record take `name`.

## Step 3 — Build the rows file
For each overdue activity, build one row:
```json
{
  "activity_id": 553,
  "subject": "followup",
  "due_date": "2026-06-02",
  "days_overdue": 77,
  "contact_name": "Joe Zhao",
  "email": "joe@gozleo.com",
  "org_name": "Zleo"
}
```
- `days_overdue`: whole days between the activity's `due_date` and today.
- `contact_name`/`email`: from the linked person, or `null` if the activity has no `person_id` or
  the person lookup failed.
- `org_name`: from the linked person's org, falling back to the activity's own `org_id` if the
  person has none, or `null` if neither resolves.

Write the array to a scratch file, e.g. `/tmp/rachel-overdue-rows.json`.

## Step 4 — Generate the report
From `/home/user/smartlead-api-client`, run:
```
node scripts/build-overdue-report.mjs /tmp/rachel-overdue-rows.json /tmp/rachel-overdue-report.html "<today's date, e.g. Aug 19, 2026 9:00am ET>"
```
This script does the Smartlead lookups itself (lead-by-email, latest campaign, message history)
and writes a complete, self-contained HTML report — don't reimplement its logic. It prints a
one-line summary (`activities / matched / replied`) when done; check that it succeeded before
continuing.

If `SMARTLEAD_API_KEY` is missing or the script errors, don't invent numbers — publish nothing and
report the failure instead (see Step 6).

## Step 5 — Publish
Call the Artifact tool with:
- `file_path`: `/tmp/rachel-overdue-report.html`
- `url`: `https://claude.ai/code/artifact/8a2280a3-ca6e-4abb-ac1f-cba0c7d76e75` (updates the
  existing page in place — do **not** omit this, it would create a duplicate artifact)
- `favicon`: `📋`
- `title`: `Rachel's Overdue Desk`
- `description`: one sentence noting the refresh time and headline numbers, e.g. "Overdue
  Pipedrive activities for Rachel cross-checked against Smartlead, refreshed 4pm ET Aug 19 — 55
  overdue, 12 awaiting your reply."

## Step 6 — Report
One or two sentences: activities pulled, how many matched in Smartlead, how many have unanswered
replies waiting (the number to actually act on), and any errors encountered (missing API key,
Pipedrive/Smartlead failures, etc. — call these out rather than silently skipping). No further
action needed from anyone unless something failed.
