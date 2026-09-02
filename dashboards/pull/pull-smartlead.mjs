#!/usr/bin/env node
// Pulls everything the command center's SmartLead page needs and writes
// dashboards/pull/out/smartlead-pull.json. Dates are computed in America/New_York.
//
// Usage: node dashboards/pull/pull-smartlead.mjs [--today=YYYY-MM-DD]
// Needs SMARTLEAD_API_KEY in the environment or in .env at the repo root.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../../src/client.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const outDir = path.join(here, "out");
fs.mkdirSync(outDir, { recursive: true });

const envPath = path.join(root, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim(); if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("="); if (eq === -1) continue;
    const k = t.slice(0, eq).trim(), v = t.slice(eq + 1).trim();
    if (!(k in process.env)) process.env[k] = v;
  }
}
if (!process.env.SMARTLEAD_API_KEY) { console.error("SMARTLEAD_API_KEY is not set"); process.exit(2); }

const ET = "America/New_York";
function etDate(d) { return new Intl.DateTimeFormat("en-CA", { timeZone: ET, year: "numeric", month: "2-digit", day: "2-digit" }).format(d); }
function shiftDay(iso, n) { const d = new Date(iso + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); }
// midnight in ET for a YYYY-MM-DD, as an ISO UTC string
function etMidnightUtc(iso) {
  const probe = new Date(iso + "T05:00:00Z"); // roughly midnight ET; correct for the exact offset below
  const parts = new Intl.DateTimeFormat("en-US", { timeZone: ET, hour12: false, hour: "2-digit", minute: "2-digit" }).formatToParts(probe);
  const h = Number(parts.find((p) => p.type === "hour").value) % 24, m = Number(parts.find((p) => p.type === "minute").value);
  return new Date(probe.getTime() - (h * 60 + m) * 60000).toISOString();
}

const todayArg = process.argv.find((a) => a.startsWith("--today="));
const TODAY = todayArg ? todayArg.split("=")[1] : etDate(new Date());
const YESTERDAY = shiftDay(TODAY, -1);
const WINDOW_START = shiftDay(TODAY, -7);

const client = new SmartleadClient({});
const log = (...a) => console.error(new Date().toISOString().slice(11, 19), ...a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const result = { pulledAt: new Date().toISOString(), today: TODAY, yesterday: YESTERDAY, windowStart: WINDOW_START, errors: [] };

// 1. campaigns + all-time analytics per campaign
const campaigns = await client.listCampaigns();
log("campaigns:", campaigns.length);
result.campaigns = [];
for (const c of campaigns) {
  let a = null;
  for (let attempt = 0; attempt < 3 && !a; attempt++) {
    try { a = await client.getCampaignAnalytics(c.id); }
    catch (e) { result.errors.push({ step: "analytics", id: c.id, msg: e.message }); await sleep(1500 * (attempt + 1)); }
  }
  result.campaigns.push({ id: c.id, name: c.name, status: c.status, created: c.created_at, analytics: a });
  await sleep(120);
}
log("analytics done, errors:", result.errors.length);

// 2. yesterday's sends per campaign: every ACTIVE campaign plus recent ones that have sent
result.yesterdayByCampaign = [];
const recent = shiftDay(TODAY, -90);
const maybeSending = result.campaigns.filter((c) => c.status === "ACTIVE" ||
  (c.analytics && Number(c.analytics.sent_count) > 0 && c.created && c.created.slice(0, 10) >= recent));
log("checking yesterday for", maybeSending.length, "campaigns");
for (const c of maybeSending) {
  try {
    const r = await client.getCampaignAnalyticsByDate(c.id, { startDate: YESTERDAY, endDate: YESTERDAY });
    result.yesterdayByCampaign.push({ id: c.id, name: c.name, status: c.status, data: r });
  } catch (e) { result.errors.push({ step: "byDate", id: c.id, msg: e.message }); }
  await sleep(120);
}

// 3. email accounts, fully paginated (the API caps a page at 100)
result.emailAccounts = [];
for (let offset = 0; ; offset += 100) {
  const page = await client.listEmailAccounts({ offset, limit: 100 });
  const arr = Array.isArray(page) ? page : page.data || [];
  result.emailAccounts.push(...arr.map((x) => ({ id: x.id, email: x.from_email, warmup: x.warmup_details && x.warmup_details.status, reputation: x.warmup_details && x.warmup_details.warmup_reputation, type: x.type })));
  if (arr.length < 100) break;
}
log("inboxes:", result.emailAccounts.length);

// 4. Master Inbox replies for the trailing 7 days (ET midnight boundaries), with categories
result.categories = await client.getLeadCategories();
result.replies7d = [];
const from = etMidnightUtc(WINDOW_START), to = new Date().toISOString();
for (let offset = 0; ; offset += 20) {
  const res = await client.getMasterInboxReplies({ offset, limit: 20, sortBy: "REPLY_TIME_DESC", filters: { emailStatus: "Replied", replyTimeBetween: [from, to] } }, false);
  const items = res.data || res.items || [];
  result.replies7d.push(...items.map((i) => ({
    lead_email: i.lead_email, first_name: i.lead_first_name, last_name: i.lead_last_name,
    campaign_id: i.email_campaign_id, campaign: i.email_campaign_name, category_id: i.lead_category_id, time: i.last_reply_time, lead_id: i.email_lead_id,
  })));
  if (items.length < 20 || offset > 2000) break;
  await sleep(150);
}
log("replies in window:", result.replies7d.length);

const out = path.join(outDir, "smartlead-pull.json");
fs.writeFileSync(out, JSON.stringify(result));
log("written", out);
