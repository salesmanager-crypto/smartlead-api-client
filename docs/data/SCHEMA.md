# Dashboard data contract

All values in the code blocks below are illustrative placeholders, not real data.

Every file the GitHub Pages dashboard and the Claude artifact read. Both dashboards
render only what is in these files, so a number that is wrong here is wrong in both,
and fixing the pull script that writes it fixes both.

Served from `docs/data/` on `main` (GitHub Pages source: `main` / `/docs`).

## Conventions

- **Timestamps** (`generatedAt`, `pulledAt`, `lastSuccess`, `lastAttempt`, `t`) are
  ISO 8601 in UTC, e.g. `"2026-09-25T09:17:42.113Z"`.
- **Dates** (`today`, `due`, `day`, `date`, `created`, `added`) are `YYYY-MM-DD` in
  **America/New_York**, the business day the team works in. "Today", "yesterday",
  "overdue" and "due in N days" are all computed in Eastern time.
- **Missing values are `null`**, never `0` and never an empty string. `0` means the
  API said zero. A field an API does not expose is `null` and is listed under
  "Not available from the API" for that file.
- **Percentages** in fields ending `Pct` or `Rate` are 0 to 100 (`2.1` means 2.1%).
  Growth fields (`momGrowth`, `mom12Growth`) are fractions (`0.027` means +2.7%)
  because that is what SmartScout returns; the dashboards format them.
- **Money** is a plain number in USD, no currency symbol.
- **IDs** are the source system's numeric ids (Pipedrive user, person, org, activity,
  deal; SmartLead campaign; HeyReach campaign).

### Plain vs encrypted files

The repository is public. Files with person-level data (names, email addresses) are
committed **encrypted**; everything else is plain JSON.

| File | Committed as | Why |
|---|---|---|
| `pipedrive.json` | `pipedrive.json.enc` | contact names, org names, activity subjects |
| `smartlead.json` | `smartlead.json.enc` | reply senders' names and email addresses |
| everything else | plain `.json` | aggregates, brand-level data, or hand-maintained reference data |

An `.enc` file is JSON:

```json
{ "v": 1, "alg": "AES-256-GCM", "iv": "<base64, 12 bytes>", "ct": "<base64, ciphertext with 16-byte tag appended>" }
```

The key is the dashboard's **content key**: the same 32-byte AES key the sign-in page
unwraps for each user (Actions secret `DASHBOARD_CONTENT_KEY`, base64). After sign-in
the page decrypts `.enc` files with WebCrypto `AES-GCM`; the plaintext is the UTF-8
JSON documented below. When run locally, the pull scripts also write the plaintext to
`.private/data/` (gitignored) so you can read it without decrypting.

---

## `manifest.json`

Written last by `scripts/pull/run-all.mjs`. `smartscout` is updated by the Claude
scheduled task.

```json
{
  "generatedAt": "2026-09-25T09:17:42.113Z",
  "today": "2026-09-25",
  "sources": {
    "smartlead":  { "lastSuccess": "...", "lastAttempt": "...", "status": "ok", "error": null, "records": 214, "note": null },
    "pipedrive":  { "...": "same shape" },
    "heyreach":   { "...": "same shape" },
    "semrush":    { "...": "same shape" },
    "seoIssues":  { "...": "same shape" },
    "smartscout": { "...": "same shape" },
    "tradeshows": { "...": "same shape" }
  }
}
```

| Field | Type | Meaning |
|---|---|---|
| `generatedAt` | timestamp | when the GitHub refresh finished |
| `today` | date | the business date the refresh ran for (Eastern) |
| `sources.<name>.lastSuccess` | timestamp or null | last run that wrote this source's file. Kept from the previous manifest when a run fails, so a failure never erases the last good date |
| `sources.<name>.lastAttempt` | timestamp | last time anything tried to refresh it |
| `sources.<name>.status` | `ok` / `stale` / `error` | `error`: the most recent attempt failed. `stale`: the most recent attempt did not fail, but `lastSuccess` is older than 36 hours (or null), for example the Claude task did not run, or a source was skipped for missing credentials. `ok`: otherwise |
| `sources.<name>.error` | string or null | the failure message for `error`, secret-free, at most 300 characters. Shown on hover in both dashboards |
| `sources.<name>.records` | number or null | main row count written (campaigns, activities, brands...), for a quick sanity check |
| `sources.<name>.note` | string or null | why a source is `stale` when it is not a failure, e.g. "Google secrets not set, showing the Sep 11 snapshot" |

`seoIssues` is a seventh source beyond the brief's six because the Pages SEO page
renders the issue tracker.

---

## `smartlead.json` (committed as `smartlead.json.enc`)

Written by `scripts/pull/smartlead.mjs`. Needs `SMARTLEAD_API_KEY`, and
`PIPEDRIVE_API_TOKEN` + `PIPEDRIVE_COMPANY_DOMAIN` for the sync check.

```json
{
  "pulledAt": "...",
  "today": "2026-09-25",
  "window": { "from": "2026-09-12", "to": "2026-09-25", "days": 14 },
  "syncCategories": ["Interested", "Meeting Request", "Follow Up"],
  "campaigns": [ ... ],
  "daily": [ ... ],
  "yesterday": { ... },
  "inboxLog": [ ... ],
  "inboxes": { "total": 111, "domains": 37 }
}
```

### `campaigns[]` -> artifact `CAMPAIGNS`

Every campaign in the account, newest `created` first.

| Field | Type | Meaning |
|---|---|---|
| `id` | number | SmartLead campaign id |
| `name` | string | campaign name |
| `status` | string | `ACTIVE`, `PAUSED`, `DRAFTED`, `COMPLETED`, `STOPPED` |
| `created` | date | campaign creation date |
| `started` | date or null | first day in `daily` with `sent > 0`; null if it has not sent in the window and the API gives no start date |
| `lastActivity` | date or null | most recent day in `daily` with any send or reply |
| `sent` | number | emails sent, all time |
| `reply` | number | replies, all time (named `reply`, not `replies`, because both dashboards' code reads `c.reply`) |
| `bounce` | number | bounces, all time |
| `leads` | number | leads loaded in the campaign |
| `interested` | number | leads in the Interested category |
| `replyRate` | number | `reply / sent * 100`, one decimal |
| `bounceRate` | number | `bounce / sent * 100`, one decimal |
| `rep` | string or null | `Yoni`, `Rachel` or `Eikko`, from a campaign tag or a `Name - ` prefix; null if neither |

### `daily[]` (new: per-campaign per-day rows for the 14-day window)

One row per campaign per day, only for campaigns that sent something in the window.

| Field | Type | Meaning |
|---|---|---|
| `date` | date | the day |
| `campaignId` | number | SmartLead campaign id |
| `sent` | number or null | emails sent that day (null: that day's analytics call failed) |
| `replies` | number or null | replies SmartLead counted for that day (null: the call failed) |

### `yesterday` -> artifact `YESTERDAY`

| Field | Type | Meaning |
|---|---|---|
| `label` | string | display date, `"Sep 24"` |
| `date` | date | yesterday, Eastern |
| `sent` | number | emails sent yesterday, all campaigns |
| `sendingCampaigns` | number | campaigns that sent at least one email yesterday |
| `replies` | number | Master Inbox replies whose Eastern `day` is yesterday |
| `interested` | number | of those, category Interested |
| `replyMix` | array of `[category, count]` | yesterday's replies by category, largest first; no category is `"Uncategorized"` |

### `inboxLog[]` -> artifact `INBOX_LOG`

Every Master Inbox reply in the window, newest first. This is the daily inbox log with
the SmartLead-to-Pipedrive sync check.

| Field | Type | Meaning |
|---|---|---|
| `t` | timestamp | reply time |
| `day` | date | reply date in Eastern time |
| `name` | string | lead's first + last name, `"[not provided]"` if SmartLead has neither |
| `email` | string | lead's email address |
| `campaign` | string | campaign name |
| `campaignId` | number | campaign id |
| `cat` | string or null | SmartLead lead category name; null = not categorized yet |
| `catId` | number or null | category id |
| `pd` | number or null | id of the Pipedrive person whose email matches `email`; null = no Pipedrive record |
| `status` | string | `synced`: `cat` is a sync category and `pd` exists. `gap`: sync category but no Pipedrive record ("Sync missing"). `uncategorized`: `cat` is null. `none`: a category the automation does not sync |

### `inboxes` -> artifact `INBOXES`

| Field | Type | Meaning |
|---|---|---|
| `total` | number | connected sending inboxes, fully paginated |
| `domains` | number | distinct sending domains among them |

`syncCategories` -> artifact `SYNC_CATEGORIES`.

---

## `pipedrive.json` (committed as `pipedrive.json.enc`)

Written by `scripts/pull/pipedrive.mjs`. Needs `PIPEDRIVE_API_TOKEN` and
`PIPEDRIVE_COMPANY_DOMAIN`.

```json
{
  "pulledAt": "...",
  "today": "2026-09-25",
  "overdue": [ ... ],
  "dueToday": [ ... ],
  "upcoming": [ ... ],
  "deals": [ ... ],
  "meta": { ... },
  "repNames": { "25109251": "Yoni", "25102178": "Rachel" }
}
```

### Activity rows: `overdue[]`, `dueToday[]`, `upcoming[]` -> `OVERDUE`, `DUE_TODAY`, `UPCOMING`

Open activities (`done = 0`) with a due date. Sorted by `due`, then `id`.

| Field | Type | Meaning |
|---|---|---|
| `id` | number | activity id |
| `subject` | string | activity subject |
| `type` | string | `call`, `task`, `meeting`, ... |
| `due` | date | due date |
| `person` | number or null | linked person id |
| `personName` | string or null | that person's name |
| `org` | number or null | linked organization id |
| `orgName` | string or null | that organization's name |
| `owner` | number | Pipedrive user id of the assignee |
| `days` | number | `overdue[]` only: days past due (1 or more) |
| `inDays` | number | `dueToday[]` (always 0) and `upcoming[]` (1 to 7): days until due |

`upcoming[]` covers the next 7 days after today.

### `deals[]` -> artifact `DEALS`

All deals (open, won and lost; both dashboards show won deals), oldest `added` first.

| Field | Type | Meaning |
|---|---|---|
| `id` | number | deal id |
| `title` | string | deal title |
| `stage` | string or null | stage name |
| `status` | string | `open`, `won`, `lost` |
| `value` | number | deal value (0 when not set; the team does not track value today) |
| `added` | date | date added |
| `closed` | date or null | close date |
| `owner` | number | owner user id |

### `meta` -> artifact `PD_META`

| Field | Type | Meaning |
|---|---|---|
| `openTotal` | number | open activities with a due date |
| `openTypeCounts` | object | open activities by type, e.g. `{ "call": 169, "task": 8, "meeting": 6 }` |
| `leadsByOwner` | object | non-archived leads per owner user id (keys are strings) |
| `leadsTotal` | number | non-archived leads |
| `leadsUnseen` | number | leads never opened (`was_seen = false`) |
| `personsTotal` | number | persons, fully paginated |
| `orgsTotal` | number | organizations, fully paginated |

### `repNames` -> artifact `REP_NAME`

Active Pipedrive user id (string key) to display name. Rep filter chips and "by rep"
charts are built from this, not from a hard-coded list.

---

## `heyreach.json`

Written by `scripts/pull/heyreach.mjs`. Needs `HEYREACH_API_KEY` (workspace key).

```json
{
  "pulledAt": "...",
  "primaryCampaignId": 12345,
  "linkedin": { ... },
  "campaigns": [ { "id": 12345, ... } ]
}
```

`linkedin` is the artifact's `LINKEDIN` constant, for the primary campaign (the first
campaign that is not a draft). `campaigns[]` has one row per campaign with the same
fields plus `id`, and without `campaigns` (the count).

| Field | Type | Meaning |
|---|---|---|
| `campaigns` | number | `linkedin` only: number of campaigns in the workspace |
| `id` | number | `campaigns[]` only: HeyReach campaign id |
| `campaignName` | string | campaign name |
| `status` | string | `Draft`, `In progress`, `Paused`, `Finished`, ... (HeyReach status, first letter capitalised) |
| `started` | date or null | start date, else creation date |
| `listName` | string or null | lead list the campaign targets |
| `senders` | number | LinkedIn sender accounts on the campaign |
| `leads` | number | leads in the campaign |
| `processed` | number | leads HeyReach has started working (returned by the leads endpoint) |
| `pending` | number | leads not started yet |
| `connectionsSent` | number | processed leads whose connection status is anything but `None` |
| `accepted` | number | connection status `ConnectionAccepted` |
| `connNone` | number | connection status `None` |
| `messagesSent` | number | message status anything but `None` |
| `replies` | number | message status `MessageReply` |
| `inSequence` | number | campaign status `InSequence` |
| `pendingInBatch` | number | campaign status `Pending` |
| `failed` | number | leads HeyReach reports as failed |
| `finished` | number | leads that finished the sequence |

Not available from the API: none known today. Stage 3 confirms each field against a
real response; any field HeyReach does not return is set to `null` and listed here.

---

## `semrush.json`

Written by `scripts/pull/semrush.mjs`. Needs `SEMRUSH_API_KEY`; `SEMRUSH_SITE_AUDIT_ID`
optional. One fixed call set, at most once per Eastern day (a second run the same day
keeps the morning's file unless `SEMRUSH_FORCE=1`): `domain_ranks` and `domain_organic` for
albertscott.com, `phrase_organic` with `display_limit=1` for each keyword in
`seo_keywords.json`, and the Site Audit snapshot when the project id is set.

```json
{
  "pulledAt": "...",
  "baselineAt": "2026-08-27",
  "domain": "albertscott.com",
  "database": "us",
  "unitsUsed": 180,
  "keywords": [ { "q": "Amazon agency", "pos": null, "top": "myamazonguy.com", "branded": false, "url": null, "volume": 2900 } ],
  "geo": { "checkedAt": "2026-09-03", "baselineAt": "2026-08-27", "sources": [ ... ] },
  "health": { "source": "semrush" , "checkedAt": "...", "items": [ ... ] }
}
```

| Field | Type | Meaning |
|---|---|---|
| `pulledAt` | timestamp | Semrush call time. Artifact `SEO_PULLED` is this, formatted `"Sep 25, 2026"` |
| `baselineAt` | date | baseline the page compares against. Artifact `SEO_BASELINE`, formatted |
| `unitsUsed` | number | API units this run spent: the balance before minus after, or an estimate of 10 per row if the balance could not be read |
| `unitsLeft` | number or null | the account's remaining API units after the run |
| `rankedKeywords` | number | how many keywords albertscott.com ranks for in the database (sets how many `domain_organic` rows are bought, capped at 100) |
| `keywords[]` | array | artifact `SEO_KEYWORDS`, one row per keyword in `seo_keywords.json`, same order |
| `keywords[].q` | string | the keyword |
| `keywords[].pos` | number or null | albertscott.com's organic position in the Semrush US database; null = not in the top 100 |
| `keywords[].top` | string or null | the #1 organic result's domain |
| `keywords[].branded` | boolean | from `seo_keywords.json` |
| `keywords[].url` | string or null | the albertscott.com URL that ranks |
| `keywords[].volume` | number or null | monthly search volume |
| `geo` | object | artifact `SEO_GEO` / Pages `SEO_GEO_SOURCES` is `geo.sources`. **Not from Semrush**: copied as-is from `seo_geo.json` |
| `health.source` | `semrush` or `manual` | `manual` when `SEMRUSH_SITE_AUDIT_ID` is not set: items are copied from `seo_health_manual.json` |
| `health.items[]` | array | artifact `SEO_HEALTH`: `{ item, status: "good" or "bad", note }` |

Positions are Semrush database positions (updated on Semrush's schedule), not a live
Google check like the Sep 3 pulse, so they can differ from what a browser shows.

---

## `seo_issues.json`

The albertscott.com audit backlog the Pages SEO page renders. Written by
`scripts/pull/seo-issues.mjs` from the shared Google Sheet when
`GOOGLE_SERVICE_ACCOUNT_JSON` and `SEO_TRACKER_FILE_ID` are set; until then it holds the
Sep 11 snapshot that was embedded in the page, and the manifest marks it `stale`.

```json
{ "sourceUpdated": "2026-09-11", "source": "...", "issues": [ { "id": "AS-001", "pri": "P1", "ref": "R15", "cat": "...", "page": "...", "url": "...", "issue": "...", "desc": "...", "fix": "...", "st": "Open" } ] }
```

| Field | Meaning |
|---|---|
| `sourceUpdated` | the sheet's last-edited date. Pages `SEO_SOURCE_UPDATED` is this, formatted |
| `issues[]` | Pages `SEO_ISSUES`: `id` tracker id, `pri` P1 to P3, `ref` roadmap workstream (looked up in `SEO_TRACKS` in code), `cat` category, `page`, `url`, `issue`, `desc`, `fix`, `st` Open / Done / Skipped |

---

## `smartscout.json` (written by the Claude scheduled task, not by GitHub)

SmartScout has no server-side API on this plan, so GitHub never writes this file. The
daily Claude task ("Dashboard sync: SmartScout + artifact", 10:15 UTC) pulls every brand
in `smartscout_watchlist.json` through the SmartScout connector and commits this file
to `main`. Until its first run the file is `{ "pulledAt": null, "watchlist": [], "brands": [] }`
and both dashboards show "Waiting for first SmartScout sync".

```json
{
  "pulledAt": "2026-09-25T10:21:05.000Z",
  "watchlist": ["Example Brand"],
  "brands": [
    {
      "brand": "Example Brand",
      "category": "Beauty & Personal Care",
      "subcategory": "Example Subcategory",
      "monthlyRevenue": 100000,
      "ttmRevenue": 1200000,
      "totalProducts": 50,
      "totalReviews": 1000,
      "avgRating": 4.5,
      "avgSellers": 2.0,
      "dominantSeller": "Example Seller LLC",
      "dominantSellerSharePct": 70.0,
      "amazon1pPct": 10.0,
      "momGrowth": 0.03,
      "mom12Growth": 0.1,
      "storefrontUrl": null,
      "topSellers": [ { "name": "Example Seller LLC", "sharePct": 70.0 } ],
      "topSubcategories": [ { "name": "Example Subcategory", "marketSharePct": 3.0, "rank": 5 } ],
      "error": null
    }
  ]
}
```

| Field | Type | SmartScout source and conversion |
|---|---|---|
| `pulledAt` | timestamp | when the task ran |
| `watchlist` | string[] | the watchlist as read that run (first 150 if longer) |
| `brands[]` | array | one row per watchlist brand, same order |
| `brand` | string | the watchlist name exactly as written in the watchlist |
| `category` | string or null | profile "Primary Category" |
| `subcategory` | string or null | profile "Primary Subcategory" |
| `monthlyRevenue` | number or null | profile "Total Monthly Revenue", USD |
| `ttmRevenue` | number or null | profile "Trailing 12-Month Revenue", USD |
| `totalProducts` | number or null | profile "Total Products" |
| `totalReviews` | number or null | profile "Total Reviews" |
| `avgRating` | number or null | profile "Average Rating" (0 to 5) |
| `avgSellers` | number or null | profile "Average Sellers" |
| `dominantSeller` | string or null | the seller with the largest share in the seller-coverage query (falls back to profile "Single Seller Name") |
| `dominantSellerSharePct` | number or null | that seller's "Estimated Brand Share", already 0 to 100 |
| `amazon1pPct` | number or null | profile "Average Amazon Revenue %" **times 100** (SmartScout returns a fraction, `0.816` becomes `81.6`) |
| `momGrowth` | number or null | profile "Average MoM Growth", kept as a fraction |
| `mom12Growth` | number or null | profile "Average 12-Month MoM Growth", kept as a fraction |
| `storefrontUrl` | string or null | profile "Storefront URL"; null when "Has Storefront" is false or the URL is empty |
| `topSellers[]` | array | up to 5 sellers from the seller-coverage query, largest first: `{ name, sharePct }` (share 0 to 100) |
| `topSubcategories[]` | array | up to 3 from the subcategory query: `{ name, marketSharePct, rank }` (the brand's share of that subcategory, 0 to 100, and its rank there) |
| `error` | string or null | `"not found"` when SmartScout has no such brand (every other field null); another message for a failed query |

Never estimate or fill a number SmartScout did not return; leave it null.

### `smartscout_watchlist.json` (hand-edited)

A JSON array of brand names exactly as SmartScout spells them. Add a brand here and it
appears in both dashboards after the next Claude task run.

Seeded with current clients found in the repo and the artifact (won Pipedrive deals and
client call recordings): Scentco, Mexico's Finest, Art of Beauty, Rufus Teague,
Wholesome Hippy, Katjes, Zoya.

---

## `tradeshows.json` (the trade show calendar, maintained outside this pipeline)

The calendar produced by the trade show calendar project (the Calendar tab of
`tradeshow_calendar_FINAL.xlsx`, as JSON), committed exactly as delivered.
`scripts/pull/tradeshows.mjs` only validates it and updates `manifest.sources.tradeshows`;
it never rewrites the file. The shape is that project's, kept as-is: a JSON **array** of
shows (an object `{ "shows": [...] }` is also accepted).

| Field | Type | Meaning |
|---|---|---|
| `showName` | string | show name (required) |
| `startDate` | date | first day (required) |
| `endDate` | date | last day, not before `startDate` |
| `city`, `state`, `venue` | string | location; `""` when unknown |
| `website` | string | official site |
| `exhibitorListUrl` | string | public exhibitor list, `""` if none |
| `industryCategories` | string | what the show covers |
| `whyAmazonRelevant` | string | why the exhibitors are Amazon prospects |
| `estExhibitors`, `estAttendees` | string | published counts as text (`"1,200+"`), `""` if none |
| `relevance` | string | `High`, `Medium`, `Low` |
| `status` | string | the calendar project's verification status: `Verified`, `New`, `Date changed`, or `""` |
| `sourceUrls` | string[] | where the dates and counts came from |
| `notes` | string | the calendar project's research notes (not attendance notes) |
| `lastVerified` | date | when the row was last checked |

**Show id.** Rows carry no id, so both dashboards and the notes file use
`showId = slug(showName) + "-" + startDate`, e.g. `coffee-fest-2026-10-17` (the slug is the
name lowercased, accents stripped, every run of non-alphanumerics turned into `-`). The
name and start date together are unique (Coffee Fest appears twice, on different dates).
If a show's start date changes, its id changes; the notes file keeps the old entry and the
dashboards flag it as an orphaned note.

The validator rejects the file for a missing `showName` or `startDate`, a bad date,
`endDate` before `startDate`, a non-array `sourceUrls`, or two rows with the same id.

---

## `tradeshow_notes.json` (attendance notes, written by the Claude task)

Who is going to which show, and notes about it. Yoni edits these on the Trade Shows page of
the Claude artifact, where they are saved immediately in the artifact's own shared store.
The daily Claude task copies them into this file, so the GitHub Pages calendar shows them
(read-only) at most a day later. Kept separate from `tradeshows.json` so a new calendar
delivery never overwrites anyone's notes.

```json
{
  "updatedAt": "2026-09-26T10:20:00.000Z",
  "people": ["Yoni", "Maria", "Rachel"],
  "notes": {
    "example-show-2026-11-03": {
      "attending": ["Yoni"],
      "note": "Booth meetings booked Tuesday",
      "updatedBy": "Yoni",
      "updatedAt": "2026-09-26T09:58:12.000Z"
    }
  }
}
```

| Field | Type | Meaning |
|---|---|---|
| `updatedAt` | timestamp or null | when the Claude task last copied notes into this file |
| `people` | string[] | who can be marked as attending: Yoni, Maria, Rachel |
| `notes` | object | keyed by show id (see above) |
| `notes.<id>.attending` | string[] | people attending, each one of `people`; `[]` = nobody yet |
| `notes.<id>.note` | string | free-text note, `""` when none |
| `notes.<id>.updatedBy` | string or null | who last saved it, when the artifact knows |
| `notes.<id>.updatedAt` | timestamp | when it was last saved in the artifact |

---

## `resources.json` (hand-edited)

The Resources page, moved out of code. Data from the Sep 12, 2026 invoice sweep.

| Key | Artifact / Pages constant | Row fields |
|---|---|---|
| `checkedAt` | `TOOL_CHECKED` | display date string |
| `platformTools[]` | `PLATFORM_TOOLS` | `name, state, purpose, plan, monthly, annual, renewal, last, ref, note` |
| `vendors[]` | `VENDORS` | `name, purpose, monthly, annual, coverage, renewal, ref` |
| `domainWaves[]` | `DOMAIN_WAVES` | `wave, registrar, count, mailboxProvider, perYear, renewal` |
| `otherTools[]` | `OTHER_TOOLS` | `name, state, purpose, monthly, day, last, ref, note` |
| `metaAds` | `META_ADS` | `charges, total, from, to, since` |

`state` is one of `verified`, `partial`, `usage`, `none`. `monthly` / `annual` are null
when no price is on file.

Text fields may contain live-count tokens that the page fills in at render time from
the other files: `{{INBOXES.total}}`, `{{PD_META.leadsTotal}}`, `{{PD_META.openTotal}}`,
`{{PD_META.personsTotal}}`, `{{LINKEDIN.campaigns}}`, `{{LINKEDIN.leads}}`. This keeps
"all 111 mailboxes" correct when the inbox count changes.

The Pages version is the source: Smartlead moved from `vendors` to `platformTools` on
Sep 12 with the Sep 1 receipt, so the artifact's older 7-row vendor list (Smartlead
included, Sep 2 receipt) is retired.

---

## Seed and reference files (hand-edited, plain)

| File | Shape | Used by |
|---|---|---|
| `seo_keywords.json` | `[{ q, branded }]` | the keyword list `semrush.mjs` tracks. Seeded from the artifact's 15 `SEO_KEYWORDS`. Every keyword added costs about 10 Semrush units per day |
| `seo_geo.json` | `{ checkedAt, baselineAt, sources: [{ source, status: "checked" or "blocked", listed: true/false/null, note }] }` | AI-search directory checks. No API provides these; update by hand or with the SEO skill |
| `seo_health_manual.json` | `{ checkedAt, items: [{ item, status, note }] }` | fallback for `semrush.json` `health` when no Site Audit project is configured |

---

## `history/YYYY-MM-DD.json`

One small file per day, written by `run-all.mjs` after the pulls (and the SmartScout
total patched in by the Claude task). Files older than 180 days are deleted on each
run. Plain JSON: aggregates only.

```json
{
  "date": "2026-09-25",
  "generatedAt": "...",
  "sent": 2150,
  "replies": 23,
  "interested": 1,
  "overdue": 183,
  "dealsOpen": 1,
  "linkedinAccepted": 16,
  "smartscoutWatchlistRevenue": null
}
```

| Field | Meaning |
|---|---|
| `date` | the refresh date (Eastern); the file name |
| `sent`, `replies`, `interested` | `smartlead.yesterday` values, i.e. activity on the day before `date` |
| `overdue` | `pipedrive.overdue.length` |
| `dealsOpen` | deals with `status = open` |
| `linkedinAccepted` | `heyreach.linkedin.accepted` (campaign to date) |
| `smartscoutWatchlistRevenue` | sum of `monthlyRevenue` over watchlist brands that have one; null until SmartScout has run |

A source that failed that day writes `null` for its fields rather than repeating
yesterday's number.

---

## Built artifact

`scripts/build-artifact.mjs` turns this data into the complete Claude artifact page:
`docs/artifact/alberscott-dashboard.html.enc` (same `.enc` format, the plaintext is the
HTML). Its DATA BLOCK emits `DATA_DATE`, `TODAY`, `OVERDUE`, `DUE_TODAY`, `UPCOMING`,
`CAMPAIGNS`, `DEALS`, `INBOX_LOG`, `YESTERDAY`, `LINKEDIN`, `PD_META`, `INBOXES`,
`REP_NAME`, `SYNC_CATEGORIES`, `SEO_PULLED`, `SEO_BASELINE`, `SEO_KEYWORDS`, `SEO_GEO`,
`SEO_HEALTH`, `SEO_ISSUES`, `SEO_SOURCE_UPDATED`, `VENDORS`, `DOMAIN_WAVES`,
`PLATFORM_TOOLS`, `OTHER_TOOLS`, `META_ADS`, `TOOL_CHECKED`, `SMARTSCOUT`, `MANIFEST`,
each on its own line as `const NAME = <json>;` so the Claude task can replace the
`SMARTSCOUT` line and patch `MANIFEST` without touching anything else.
