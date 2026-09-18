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

**This table is the complete, verified list of every category ID that exists on this SmartLead
account** — confirmed 2026-09-14 against the live `getLeadCategories()` / `GET
/leads/fetch-categories` endpoint (the authoritative source) and cross-checked against 1,157 real
replies since June 2026. Three of the IDs below (`8`, `5270`, `5302`) have zero historical hits as of
this check but exist on the account and are documented now so they're handled correctly the first
time they appear, rather than falling through undefined. `5303` ("Unqualified") already has 15+ real
leads carrying it in production — it was previously undocumented and unhandled; that gap is now
closed.

Read the actual inbound reply body (`type: "REPLY"` entries in `email_history`, HTML-stripped) and
assign exactly one category **for a reply you are classifying yourself** (the "You apply this"
column). The other categories only ever arrive pre-existing (set by SmartLead's own AI or by a
teammate in the SmartLead UI) — never apply those yourself; just handle them correctly when you see
them already set (see Step 3's pre-categorized-lead handling).

| Category | id | When to use | You apply this? |
|---|---|---|---|
| Interested | 1 | Real interest in an Amazon US conversation | Yes |
| Meeting Request | 2 | Explicitly asks to schedule a call | Yes |
| Not Interested | 3 | Explicit rejection, "not for now," similar | Yes |
| Do Not Contact | 4 | "No"/"stop"/unsubscribe/any clear opt-out — even one word | Yes |
| Information Request | 5 | Legacy id, semantically identical to "Follow Up" (5301) below. Superseded in practice — use 5301 when classifying yourself. If a lead already carries id 5 from before this switch (or from elsewhere), treat it exactly like Follow Up for sync purposes. | No (legacy — treat pre-existing hits as Follow Up) |
| Out Of Office | 6 | Autoresponder / OOO message | Yes |
| Wrong Person | 7 | Says they're not the right contact, no other contact given | Yes |
| Uncategorizable by Ai | 8 | SmartLead's own AI classifier's catch-all bucket for messages it can't classify — same idea as Sender Originated Bounce (9) below, applied by SmartLead itself. | No — leave pre-existing hits alone, same as a bounce |
| Sender Originated Bounce | 9 | The "reply" is actually an NDR/bounce notice (e.g. Office 365/Gmail spam rejection) or other delivery-failure artifact misfiled as a reply — not a genuine message from the lead | Yes, but only when you find one mis-filed as `null` (see note below) |
| Ignore | 4497 | Auto-generated, no human signal either way | Yes |
| Action Needed | 5270 | Pre-existing only — a teammate flagged this lead as needing a human follow-up action. Currently unused (0 hits as of 2026-09-14) but documented for when it appears. | No — if seen pre-existing, sync it (Step 4) same as Interested/Follow Up/Meeting Request |
| Unsure | 5271 | Ambiguous, can't tell intent — genuine human reply, just unclear | Yes |
| Follow Up | 5301 | Wants more info, hasn't clearly committed | Yes |
| Client | 5302 | Pre-existing only — this lead has already converted to an actual client. Currently unused (0 hits as of 2026-09-14) but documented for when it appears. | No — if seen pre-existing, sync it (Step 4) same as Interested, but **never block their domain** — they're an active client, not a dead end |
| Unqualified | 5303 | Pre-existing only — a teammate manually disqualified this lead. **Confirmed live in production: 15+ leads already carry this id.** | No — if seen pre-existing, treat exactly like Not Interested: no Pipedrive sync, block the domain |

Category 9 is SmartLead's own built-in bounce classifier — it sometimes auto-applies this before this
script ever sees the reply (leave those alone, already handled). When a "reply" is clearly a bounce/NDR
artifact and still shows `lead_category_id: null`, apply category 9 yourself rather than filing it under
Unsure — no domain action either way (the block/Pipedrive tables below don't cover a bounce, since it
isn't a real signal from the lead).

Apply via: POST `${BASE}/campaigns/{campaignId}/leads/{leadId}/category?api_key=...`
body `{"category_id": <id>, "pause_lead": <true if disqualifying/handled, false if OOO with no other action needed>}`
(campaignId = `email_campaign_id`, leadId = `email_lead_id` from the reply record.)

Once a lead is tagged **Out Of Office, Do Not Contact, Ignore, or Not Interested**, the category
call above is the only action needed on its read state — do not also try to mark the inbox
thread unread (that was the old "Ignore Reply" workaround from the production doc's
`mark_master_inbox_lead_as_unread` tool; it doesn't apply to this category-based flow and isn't
needed here).

**Known limitation — the unread badge stays on after tagging.** `has_new_unread_email` does not
flip to false when a category is applied via the API, and no REST endpoint for marking a thread
read could be found (tested and confirmed 404 across every plausible path, including the
single-lead message-history endpoint). This appears to be a UI-only side effect of opening a
conversation in SmartLead's Master Inbox directly — not something reachable from this REST-only
integration. Accepted as-is: Yoni reviews tagged leads manually in the SmartLead UI to confirm
correct tagging, which also clears the unread badge as a side effect. Do not spend time trying to
clear it programmatically.

## Step 3 — Category-specific action (Section 5 of the production doc)

| Category | Pipedrive sync | Block domain |
|---|---|---|
| Interested, Follow Up (incl. legacy id 5, "Information Request"), Meeting Request, Action Needed (5270), Client (5302) | ✓ Org + Person + Lead + Activity | ✓ — **except Client: never block**, they're an active customer |
| Do Not Contact, Not Interested, Ignore, Unqualified (5303) | ✗ | ✓ (email + domain) |
| Out of Office (any case) | ✗ | ✗ — never block, they'll return |
| Wrong Person | ✗ | ✗ — never block, contact is still reachable |
| Unsure, Uncategorizable by Ai (8) | ✗ | use judgment — block only if clearly a dead end |

**Pre-categorized leads (`lead_category_id` already non-null when fetched):** as of 2026-08-26,
do NOT blanket-skip these. If the existing category is Interested, Follow Up (or legacy id 5),
Meeting Request, Action Needed, or Client, run Step 4 for it same as a freshly-classified one —
first `searchOrganization`/`searchPersons` to check whether a Pipedrive record already exists
(these leads are sometimes added manually before this script gets to them), and only create what's
missing; always still check the activity history for a duplicate before adding a new one. For
Client specifically, still sync but never block the domain. Do not re-run category classification
or touch the category/pause state on an already-categorized lead — that part of the old
blanket-skip rule still applies. For every other pre-existing category (Not Interested, Do Not
Contact, Ignore, OOO, Wrong Person, Unsure, Uncategorizable by Ai, Unqualified), the old behavior
is unchanged: leave it alone, no action (Unqualified and Not Interested/Do Not Contact/Ignore do
still get the domain-block treatment above if not already blocked).

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
   and Calendly): `getLeads` with `person_id: <the person_id from step 2>` before creating a Lead.**
   Do NOT use `searchLeads` by email/name for this — existing leads are usually titled by company
   ("Herbacin", "FoodYoung", "Airloons"), so a name/email search misses them; that gap is exactly
   how 7 duplicate "Calendly Booking - {name}" leads got created on 2026-09-09 (fixed 2026-09-18).
   `getLeads(person_id)` returns every non-archived lead on the person regardless of title. If it
   returns one or more leads — from an earlier run of this step, a manual entry, or a prior Calendly
   booking (Step 5) — reuse the existing `lead_id` (the oldest one, if several) and skip straight to
   `addActivity` below; do not call `addLead` again. Otherwise
   `addLead`: `title`: "<Category> - {name}", `person_id`, `organization_id` (if any),
   `owner_id: 26939288`. One Person, one Lead per email address, regardless of which flow
   (SmartLead or Calendly) got there first — SmartLead is the canonical source, so never create a
   second Lead for someone who already has one.
4. `addActivity`:
   - `type`: `"call"` (confirmed against existing production records — not "Meeting"/"Follow Up"
     as earlier drafts of this doc said)
   - `subject`: the category name verbatim ("Interested", "Follow Up", or "Meeting Request")
   - `note`: `Smartlead reply — campaign "<email_campaign_name>" Reply <date> from <a
     href="mailto:<email>"><email></a>: "<full inbound reply text>"` — use a real `<a href=...>`
     tag (not HTML-escaped entities) so Pipedrive renders it as a clickable link, matching existing
     notes.
   - `participants`: `[{ "person_id": <id>, "primary": true }]` — **never** pass `person_id` at
     the top level, it's read-only and 400s.
   - `lead_id`: the id from step 3 above — link the activity to the **lead**, not just the person
   - `owner_id`: **25109251 (Yoni)** — fixed 2026-09-14. `26939288` is Eikko (this automation's own
     API identity — it's also permanently baked into every record's immutable `creator_user_id`
     field no matter what `owner_id` is set to, so don't mistake that field for the assignee). Every
     Activity this automation had ever created was wrongly left on Eikko as owner until this fix;
     all pre-existing ones were bulk-reassigned to 25109251 on 2026-09-14. The Org/Person/Lead
     themselves stay on `owner_id: 26939288` (Eikko) as before — this fix is Activities only.
   - `due_date`: today, ISO date

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
2. `getLeads` with `person_id` from step 1 — **not** `searchLeads` by name (see Step 4.3 for why:
   company-titled leads don't match a name search, which produced 7 duplicate leads on 2026-09-09).
   **If any Lead already exists for this person (from Step 4, a manual entry, or an earlier Calendly
   booking), reuse that `lead_id` and skip straight to the `addActivity` call below — do not call
   `addLead` again.** This is the fix for the duplicate-entry issue Rachel flagged:
   SmartLead is the canonical source, so someone who already has a SmartLead-sourced Lead must never
   get a second `"Calendly Booking - {name}"` Lead just because they also booked a call.
3. Only when step 2 found no existing Lead: **`addLead`** (`title`: `"Calendly Booking - {name}"`,
   `person_id`, `organization_id` if present, `owner_id: 26939288`) — **required for a genuinely new
   prospect, do not skip**: without this call the booking is just a bare contact, not a Lead, which
   is exactly the bug flagged in the Aug 18 meeting ("Fix Calendly→Pipedrive: create leads, not
   contacts", fixed 2026-08-19).
4. `addActivity` type "Meeting" subject "Calendly Booking" with the date/time, linked via `lead_id`
   (from step 2 or 3 above) rather than just `person_id`. `owner_id: 25109251` (Yoni) — same
   Activity-owner fix as Step 4 (fixed 2026-09-14); the Lead/Person/Org stay on `26939288` (Eikko).
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
