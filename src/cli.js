#!/usr/bin/env node
/**
 * Tiny CLI wrapper around SmartleadClient. No dependencies.
 *
 * Usage:
 *   node src/cli.js campaigns:list
 *   node src/cli.js campaigns:get <campaignId>
 *   node src/cli.js campaigns:create '{"name":"Q3 Outreach"}'
 *   node src/cli.js campaigns:start <campaignId>
 *   node src/cli.js campaigns:pause <campaignId>
 *   node src/cli.js campaigns:stop <campaignId>
 *   node src/cli.js campaigns:analytics <campaignId>
 *   node src/cli.js campaigns:statistics <campaignId>
 *   node src/cli.js inboxes:list
 *   node src/cli.js inboxes:health
 *   node src/cli.js inboxes:warmup-stats <emailAccountId>
 *   node src/cli.js leads:add <campaignId> '[{"email":"a@b.com","first_name":"A"}]'
 *   node src/cli.js qev:verify a@b.com
 *   node src/cli.js qev:verify-list '["a@b.com","c@d.com"]'
 *   node src/cli.js pi:workspaces
 *   node src/cli.js pi:email-accounts <workspaceId>
 *   node src/cli.js pi:orders <workspaceId>
 *   node src/cli.js pi:subscriptions <workspaceId>
 *   node src/cli.js pk:ping
 *   node src/cli.js pk:domains
 *   node src/cli.js pk:dns <domain>
 *   node src/cli.js pk:nameservers <domain>
 *   node src/cli.js nc:domains
 *   node src/cli.js nc:dns-hosts <domain>
 *   node src/cli.js fa:meetings
 *   node src/cli.js gs:read <range>
 *   node src/cli.js gs:append <range> '["col1","col2","col3"]'
 *   node src/cli.js hr:check
 *   node src/cli.js hr:campaigns
 *   node src/cli.js hr:campaign <campaignId>
 *   node src/cli.js hr:campaign-pause <campaignId>
 *   node src/cli.js hr:campaign-resume <campaignId>
 *   node src/cli.js hr:campaign-leads <campaignId>
 *   node src/cli.js hr:workspaces
 *
 * Reads SMARTLEAD_API_KEY (and optional SMARTLEAD_BASE_URL) from the environment.
 * qev: commands read QUICKEMAILVERIFICATION_API_KEY instead.
 * pi: commands read PREMIUM_INBOXES_API_KEY instead. pi:orders and pi:subscriptions
 * print the *summary* shape (no mailbox passwords) — see src/premiuminboxes.js if you
 * genuinely need the raw provisioning payload.
 * pk: commands read PORKBUN_API_KEY / PORKBUN_SECRET_API_KEY instead. pk:dns and
 * pk:nameservers only work for domains with API access enabled in Porkbun's account
 * settings — see src/porkbun.js.
 * nc: commands read NAMECHEAP_API_USER / NAMECHEAP_API_KEY / NAMECHEAP_USERNAME /
 * NAMECHEAP_CLIENT_IP instead. NAMECHEAP_CLIENT_IP must be whitelisted in the
 * Namecheap account (Profile > Tools > API Access) or every nc: call fails — see
 * src/namecheap.js.
 * fa: commands read FATHOM_API_KEY instead. fa:meetings only ever returns meetings
 * titled "Albert Scott" in some form — see src/fathom.js for why that's structural,
 * not just a filter.
 * gs: commands read GOOGLE_SERVICE_ACCOUNT_EMAIL / GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY /
 * GOOGLE_SHEETS_SPREADSHEET_ID instead, and need the sheet shared with that service
 * account as an Editor — see src/googlesheets.js.
 * hr: commands read HEYREACH_API_KEY (workspace-level: campaigns/leads/network) and/or
 * HEYREACH_ORG_API_KEY (organization-level: hr:workspaces only) instead — the two are not
 * interchangeable, see src/heyreach.js.
 * Loads a local .env file automatically if present (no dotenv dependency needed).
 */

import fs from "node:fs";
import path from "node:path";
import { SmartleadClient } from "./client.js";
import { QuickEmailVerificationClient } from "./quickemailverification.js";
import { PremiumInboxesClient } from "./premiuminboxes.js";
import { PorkbunClient } from "./porkbun.js";
import { NamecheapClient } from "./namecheap.js";
import { FathomClient } from "./fathom.js";
import { GoogleSheetsClient } from "./googlesheets.js";
import { HeyReachClient } from "./heyreach.js";

loadDotEnv();

const [, , cmd, ...args] = process.argv;

// Built lazily inside main() so an unknown command or a `--help`-style call
// doesn't blow up on a missing API key before we even validate the command.
let client;
let qevClient;
let piClient;
let pkClient;
let ncClient;
let faClient;
let gsClient;
let hrClient;

const commands = {
  "campaigns:list": () => client.listCampaigns(),
  "campaigns:get": (id) => client.getCampaign(id),
  "campaigns:create": (json) => client.createCampaign(JSON.parse(json)),
  "campaigns:start": (id) => client.startCampaign(id),
  "campaigns:pause": (id) => client.pauseCampaign(id),
  "campaigns:stop": (id) => client.stopCampaign(id),
  "campaigns:analytics": (id) => client.getCampaignAnalytics(id),
  "campaigns:statistics": (id) => client.getCampaignStatistics(id),
  "inboxes:list": () => client.listEmailAccounts(),
  "inboxes:health": () => client.getAllInboxHealth(),
  "inboxes:warmup-stats": (id) => client.getEmailAccountWarmupStats(id),
  "leads:add": (campaignId, json) => client.addLeadsToCampaign(campaignId, JSON.parse(json)),
  "leads:categories": () => client.getLeadCategories(),
  "leads:get-by-email": (email) => client.getLeadByEmail(email),
  "leads:message-history": (campaignId, leadId) => client.getLeadMessageHistory(campaignId, leadId),
  "leads:campaigns-for-lead": (leadId) => client.getCampaignsForLead(leadId),
  "leads:pause": (campaignId, leadId) => client.pauseLead(campaignId, leadId),
  "leads:resume": (campaignId, leadId) => client.resumeLead(campaignId, leadId),
  "leads:unsubscribe-global": (leadId) => client.unsubscribeLeadGlobally(leadId),
  "leads:set-category": (campaignId, leadId, categoryId, pauseLead) =>
    client.updateLeadCategory(campaignId, leadId, Number(categoryId), { pauseLead: pauseLead === "true" }),
  "master-inbox:replies": (json, fetchHistory) =>
    client.getMasterInboxReplies(json ? JSON.parse(json) : {}, fetchHistory === "true"),
  "leads:block-list": (filterEmailOrDomain) => client.getDomainBlockList({ filterEmailOrDomain }),
  "leads:block": (domainOrEmail) => client.blockDomainOrEmail({ domain_block_list: [domainOrEmail], client_id: null }),
  "leads:unblock": (id) => client.deleteDomainBlockListEntry(id),

  "qev:verify": (email) => qevClient.verifyEmail(email),
  "qev:verify-list": (jsonArray) => qevClient.verifyEmails(JSON.parse(jsonArray)),

  "pi:workspaces": () => piClient.listWorkspaces(),
  "pi:email-accounts": (workspaceId) => piClient.listEmailAccounts({ workspaceId }),
  "pi:orders": (workspaceId) => piClient.getOrderSummaries({ workspaceId }),
  "pi:subscriptions": (workspaceId) => piClient.getSubscriptionSummaries({ workspaceId }),

  "pk:ping": () => pkClient.ping(),
  "pk:domains": () => pkClient.listDomains(),
  "pk:dns": (domain) => pkClient.getDnsRecords(domain),
  "pk:nameservers": (domain) => pkClient.getNameservers(domain),

  "nc:domains": () => ncClient.listDomains(),
  "nc:dns-hosts": (domain) => ncClient.getDnsHosts(domain),

  "fa:meetings": () => faClient.listAlbertScottMeetings(),

  "gs:read": (range) => gsClient.getValues(range),
  "gs:append": (range, jsonArray) => gsClient.appendRow(range, JSON.parse(jsonArray)),
  "gs:clear": (range) => gsClient.clearRange(range),

  "hr:check": () => hrClient.checkApiKey(),
  "hr:campaigns": () => hrClient.listCampaigns(),
  "hr:campaign": (campaignId) => hrClient.getCampaign(campaignId),
  "hr:campaign-start": (campaignId) => hrClient.startCampaign(campaignId),
  "hr:campaign-pause": (campaignId) => hrClient.pauseCampaign(campaignId),
  "hr:campaign-resume": (campaignId) => hrClient.resumeCampaign(campaignId),
  "hr:campaign-leads": (campaignId) => hrClient.getLeadsFromCampaign({ campaignId: Number(campaignId) }),
  "hr:workspaces": () => hrClient.listWorkspaces(),
};

async function main() {
  const fn = commands[cmd];
  if (!fn) {
    console.error(`Unknown or missing command: ${cmd ?? "(none)"}\n`);
    console.error("Available commands:\n  " + Object.keys(commands).join("\n  "));
    process.exit(1);
  }
  try {
    if (cmd.startsWith("qev:")) {
      qevClient = new QuickEmailVerificationClient({});
    } else if (cmd.startsWith("pi:")) {
      piClient = new PremiumInboxesClient({});
    } else if (cmd.startsWith("pk:")) {
      pkClient = new PorkbunClient({});
    } else if (cmd.startsWith("nc:")) {
      ncClient = new NamecheapClient({});
    } else if (cmd.startsWith("fa:")) {
      faClient = new FathomClient({});
    } else if (cmd.startsWith("gs:")) {
      gsClient = new GoogleSheetsClient({});
    } else if (cmd.startsWith("hr:")) {
      hrClient = new HeyReachClient({});
    } else {
      client = new SmartleadClient({});
    }
    const result = await fn(...args);
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error(err.message);
    if (err.body) console.error(JSON.stringify(err.body, null, 2));
    process.exit(1);
  }
}

function loadDotEnv() {
  const envPath = path.resolve(process.cwd(), ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = value;
  }
}

main();
