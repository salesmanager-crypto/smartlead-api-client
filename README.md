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

## Tracking-domain (CNAME) audit

Smartlead flags mailboxes with a "CNAME issue" without saying which half is broken, and the
API exposes `custom_tracking_domain` as a plain string with no verification state. This script
checks the three things that can actually be wrong: no tracking domain set, a hostname that
doesn't CNAME to Smartlead's tracking edge (`open.sleadtrack.com`), or a CNAME that resolves
but has no certificate covering it.

```bash
node scripts/check-tracking-domains.mjs
```

For mailboxes with nothing set it also probes the usual prefixes on the sending domain, so the
output separates "DNS is ready, just fill in the field" from "DNS first". Registrar wildcards
are the common trap: Porkbun parks `*.domain` at `uixie.porkbun.com`, so every prefix looks
like it resolves, but to the parking host rather than the tracking edge. Exits non-zero when
any mailbox needs attention, so it works as a scheduled check.

Smartlead's "Custom Tracking Domain Needs Attention" banner lumps a fourth case in with these:
a domain that is set and resolves fine, but that Smartlead hasn't verified yet. That state
lives only in their UI and is tracked per mailbox rather than per domain, so two mailboxes
sharing one healthy tracking domain can disagree. Paste the banner's emails into a file (one
per line) to split their list against live DNS:

```bash
node scripts/check-tracking-domains.mjs --flagged flagged.txt
```

Anything it reports as "set and resolving correctly" needs no DNS work at all, only the Verify
click in Smartlead.

Two companion scripts do the repairs, both dry-run unless given `--apply`:

```bash
node scripts/setup-tracking-dns.mjs     # create the missing CNAMEs at Porkbun
node scripts/fix-tracking-domains.mjs   # set the tracking domain on the Smartlead side
```

`setup-tracking-dns.mjs` derives the domains needing a record from Smartlead itself, so it
only ever touches domains with inboxes actually sending without tracking. It checks for an
explicit record through Porkbun's API rather than a DNS lookup, because a parked domain's
wildcard makes every subdomain resolve. Per-domain API access is off by default at Porkbun and
is separate from having a key, so the script names the domains needing that toggle up front
instead of failing partway through.

`fix-tracking-domains.mjs` fills in a missing tracking domain only where DNS already supports
it, preferring whatever a working sibling on the same sending domain uses so one domain never
splits across two tracking hostnames. It also normalises hostnames stored with capitals, and
`--reverify` re-submits already-correct values to clear a stale verification, and needs
`--flagged` so it only touches mailboxes the banner actually reports. Writing
`custom_tracking_url` makes Smartlead re-run its check rather than just storing the value
(confirmed against a live account), so a mailbox verifies itself once the field is set and
never needs the Verify click. It deliberately leaves alone any mailbox whose tracking domain
doesn't resolve: that is a DNS problem, and writing the Smartlead field would only hide it.

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
