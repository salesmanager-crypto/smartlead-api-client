# Fathom → Task Tracker Sync (scheduled task prompt)

You are running Albert Scott's Fathom meeting → Task Tracker sync, unattended, on a schedule.
This prompt is fully self-contained — you have no memory of any prior run.

## Access
- Fathom: direct REST API via `/home/user/smartlead-api-client` (`src/fathom.js`). API key loads
  from `/home/user/smartlead-api-client/.env` (`FATHOM_API_KEY`).
- Task Tracker: Google Sheets API via `src/googlesheets.js` / `node src/cli.js gs:*`. Credentials
  load from `.env` (`GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY`,
  `GOOGLE_SHEETS_SPREADSHEET_ID`). Sheet tab is `Sheet1`; columns A–D are Task, Category, Status,
  Notes.
- Checkpoint file: `/home/user/smartlead-api-client/.fathom-last-checkpoint` — an ISO 8601
  timestamp of the newest meeting `created_at` successfully processed. Read it at the start; write
  the newest value you processed back to it at the end. If the file doesn't exist, default to 7
  days before now.

## Scope — read this before touching anything
- **Only ever consider meetings whose title matches `/albert\s*-?\s*scott/i`** (contains some
  spacing/hyphenation of "Albert Scott" — matches "Yoni - Albertscott", "Albert-Scott", "Yoni -
  Albertscott Work Task", etc.). `FathomClient.listAlbertScottMeetings()` already enforces this —
  never call the raw Fathom API directly and never loosen this filter. A misspelled title (seen in
  practice: "Yoni - Alberscott", missing a letter) will not match, and that's intentional — do not
  fuzzy-match titles to work around it; a near-miss risks pulling in an unrelated meeting instead.
- Never fetch, log, or reference content (summary/transcript/action items) for any meeting outside
  that filter, even out of curiosity. It's fine that `listAlbertScottMeetings()` sees every
  meeting's title to filter them — just never go further than the title for a non-match.

## Step 1 — Pull new Albert Scott meetings
Use `FathomClient.listAlbertScottMeetings({ createdAfter: <checkpoint> })` (import the client
directly in a short Node script, or call it from a REPL) — do **not** use the unfiltered-by-date
`fa:meetings` CLI command here, since that pulls the account's whole history every time. If
`matches` is empty, skip straight to Step 6 and report "no new Albert Scott meetings since
<checkpoint>."

## Step 2 — Pull action items for the matched meetings only
Call `FathomClient.getMeetingContent(matches)` to get `action_items`, `default_summary`, and
`transcript` for just those meetings — this is what makes the per-meeting content fetch itself
scoped server-side to only Albert Scott recordings (see the `recording_ids[]` filter in
`getMeetingContent`). Skip any meeting whose `action_items` come back empty or null.

## Step 3 — Read the current tracker
`node src/cli.js gs:read "Sheet1!A2:D"` (skip the header row) for every existing task's
Task/Category/Status/Notes.

## Step 4 — Classify each action item: new vs. possible match
For each Fathom action item, compare its description against every existing Task cell:
- **New**: no existing task shares significant overlap with it. Heuristic: normalize both to
  lowercase, strip punctuation, and check for either a substring match in either direction or
  meaningful word overlap on the distinctive nouns (not just "build"/"the"/"a"). When genuinely
  unsure, treat it as new — a duplicate row is far cheaper to clean up later than a silently
  dropped task.
- **Possible match**: it clearly refers to the same work as an existing row (same project name,
  same key nouns, same person it's blocked on).

## Step 5 — Act
- **New action items** → append immediately, no approval needed (an append can't corrupt existing
  data):
  `node src/cli.js gs:append "Sheet1!A:D" '["<task text>","Fathom - <meeting date, e.g. Aug 18>","Not Started","From meeting: <meeting title>, <date>. <assignee if Fathom gave one>"]'`
- **Possible matches to an existing row** → do **NOT** edit that row yourself. Collect it into a
  "Suggested updates" list for Step 8 instead: the existing task's exact text, its current Status,
  what the meeting implies it should change to, and why you think it's the same task. A human
  reviews these and applies them by hand — this script never overwrites a row that already exists.

## Step 6 — Update checkpoint
Write the newest `created_at` across every meeting processed this run to `.fathom-last-checkpoint`
(leave the file unchanged if Step 1 found nothing new).

## Step 7 — Log every meeting processed
Append one row per Albert Scott meeting whose action items you pulled to
`/home/user/smartlead-api-client/logs/fathom-sync-log.csv` (create it with a header row if it
doesn't exist yet). Columns, in order:
`timestamp,meeting_title,meeting_created_at,action_items_found,new_tasks_added,possible_matches_flagged`

## Step 8 — Report
One-paragraph summary covering: how many Albert Scott meetings were found since the checkpoint;
how many non-Albert-Scott meetings were seen in the same listing call and skipped (**count only —
never their titles or content**); how many action items were extracted; how many new rows were
added (list each one); and the full "Suggested updates" list from Step 5, for human review. Call
out any errors explicitly (a Sheets write failing on a permissions error, Fathom returning nothing,
an unexpected payload shape) rather than silently swallowing them.
