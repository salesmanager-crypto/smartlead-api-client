# SmartLead → Pipedrive Inbox Sync (scheduled task prompt)

You are running Albert Scott's SmartLead ↔ Pipedrive sync, unattended, on a schedule.
This prompt is fully self-contained — you have no memory of any prior run.

## Access
- SmartLead: direct REST API via `/home/user/smartlead-api-client` (`src/client.js` / `src/cli.js`).
  Base URL and API key load from `/home/user/smartlead-api-client/.env`. Company account.
- Pipedrive: use the connected Pipedrive MCP tools directly.
- Checkpoint file: `/home/user/smartlead-api-client/.last-checkpoint` — an ISO 8601 timestamp
  of the last reply successfully processed. Read it at the start; write the newest
  `last_reply_time` you processed back to it at the end. If the file doesn't exist, default to
  24 hours before now.

## Scope
- **Skip every lead whose `email_campaign_name` starts with "Rachel -"** — different owner,
  handled separately. Never touch category, pause state, or block list for these.
- Only process replies with `has_new_unread_email: true`.

## Step 1 — Pull new replies
POST `${SMARTLEAD_BASE_URL}/master-inbox/inbox-replies?api_key=${SMARTLEAD_API_KEY}&fetch_message_history=true`
body: `{"offset":0,"limit":20,"sortBy":"REPLY_TIME_DESC","filters":{"emailStatus":"Replied","replyTimeBetween":["<checkpoint>","<now, ISO8601>"]}}`
Paginate (increase offset by 20) until `total_count` is exhausted or you've covered the window.
Filter out `email_campaign_name` starting with "Rachel -" and anything with `has_new_unread_email: false`.

## Step 2 — Classify each remaining reply
Read the actual inbound reply body (`type: "REPLY"` entries in `email_history`, HTML-stripped) and
assign exactly one category:

| Category | id | When to use |
|---|---|---|
| Interested | 1 | Real interest in an Amazon US conversation |
| Meeting Request | 2 | Explicitly asks to schedule a call |
| Not Interested | 3 | Explicit rejection, "not for now," similar |
| Do Not Contact | 4 | "No"/"stop"/unsubscribe/any clear opt-out — even one word |
| Information Request | 5 | Wants more info, hasn't committed (docs call this "Follow Up" — use id 5301 "Follow Up" to match the production doc's exact label, not id 5) |
| Out Of Office | 6 | Autoresponder / OOO message |
| Wrong Person | 7 | Says they're not the right contact, no other contact given |
| Unsure | 5271 | Ambiguous, can't tell intent |
| Follow Up | 5301 | Wants more info, hasn't clearly committed |
| Ignore | 4497 | Auto-generated, no human signal either way |

Apply via: POST `${BASE}/campaigns/{campaignId}/leads/{leadId}/category?api_key=...`
body `{"category_id": <id>, "pause_lead": <true if disqualifying/handled, false if OOO with no other action needed>}`
(campaignId = `email_campaign_id`, leadId = `email_lead_id` from the reply record.)

## Step 3 — Category-specific action (Section 5 of the production doc)

| Category | Pipedrive sync | Block domain |
|---|---|---|
| Interested, Follow Up, Meeting Request | ✓ Org + Person + Activity | ✓ |
| Do Not Contact, Not Interested, Ignore | ✗ | ✓ (email + domain) |
| Out of Office — no other contact named | ✗ | ✓ |
| Out of Office — names a reachable colleague | ✗ | ✗ — do not block, leave reachable |
| Wrong Person, Unsure | ✗ | use judgment — block only if clearly a dead end |

**Before blocking**, always check first:
GET `${BASE}/leads/get-domain-block-list?api_key=...&filter_email_or_domain=<domain>`
If not already present, block the **entire domain** (not just the email):
POST `${BASE}/leads/add-domain-block-list?api_key=...` body `{"domain_block_list":["<domain>"],"client_id":null}`

## Step 4 — Pipedrive sync (only for Interested / Follow Up / Meeting Request)
1. `searchOrganization` by company name → use `org_id` if found, else `addOrganization`.
2. `searchPersons` by email → use `person_id` if found — this also catches a person already
   created by the Calendly step (Step 5) if they booked before replying — else `addPerson` with
   first name, last name, email, `org_id`. **Omit `job_title`, `notes`, `postal_address`, `im`,
   `birthday`** — these 403 on this account (contact sync isn't enabled). Put that context in the
   Activity note instead.
3. **Dedup check (fixed 2026-08-28 — Rachel flagged duplicate Pipedrive entries between SmartLead
   and Calendly): `searchLeads` by email/name before creating a Lead.** If this person already has
   a Lead — from an earlier run of this step, or from a prior Calendly booking (Step 5) — reuse
   that `lead_id` and skip straight to `addActivity` below; do not call `addLead` again. Otherwise
   `addLead`: `title`: "<Category> - {name}", `person_id`, `organization_id` (if any),
   `owner_id: 26939288`. One Person, one Lead per email address, regardless of which flow
   (SmartLead or Calendly) got there first — SmartLead is the canonical source, so never create a
   second Lead for someone who already has one.
4. `addActivity`:
   - `type`: "Meeting" for Meeting Request, "Follow Up" otherwise
   - `subject`: short description
   - `note`: the full inbound reply text
   - `participants`: `[{ "person_id": <id>, "primary": true }]` — **never** pass `person_id` at
     the top level, it's read-only and 400s.
   - `lead_id`: the id from step 3 above — link the activity to the **lead**, not just the person
   - `owner_id`: 26939288

## Step 5 — Calendly (verified 2026-08-19; dedup fix 2026-08-28)
Search Gmail (`yoni@albertscott.com` — corrected 2026-08-19; previously documented as
salesmanager@albertscott.com, which was wrong) for messages `from:notifications@calendly.com` whose
subject starts with **"New Event:"** (a reschedule shows **"Updated:"** instead), received since the
checkpoint. **Do not filter on "scheduled" in the subject** — that word only appears in the email
body, never the subject; a subject search for it silently matches nothing, which is exactly the bug
that made this step a no-op before. The same sender also sends password-reset and meeting-recap
mail unrelated to bookings — the "New Event:"/"Updated:" subject prefix is the actual signal. For any
booking found, extract name/email/date/time, then:

1. `searchPersons` by email. If found — most often because this prospect already replied to a
   SmartLead campaign and Step 4 created their record first — **reuse that `person_id`/`org_id`; do
   not create a second Person or Organization.** If not found, create person+org as in Step 4.
2. `searchLeads` by email/name. **If a Lead already exists for this person (from Step 4, or from an
   earlier Calendly booking), reuse that `lead_id` and skip straight to the `addActivity` call below
   — do not call `addLead` again.** This is the fix for the duplicate-entry issue Rachel flagged:
   SmartLead is the canonical source, so someone who already has a SmartLead-sourced Lead must never
   get a second `"Calendly Booking - {name}"` Lead just because they also booked a call.
3. Only when step 2 found no existing Lead: **`addLead`** (`title`: `"Calendly Booking - {name}"`,
   `person_id`, `organization_id` if present, `owner_id: 26939288`) — **required for a genuinely new
   prospect, do not skip**: without this call the booking is just a bare contact, not a Lead, which
   is exactly the bug flagged in the Aug 18 meeting ("Fix Calendly→Pipedrive: create leads, not
   contacts", fixed 2026-08-19).
4. `addActivity` type "Meeting" subject "Calendly Booking" with the date/time, linked via `lead_id`
   (from step 2 or 3 above) rather than just `person_id`.
5. Block that domain+email in Smartlead so no campaign re-contacts them.

## Step 6 — Update checkpoint
Write the max `last_reply_time` across everything you just processed (or now, if nothing new) to
`/home/user/smartlead-api-client/.last-checkpoint`.

## Step 7 — Log every processed contact
Append one row per lead you took any action on (category set, Pipedrive synced, and/or domain
blocked) to `/home/user/smartlead-api-client/logs/inbox-sync-log.csv` (create it with a header
row if it doesn't exist yet). Columns, in order:
`timestamp,campaign,lead_name,lead_email,category_applied,pipedrive_action,domain_blocked,reply_excerpt`
- `timestamp`: now, ISO 8601
- `pipedrive_action`: "created" (new Person and/or Lead) / "updated" (existing Person updated) /
  "reused-lead" (dedup check in Step 4/5 found an existing Lead from the other channel and attached
  an Activity to it instead of creating a new one — log this distinctly so duplicate-prevention is
  auditable) / "none"
- `domain_blocked`: "yes" / "no"
- `reply_excerpt`: the inbound reply body, HTML-stripped, collapsed to one line, truncated to 200
  chars. Escape commas/quotes properly for CSV (wrap the field in double quotes, double any
  embedded quotes).
Skip logging leads you filtered out (Rachel campaigns, already-read) — the log is for actions
taken, not everything scanned.

## Step 8 — Report
One-paragraph summary: replies pulled, how many skipped (Rachel campaigns), how many per category,
deals/persons created or updated in Pipedrive, domains blocked, any Calendly bookings synced, any
errors (403s, unexpected payload shapes, etc. — call these out, don't silently swallow them). Also
call out how many `reused-lead` dedup hits happened this run (a SmartLead reply and a Calendly
booking resolving to the same existing Lead) — that's the duplicate-prevention check working, worth
surfacing so it stays visible that it's active.

## Weekly backlog scan (only on the run tagged "weekly")
Instead of using the checkpoint file, set the `replyTimeBetween` start to 8 days before now, to
catch anything missed during a reply-volume spike. Otherwise identical to Steps 1–8.
