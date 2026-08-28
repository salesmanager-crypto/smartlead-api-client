# Daily Bounced-Lead Pause (scheduled task prompt)

You are running Albert Scott's daily bounced-lead pause job, unattended, on a schedule.
This prompt is fully self-contained — you have no memory of any prior run.

## Why this exists

Root-cause review on 2026-08-28 found that `stop_lead_settings` on Smartlead campaigns only halts
a lead's sequence on a reply — never on a bounce. A lead that hard-bounces on step 1 can still get
sent step 2, step 3, etc. weeks later, bouncing again each time and damaging sender reputation. This
job finds every `is_bounced` lead across all ACTIVE campaigns and pauses them via the Smartlead API
so later sequence steps never fire. See `scripts/pause-bounced-leads.mjs` for the implementation.

## Access

SmartLead: direct REST client at `/home/user/smartlead-api-client` (`src/client.js` /
`scripts/pause-bounced-leads.mjs`). `SMARTLEAD_API_KEY` / `SMARTLEAD_BASE_URL` come from the
environment — do not hardcode, guess, or fabricate a key. If `SMARTLEAD_API_KEY` isn't set, stop and
report that plainly rather than reporting a fake "0 bounces" clean run.

## Step 1 — Run the script

```
node scripts/pause-bounced-leads.mjs --all-active --apply
```

`--all-active` covers every ACTIVE campaign on the account, not a fixed list, so new campaigns get
the same protection automatically without this file needing to be updated. It logs a per-campaign
summary to `scripts/pause-bounced-leads-log.txt` (git-ignored — aggregate counts only, no lead-level
emails/PII, safe to read/report from).

## Step 2 — Sanity check

- Confirm the script exited 0 and printed a summary line for every ACTIVE campaign it saw.
- Any campaign with `failed > 0` is worth calling out in the report, not silently dropped.

## Step 3 — Report

One or two sentences: total bounced leads paused this run (sum across campaigns), which campaign(s)
had the most, any failures, and whether the script ran at all — if `SMARTLEAD_API_KEY` was missing
or the script errored, say so plainly rather than reporting zero pauses as if it were a clean run.
This report is the routine's final message — there is no further notification step.
