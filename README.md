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
