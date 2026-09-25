# smartlead-api-client

Minimal, dependency-free Node.js client + CLI for the [Smartlead.ai](https://smartlead.ai) REST API.
Requires **Node.js 18+** (uses the built-in `fetch`, no `npm install` needed).

## Setup

```bash
cd ~/smartlead-api-client
cp .env.example .env
# then edit .env and paste your real Smartlead API key
```

Get your key from the Smartlead dashboard: **Settings → API Key**.

> Keep `.env` out of version control (already covered by `.gitignore`) and never paste
> your real key into a chat/AI tool — edit the file directly.

## CLI usage

```bash
node src/cli.js campaigns:list
node src/cli.js campaigns:get 12345
node src/cli.js campaigns:create '{"name":"Q3 Outreach"}'
node src/cli.js campaigns:start 12345
node src/cli.js campaigns:pause 12345
node src/cli.js campaigns:stop 12345
node src/cli.js campaigns:analytics 12345
node src/cli.js campaigns:statistics 12345

node src/cli.js inboxes:list
node src/cli.js inboxes:health              # warmup/deliverability across every connected inbox
node src/cli.js inboxes:warmup-stats 987

node src/cli.js leads:add 12345 '[{"email":"lead@example.com","first_name":"Jane"}]'

node src/cli.js qev:verify lead@example.com
node src/cli.js qev:verify-list '["a@example.com","b@example.com"]'
```

## Programmatic usage

```js
import { SmartleadClient } from "./src/client.js";

const client = new SmartleadClient(); // reads SMARTLEAD_API_KEY from env
// or: new SmartleadClient({ apiKey: "sl_..." })

const campaigns = await client.listCampaigns();
await client.startCampaign(campaigns[0].id);

const health = await client.getAllInboxHealth();
console.log(health);
```

## Coverage

- **Campaigns**: list, get, create, delete, status (start/pause/stop), schedule, settings,
  sequences, analytics, statistics, analytics-by-date, global analytics overview.
- **Email accounts / deliverability**: list, create, update, get, warmup config, warmup stats,
  aggregate inbox health helper (`getAllInboxHealth`), assign/remove accounts on a campaign.
- **Leads**: list, add (bulk), update, pause/resume, delete, unsubscribe (per-campaign & global),
  domain/email block list, message history, reply-to-thread, CSV export, categories,
  find campaigns for a lead.

All methods map directly to Smartlead's documented REST endpoints
(`https://api.smartlead.ai/reference`). Extend `SmartleadClient` with `client.get/post/patch/delete`
for any endpoint not yet wrapped.

## Email verification (QuickEmailVerification)

A separate, minimal client for [QuickEmailVerification.com](https://www.quickemailverification.com/)
lives in `src/quickemailverification.js` — useful for checking lead emails (deliverability, disposable,
role-based, accept-all domains) before importing them into a Smartlead campaign.

```js
import { QuickEmailVerificationClient } from "./src/quickemailverification.js";

const qev = new QuickEmailVerificationClient(); // reads QUICKEMAILVERIFICATION_API_KEY from env
const check = await qev.verifyEmail("lead@example.com");
console.log(check.result, check.safe_to_send, check.remainingCredits);

const batch = await qev.verifyEmails(["a@example.com", "b@example.com"]);
```

`result` is one of `valid`, `invalid`, or `unknown`. Treat `invalid` as a hard skip before adding a
lead; `unknown`/`accept_all: true` domains can't be confirmed by SMTP and are a judgment call.

## Daily refresh (the dashboards)

Two dashboards show the same data from the same code: the **GitHub Pages dashboard**
(https://salesmanager-crypto.github.io/smartlead-api-client/, behind the sign-in page) and the
**Claude artifact** "Alberscott Dashboard" (https://claude.ai/artifact/Vei7Pm31JHf9QmzR4bJo5G).

**How data flows**

1. **09:15 UTC, GitHub Actions** (`.github/workflows/daily-refresh.yml`) runs
   `scripts/pull/run-all.mjs`: SmartLead, Pipedrive and HeyReach over their APIs, the SEO issue
   tracker (once the Google secrets exist), and a check of the trade show calendar. It writes
   `docs/data/*.json` and `docs/data/manifest.json`, then rebuilds `docs/index.html` (the Pages
   dashboard) and `docs/artifact/alberscott-dashboard.html.enc` (the artifact page), and commits
   `docs/` if anything changed. Pages serves `main` / `docs`, so that push is the deploy.
2. **In the browser**, the Pages dashboard signs you in, then fetches `docs/data/*.json` and
   renders. Nothing is fetched from SmartLead, Pipedrive or HeyReach at view time.
3. **10:15 UTC, the Claude scheduled task** (prompt: `docs/CLAUDE_TASK_dashboard_sync.md`) pulls
   SmartScout through its connector, copies the trade show attendance notes out of the artifact,
   commits both to `docs/data/`, rebuilds the artifact page from the repo's JSON with
   `scripts/build-artifact.mjs`, and republishes it to the same artifact URL.

APIs -> Actions -> `docs/data/*.json` -> Pages; `docs/data/*.json` -> `build-artifact.mjs` ->
Claude task -> artifact. Every field is documented in `docs/data/SCHEMA.md`.

The top bar of both dashboards shows "Data as of" (the last GitHub refresh) and one pill per
source: green ok, amber stale (no success in 36 hours, or waiting on setup), red error (hover for
the message).

**Secrets** live in GitHub: Settings > Secrets and variables > Actions.
`SMARTLEAD_API_KEY`, `PIPEDRIVE_API_TOKEN`, `PIPEDRIVE_COMPANY_DOMAIN`, `HEYREACH_API_KEY`, and
`DASHBOARD_CONTENT_KEY` (the sign-in page's content key; print it with
`node scripts/recover-content-key.mjs` and your dashboard login). Optional:
`GOOGLE_SERVICE_ACCOUNT_JSON` + `SEO_TRACKER_FILE_ID` for the live SEO issue tracker. The Claude
task holds its own copy of the content key in its prompt.

**Run a refresh by hand**: Actions > "Daily dashboard refresh" > Run workflow. Or locally, with
the keys in `.env` (see `.env.example`):

```sh
node scripts/pull/run-all.mjs      # all sources, manifest, today's history file
node scripts/pull/smartlead.mjs    # or one source
node scripts/build-pages.mjs       # rebuild docs/index.html
node scripts/build-artifact.mjs    # rebuild the artifact page
```

Locally, the Pipedrive and SmartLead data is also written in plain text to `.private/data/`
(gitignored).

**Track a brand in SmartScout**: add its exact SmartScout name to
`docs/data/smartscout_watchlist.json`. It appears on both dashboards after the next Claude task run.

**Trade shows**: the calendar is `docs/data/tradeshows.json` (from the trade show calendar
project, committed as delivered). Replace the file to update it. Attendance (Yoni, Maria,
Rachel) and notes are edited on the artifact's Trade Shows page and synced into
`docs/data/tradeshow_notes.json` daily.

**Add a source**: write `scripts/pull/<source>.mjs` exporting `pull(env, ctx)` that returns the
data (see `heyreach.mjs` for the smallest example), add it to `SOURCES` in
`scripts/pull/write.mjs` (and to `ENCRYPTED` if it has names or email addresses), call it from
`run-all.mjs`, map it to page constants in `dashboard/data-map.js`, document it in
`docs/data/SCHEMA.md`, and pass its secret in `daily-refresh.yml`.

**The repository is public**, so every plain file in `docs/data/` is readable by anyone. Files
with names or email addresses (Pipedrive, SmartLead) and the built artifact are committed
encrypted under the dashboard's content key; the rest are aggregates and reference data.
