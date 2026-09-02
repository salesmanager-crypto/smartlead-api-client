// Pull everything the dashboard's SmartLead page needs. Output: smartlead-pull.json
import fs from "node:fs";
import { SmartleadClient } from "../../src/client.js";

for (const line of fs.readFileSync("../../.env", "utf8").split("\n")) {
  const t = line.trim(); if (!t || t.startsWith("#")) continue;
  const eq = t.indexOf("="); if (eq === -1) continue;
  const k = t.slice(0, eq).trim(), v = t.slice(eq + 1).trim();
  if (!(k in process.env)) process.env[k] = v;
}
const OUT = "./smartlead-pull.json";
const YESTERDAY = "2026-09-01";
const client = new SmartleadClient({});
const log = (...a) => console.error(new Date().toISOString().slice(11, 19), ...a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const result = { pulledAt: new Date().toISOString(), errors: [] };

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

// 2. yesterday's sends per campaign (active + anything that could have sent)
result.yesterdayByCampaign = [];
const maybeSending = result.campaigns.filter((c) => ["ACTIVE", "PAUSED", "COMPLETED", "STOPPED"].includes(c.status) &&
  (c.status === "ACTIVE" || (c.analytics && c.analytics.sent_count > 0 && new Date(c.created) > new Date("2026-06-01"))));
log("checking yesterday for", maybeSending.length, "campaigns");
for (const c of maybeSending) {
  try {
    const r = await client.getCampaignAnalyticsByDate(c.id, { startDate: YESTERDAY, endDate: YESTERDAY });
    result.yesterdayByCampaign.push({ id: c.id, name: c.name, status: c.status, data: r });
  } catch (e) { result.errors.push({ step: "byDate", id: c.id, msg: e.message }); }
  await sleep(120);
}

// 3. email accounts, fully paginated
result.emailAccounts = [];
for (let offset = 0; ; offset += 100) {
  const page = await client.listEmailAccounts({ offset, limit: 100 });
  const arr = Array.isArray(page) ? page : page.data || [];
  result.emailAccounts.push(...arr.map((x) => ({ id: x.id, email: x.from_email, warmup: x.warmup_details && x.warmup_details.status, reputation: x.warmup_details && x.warmup_details.warmup_reputation, type: x.type })));
  if (arr.length < 100) break;
}
log("inboxes:", result.emailAccounts.length);

// 4. last 7 days of replies from master inbox, with categories (feeds the daily inbox log)
const cats = await client.getLeadCategories();
result.categories = cats;
result.replies7d = [];
result.replySampleKeys = null;
for (let offset = 0; ; offset += 20) {
  const res = await client.getMasterInboxReplies({
    offset, limit: 20, sortBy: "REPLY_TIME_DESC",
    filters: { emailStatus: "Replied", replyTimeBetween: ["2026-08-26T00:00:00.000Z", "2026-09-02T23:59:59.999Z"] },
  }, false);
  const items = res.data || res.items || [];
  if (!result.replySampleKeys && items[0]) result.replySampleKeys = Object.keys(items[0]);
  result.replies7d.push(...items.map((i) => ({
    lead_email: i.lead_email, lead_name: i.lead_name, first_name: i.lead_first_name || i.first_name, last_name: i.lead_last_name || i.last_name,
    campaign_id: i.campaign_id, campaign: i.campaign_name, category_id: i.lead_category_id, time: i.last_reply_time,
    lead_id: i.lead_id, stats_id: i.stats_id, raw: i,
  })));
  if (items.length < 20 || offset > 1000) break;
  await sleep(150);
}
log("replies 7d:", result.replies7d.length);

// 5. last-7-days overview
try { result.overview7d = await client.getAnalyticsOverview({ start_date: "2026-08-26", end_date: "2026-09-02" }); }
catch (e) { result.errors.push({ step: "overview", msg: e.message }); }

fs.writeFileSync(OUT, JSON.stringify(result));
log("written", OUT);
