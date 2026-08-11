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
 *
 * Reads SMARTLEAD_API_KEY (and optional SMARTLEAD_BASE_URL) from the environment.
 * Loads a local .env file automatically if present (no dotenv dependency needed).
 */

import fs from "node:fs";
import path from "node:path";
import { SmartleadClient } from "./client.js";

loadDotEnv();

const [, , cmd, ...args] = process.argv;

// Built lazily inside main() so an unknown command or a `--help`-style call
// doesn't blow up on a missing API key before we even validate the command.
let client;

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
};

async function main() {
  const fn = commands[cmd];
  if (!fn) {
    console.error(`Unknown or missing command: ${cmd ?? "(none)"}\n`);
    console.error("Available commands:\n  " + Object.keys(commands).join("\n  "));
    process.exit(1);
  }
  try {
    client = new SmartleadClient({});
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
