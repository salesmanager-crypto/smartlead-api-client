# Dashboard sync plan: one data pipeline for Pages + the Claude artifact

Stage 1 output. Nothing in the repo was changed to write this except this file.
Inspected on 2026-09-25 against `main` at `a3e038e`, every remote branch, the live
Pages site, the Actions run history, and the live artifact
(`https://claude.ai/artifact/Vei7Pm31JHf9QmzR4bJo5G`, version `1789395094-0f22`).

---

## 0. Findings that change the plan

Read these first. Four of them need a decision before stage 2 (section 8).

1. **Pages does not serve `main`.** The live site is built by GitHub's legacy
   "pages build and deployment" from the **root of branch
   `claude/crm-live-dashboard-abd47v`** (run 35757560379, head `a431c8f`,
   "Dashboard build 2026-09-22 12:57 EDT"). That branch forked from an old base and
   also carries an unrelated React/Vite prototype under `dashboard/src/`. `main`'s
   `index.html` is a redirect to `dashboard/command-center.html`, which 404s on the
   live site. So today there is no folder on `main` that Pages serves.
2. **The login is real encryption, not a cosmetic gate.** The live `index.html`
   (585 KB) is a sign-in page plus one AES-256-GCM ciphertext of the whole filled
   dashboard. Each account (`sales`, `yoni`) has its own copy of the content key,
   wrapped under PBKDF2-SHA256 (600,000 iterations) of `username + NUL + password`.
   Commit `83bbcf5` says this was done on purpose: "this public branch holds
   ciphertext only". The script that produced the ciphertext is **not in any branch**;
   the builds were made locally and committed by hand.
3. **The live Pages data is 3 days stale and nothing refreshes it.**
   `refresh-data.yml` succeeds every ~6 hours on `main` (so `SMARTLEAD_API_KEY`,
   `PIPEDRIVE_API_TOKEN`, `PIPEDRIVE_COMPANY_DOMAIN`, `HEYREACH_API_KEY` secrets exist
   and work), but it only uploads a workflow artifact and discards the fill. The
   encrypted page was last rebuilt by hand on Sep 22.
4. **The two dashboards already run different code, not just different data.**
   `dashboard/command-center.html` (the Pages source) has moved on from the artifact
   template: SmartLead has campaign and inbox drill-down routes, SEO is an issue
   tracker (`SEO_ISSUES`, `SEO_TRACKS`) plus the keyword pulse, Resources has
   `PLATFORM_TOOLS`, `OTHER_TOOLS`, `META_ADS`, and `REP_NAME` is generated. The
   artifact template still has the Sep 2 layout (`SEO_HEALTH`, old `VENDORS` with
   Smartlead in it, hard-coded `REP_NAME`). A shared data layer alone will not make
   them match; see decision D3.
5. **SEO data is not from Semrush today.** Both dashboards say "no Semrush or paid
   rank tracker": `SEO_KEYWORDS` and `SEO_GEO` came from a WebSearch/WebFetch pulse on
   Sep 3, `SEO_HEALTH` is three hand-written spot checks. `SEO_GEO` (is Albert Scott
   listed on novadata.io / clutch.co) has no Semrush equivalent at all.
6. **No trade show calendar exists** in any branch. `claude/lucid-fermi-e28tzl` and
   `claude/eager-einstein-b2th04` hold exhibitor-list enrichment work (lead lists),
   not a calendar. `tradeshows.json` will be created empty with a defined shape.
7. **No SmartScout section exists** on either dashboard (placeholder page on both), so
   there is no tracked brand list to seed the watchlist from.
8. **`artifact_template_alberscott_dashboard.html` is not in the repo.** I pulled the
   current artifact HTML with the Artifact tool instead (1532 lines, 183.7 KB). Stage 6
   commits that copy as the template.
9. **Pipedrive has no client on `main`.** `apply-constants.mjs` calls the API with
   raw `fetch`; a v1 `PipedriveClient` exists only on the crm-live branch
   (`src/pipedrive.js`, write-oriented, no pagination cursor). The existing pull code
   also needs `PIPEDRIVE_COMPANY_DOMAIN`, a fifth secret the brief does not list.
10. **Workflow artifacts are not private on a public repo.** `refresh-data.yml` says
    the filled dashboard is "visible only to people with repo access"; on a public
    repo any signed-in GitHub user can download it. Worth knowing whatever we pick.

---

## 1. Which folder Pages serves

| | Today | Proposed |
|---|---|---|
| Source | Branch `claude/crm-live-dashboard-abd47v`, `/ (root)`, legacy build | Branch `main`, folder `/docs`, legacy build |
| Entry | `index.html` (encrypted, 585 KB) | `docs/index.html` (same sign-in page) |
| Jekyll | On (no front matter, so HTML passes through) | Off, via `docs/.nojekyll`, so `.json` and `_`-prefixed files serve raw |

`<pages>` below means `docs/`. Why `/docs` on `main`: it is one of the two folders a
branch deploy can serve, the scheduled task prompt already looks there first, and the
daily workflow's push then *is* the deploy (no Pages deploy step needed).

Cutover is one setting change Yoni makes after stage 5 is verified:
**Settings > Pages > Build and deployment > Branch: `main`, folder `/docs`**. Until
then the current site keeps serving from the crm-live branch, so there is no downtime.

## 2. How the login gate works

Everything is client-side, in the live `index.html`:

- `U = { sales: {s, i, w}, yoni: {s, i, w} }`: per-user salt, IV, and the wrapped
  content key. `D = { iv, ct, iter: 600000 }`: the encrypted dashboard.
- `unlock(user, pass)`: PBKDF2-SHA256(`user\0pass`, salt, 600k) -> key-encryption key ->
  AES-GCM unwrap of the content key -> AES-GCM decrypt of `D.ct` -> HTML string ->
  `document.open(); document.write(html)`.
- Wrong user and wrong password fail identically (GCM auth failure).
- Remembers `{n, p}` in `sessionStorage["cc-session"]` for the tab; also accepts a
  bookmarked `#u=...&p=...` fragment, which it strips from the address bar.

Consequence: whoever rebuilds the page needs the **content key** (same key for every
user). Any one user's password recovers it. New ciphertext encrypted with that key
keeps working with the existing `U` records, so no one's password changes.

## 3. Sections on the Pages dashboard and where their data comes from today

Source file: `dashboard/command-center.html` (committed data-free). The DATA BLOCK is
filled at build time by `dashboard/pull/apply-constants.mjs`, then the whole page is
encrypted by hand. **Nothing is fetched at runtime; everything is embedded.**

| Route | Section | Constants used | Source today |
|---|---|---|---|
| `#/` Main | Overdue / due today / open deals KPIs, overdue by rep, most overdue, yesterday's sends, replies, LinkedIn | `OVERDUE`, `DUE_TODAY`, `UPCOMING`, `DEALS`, `PD_META`, `YESTERDAY`, `INBOX_LOG`, `LINKEDIN`, `REP_NAME`, `DATA_DATE`, `TODAY` | Embedded, from APIs at build |
| `#/smartlead` (+ `/inbox`, `/campaign/:id`) | KPIs, daily inbox log with Pipedrive sync check, status mix, reply mix, campaigns table, drill-downs | `CAMPAIGNS`, `INBOX_LOG`, `YESTERDAY`, `INBOXES`, `SYNC_CATEGORIES` | Embedded, from SmartLead (+ Pipedrive persons for the sync check) |
| `#/pipedrive` | Activity KPIs, overdue/today/upcoming table, deals, leads by owner, contacts on file, BlueDot list | `OVERDUE`, `DUE_TODAY`, `UPCOMING`, `DEALS`, `PD_META`, `REP_NAME` | Embedded, from Pipedrive. BlueDot list is hard-coded HTML (Aug 27) |
| `#/linkedin` | Campaign KPIs, lead progress, connection status | `LINKEDIN` | Embedded, from HeyReach (first non-draft campaign only) |
| `#/seo` | Issue tracker (status/priority/workstream filters), keyword table, GEO sources | `SEO_ISSUES`, `SEO_SOURCE_UPDATED`, `SEO_TRACKS`, `SEO_KEYWORDS`, `SEO_GEO_SOURCES`, `SEO_PULLED`, `SEO_BASELINE` | `SEO_ISSUES` block from Google Sheet via `pull-seo-tracker.mjs` (secrets not set, so static Sep 11); the rest hand-typed |
| `#/smartscout` | Placeholder | none | none |
| `#/general` Resources | Platform tools, vendors, domain waves, other tools, Meta ads | `PLATFORM_TOOLS`, `VENDORS`, `DOMAIN_WAVES`, `OTHER_TOOLS`, `META_ADS`, `TOOL_STATE`, `TOOL_CHECKED` | Hand-typed (invoice sweep Sep 12) |
| `#/automation` | Placeholder (Claude Activity Log) | none | none |

## 4. APIs the repo already calls, and their env vars

| API | Code | Env vars |
|---|---|---|
| SmartLead | `src/client.js` (`SmartleadClient`, retries 429/5xx, `maxRetries=3`); vendored copy `dashboard/pull/vendor/smartlead-client.js` (identical) | `SMARTLEAD_API_KEY`, `SMARTLEAD_BASE_URL` (optional) |
| HeyReach | `src/heyreach.js` (`HeyReachClient`); vendored copy (identical) | `HEYREACH_API_KEY` (workspace), `HEYREACH_ORG_API_KEY` (org, optional) |
| Pipedrive | raw `fetch` inside `apply-constants.mjs` (v1 + v2, cursor pagination, 429 retry); `src/pipedrive.js` only on crm-live branch | `PIPEDRIVE_API_TOKEN`, `PIPEDRIVE_COMPANY_DOMAIN` |
| Google Drive/Sheets | `dashboard/pull/vendor/google-auth.js`, `src/googlesheets.js` | `GOOGLE_SERVICE_ACCOUNT_JSON`, `SEO_TRACKER_FILE_ID`, `SEO_TRACKER_TAB` (Actions); `GOOGLE_SERVICE_ACCOUNT_EMAIL`, `..._PRIVATE_KEY`, `GOOGLE_SHEETS_SPREADSHEET_ID` (local) |
| QuickEmailVerification | `src/quickemailverification.js` | `QUICKEMAILVERIFICATION_API_KEY` |
| Premium Inboxes | `src/premiuminboxes.js` | `PREMIUM_INBOXES_API_KEY` |
| Porkbun | `src/porkbun.js` | `PORKBUN_API_KEY`, `PORKBUN_SECRET_API_KEY` |
| Namecheap | `src/namecheap.js` | `NAMECHEAP_API_USER`, `NAMECHEAP_API_KEY`, `NAMECHEAP_USERNAME`, `NAMECHEAP_CLIENT_IP` |
| Fathom | `src/fathom.js` | `FATHOM_API_KEY` |
| Semrush | **none** | `SEMRUSH_API_KEY` (new) |
| SmartScout | **none** (Claude connector only) | n/a |

The `scripts/*.mjs` (bounce pause, deliverability, inbox report, etc.) use the same
SmartLead/Porkbun clients and are unrelated to the dashboards.

## 5. Workflows

| Workflow | Trigger | What it does |
|---|---|---|
| `.github/workflows/refresh-data.yml` "Refresh dashboard data" | cron `17 */6 * * *` + manual | Checks out `main`, runs `apply-constants.mjs` with the SmartLead/Pipedrive/HeyReach secrets, tries `pull-seo-tracker.mjs` (skips: Google secrets unset), uploads the filled HTML as a 7-day workflow artifact, discards the fill. Does not publish anything. `permissions: contents: read`. |
| `.github/workflows/deploy-pages.yml` "Deploy dashboard" | manual only | Actions-based Pages deploy of the **data-free** `command-center.html`. Unused: Pages is on a branch source, and if it were run it would publish an empty, unencrypted dashboard. |
| "pages build and deployment" (GitHub-managed) | push to `claude/crm-live-dashboard-abd47v` | Serves that branch's root. |

## 6. Artifact constants and where each will come from

The builder must emit every one with the same name and shape. Shapes below are taken
from the live artifact.

| Constant | Shape (fields) | Source file | Produced by |
|---|---|---|---|
| `DATA_DATE` | `"Sep 2, 2026"` | `manifest.json` (`today`, formatted) | run-all |
| `TODAY` | `"2026-09-02"` (America/New_York) | `manifest.json` | run-all |
| `OVERDUE` | `{id, subject, type, due, person, personName, org, orgName, owner, days}` | `pipedrive.json` `.overdue` | Pipedrive activities `done=0`, `due < today` |
| `DUE_TODAY` | same, `inDays: 0` instead of `days` | `pipedrive.json` `.dueToday` | `due == today` |
| `UPCOMING` | same, `inDays` 1..7 | `pipedrive.json` `.upcoming` | `today < due <= today+7` |
| `DEALS` | `{id, title, stage, status, value, added, closed, owner}` | `pipedrive.json` `.deals` | Pipedrive v2 deals + stages |
| `PD_META` | `{openTotal, openTypeCounts{call,task,meeting,...}, leadsByOwner{id:n}, leadsTotal, leadsUnseen, personsTotal, orgsTotal}` | `pipedrive.json` `.meta` | Pipedrive activities, leads, persons, orgs |
| `REP_NAME` (outside the artifact block today) | `{userId: name}` | `pipedrive.json` `.repNames` | Pipedrive `/users` (active) |
| `CAMPAIGNS` | `{id, name, status, created, sent, reply, bounce, leads, interested, replyRate, bounceRate, rep}` | `smartlead.json` `.campaigns` | SmartLead campaigns + per-campaign analytics |
| `INBOX_LOG` | `{t, day, name, email, campaign, campaignId, cat, catId, pd, status}` | `smartlead.json` `.inboxLog` | SmartLead master inbox (7 days) + lead categories + Pipedrive person emails |
| `YESTERDAY` | `{label, date, sent, sendingCampaigns, replies, interested, replyMix[[cat,n]]}` | `smartlead.json` `.yesterday` | analytics-by-date for yesterday + inbox log |
| `INBOXES` | `{total, domains}` | `smartlead.json` `.inboxes` | SmartLead email accounts (paginated) |
| `SYNC_CATEGORIES` | `["Interested","Meeting Request","Follow Up"]` | `smartlead.json` `.syncCategories` | constant in the pull script |
| `LINKEDIN` | `{campaigns, campaignName, status, started, listName, senders, leads, processed, pending, connectionsSent, accepted, connNone, messagesSent, replies, inSequence, pendingInBatch, failed, finished}` | `heyreach.json` (primary campaign, plus a `campaigns[]` array of the same shape) | HeyReach campaigns + leads |
| `SEO_PULLED`, `SEO_BASELINE` | date strings | `semrush.json` `.pulledAt`, `.baselineAt` | semrush.mjs |
| `SEO_KEYWORDS` | `{q, pos, top, branded}` | `semrush.json` `.keywords` (list from `seo_keywords.json`) | Semrush (see decision D4) |
| `SEO_GEO` (Pages calls it `SEO_GEO_SOURCES`) | `{source, status, listed, note}` | `semrush.json` `.geo`, carried from a hand-edited `seo_geo.json` | **not Semrush**; manual / SEO skill |
| `SEO_HEALTH` | `{item, status: good/bad, note}` | `semrush.json` `.health` | Semrush Site Audit summary (needs a Site Audit project id) |
| `VENDORS` | `{name, purpose, monthly, annual, coverage, renewal, ref}` | `resources.json` `.vendors` | hand-edited data file |
| `DOMAIN_WAVES` | `{wave, registrar, count, mailboxProvider, perYear, renewal}` | `resources.json` `.domainWaves` | hand-edited data file |
| `SMARTSCOUT` (new) | per SCHEMA.md | `smartscout.json` | Claude scheduled task |
| `MANIFEST` (new) | `{generatedAt, today, sources{...}}` | `manifest.json` | run-all / write.mjs |

Pages-only constants that the artifact will also need if it is to mirror Pages
(decision D3): `SEO_ISSUES`, `SEO_SOURCE_UPDATED` (-> `seo_issues.json`),
`PLATFORM_TOOLS`, `OTHER_TOOLS`, `META_ADS`, `TOOL_CHECKED` (-> `resources.json`).
`SEO_TRACKS` and `TOOL_STATE` are lookup tables that stay in code.

Hard-coded numbers inside render functions that go stale and will be wired to data:
Pipedrive rep chips and `leadsByOwner` literal, Resources "37 domains" and
"$550.08/yr", overview rep list `[25109251, 25102178, 26939288]`, SEO "3 checked".

---

## 7. Files I will add or change

### Stage 2: data contract
- add `docs/.nojekyll`
- add `docs/data/SCHEMA.md` (every field of every file below)
- add `docs/data/smartscout_watchlist.json` (seed, see D5)
- add `docs/data/seo_keywords.json` (seeded from the artifact's 15 `SEO_KEYWORDS`)
- add `docs/data/seo_geo.json` (seeded from `SEO_GEO`, hand-maintained)
- add `docs/data/resources.json` (`VENDORS`, `DOMAIN_WAVES`, plus Pages' `PLATFORM_TOOLS`, `OTHER_TOOLS`, `META_ADS`, `TOOL_CHECKED`)
- add `docs/data/tradeshows.json` (empty `shows: []`, shape defined)
- add `docs/data/smartscout.json` (empty `brands: []`, shape defined, until the Claude task writes it)

### Stage 3: pull scripts
- add `scripts/pull/lib.mjs` (env loading from `.env`, retrying fetch for 429/5xx x3 with backoff, ET date helpers, secret-free error messages)
- add `scripts/pull/write.mjs` (atomic JSON write, manifest update with ok/stale/error, history write + 180-day prune)
- add `scripts/pull/smartlead.mjs` (uses `src/client.js`)
- add `scripts/pull/pipedrive.mjs` (adds cursor-paginated reads; see below)
- add `scripts/pull/heyreach.mjs` (uses `src/heyreach.js`)
- add `scripts/pull/semrush.mjs` (one fixed call set per run, unit budget logged)
- add `scripts/pull/tradeshows.mjs` (validate only)
- add `scripts/pull/seo-issues.mjs` (port of `pull-seo-tracker.mjs` writing `seo_issues.json`; skips cleanly without Google secrets)
- add `scripts/pull/run-all.mjs`
- add `src/pipedrive.js` (read-side client: v1/v2 GET with pagination, retry; ported from the crm-live branch version and extended)
- change `.env.example` (add `PIPEDRIVE_API_TOKEN`, `PIPEDRIVE_COMPANY_DOMAIN`, `SEMRUSH_API_KEY`; SmartLead/HeyReach already there)
- change `package.json` (npm scripts `pull`, `build:artifact`; no dependencies)
- add generated `docs/data/{manifest,smartlead,pipedrive,heyreach,semrush,seo_issues}.json`, `docs/data/history/2026-09-2x.json`

### Stage 4: workflow
- add `.github/workflows/daily-refresh.yml` (09:15 UTC + manual, concurrency group, `contents: write`, commit only if `docs/data/` or `docs/artifact/` changed)
- change `.github/workflows/refresh-data.yml`: delete (superseded; it would otherwise keep pulling every 6h for nothing)
- change `.github/workflows/deploy-pages.yml`: delete (Pages will be a branch deploy from `/docs`; this workflow would publish an unencrypted empty page)

### Stage 5: Pages reads the data files
- change `dashboard/command-center.html`: replace the embedded DATA BLOCK with a loader that fetches `data/*.json` and assigns the same global names, then renders; add "Data as of" + per-source status pills to the top bar; real SmartScout page with "Waiting for first SmartScout sync"; wire the hard-coded numbers listed in section 6
- add `scripts/build-pages.mjs`: encrypts `dashboard/command-center.html` into `docs/index.html` using the existing sign-in page and `DASHBOARD_CONTENT_KEY` (see D1/D2)
- add `scripts/recover-content-key.mjs`: Yoni runs it once locally with his own username/password to print the content key for the secret (never committed, never sent to me)
- add `scripts/test/screenshot-routes.mjs` (Playwright, uses the preinstalled Chromium; dev-only, not a runtime dependency)
- add `docs/screenshots/pages-*.png`
- change `dashboard/pull/apply-constants.mjs`, `dashboard/build.mjs`: delete after cutover (replaced by `scripts/pull/*`); `dashboard/pull/vendor/` goes with them
- change `index.html` (root): delete or leave as redirect to `docs/`; root is no longer served

### Stage 6 and 7 (listed for completeness)
- add `dashboard/artifact/template.html` (the artifact copy; I would use `dashboard/` rather than a new `dashboards/` folder so there is one dashboard folder, say if you want the brief's path instead)
- add `scripts/build-artifact.mjs`, generated `docs/artifact/alberscott-dashboard.html`, `docs/screenshots/artifact-*.png`
- change `README.md`, `dashboard/README.md`

---

## 8. Decisions needed before stage 2

**D1. What happens to the login's protection.** The brief moves the data to plain
`docs/data/*.json` in a public repo. That makes the sign-in page decorative: anyone
can open `.../data/pipedrive.json` or `raw.githubusercontent.com/...` and read every
prospect name, every Master Inbox reply sender's email address (about 80 per week), deal
names, and vendor order numbers, with no login. `noindex` does not apply to JSON files.
Today that data is ciphertext only. Yoni has said the repo stays public and he knows
the JSON is readable, so option A is the default; I am flagging it once because the
current page was built specifically to avoid this and the data is mostly other
people's contact details.

- **A. As briefed (default).** Plain JSON, sign-in page kept for looks. Simplest; the
  Claude task reads plain files.
- **B. Keep real protection for person-level files (my recommendation).** `pipedrive.json`
  and `smartlead.json` are written encrypted (`.json.enc`, same content key as the
  login) by the workflow; the page decrypts them after sign-in. Aggregate files
  (`manifest`, `heyreach`, `semrush`, `smartscout`, `tradeshows`, `history`) stay plain,
  so the SmartScout write-back needs no key. Cost: one extra secret
  (`DASHBOARD_CONTENT_KEY`), and the built artifact file can then not sit in the repo
  in plain text; the workflow commits it encrypted and the Claude task decrypts it
  with the key held in the task's prompt (the task needs a shell to run one `node`
  command).

**D2. The content key.** Either way, re-encrypting the Pages app needs the content key
(section 2). Yoni runs `node scripts/recover-content-key.mjs` locally once (it asks for
his username and password, prints the key) and saves the output as the Actions secret
`DASHBOARD_CONTENT_KEY`. If he would rather issue new passwords instead, I build a
fresh key and he sets `DASHBOARD_USERS` (JSON of user to password) as a secret.

**D3. One page codebase instead of two.** "Same sections, same data" is not true today
(finding 4). Recommendation: generate the artifact from the **Pages source**
(`dashboard/command-center.html`) with the data inlined into the DATA BLOCK, rather than
from the older artifact template. Then there is one set of render code and drift is
impossible. The artifact template is kept as the reference for constant names and
shapes, and the builder still emits every constant in section 6. If you want the
artifact's current look kept instead, I port the Pages-only sections into the template
and we live with two codebases.

**D4. What Semrush should populate.** Semrush replaces a free live-SERP pulse, so the
numbers will change meaning (Semrush's database positions, not a live Google check).
Proposed call set, once per run: `domain_organic` for albertscott.com (our position on
each tracked keyword; billed per row returned, capped with `display_limit`), `phrase_organic` with
`display_limit=1` per tracked keyword for the `#1 result` column (15 keywords, about 150
units/day at the standard 10 units per line), and the Site Audit snapshot for
`SEO_HEALTH`, which needs the Site Audit project id (`SEMRUSH_SITE_AUDIT_ID`). `SEO_GEO`
cannot come from Semrush and stays a hand-edited file. Please confirm the budget and
send the project id, or say skip Site Audit and I keep `SEO_HEALTH` hand-edited too.

**D5. SmartScout watchlist seed.** Nothing tracks brands today (finding 7). Proposed seed
from clients visible in the repo and artifact (won deals and client call recordings):
`Scentco`, `Mexico's Finest`, `Art of Beauty`, `Rufus Teague`, `Wholesome Hippy`,
`Katjes`, `Zoya`. Correct or replace the list; names must match SmartScout exactly.

Also confirm: delete `refresh-data.yml` and `deploy-pages.yml` in stage 4 (section 7),
and the Pages source switch to `main` + `/docs` at the end of stage 5.

---

## 9. Decisions (Yoni, 2026-09-25)

- **D1: B.** `pipedrive.json` and `smartlead.json` are committed encrypted (`.enc`) under
  the login's content key; the built artifact is committed encrypted too. Everything
  else is plain JSON.
- **D2:** Yoni recovers the content key locally with `scripts/recover-content-key.mjs`
  and stores it as the Actions secret `DASHBOARD_CONTENT_KEY`.
- **D3:** one page codebase. The artifact is generated from `dashboard/command-center.html`
  with the data inlined; the old artifact template is kept only as the reference for
  constant names and shapes.
- **D4:** Semrush call set as proposed. No Site Audit project id given yet, so
  `SEO_HEALTH` falls back to `seo_health_manual.json` until `SEMRUSH_SITE_AUDIT_ID` is set.
- **D5:** watchlist seeded with Scentco, Mexico's Finest, Art of Beauty, Rufus Teague,
  Wholesome Hippy, Katjes, Zoya.
- `refresh-data.yml` and `deploy-pages.yml` are removed in stage 4; Pages moves to
  `main` + `/docs` after stage 5.

## 10. Additions (Yoni, 2026-09-25)

- **Trade Shows page on both dashboards**, in the sidebar directly below SmartScout: a
  calendar of the shows in `docs/data/tradeshows.json` (226 US shows, Sep 25, 2026 to
  Aug 18, 2027, delivered as `tradeshow_calendar_FINAL.xlsx` + `tradeshows.json` and
  committed unchanged).
- **Attendance notes**: per show, who is attending (Yoni, Maria, Rachel) and a free-text
  note. Edited in the **Claude artifact**, where the page saves them to the artifact's
  shared store (the artifact's `db` runtime capability: the one exception to "no runtime
  calls", since a static page cannot save anything). The daily Claude task copies them into
  `docs/data/tradeshow_notes.json`, so the Pages calendar shows them read-only, at most a
  day behind.
- **Semrush**: the key provided is a v4 key (`semrtkn-pat-...`). Semrush's v4 SEO API
  covers backlinks and keyword metrics only; domain positions and the #1 result per
  keyword are only in the v3 Standard API, which needs the legacy 32-hex key. Open item:
  a legacy key, or pull Semrush through the Claude Semrush connector in the daily task.
- **Semrush decision (Yoni): pull it through the Semrush connector in the daily Claude
  task**, like SmartScout, instead of the GitHub workflow. `scripts/pull/semrush.mjs` and
  the `SEMRUSH_*` secrets are dropped. Checked 2026-09-25: the connector also needs Semrush
  API units and the account has none (`no_api_units`), so until units are added the SEO
  page shows the Sep 3 manual check, labeled as such.
