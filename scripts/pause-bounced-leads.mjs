// Finds leads that have hard-bounced in one or more campaigns and pauses them, so they stop
// receiving later sequence steps. Smartlead's `stop_lead_settings` only stops a lead's sequence
// on a reply/click/open — it does NOT auto-stop on bounce — so a lead that bounces on step 1 can
// still get sent step 2, step 3, etc. weeks later, repeatedly bouncing and hurting sender
// reputation each time. This closes that gap.
//
// Defaults to dry-run: it reports what it *would* pause without changing anything. Pass --apply
// to actually pause leads.
//
// Usage:
//   node scripts/pause-bounced-leads.mjs                        # dry-run, the 8 campaigns flagged in the bounce-rate review
//   node scripts/pause-bounced-leads.mjs --apply                # actually pause them
//   node scripts/pause-bounced-leads.mjs 3838869 3838867 --apply  # target specific campaign IDs instead
//   node scripts/pause-bounced-leads.mjs --all-active --apply     # every ACTIVE campaign on the account

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const envPath = path.join(projectRoot, ".env");
for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#")) continue;
  const eq = t.indexOf("=");
  if (eq === -1) continue;
  const k = t.slice(0, eq).trim();
  const v = t.slice(eq + 1).trim();
  if (!(k in process.env)) process.env[k] = v;
}

// The 8 campaigns identified in the Aug 2026 bounce-rate root-cause review.
const DEFAULT_CAMPAIGN_IDS = [
  2302690, // Cosmoprof Follow up
  3756194, // Eikko - Tea Expo
  3732474, // Eikko - ICAST 2026
  3731861, // Rachel - Nordstil
  3738501, // Rachel - ISM Cologne
  3730127, // Eikko - Cosmoprof 2026
  3738533, // Rachel - Spoga+gafa
  3792273, // Eikko - Fancy Foods Q4
];

const LOG_PATH = path.join(projectRoot, "scripts", "pause-bounced-leads-log.txt");
function log(line) {
  const stamped = `[${new Date().toISOString()}] ${line}`;
  fs.appendFileSync(LOG_PATH, stamped + "\n");
}

const args = process.argv.slice(2);
const apply = args.includes("--apply");
const allActive = args.includes("--all-active");
const explicitIds = args.filter((a) => /^\d+$/.test(a)).map(Number);

const client = new SmartleadClient({});

async function fetchAllStats(campaignId) {
  const limit = 500;
  let offset = 0;
  let all = [];
  while (true) {
    const page = await client.getCampaignStatistics(campaignId, { offset, limit });
    const data = page.data || [];
    all = all.concat(data);
    if (data.length < limit) break;
    offset += limit;
    if (offset > 20000) break; // safety valve
  }
  return all;
}

async function resolveCampaigns() {
  if (allActive) {
    const campaigns = await client.listCampaigns();
    return campaigns.filter((c) => c.status === "ACTIVE").map((c) => ({ id: c.id, name: c.name }));
  }
  const ids = explicitIds.length ? explicitIds : DEFAULT_CAMPAIGN_IDS;
  const results = [];
  for (const id of ids) {
    try {
      const c = await client.getCampaign(id);
      results.push({ id: c.id, name: c.name });
    } catch (err) {
      log(`WARN: could not load campaign ${id}: ${err.message}`);
    }
  }
  return results;
}

async function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function main() {
  const campaigns = await resolveCampaigns();
  log(`Run start — mode: ${apply ? "APPLY" : "DRY-RUN"} — campaigns: ${campaigns.map((c) => c.id).join(", ")}`);

  const summary = [];

  for (const campaign of campaigns) {
    let stats;
    try {
      stats = await fetchAllStats(campaign.id);
    } catch (err) {
      log(`${campaign.name} (${campaign.id}): failed to fetch statistics — ${err.message}`);
      summary.push({ campaign: campaign.name, id: campaign.id, error: err.message });
      continue;
    }

    const bouncedEmails = [...new Set(stats.filter((s) => s.is_bounced).map((s) => s.lead_email.toLowerCase()))];

    const result = { campaign: campaign.name, id: campaign.id, bouncedLeads: bouncedEmails.length, paused: 0, alreadyClear: 0, failed: [] };

    for (const email of bouncedEmails) {
      let leadId;
      try {
        const lead = await client.getLeadByEmail(email);
        leadId = lead?.id;
        if (!leadId) throw new Error("lead lookup returned no id");
      } catch (err) {
        result.failed.push({ email, stage: "lookup", error: err.message });
        continue;
      }

      if (!apply) {
        result.paused += 1; // "would pause"
        continue;
      }

      try {
        await client.pauseLead(campaign.id, leadId);
        result.paused += 1;
      } catch (err) {
        result.failed.push({ email, stage: "pause", error: err.message });
      }
      await sleep(150); // be polite to the API
    }

    summary.push(result);
    const line = `${campaign.name} (${campaign.id}): ${bouncedEmails.length} bounced lead(s), ` +
      `${apply ? "paused" : "would pause"} ${result.paused}, ${result.failed.length} failed`;
    log(line);
    console.log(line);
  }

  const failedDetails = summary.flatMap((r) => (r.failed || []).map((f) => ({ campaign: r.campaign, ...f })));
  if (failedDetails.length) {
    console.log(`\n${failedDetails.length} lead(s) failed to resolve/pause — see ${LOG_PATH} for the run summary.`);
    log(`Failures: ${JSON.stringify(failedDetails)}`);
  }

  if (!apply) {
    console.log("\nDry-run only — nothing was changed. Re-run with --apply to actually pause these leads.");
  }
}

main().catch((err) => {
  log(`ERROR: ${err.message}`);
  console.error(err);
  process.exit(1);
});
