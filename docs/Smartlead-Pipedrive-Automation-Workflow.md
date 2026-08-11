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
2. `searchPersons` by email — if found, use that `person_id`; if not, `addPerson` with first name, last name, email, and `org_id` (omit the 403-prone fields from rule 4 above).
3. `addActivity` with:
   - `type`: "Follow Up" or "Meeting" depending on category
   - `subject`: short description
   - `note`: the full inbound reply text, for context
   - `participants`: `[{ "person_id": <id>, "primary": true }]`
   - `owner_id`: 26939288 (Yoni)

### Step 5 — Block in SmartLead
Categorize the lead in SmartLead's Master Inbox, then block email + domain (with the "block entire domain" checkbox) unless the lead falls under the Out of Office exception in rule 3.

### Step 6 — Weekly backlog scan
At least once a week, scan back through Unread Replies to the last confirmed checkpoint to make sure nothing was missed — trade-show reply volume can spike and outrun the hourly check.

---

## 5. Quick Reference: Category → Action

| Category | SmartLead Tag | Pipedrive Sync | Block Domain |
|---|---|---|---|
| Interested | ✓ | ✓ Org + Person + Activity | ✓ |
| Follow Up | ✓ | ✓ Org + Person + Activity | ✓ |
| Meeting Request | ✓ | ✓ Org + Person + Activity (type: Meeting) | ✓ |
| Do Not Contact | ✓ | ✗ | ✓ (email + domain) |
| Not Interested | ✓ | ✗ | ✓ (email + domain) |
| Ignore | ✓ | ✗ | ✓ (email + domain) |
| Out of Office (no other contacts) | ✓ | ✗ | ✓ |
| Out of Office (colleague contacts listed) | Ignore Reply | ✗ | ✗ — do not block |

---

## 6. Calendly Booking Flow (separate trigger, same destination)

Calendly confirmations land in salesmanager@albertscott.com, separate from SmartLead replies, but resolve to the same Pipedrive sync pattern:

1. Detect new Calendly booking email (from notifications@calendly.com, "scheduled" in subject)
2. Extract: name, email, meeting date/time
3. `searchPersons` by email → update if found, else `addOrganization` (if company known) + `addPerson`
4. `addActivity`: type "Meeting", subject "Calendly Booking", date/time from the email, `participants` array (rule 5), owner_id 26939288
5. Add email + domain to SmartLead's blocklist so no campaign re-contacts them

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

---

**Last Updated:** August 12, 2026
**Source:** Compiled from Eikko's live SmartLead↔Pipedrive automation, in use since early August 2026
