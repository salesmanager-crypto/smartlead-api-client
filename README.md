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

## Campaign analytics report

`scripts/campaign-analytics-report.mjs` pulls performance for every campaign created on/after
a given date, aggregates per-lead engagement *across* those campaigns, and flags what's worth
acting on — high-bounce or low-open-rate campaigns, leads who never open after repeated sends,
addresses that bounce, leads who open repeatedly but never convert, and unhealthy sending
inboxes. `scripts/build-analytics-dashboard.mjs` turns its JSON output into a self-contained
HTML dashboard.

```bash
# live run against your real account
node scripts/campaign-analytics-report.mjs --since=2026-07-01 --end=2026-08-14
node scripts/build-analytics-dashboard.mjs scripts/output/2026-07-01_2026-08-14-campaign-report.json
# open the resulting .html directly, or publish it as a Claude Artifact

# try it with bundled synthetic sample data — no API key needed
node scripts/campaign-analytics-report.mjs --fixture
```

Key flags: `--since`, `--start`/`--end` (analytics window, defaults to `--since`..today),
`--status=ACTIVE|ALL`, `--out=path.json`, `--skip-inbox-health`, and threshold overrides
(`--bounce-warn`, `--bounce-critical`, `--open-warn`, `--open-critical`, `--unsub-warn`,
`--unsub-critical`, `--min-sends`). Defaults live in `scripts/lib/analytics-report-core.mjs`.

For a recurring run, see `scripts/scheduled-analytics-report-prompt.md` (same pattern as
`scripts/scheduled-inbox-sync-prompt.md`).

## Coverage

- **Campaigns**: list, get, create, delete, status (start/pause/stop), schedule, settings,
  sequences, analytics, statistics (+ auto-paginated `getAllCampaignStatistics`),
  analytics-by-date, global analytics overview.
- **Email accounts / deliverability**: list, create, update, get, warmup config, warmup stats,
  aggregate inbox health helper (`getAllInboxHealth`), assign/remove accounts on a campaign.
- **Leads**: list, add (bulk), update, pause/resume, delete, unsubscribe (per-campaign & global),
  domain/email block list, message history, reply-to-thread, CSV export, categories,
  find campaigns for a lead.

All methods map directly to Smartlead's documented REST endpoints
(`https://api.smartlead.ai/reference`). Extend `SmartleadClient` with `client.get/post/patch/delete`
for any endpoint not yet wrapped.
