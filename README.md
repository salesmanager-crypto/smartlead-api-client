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

## Google Drive export (optional)

Upload, organize, and move CSV exports (e.g. the output of
`scripts/export-campaign-leads-csv.mjs`) in Google Drive.

**One-time setup:**

1. In Google Cloud Console, create an OAuth client of type **Web application**
   (APIs & Services → Credentials → Create Credentials → OAuth client ID).
2. Copy its `client_id` / `client_secret` into `.env` (see `.env.example`).
3. Run `node scripts/google-drive-auth.mjs`, open the printed URL, sign in with the
   Google account to connect, then paste the resulting redirect URL/code back in.
   It prints a `GOOGLE_REFRESH_TOKEN` line — add that to `.env` too.

**CLI usage:**

```bash
node src/drive-cli.js drive:upload exports/fancy-food-leads.csv          # upload a CSV
node src/drive-cli.js drive:upload exports/fancy-food-leads.csv 1AbC...  # ...into a specific folder
node src/drive-cli.js drive:create-folder "Fancy Foods Exports"
node src/drive-cli.js drive:move <fileId> <newParentFolderId> <oldParentFolderId>
node src/drive-cli.js drive:list "name contains 'fancy-food'"
node src/drive-cli.js drive:get <fileId>
```

Uses the `drive.file` scope, so it can only see/manage files it creates (or files a
user explicitly opens with it) — not your whole Drive.

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
