#!/usr/bin/env node
/**
 * Pulls every Smartlead-side number needed for Rachel's Sales & Marketing Command
 * Center: campaign roster + analytics, yesterday's send totals, the trailing-7-day
 * Master Inbox reply log, and mailbox/sending-domain counts. Writes one JSON blob to
 * stdout (or the path given as the first arg) — Pipedrive data is pulled separately
 * via the connected MCP tools and merged in when the dashboard HTML is built.
 *
 * Usage:
 *   node scripts/pull-command-center-data.mjs [output.json]
 *
 * Requires SMARTLEAD_API_KEY in the environment (see README.md).
 */

import { writeFileSync } from "node:fs";
import { SmartleadClient } from "../src/client.js";

const outPath = process.argv[2] || null;
const client = new SmartleadClient({});

async function pool(items, worker, concurrency = 10) {
  const results = new Array(items.length);
  let idx = 0;
  async function run() {
    while (idx < items.length) {
      const i = idx++;
      results[i] = await worker(items[i], i);
    }
  }
  await Promise.all(Array.from({ length: Math.min(concurrency, items.length) }, run));
  return results;
}

function ymd(d) {
  return d.toISOString().slice(0, 10);
}

const now = new Date();
const todayStr = ymd(now);
const yesterday = new Date(now.getTime() - 24 * 3600 * 1000);
const yesterdayStr = ymd(yesterday);
const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 3600 * 1000);

console.error(`Pulling Smartlead data as of ${now.toISOString()} (yesterday = ${yesterdayStr})`);

// ---- Campaigns + analytics --------------------------------------------------

const campaigns = await client.listCampaigns();
console.error(`Found ${campaigns.length} campaigns. Fetching analytics...`);

const campaignAnalytics = await pool(campaigns, async (c) => {
  try {
    const a = await client.getCampaignAnalytics(c.id);
    return { id: c.id, name: c.name, status: c.status, created_at: c.created_at, analytics: a, error: null };
  } catch (err) {
    return { id: c.id, name: c.name, status: c.status, created_at: c.created_at, analytics: null, error: err.message };
  }
});

console.error(`Fetching yesterday's per-campaign analytics-by-date (${yesterdayStr})...`);

const campaignYesterday = await pool(campaigns, async (c) => {
  try {
    const a = await client.getCampaignAnalyticsByDate(c.id, { startDate: yesterdayStr, endDate: yesterdayStr });
    return { id: c.id, name: c.name, byDate: a, error: null };
  } catch (err) {
    return { id: c.id, name: c.name, byDate: null, error: err.message };
  }
});

// ---- Master Inbox replies, trailing 7 days ---------------------------------

console.error(`Fetching Master Inbox replies since ${sevenDaysAgo.toISOString()}...`);

const cutoffMs = sevenDaysAgo.getTime();
let replies = [];
let offset = 0;
const PAGE = 20;
const MAX_PAGES = 150; // safety cap (3000 replies)
for (let page = 0; page < MAX_PAGES; page++) {
  const r = await client.getMasterInboxReplies(
    {
      offset,
      limit: PAGE,
      sortBy: "REPLY_TIME_DESC",
      filters: { replyTimeBetween: [sevenDaysAgo.toISOString(), now.toISOString()] },
    },
    false
  );
  const batch = r?.data || [];
  if (batch.length === 0) break;
  replies.push(...batch);
  const oldestInBatch = batch[batch.length - 1]?.last_reply_time;
  offset += PAGE;
  if (oldestInBatch && new Date(oldestInBatch).getTime() < cutoffMs) break;
  if (batch.length < PAGE) break;
}
// belt-and-suspenders: trim anything outside the window the API didn't filter out itself
replies = replies.filter((r) => r.last_reply_time && new Date(r.last_reply_time).getTime() >= cutoffMs);
console.error(`Collected ${replies.length} replies in the trailing 7 days.`);

const leadCategories = await client.getLeadCategories().catch(() => []);

// ---- Mailboxes / sending domains -------------------------------------------

console.error("Fetching email accounts...");
let accounts = [];
let acctOffset = 0;
for (;;) {
  const batch = await client.listEmailAccounts({ limit: 500, offset: acctOffset });
  if (!batch || batch.length === 0) break;
  accounts.push(...batch);
  acctOffset += 500;
  if (batch.length < 500) break;
}

const domains = new Set(accounts.map((a) => (a.from_email || "").split("@")[1]?.toLowerCase()).filter(Boolean));

const out = {
  pulled_at: now.toISOString(),
  yesterday: yesterdayStr,
  today: todayStr,
  campaigns: campaignAnalytics,
  campaignsYesterday: campaignYesterday,
  masterInboxReplies7d: replies,
  leadCategories,
  mailboxCount: accounts.length,
  sendingDomainCount: domains.size,
  sendingDomains: [...domains].sort(),
};

const json = JSON.stringify(out, null, 2);
if (outPath) {
  writeFileSync(outPath, json);
  console.error(`Wrote ${outPath} (${json.length} bytes)`);
} else {
  console.log(json);
}
