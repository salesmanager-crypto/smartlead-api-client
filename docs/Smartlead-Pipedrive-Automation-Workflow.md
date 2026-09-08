# SmartLead ↔ Pipedrive Automation Workflow
**Albert Scott — Sales Operations**
**For: Yoni's Claude account (transfer of existing automation, per Aug 11 meeting)**

This document is the full operating workflow currently run on Eikko's Claude account. It's written so it can be dropped into Yoni's own Claude setup once the SmartLead connector is fixed (see Master Task List Section 9) and reproduce the same process exactly.

---

## 1. Purpose

Monitor SmartLead's Master Inbox for new lead replies, categorize each one correctly, sync qualifying leads into Pipedrive, and keep SmartLead's blocklist clean — all without manual copy-paste between the two systems.

**Owner:** Yoni Lebovits (Pipedrive `owner_id: 26939288`)
**Monitored inbox:** SmartLead Master Inbox (all campaigns except any owned by "Rachel")
**Frequency:** Hourly during work hours; a full backlog scan back to the last confirmed checkpoint at least once a week

---

## 2. Systems & Access

| System | Purpose | Access |
|---|---|---|
| SmartLead | Cold email campaigns, Master Inbox, lead categorization, domain blocklist | `app.smartlead.ai` — MCP connector (once fixed on Yoni's account) |
| Pipedrive | CRM — organizations, persons, activities | `albertscott.pipedrive.com` — MCP connector |
| Gmail (salesmanager@albertscott.com) | Calendly booking notifications | Gmail / browser |

**MCP tools used (SmartLead):**
- `fetch_master_inbox_unread_replies` / `fetch_master_inbox_replies` — pull new inbox activity
- `update_master_inbox_lead_category` — apply a category tag to a lead
- `create_master_inbox_lead_note` — log context on a lead
- `add_domain_block_list` / `block_master_inbox_domains` — block a domain
- `get_domain_block_list` — check existing blocks before re-blocking
- `mark_master_inbox_lead_as_unread` — used for "Ignore Reply" handling (see below)

**MCP tools used (Pipedrive):**
- `searchPersons`, `searchOrganization` — **always search before creating**, to avoid duplicates
- `addOrganization`, `addPerson` — create new records
- `addActivity` — log the interaction

---

## 3. Standing Rules (learned in production — do not skip these)

1. **"No" / "stop" / unsubscribe-style replies → always categorize "Do Not Contact"**, even if the wording is casual or one word.
2. **When blocking a domain, always check "Block the entire domain associated with this lead"** in the same action — don't block the email address alone.
3. **Never block a domain if the reply lists other reachable contacts at that company** (e.g., an out-of-office autoresponder that names a colleague). Use **Ignore Reply** instead of blocking, so those colleagues stay reachable.
4. **Pipedrive `addPerson` will 403 on these fields — omit them entirely:** `job_title`, `notes`, `postal_address`, `im`, `birthday`. This is because contact sync isn't enabled on the account. Put any context you'd have put in those fields into the linked Activity's `note` field instead.
5. **Pipedrive `addActivity` — `person_id` is read-only.** Passing it directly causes a 400 error. Use:
   ```
   participants: [{ "person_id": <id>, "primary": true }]
   ```
   instead of a top-level `person_id`.
6. **Every synced lead gets blocked in SmartLead** (email + domain, per rule 2) to prevent a duplicate campaign from re-contacting them later — except Do Not Contact/Not Interested/Ignore/Out of Office cases, which follow the table in Section 5.
7. **One Person, one Lead per prospect — never per channel.** (Fixed 2026-08-28 — Rachel flagged duplicate Pipedrive entries: the same prospect landing once from SmartLead and again from Calendly.) SmartLead and Calendly are two entry points into the same pipeline, not two separate ones. Before creating an Organization, Person, or Lead in *either* flow, search Pipedrive first — `searchPersons` by email, then check that person's existing Leads (`searchLeads`) — and reuse whatever is already there. **SmartLead is the canonical source:** if a prospect already has a Person/Lead record because they replied to a campaign, a later Calendly booking must attach to that same record (reuse `person_id`/`org_id`/`lead_id`, log the booking as a new Activity) instead of creating a second `"Calendly Booking - {name}"` Lead. Only originate a fresh Lead from Calendly when no existing Person/Lead is found for that email at all.

---

## 4. Step-by-Step Process

### Step 1 — Pull new inbox activity
Fetch unread replies from the SmartLead Master Inbox. Filter out anything under a "Rachel" campaign (different owner, handled separately).

### Step 2 — Read and classify each reply
For each new reply, read the content and assign exactly one category:

| Category | When to use |
|---|---|
| **Interested** | Lead shows real interest in an Amazon US conversation |
| **Follow Up** | Lead wants more info but hasn't clearly committed |
| **Meeting Request** | Lead explicitly asks to schedule a call |
| **Do Not Contact** | Reply says no / stop / unsubscribe / any clear opt-out |
| **Not Interested** | Explicit rejection, "not for now," or similar |
| **Out of Office** | Autoresponder / OOO message |
| **Ignore** | Auto-generated response with no human signal either way |

### Step 3 — Take the category-specific action
See the reference table in Section 5. In general: qualifying replies (Interested / Follow Up / Meeting Request) get synced to Pipedrive and the domain gets blocked; disqualifying replies (Do Not Contact / Not Interested / Ignore) just get blocked; Out of Office gets "Ignore Reply" (not a block) unless it's clearly a dead end with no other contacts listed.

### Step 4 — Sync qualifying leads to Pipedrive
1. `searchOrganization` by company name — if found, use that `org_id`; if not, `addOrganization`.
2. `searchPersons` by email — if found, use that `person_id` (this also catches a person a prior Calendly booking already created — reuse it, don't re-add); if not, `addPerson` with first name, last name, email, and `org_id` (omit the 403-prone fields from rule 4 above).
3. Check for an existing Lead on that person first (`searchLeads` by email/name) before creating one. If a Lead already exists — including one created by the Calendly flow (Section 6) — reuse its `lead_id`. Otherwise `addLead`: `title`: "<Category> - {name}", `person_id`, `organization_id` (if any), `owner_id: 26939288`. (Rule 7 — one Lead per prospect, not per channel.)
4. `addActivity` with:
   - `type`: "Follow Up" or "Meeting" depending on category
   - `subject`: short description
   - `note`: the full inbound reply text, for context
   - `participants`: `[{ "person_id": <id>, "primary": true }]`
   - `lead_id`: the id from step 3 — link the activity to the **lead**, not just the person
   - `owner_id`: 26939288 (Yoni)

### Step 5 — Block in SmartLead
Categorize the lead in SmartLead's Master Inbox, then block email + domain (with the "block entire domain" checkbox) unless the lead falls under the Out of Office exception in rule 3.

### Step 6 — Weekly backlog scan
At least once a week, scan back through Unread Replies to the last confirmed checkpoint to make sure nothing was missed — trade-show reply volume can spike and outrun the hourly check.

---

## 5. Quick Reference: Category → Action

| Category | SmartLead Tag | Pipedrive Sync | Block Domain |
|---|---|---|---|
| Interested | ✓ | ✓ Org + Person + Lead + Activity | ✓ |
| Follow Up | ✓ | ✓ Org + Person + Lead + Activity | ✓ |
| Meeting Request | ✓ | ✓ Org + Person + Lead + Activity (type: Meeting) | ✓ |
| Do Not Contact | ✓ | ✗ | ✓ (email + domain) |
| Not Interested | ✓ | ✗ | ✓ (email + domain) |
| Ignore | ✓ | ✗ | ✓ (email + domain) |
| Out of Office (no other contacts) | ✓ | ✗ | ✓ |
| Out of Office (colleague contacts listed) | Ignore Reply | ✗ | ✗ — do not block |

---

## 6. Calendly Booking Flow (separate trigger, same destination)

Calendly confirmations land in **yoni@albertscott.com** (corrected 2026-08-19 — previously documented as
salesmanager@albertscott.com, which was wrong; verified against real headers: `to: yoni@albertscott.com`),
separate from SmartLead replies, but resolve to the same Pipedrive sync pattern:

1. Detect new Calendly booking email: `from:notifications@calendly.com`, subject starting with **"New
   Event:"** (a reschedule instead shows **"Updated:"**). **Do not filter on "scheduled" in the subject —
   that word only ever appears in the email body, never the subject; a subject-line search for it matches
   zero emails.** (Corrected 2026-08-19 — this was silently returning no bookings every run.) The same
   sender also sends password-reset and meeting-recap/action-item mail unrelated to bookings — the
   "New Event:"/"Updated:" subject prefix is what distinguishes an actual booking notification.
2. Extract: name, email, meeting date/time
3. `searchPersons` by email → if found, **reuse that Person/Org as-is** (most often because they already replied to a SmartLead campaign and Step 4 created the record first) — update it, don't create a second one; if not found, `addOrganization` (if company known) + `addPerson`.
4. Check whether this person already has a Lead in Pipedrive (`searchLeads` by email/name). **If one already exists — from a prior SmartLead sync or an earlier Calendly booking — reuse that `lead_id` and skip straight to step 6; do not call `addLead` again.** (Fixed 2026-08-28, rule 7 — SmartLead is the canonical source, so a Calendly booking from someone already in the pipeline must never spawn a second `"Calendly Booking - {name}"` Lead; it just adds a Meeting Activity to their existing Lead.)
5. Only when step 4 found no existing Lead: **`addLead`** — `title`: `"Calendly Booking - {name}"`, `person_id` (from step 3), `organization_id` (if one was created/found), `owner_id: 26939288`. **This step must not be skipped for a genuinely new prospect:** steps 1–3 only get you a bare Person/Organization record; the booking doesn't become a Lead in Pipedrive's Leads Inbox until this call runs. (Fixed 2026-08-19 — this call was missing, so Calendly bookings were landing as contacts only, never as leads.)
6. `addActivity`: type "Meeting", subject "Calendly Booking", date/time from the email, `participants` array (rule 5), owner_id 26939288 — link the activity to the **lead** from step 4 or 5 (`lead_id`), not just the person
7. Add email + domain to SmartLead's blocklist so no campaign re-contacts them

---

## 7. Worked Example (from production)

**Lead:** Ronald Goenawan, Bukit Sari Organic Plantation, replied to a Tea Expo campaign confirming active US market interest but blocked on finding a distributor.

1. Categorized "Interested" in SmartLead
2. `searchOrganization("Bukit Sari Organic Plantation")` → not found → `addOrganization` → org_id 998
3. `searchPersons("Ronald Goenawan")` → not found → `addPerson` (first/last name, email, org_id 998) → person_id 1719
4. `addActivity`: type "Follow Up", note = full reply text, `participants: [{"person_id": 1719, "primary": true}]`, owner_id 26939288
5. Blocked ronald's domain in SmartLead (entire-domain checkbox checked)

This exact pattern repeats for every Interested/Follow Up/Meeting Request lead.

---

## 8. Known Issues / Troubleshooting

- **SmartLead connector currently broken on Yoni's account** (as of Aug 11) — "Add Custom Connector" is admin-only on the team plan; Shimi needs a new API key from Eikko to fix it manually before this workflow can run on Yoni's own Claude account. Pipedrive's connector already works.
- **Google Sheets Task Tracker access**: if the Task Tracker sheet shows "You need access," the connected Chrome profile/account doesn't have Editor rights — switch to the correct Google account or share the sheet with the connected account.
- **Large `get_campaigns` / `get_campaign_leads` pulls** can exceed tool output limits — results get saved to a file; use Grep with `output_mode: "content"` on that file rather than trying to read it directly.
- **Duplicate Pipedrive entries between SmartLead and Calendly (fixed 2026-08-28)** — Rachel flagged the same prospect showing up twice: once synced from a SmartLead reply, once from a Calendly booking. Root cause was neither flow checked whether the other had already created the Person/Lead. See rule 7 (Section 3) and the dedup checks now in Steps 4 and 6 — going forward, both flows search for an existing Person and Lead before creating one, and SmartLead is treated as the canonical source. This does not retroactively merge duplicates already created in Pipedrive before this fix — those need a manual merge in Pipedrive's UI.

---

**Last Updated:** August 28, 2026
**Source:** Compiled from Eikko's live SmartLead↔Pipedrive automation, in use since early August 2026
