#!/usr/bin/env node
// Bulk SmartLead lookup for the Pipedrive re-engagement lead recap project.
//
// Given a JSON file of email addresses (a flat array), looks up each one via
// GET /leads/ (by email), and for any match, pulls its campaign associations
// + per-campaign category + latest message history so a downstream recap
// step (Gmail + SmartLead synthesis) has real SmartLead history to work from
// without re-hitting the API per lead.
//
// Usage: node scripts/lead-recap-smartlead-lookup.mjs <emails.json> <output.json>
//
// Reads SMARTLEAD_API_KEY / SMARTLEAD_BASE_URL from .env (repo convention).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const envPath = path.join(projectRoot, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq === -1) continue;
    const k = t.slice(0, eq).trim();
    const v = t.slice(eq + 1).trim();
    if (!(k in process.env)) process.env[k] = v;
  }
}

const [, , emailsPath, outPath] = process.argv;
if (!emailsPath || !outPath) {
  console.error("Usage: node scripts/lead-recap-smartlead-lookup.mjs <emails.json> <output.json>");
  process.exit(1);
}

const emails = JSON.parse(fs.readFileSync(emailsPath, "utf8"));
const client = new SmartleadClient({});

console.error(`Fetching lead category map...`);
const categories = await client.getLeadCategories();
const CAT_NAME = {};
for (const c of categories) CAT_NAME[c.id] = c.name;

// Bulk-pull the Master Inbox's full reply history (all-time, not date-windowed) so we can
// attach lead_category_id + lead_status per (email, campaign) without an extra per-lead call.
// getCampaignsForLead/getLeadMessageHistory (below) don't expose category at all.
console.error(`Pulling all-time Master Inbox reply history for category/status data...`);
const replyMeta = {}; // key: `${email}|${campaignId}` -> { category, leadStatus, lastReplyTime }
{
  const limit = 20; // Smartlead caps master-inbox-replies at 20/page
  let offset = 0;
  for (;;) {
    const res = await client.getMasterInboxReplies(
      { offset, limit, sortBy: "REPLY_TIME_DESC", filters: { emailStatus: "Replied" } },
      false
    );
    const items = res?.data || [];
    for (const item of items) {
      const key = `${(item.lead_email || "").toLowerCase()}|${item.email_campaign_id}`;
      replyMeta[key] = {
        category: item.lead_category_id != null ? CAT_NAME[item.lead_category_id] || `Unknown (${item.lead_category_id})` : null,
        leadStatus: item.lead_status,
        lastReplyTime: item.last_reply_time,
      };
    }
    if (items.length < limit) break;
    offset += limit;
    if (offset % 2000 === 0) console.error(`  ...${offset} reply records scanned so far`);
    if (offset > 200000) break; // sanity backstop
  }
  console.error(`  ${Object.keys(replyMeta).length} (email, campaign) reply records indexed.`);
}

console.error(`Looking up ${emails.length} emails against SmartLead...`);

const CONCURRENCY = 10;
let idx = 0;
let done = 0;
let foundCount = 0;
const results = {};

async function processOne(email) {
  try {
    const lead = await client.getLeadByEmail(email);
    if (!lead || (Array.isArray(lead) && lead.length === 0) || lead?.ok === false) {
      return;
    }
    const leadRecord = Array.isArray(lead) ? lead[0] : lead?.data ?? lead;
    if (!leadRecord || !leadRecord.id) return;

    let campaigns = [];
    try {
      campaigns = await client.getCampaignsForLead(leadRecord.id);
      campaigns = Array.isArray(campaigns) ? campaigns : campaigns?.data ?? [];
    } catch {
      campaigns = [];
    }

    const campaignSummaries = [];
    for (const camp of campaigns) {
      const campaignId = camp.campaign_id ?? camp.id;
      const meta = replyMeta[`${email.toLowerCase()}|${campaignId}`];
      let lastMessage = null;
      try {
        const history = await client.getLeadMessageHistory(campaignId, leadRecord.id);
        const msgs = history?.history || history?.data || [];
        const replies = msgs.filter((m) => m.type === "REPLY");
        const target = replies[replies.length - 1] || msgs[msgs.length - 1];
        if (target) {
          lastMessage = {
            type: target.type,
            time: target.time,
            from: target.from,
            subject: target.subject,
            snippet: (target.email_body || "").replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim().slice(0, 500),
          };
        }
      } catch {
        // per-campaign message history can 404/error for edge cases; skip silently
      }
      campaignSummaries.push({
        campaign_id: campaignId,
        campaign_name: camp.campaign_name ?? camp.name,
        campaign_status: camp.status,
        category: meta?.category ?? null,
        lead_status: meta?.leadStatus ?? null,
        last_message: lastMessage,
      });
    }

    results[email] = {
      smartlead_lead_id: leadRecord.id,
      first_name: leadRecord.first_name,
      last_name: leadRecord.last_name,
      company: leadRecord.company_name,
      campaigns: campaignSummaries,
    };
    foundCount++;
  } catch (err) {
    if (err?.status && err.status !== 404) {
      results[email] = { error: err.message, status: err.status };
    }
    // 404 = not a SmartLead lead at all; expected for most Pipedrive/Salesforce-only rows, skip silently
  } finally {
    done++;
    if (done % 100 === 0 || done === emails.length) {
      console.error(`  ${done}/${emails.length} checked, ${foundCount} found in SmartLead`);
    }
  }
}

async function worker() {
  while (idx < emails.length) {
    const email = emails[idx++];
    await processOne(email);
  }
}

await Promise.all(Array.from({ length: CONCURRENCY }, worker));

fs.writeFileSync(outPath, JSON.stringify(results, null, 2));
console.error(`Wrote ${outPath}: ${foundCount}/${emails.length} emails matched a SmartLead lead.`);
