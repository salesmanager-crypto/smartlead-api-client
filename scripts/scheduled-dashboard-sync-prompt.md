# Outbound Command Center — dashboard data refresh (scheduled task prompt)

You are refreshing the **Outbound Command Center** dashboard — a single self-contained HTML
Artifact that gives Yoni one live view across Smartlead, Pipedrive, Gmail, Bluedot and Calendly.
This prompt is fully self-contained; you have no memory of any prior run.

Artifact URL: `https://claude.ai/code/artifact/439c19b3-6769-49ee-8364-8d57bd02d378`
("Outbound Command Center", owned by this account — shared with the org).

Never invent or estimate a number. Every figure you write must trace to a value a connector
actually returned this run. Where a source is unreachable, leave that piece of the DATA block
exactly as it was on the previous publish and say so plainly in your Step 7 report — do not
silently drop it and do not guess a plausible-looking substitute.

## Step 0 — Repo
If `/home/user/smartlead-api-client/.git` doesn't exist, use
`mcp__Claude_Code_Remote__list_repos` to find `salesmanager-crypto/smartlead-api-client` and
clone its https URL there (credentials are pre-configured). If it exists, `cd` in and run
`git fetch origin main && git reset --hard origin/main`. This file
(`scripts/scheduled-dashboard-sync-prompt.md`) and
`docs/Smartlead-Pipedrive-Automation-Workflow.md` are your reference docs for taxonomy, owner
ids and the sync rules — read the latter before Step 2.

## Step 1 — Read the current artifact
Call `Artifact` with `action: "read"` on the URL above. This will very likely tell you the full
source (150KB+) has been saved to a local file and that the version only counts as "viewed" once
you have Read **every line** of that saved file in this same turn, immediately before you publish
— no other tool call in between the last Read and the `Artifact publish` call, and republishing
requires a fresh full re-read even if you already read the file earlier in the run (re-reading a
file an earlier refusal handed you does not count; if content you submit is byte-identical to a
submission that was already refused, it will be refused again even once you satisfy the view
requirement — make sure the file you publish actually differs from anything you tried before).
Budget real turns for this: reading a 1500-line file within the tool's ~25k-token-per-call cap
takes 5-7 sequential `Read` calls with non-overlapping offset/limit ranges. If publish is refused
twice for reasons you don't understand, stop, leave the live artifact untouched, and say so
plainly in your Step 7 report rather than burning the run on retries.

In the `<script>` block, six top-level `const` declarations carry the live data and appear as a
contiguous run near the top, in this order: `CONTACTS`, `THREADS`, `MEETINGS`, `COLLECTIONS`,
`PIPEDRIVE`, then (after a `"use strict";` line and a short comment) `SNAPSHOT` and `TODAY`. Those
seven names are what you rebuild this run — match each one's exact shape to what's already there
(read the existing array/object literal closely before replacing it). Everything else in the file
— all CSS, all HTML, every other `const` (`CATS`, `OWNER_LEAD`, `OWNER_ACTIVITY`, `STANDING_LABEL`,
`BLOCK_RULE`, `STAGES`, `ACT_TYPE`, `USERS`, `CAT_COLOR`, `CATP`, `INTEGRATIONS`, `WINDOWS`), every
function, and the two hand-written `<div class="blocked">` narrative banners in the Automation view
and the Profile view — is configuration and commentary. Do not touch it. If something in that
config looks wrong (an owner id, a status on `INTEGRATIONS`), say so in your Step 7 report instead
of editing it yourself.

## Step 2 — Pull live data

Load tool schemas with `ToolSearch` as you go (e.g. `select:mcp__Pipedrive__getLeads,mcp__Pipedrive__getActivities`).

**Pipedrive** — rebuild the `PIPEDRIVE` object:
- `getLeads`, paginated (limit 100, `start` cursor) until exhausted, non-archived. Compute
  `leads.total`, `leads.byOwner` (owner_id → count), `leads.bySource` (from `origin` /
  `channel_id` — match the existing field's meaning), `leads.byChannel`, `leads.last30` (leads
  added in the last 30 days, same owner breakdown), `leads.noLabels` / `leads.withLabels` (by
  `label_ids` empty or not), `leads.unseen` (`is_archived:false` and `was_seen:false` if exposed;
  otherwise state you could not compute it and keep the prior value), `leads.calendlyTitled`
  (title starts with "Calendly Booking"). Also keep the 20 most recent as `recentLeads`: `id`
  (first 8 chars of the lead's UUID), `t` (title), `o` (owner_id), `s` (source/origin label as
  currently shown, e.g. "Manually created" / "API"), `ch` (channel name or null), `d` (add_time
  date), `lb` (label count), `seen` (was_seen boolean if available, else keep prior).
- `getActivities` with `done=false`, paginated. Compute `activities.open`, `activities.openByOwner`,
  `activities.overdue` (`due_date` before today), `activities.overdueByOwner`,
  `activities.overdueByType`, `activities.oldestDue`. Keep `overdueList` as every overdue activity:
  `id`, `s` (subject), `ty` (type), `o` (owner_id), `d` (due_date), `p` (person_id or null),
  `g` (org_id or null), `l` (lead_id, first 8 chars, or null).

**Contacts, threads, meetings** — this is the cross-referenced part and needs judgment, not just
a raw dump. Follow the same method the existing data used (see the `CONTACTS` entries already in
the DATA block for the exact shape each record needs — `n,e,co,org,p,own,src,cat,camp,bk,bd,last,
th,calLead,calAct,slAct,actState,orgState,actOwner,leadLabels,wantLabel`):
1. Pull the last ~30 days of Smartlead master-inbox replies (same endpoint and classification
   rules as `scripts/scheduled-inbox-sync-prompt.md` Steps 1–2 — read live, don't re-derive from
   the checkpoint file, this is a reporting pass not a sync pass) for the `src:"smartlead"` /
   `cat` / `camp` fields.
2. Pull Calendly bookings the same way `scripts/scheduled-inbox-sync-prompt.md` Step 5 does
   (Gmail `from:notifications@calendly.com`, "New Event:" / "Updated:" subjects) for the `bk[]`
   array (`d`, `t`, `ev` per booking) on each contact.
3. For each person that shows up, `searchPersons` / `searchOrganization` in Pipedrive for `p`,
   `org`, `own`, `orgState` (`"y"` found, `"w"` weak/only-org-no-person, `"n"` not found), and
   look up any Lead/Activity created from a Calendly booking or Smartlead reply for `calLead`,
   `calAct`, `slAct`, `actState` (`"y"` on time, `"w"` exists but off the rulebook, `null` none).
4. `bd` (Bluedot flag: 1 if this person appears as a participant on a Bluedot meeting, else 0) —
   cross-reference against the meetings you pull next.
5. Gmail thread id (`th`) — `search_threads` for the contact's email; if found, that thread's id
   also needs a `THREADS` entry (`id,e,n,co,sub,alias,camp,cat,unread,last,msgs[]`, each message
   `f,fe,t,d,dir,b` with the body HTML-stripped and collapsed).
Keep any existing `CONTACTS` entry whose facts you couldn't re-verify this run (Gmail/Pipedrive
call failed, or the contact is old enough that you didn't re-pull it) rather than deleting it —
note in Step 7 which entries are carried over unverified and how stale they are.

**Bluedot** — `list_meetings` (recent), each with `t` (title), `d` (date), `dur` (ISO 8601
duration as Bluedot returns it, e.g. `PT18M50S`), `c` (collection id or null) → `MEETINGS`.
`list_collections` → `COLLECTIONS` (`id`, `name`, `grp:"internal"` for the internal group,
omit `grp` for client collections — match the existing split).

**Timestamp** — set `SNAPSHOT` to now as `YYYY-MM-DDTHH:MM:SS+08:00` (Asia/Manila) and `TODAY` to
today's date `YYYY-MM-DD` in that same timezone.

## Step 3 — Rebuild the data
Write a new `const CONTACTS=[...]`, `const THREADS=[...]`, `const MEETINGS=[...]`,
`const COLLECTIONS=[...]`, `const PIPEDRIVE={...}`, `const SNAPSHOT=...`, `const TODAY=...` —
same minified single-line-per-const JSON-in-JS style as what's there now (no pretty-printing;
keep the file size sane) — and replace each of those seven declarations in place, verbatim
field names, nothing added or removed from the shape.

## Step 4 — Verify before publishing
Render the edited file headlessly (playwright, chromium at
`/opt/pw-browsers/chromium` — do not run `playwright install`) and confirm:
- No console errors.
- The Automation, Projects, Contacts, Inbox and Profile views all render with the new data
  (`go("automation")` etc., or click through the rail buttons).
- KPI totals are arithmetically consistent (e.g. `activities.overdueByOwner` sums to
  `activities.overdue`; `leads.byOwner` sums to `leads.total`).
- The file is valid JS — no unterminated strings from an escaping mistake in reply/meeting text.
Fix and re-render before continuing if anything fails.

## Step 5 — Publish
Call `Artifact` with `action: "publish"`, the edited file's path, and
`url: "https://claude.ai/code/artifact/439c19b3-6769-49ee-8364-8d57bd02d378"` so it updates in
place rather than creating a new artifact. Keep the existing `title` (from the file's own
`<title>`) and `favicon` — don't change either on a routine data refresh.

## Step 6 — Do not touch the narrative banners
The `<div class="blocked">` banner near the top of the Automation view and the one in the
Profile view are written by hand after a real walkthrough of the data (owner-id confirmations,
specific fixes made, specific gaps found). Leave their text exactly as published. If this run's
numbers make something in those banners factually stale or wrong, say so in your Step 7 report —
a human (or a future targeted session) updates the banner text deliberately, this refresh doesn't.

## Step 7 — Report
Short report: what changed since the last publish (contact count, overdue activities delta,
new Calendly bookings, new Bluedot meetings), anything you carried over unverified and why, any
connector that failed and what you did about it, and anything you noticed that contradicts the
hand-written banners (per Step 6) for a human to review.
