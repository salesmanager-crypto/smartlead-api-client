# Lead Recap / Overview Workflow
**Built for Yoni — per-lead recap/overview for Pipedrive re-engagement**

Given a lead list (the "Pipedrive Reengagement" Google Sheet — 3 tabs: **Master List**
[Pipedrive-sourced], **Smartlead Interested+followup**, **Salesforce**), this produces a
2-4 sentence recap per lead — what happened, where things stand now, and a short synopsis
useful for re-engaging them in Pipedrive — pulled from Gmail + SmartLead (plus whatever the
sheet already recorded from Pipedrive/Salesforce activity).

There's no MCP tool that reads/writes individual cells of a live Google Sheet (Drive's
`read_file_content`/`download_file_content` return a flattened, hard-to-parse render or
the whole file; there's no ranged-write tool at all) — the repo's `src/googlesheets.js`
*can* write cells, but only with a Google service-account key shared onto the sheet as
Editor, which wasn't available for this run. So this pipeline works from a downloaded
`.xlsx` snapshot and produces a new workbook, rather than editing the live sheet in place.

## Pipeline

1. **Export the sheet.** Via Google Drive's `download_file_content` (fileId of the sheet,
   `exportMimeType: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet`),
   base64-decode, save to disk.
2. **`node scripts/lead-recap-smartlead-lookup.mjs <emails.json> <output.json>`** — bulk
   SmartLead lookup. Given a flat JSON array of emails, looks each up via `GET /leads/`,
   and for matches pulls campaign associations + the last SENT/REPLY message per campaign,
   with category/lead_status cross-referenced from an all-time Master Inbox reply-history
   scan (neither `getCampaignsForLead` nor `getLeadMessageHistory` expose category
   directly). Reads `SMARTLEAD_API_KEY`/`SMARTLEAD_BASE_URL` from `.env` per repo
   convention. On ~1,400 emails this takes several minutes — run it in the background.
3. **`python3 scripts/lead-recap-prepare-batches.py <sheet-export.xlsx> <out-dir>`** —
   extracts the 3 tabs to `leads-<tab>.json`, collects every unique email to
   `all-unique-emails.json` (feed this to step 2), and chunks each tab into ~15-row
   batches under `<out-dir>/batches/`, recorded in `batch-manifest.json` — the `manifest`
   arg for the Workflow.
4. **Run `scripts/lead-recap-workflow.mjs` via the Workflow tool** (not `node` directly —
   `agent()`/`parallel()`/`phase()` only exist in that runtime), passing
   `args: { manifest: <batch-manifest.json contents>, smartleadLookupFile: <step 2 output path> }`.
   One agent per batch: reads its lead rows + the SmartLead lookup file, searches Gmail
   per lead (`mcp__Gmail__search_threads`, `(from:<email> OR to:<email>)`), and returns a
   structured recap per lead. ~115 batches/1,700 leads took ~10 subagent-minutes of
   wall-clock and ~2,900 tool calls in the original run.
5. **`python3 scripts/lead-recap-assemble-output.py <workflow-result.json> <batch-manifest.json> <output.xlsx>`**
   — merges recaps back onto each tab's original rows **positionally** (recap *i* belongs
   to batch row *i* — matching by the agent-echoed key string is unreliable: rows with no
   email all echo back the literal string `"null"`, and an agent occasionally botches the
   echoed key on one row even though row order is preserved). Falls back to key-matching
   only if a batch's recap count doesn't match its row count, and marks anything still
   unresolved `"NOT PROCESSED"` rather than leaving it silently blank. Writes one output
   sheet per tab (original columns + Overview / Current Status / Last Touchpoint) plus a
   Run Summary tab.

`workflow-result.json` is the Workflow tool's `result` field from its completion
notification (or the `"result"` key in its output file) — pull that out before passing it
to step 5, don't pass the whole notification payload.

## Delivering the output

The finished workbook mirrors "Complete Overview" (Master List) and
"Lead Overview"/"LeadOverview" (Salesforce) — merge it back into the live sheet by
Person ID / email (VLOOKUP), or hand the file to Yoni directly to import
(Drive → File → Import → Insert new sheet(s), or open as-is in Excel).

## Quality notes from the first full run (Aug 2026, 1,705 leads, 0 batch errors)

- Agents correctly distinguished real replies from bounces/mailer-daemon notices/OOO
  autoresponders rather than treating them as genuine interest — worth spot-checking on
  future runs, since it's an easy way for a recap to overstate engagement.
- Agents correctly flagged rows that were obviously test/dummy data in the source sheet
  (`test@example.com`, `demo@acmecorp.com`, "John Doe" / "ACME Inc", etc.) as such, rather
  than fabricating history.
- One out of 1,705 recaps came back as a literal placeholder (`"overview": "placeholder"`)
  — a real per-agent failure, not a data issue. Worth a quick pass over the output for any
  row whose Overview is unusually short or says "placeholder" before relying on it, since a
  single flaky batch won't otherwise be visible (the batch as a whole still "succeeds").
