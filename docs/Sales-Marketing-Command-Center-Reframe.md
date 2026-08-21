# Yoni Sales & Marketing Command Center — Reframe Plan

**Status:** Planning only — not implemented. Per Yoni's note on the Aug 21, 2026 feedback
email ("don't act on them yet; just set this as a task to reframe"), this document maps out
the proposed structure, click-throughs, and data before any dashboard code changes are made.

**Source:** Yoni Lebovits, "Yoni Sales & Marketing Command Center — Notes," Aug 21, 2026.

---

## 1. What exists today vs. what's being asked for

The current live dashboard (`albertscottautomation.html`) is scoped to one thing: a
Smartlead → Pipedrive reconciliation ledger — did each qualifying reply get written to
Pipedrive as Org + Person + Lead + Activity per the rulebook in
`docs/Smartlead-Pipedrive-Automation-Workflow.md`. It's a QA tool for one automation, not
a sales/marketing command center.

Yoni's ask is a **reframe**, not a bugfix: the automation-compliance view becomes one
sub-view inside a much larger structure — a home dashboard plus five (or more) channel
sections the user clicks into. Sections below map his notes to concrete pages, click-throughs,
and — critically — which data is actually available today vs. which requires new plumbing.

---

## 2. Proposed site map

```
Home (at-a-glance)
├─ SmartLead / Outbound Email
│  ├─ Campaigns (list, sort, filter)
│  │  └─ Campaign detail
│  ├─ Inboxes / Deliverability
│  └─ Domains
├─ LinkedIn Outreach (HeyReach)
│  ├─ Campaigns
│  └─ Responses / connections
├─ Pipedrive
│  ├─ Activities / follow-ups (Overdue / Due today / Upcoming)
│  └─ "Pipedrive Sync" — pending definition (see §7)
├─ SEO (Semrush)
├─ SmartScout
├─ Claude Activity / Automation Log
│  └─ Smartlead ↔ Pipedrive reconciliation ledger (today's whole dashboard, demoted to here)
└─ General — Software & Infrastructure
   └─ Per-tool detail (cost, seats, domains, inboxes, accounts, credential-manager link)
```

Each hero section is a **click-through, not a widget** — the home dashboard shows only
enough to answer "what happened / what needs attention," everything else lives one click
away, per Yoni's closing "Core Principle."

---

## 3. Home dashboard — at-a-glance

| Widget | Answers | Data | Source (available now) |
|---|---|---|---|
| Emails sent yesterday | What happened | Count of sent emails, filtered to yesterday | `client.getAnalyticsOverview()` / `getCampaignAnalyticsByDate()` — per-campaign, needs summing across active campaigns |
| Replies received yesterday | What happened | Count of new Master Inbox replies | `client.getMasterInboxReplies()` filtered by date |
| Interested replies yesterday | What happened | Count of replies categorized "Interested" | `getMasterInboxReplies()` + category, or `getLeadCategories()` join |
| Outstanding Pipedrive tasks | What needs attention | Count of open activities | Pipedrive `getActivities` (MCP) filtered `done=false` |
| Overdue Pipedrive follow-ups | What needs attention | Count of activities past due date | Pipedrive `getActivities` filtered `due_date < today, done=false` — click through to §5 |
| Owner filter (Yoni / Rachel) | Click-through | Filter by activity/campaign owner | Pipedrive activities have `owner_id`; Smartlead campaigns don't have an owner field today — **gap, see §8** |

Two of these (sent/received/interested "yesterday") are already computed in
`scripts/daily-deliverability-check.mjs` and the reconciliation-ledger dashboard's donut —
they just need to be pulled forward onto the home screen instead of buried in a sub-page.

---

## 4. SmartLead / Outbound Email section

### 4.1 Campaigns
- **List, styled like Smartlead's own campaign list** (name, status, created date, key
  metrics inline) — `client.listCampaigns()` already returns `created_at`, `status`, name.
- **Sort:** date created, status, emails sent, reply rate, bounce rate — sent/reply/bounce
  come from `getCampaignAnalytics(campaignId)` / `getCampaignStatistics(campaignId)`, one
  call per campaign (batch on load, cache per day).
- **Filter by status:** Active / Paused / Completed / Draft — `listCampaigns({ ... })`
  supports status filtering server-side per the Smartlead API; confirm exact status enum
  values Smartlead returns (`status` field) before building the filter chips.
- **Campaign detail (click-through):** emails sent, reply rate, bounce rate, Interested
  count, sequence steps (`getCampaignSequences`), assigned inboxes
  (`listCampaignEmailAccounts`).

### 4.2 Inboxes / deliverability — needs investigation before building
Yoni flagged "100/100 inboxes active" against an expected ~111. Before this section is
built, resolve:
- Does `client.getAllInboxHealth()` / `listEmailAccounts()` paginate, and is the dashboard
  only reading page 1 (default `limit`)? `listEmailAccounts({ offset, limit })` takes both —
  worth confirming no default cap is truncating the set.
- Are the missing ~11 inboxes disconnected/errored accounts that Smartlead excludes from
  the "active" count, or accounts on a different client/workspace filter?
- Once resolved, the section should show total inboxes (not just "active"), broken out by
  health status, with the same detail Smartlead's own warmup view shows
  (`getEmailAccountWarmupStats`).

### 4.3 Domains — needs a definition, not just a build
"Deliverability Watch List" is a Smartlead-side label with no explanation surfaced yet.
Before building this view: pull one flagged domain's full account/domain object via the
Smartlead API and check for the field(s) driving that label (bounce rate threshold? spam
complaints? blocklist hits?) so the dashboard can show *why* a domain is listed and *what
to do about it*, not just the label. `scripts/flagged-domain-campaigns.mjs` may already have
partial logic for this — reuse rather than re-derive.

---

## 5. LinkedIn Outreach (HeyReach)

The `heyreach.js` client already exists (`listCampaigns`, `getLeadsFromCampaign`,
`getCampaignsForLead`, `isConnection`, `getMyNetworkForSender`) — mirrors the SmartLead
section: campaign list with status/leads-added/replies, response tracking, and a
connections/network view (`isConnection`, `getMyNetworkForSender`). No new integration
needed to stand this section up; it's UI work reusing what's already wired.

---

## 6. Pipedrive section

### 6.1 Activities / follow-ups
Click into "Overdue" and see, per Yoni's spec: lead/contact, due date, activity type, owner
— all present on the Pipedrive `Activity` object (`getActivities`/`getActivity` via MCP).
Filters: **Yoni / Rachel** (by `owner_id`) and **Overdue / Due today / Upcoming** (by
`due_date` vs. today). Both are straightforward filters over the existing MCP `getActivities`
call — no data gap.

### 6.2 "Pipedrive Sync" — undefined, do not build yet
Yoni is explicit that he doesn't know what this widget currently represents. Before
touching it: find the current dashboard code/config that produces the "Pipedrive Sync"
label and trace what it's counting (likely the reconciliation ledger's "signals that became
leads" metric, given the automation-workflow doc's focus). Then decide with Yoni whether it
survives as its own element or gets folded into the Automation Log (§7) as one more metric.
**Action item, not a build task.**

---

## 7. Claude Activity / Automation Log

This absorbs what the *current* dashboard already does (the reconciliation ledger) and
extends it into a general audit log:

- **Filters:** date, action type, system (Pipedrive / SmartLead / Bluedot / Gmail), lead or
  contact, campaign, user/source.
- **Row detail (click-through):** the lead, the triggering email/reply text, what Claude
  categorized it as, and the resulting Pipedrive write(s) — this is exactly the "reconciliation
  ledger" table's current row shape (`Contact · Trigger · Received · Smartlead category ·
  P·O·A·L·Ow·Lb · Verdict · What the rulebook expected`), so the existing table becomes one
  filtered view inside this log rather than the whole dashboard.
- **Gap:** there's no persisted, queryable log today — the current dashboard recomputes the
  ledger from live Pipedrive/Smartlead/Gmail/Bluedot reads each time it loads. "Show me
  every lead Claude categorized yesterday" needs either (a) a stored action log written at
  the time each categorization/sync happens, or (b) continuing to reconstruct it from
  timestamps on Pipedrive activities + Smartlead category-change events. (a) is more
  reliable and worth scoping as its own follow-up once this reframe is approved.

---

## 8. SEO (Semrush) and SmartScout

- **SEO:** Semrush MCP tools are already connected (`domain_overview`, `traffic_overview`,
  `position_tracking`, `site_audit`, `keyword_research`, `backlinks_research`,
  `competitors_research`) — enough to build "performance, opportunities, and progress" as
  Yoni asked, no new integration required.
- **SmartScout:** **no integration exists anywhere in this repo or the connected MCP
  servers.** Before this section can be anything more than a placeholder, we need to know
  what SmartScout workflow Yoni actually runs (Amazon seller/ASIN prospecting?) and whether
  SmartScout exposes an API/export we can pull from. This is a scoping question, not a build
  task, until that's answered.

---

## 9. BlueDot — demote, don't remove entirely

Yoni's read matches what's wired today: Bluedot (`list_meetings`, `search_meetings`,
`list_participants`) is currently only cited as a **data source** in the automation-workflow
doc and the current dashboard's footer ("Bluedot — recorded calls by collection"), feeding
context into Pipedrive activity notes. There's no evidence of a dedicated Bluedot tracking
widget beyond that footer credit. Recommendation: keep Bluedot as an input line under the
Automation Log's source list (§7), and do **not** give it a home-dashboard box or its own
hero section — matches Yoni's own conclusion, just confirming there's nothing hidden to
preserve.

---

## 10. General — Software & Infrastructure

A ledger of every tool in the stack: name, purpose, monthly/annual cost, renewal date,
seats, domains, inboxes, accounts, username (no passwords — link out to the password
manager entry instead), account URL, owner/admin.

What's already got a live data hook vs. what needs manual upkeep:

| Tool | Live data available today | Still manual |
|---|---|---|
| SmartLead | Inboxes, domains, campaigns (this repo's client) | Cost/billing, seats |
| HeyReach | Campaigns, connections, workspaces | Cost/billing, seats |
| Pipedrive | Users, activities (MCP) | Cost/billing |
| Namecheap | Domain list, DNS hosts (`namecheap.js`) | Cost (varies by renewal) |
| Porkbun | Domain list (`porkbun.js`) | Cost |
| Premium Inboxes | Subscription + order summaries (`premiuminboxes.js`) — likely the best source for inbox billing | — |
| Fathom | Meetings list/content (`fathom.js`) | Cost, seats |
| Google Sheets | Read/write (`googlesheets.js`) — could be the ledger's backing store itself | — |
| QuickEmailVerification | Verification credits/usage (`quickemailverification.js`) | Cost |
| Bluedot | Meetings/workspaces (MCP) | Cost, seats |
| Semrush | Usage via MCP | Cost |
| SmartScout | None | Everything |

Recommendation: this section is the one place a plain data-entry ledger (e.g. the existing
Google Sheets client, or a small structured file in this repo) makes more sense than trying
to API-source every field — cost/renewal/seats/ownership are inherently manual facts, and
only a few tools (Premium Inboxes, Namecheap/Porkbun for domains) expose them via API at
all. Credentials should never be stored here; store a link to the password-manager entry.

---

## 11. Open questions to resolve before building (from Yoni's notes)

1. **Inboxes:** why 100 of ~111 are shown as "active" — pagination cap, exclusion filter, or
   genuinely inactive accounts? (§4.2)
2. **Domains:** what defines "Deliverability Watch List," and what's the required action
   when a domain lands on it? (§4.3)
3. **Pipedrive Sync widget:** what does it currently count, and is it still needed once the
   Automation Log exists? (§6.2)
4. **BlueDot box:** confirmed no independent function beyond source-attribution — proposal
   is to drop the home-dashboard box and keep it as a footer/source credit only (§9).
5. **SmartScout:** what workflow and what API/export, if any, exists to pull from (§8).

None of these blocks writing this plan, but all five block building the corresponding
section — they're investigation tasks, not implementation tasks.

---

## 12. Suggested build order (once the above is confirmed with Yoni)

1. Home dashboard (at-a-glance) — smallest scope, reuses existing analytics calls.
2. Pipedrive activities/follow-ups filtering (Yoni/Rachel, overdue/due-today/upcoming) —
   data already available, no open questions.
3. SmartLead campaigns view (list/sort/filter) — data already available.
4. Automation Log — absorb the current dashboard as one filtered view; decide on persisted
   logging vs. live reconstruction.
5. LinkedIn (HeyReach) section — data already available.
6. SmartLead inboxes/domains — after open questions #1–2 are resolved.
7. SEO section — data already available via Semrush.
8. General/Infrastructure ledger — after deciding the backing store (Sheet vs. repo file).
9. SmartScout — after open question #5 is resolved.
