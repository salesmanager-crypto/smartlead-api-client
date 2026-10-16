# Daily Bounce/Spam Trend Check-in (scheduled task prompt)

You are running Albert Scott's daily bounce/spam trend check-in, unattended, on a schedule.
This prompt is fully self-contained — you have no memory of any prior run.

## Why this exists

Following the 2026-08-28 bounce-rate root-cause fix (pausing hard-bounced leads + adding an
unsubscribe link across active campaigns), this tracks whether the two signals that should actually
move as a result — bounce rate on the 8 originally-flagged campaigns, and spam-folder-save counts on
the 6 accounts across 3 previously-flagged domains (`albertscottllc.com`, `albertscottny.com`,
`albertscottco.com`) — are trending the right way. See `scripts/check-bounce-spam-trend.mjs`.

## Access

SmartLead: direct REST client at `/home/user/smartlead-api-client` (`src/client.js` /
`scripts/check-bounce-spam-trend.mjs`). `SMARTLEAD_API_KEY` / `SMARTLEAD_BASE_URL` come from the
environment — do not hardcode, guess, or fabricate a key. If `SMARTLEAD_API_KEY` isn't set, stop and
report that plainly rather than reporting a fake clean run.

Google Sheets: `src/googlesheets.js`, authenticated via `GOOGLE_SERVICE_ACCOUNT_EMAIL` /
`GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY` / `GOOGLE_SHEETS_SPREADSHEET_ID` in the environment (the same
credentials the Fathom → Task Tracker Sync automation already uses in this environment).

## Step 1 — Run the script

```
node scripts/check-bounce-spam-trend.mjs
```

This appends today's snapshot to the "Bounce Spam Trend" tab of the Google Sheet configured by
`GOOGLE_SHEETS_SPREADSHEET_ID` (see `src/googlesheets.js`) and prints the delta against the previous
entry for each of the 8 campaigns and 6 accounts. The script writes directly to the sheet — no git
commit or push is needed to persist the trend, since a direct `git push` to `main` from an unattended
auto-mode session is blocked by design. If `GOOGLE_SERVICE_ACCOUNT_EMAIL`,
`GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY`, or `GOOGLE_SHEETS_SPREADSHEET_ID` isn't set, the script will
fail outright — report that plainly rather than reporting a fake clean run.

## Step 2 — Report

2-4 sentences: today's combined bounce rate across the 8 campaigns (and whether it's trending up,
down, or flat vs. the previous entry), the same for the 3 flagged domains' spam-save counts, and any
individual campaign or account that moved sharply in either direction. If a metric got worse, say so
plainly — don't bury it. If `SMARTLEAD_API_KEY` was missing or the script errored, report that
instead of fabricating numbers. This report is the routine's final message.
