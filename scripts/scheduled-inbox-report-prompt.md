# Daily Reply Triage report (scheduled task prompt)

You are refreshing Yoni's daily "Reply Triage" artifact, unattended, on a schedule. This prompt
is fully self-contained — you have no memory of any prior run.

## What you're updating

- **Artifact:** `https://claude.ai/code/artifact/e0040b83-2b2b-4cf9-aa8b-c2cfe9cc57f5` — republish
  via the Artifact tool using this exact `url` (plus `favicon: "🏷️"`) so it redeploys to the same
  link every time rather than creating a new artifact. Do not resolve it by title via
  `Artifact({action:"list"})` — use the hardcoded URL.
- This is a **standalone** report, separate from the shared "Outbound Command Center" dashboard
  (`scripts/scheduled-dashboard-sync-prompt.md`, a different repo/artifact owned by another
  account) — do not touch that one from this routine.

## Step 1 — Generate the report

From the repo root:

```
node scripts/daily-inbox-report.mjs dist/reply-triage.html
```

This pulls every Smartlead Master Inbox reply from the trailing 7 days (`SMARTLEAD_API_KEY` /
`SMARTLEAD_BASE_URL` come from the environment), fetches the current category id → name mapping
live from `/leads/fetch-categories` (never hardcode it — categories get renamed/added), and writes
a complete self-contained HTML report to the given path. If the script errors, stop and report the
error rather than publishing stale content.

## Step 2 — Sanity check before publishing

- Confirm the script's own stderr summary line (reply count, category count) looks sane — not
  zero, not wildly larger than the last few runs.
- `node --check scripts/daily-inbox-report.mjs` should already pass; if you touched the script,
  re-check it.

## Step 3 — Publish

```
Artifact({
  action: "publish",
  file_path: "dist/reply-triage.html",
  url: "https://claude.ai/code/artifact/e0040b83-2b2b-4cf9-aa8b-c2cfe9cc57f5",
  title: "Reply Triage",
  description: "Every Smartlead reply from the trailing 7 days with its full text and category, refreshed daily.",
  favicon: "🏷️",
})
```

## Step 4 — Report

One or two sentences: total replies in the window, how the category mix compares to "typical"
(call out anything that looks off — e.g. a spike in Do Not Contact/Ignore, or zero Interested
replies), and any error encountered (API failure, empty result set, etc. — don't silently
republish an empty or clearly-wrong report).
