#!/usr/bin/env node
/**
 * SmartLead -> smartlead.json (committed encrypted). Needs SMARTLEAD_API_KEY, plus
 * PIPEDRIVE_API_TOKEN + PIPEDRIVE_COMPANY_DOMAIN for the inbox-log sync check
 * (skipped from ctx when run-all already pulled Pipedrive).
 *
 *   node scripts/pull/smartlead.mjs
 *
 * Campaigns with all-time stats, per-campaign daily sent/replies for the last 14
 * days, the Master Inbox reply log for the same window with the Pipedrive sync
 * check, yesterday's summary and reply mix, inbox and domain counts.
 */
import { SmartleadClient } from "../../src/client.js";
import { PipedriveClient } from "../../src/pipedrive.js";
import { today as todayFn, addDays, ymd, num, rate, pool, fmtDate } from "./lib.mjs";
import { runStandalone, isMain } from "./write.mjs";
import { emailIndex } from "./pipedrive.mjs";

export const WINDOW_DAYS = 14;
export const SYNC_CATEGORIES = ["Interested", "Meeting Request", "Follow Up"];
const REP_TAGS = new Set(["YONI", "RACHEL", "EIKKO"]);
const CONCURRENCY = 4; // SmartLead allows roughly 10 requests per 2 seconds
const list = (r) => (Array.isArray(r) ? r : r?.data || []);
const dateOf = (v) => (v ? String(v).slice(0, 10) : null);

export async function pull(env, ctx = {}) {
  const sl = new SmartleadClient({ apiKey: env.SMARTLEAD_API_KEY, baseUrl: env.SMARTLEAD_BASE_URL || undefined });
  const TODAY = todayFn();
  const YDAY = addDays(TODAY, -1);
  const FROM = addDays(TODAY, -(WINDOW_DAYS - 1));
  const days = Array.from({ length: WINDOW_DAYS }, (_, i) => addDays(FROM, i));

  /* campaigns + all-time analytics */
  const campaigns = list(await sl.listCampaigns());
  const analytics = await pool(campaigns, CONCURRENCY, (c) => sl.getCampaignAnalytics(c.id).catch(() => null));
  const failedAnalytics = analytics.filter((a) => !a).length;
  if (campaigns.length && failedAnalytics === campaigns.length) throw new Error("every campaign analytics call failed");

  const catName = new Map(list(await sl.getLeadCategories()).map((c) => [c.id, c.name]));

  /* every sending inbox */
  const accounts = [];
  for (let offset = 0; ; offset += 100) {
    const arr = list(await sl.listEmailAccounts({ offset, limit: 100 }));
    accounts.push(...arr);
    if (arr.length < 100) break;
  }

  /* Master Inbox replies in the window */
  const replies = [];
  const since = new Date(Date.parse(FROM + "T00:00:00Z") - 12 * 3600e3); // covers FROM 00:00 Eastern
  const PAGE = 20; // the master-inbox endpoint caps limit at 20
  for (let offset = 0; offset < 10000; offset += PAGE) {
    const page = await sl.getMasterInboxReplies({
      offset, limit: PAGE, sortBy: "REPLY_TIME_DESC",
      filters: { emailStatus: "Replied", replyTimeBetween: [since.toISOString(), new Date().toISOString()] },
    });
    const arr = page?.data || [];
    replies.push(...arr);
    if (arr.length < PAGE) break;
  }

  /* daily sent/replies: one range call per campaign that has ever sent, then one
     call per day only for campaigns that were active in the window */
  const everSent = campaigns.filter((c, i) => num(analytics[i]?.sent_count) > 0);
  const inWindow = await pool(everSent, CONCURRENCY, (c) =>
    sl.getCampaignAnalyticsByDate(c.id, { startDate: FROM, endDate: TODAY }).catch(() => null)
  );
  const activeInWindow = everSent.filter((c, i) => num(inWindow[i]?.sent_count) > 0 || num(inWindow[i]?.reply_count) > 0);
  const jobs = activeInWindow.flatMap((c) => days.map((d) => ({ c, d })));
  const perDay = await pool(jobs, CONCURRENCY, ({ c, d }) =>
    sl.getCampaignAnalyticsByDate(c.id, { startDate: d, endDate: d }).catch(() => null)
  );
  const missingDays = perDay.filter((r) => !r).length;
  const daily = jobs
    .map(({ c, d }, i) => ({ date: d, campaignId: c.id, sent: perDay[i] ? num(perDay[i].sent_count) : null, replies: perDay[i] ? num(perDay[i].reply_count) : null }))
    .filter((r) => r.sent !== 0 || r.replies !== 0)
    .sort((a, b) => (a.date < b.date ? -1 : a.date > b.date ? 1 : a.campaignId - b.campaignId));

  /* Pipedrive persons for the sync check */
  let personByEmail = ctx.personByEmail;
  if (!personByEmail) {
    const pd = new PipedriveClient({ apiToken: env.PIPEDRIVE_API_TOKEN, companyDomain: env.PIPEDRIVE_COMPANY_DOMAIN });
    personByEmail = emailIndex(await pd.persons());
  }

  /* shape */
  const inboxLog = replies
    .filter((r) => r.last_reply_time && ymd(new Date(r.last_reply_time)) >= FROM)
    .map((r) => {
      const email = String(r.lead_email || "").toLowerCase().trim();
      const cat = r.lead_category_id ? catName.get(r.lead_category_id) ?? null : null;
      const pdId = personByEmail.get(email) ?? null;
      const status = !cat ? "uncategorized" : SYNC_CATEGORIES.includes(cat) ? (pdId ? "synced" : "gap") : "none";
      return {
        t: r.last_reply_time,
        day: ymd(new Date(r.last_reply_time)),
        name: [r.lead_first_name, r.lead_last_name].filter(Boolean).join(" ").trim() || "[not provided]",
        email: r.lead_email,
        campaign: r.email_campaign_name,
        campaignId: r.email_campaign_id,
        cat,
        catId: r.lead_category_id ?? null,
        pd: pdId,
        status,
      };
    })
    .sort((a, b) => (a.t < b.t ? 1 : a.t > b.t ? -1 : 0));

  const lastByCampaign = new Map();
  const firstSendByCampaign = new Map();
  for (const r of daily) {
    if (r.sent > 0 && !firstSendByCampaign.has(r.campaignId)) firstSendByCampaign.set(r.campaignId, r.date);
    lastByCampaign.set(r.campaignId, r.date);
  }
  for (const r of inboxLog) if (!lastByCampaign.has(r.campaignId) || lastByCampaign.get(r.campaignId) < r.day) lastByCampaign.set(r.campaignId, r.day);

  const campaignRows = campaigns
    .map((c, i) => {
      const a = analytics[i] || {};
      const sent = num(a.sent_count);
      const reply = num(a.reply_count);
      const bounce = num(a.bounce_count);
      const created = dateOf(c.created_at) || "";
      const tag = (a.tags || c.tags || []).map((t) => t?.name ?? t).find((n) => REP_TAGS.has(String(n).toUpperCase()));
      const prefix = /^([A-Za-z]+)\s+-\s+/.exec(c.name)?.[1];
      // SmartLead does not return a start date; use the first send when it falls in the window
      const firstSend = firstSendByCampaign.get(c.id) ?? null;
      return {
        id: c.id,
        name: c.name,
        status: c.status,
        created,
        started: dateOf(a.start_date || c.start_date) || (firstSend && created >= FROM && firstSend >= created ? firstSend : null),
        lastActivity: lastByCampaign.get(c.id) ?? null,
        sent,
        reply,
        bounce,
        leads: num(a.total_count),
        interested: num(a.campaign_lead_stats?.interested),
        replyRate: rate(reply, sent),
        bounceRate: rate(bounce, sent),
        rep: tag ? String(tag) : prefix && REP_TAGS.has(prefix.toUpperCase()) ? prefix : null,
      };
    })
    .sort((x, y) => (x.created < y.created ? 1 : x.created > y.created ? -1 : 0));

  const ydayRows = daily.filter((r) => r.date === YDAY);
  const ydayReplies = inboxLog.filter((r) => r.day === YDAY);
  const mix = {};
  for (const r of ydayReplies) mix[r.cat || "Uncategorized"] = (mix[r.cat || "Uncategorized"] || 0) + 1;

  ctx.records = campaignRows.length;
  const notes = [];
  if (failedAnalytics) notes.push(`${failedAnalytics} campaign analytics calls failed`);
  if (missingDays) notes.push(`${missingDays} daily analytics calls failed`);
  ctx.note = notes.join("; ") || null;

  return {
    pulledAt: new Date().toISOString(),
    today: TODAY,
    window: { from: FROM, to: TODAY, days: WINDOW_DAYS },
    syncCategories: SYNC_CATEGORIES,
    campaigns: campaignRows,
    daily,
    yesterday: {
      label: fmtDate(YDAY, { month: "short", day: "numeric" }),
      date: YDAY,
      sent: ydayRows.reduce((s, r) => s + num(r.sent), 0),
      sendingCampaigns: ydayRows.filter((r) => r.sent > 0).length,
      replies: ydayReplies.length,
      interested: ydayReplies.filter((r) => r.cat === "Interested").length,
      replyMix: Object.entries(mix).sort((a, b) => b[1] - a[1]),
    },
    inboxLog,
    inboxes: {
      total: accounts.length,
      domains: new Set(accounts.map((a) => String(a.from_email || "").split("@")[1]).filter(Boolean)).size,
    },
  };
}

if (isMain(import.meta.url)) await runStandalone("smartlead", pull);
