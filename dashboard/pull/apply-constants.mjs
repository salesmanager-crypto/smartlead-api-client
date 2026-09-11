#!/usr/bin/env node
/**
 * Regenerates the DATA BLOCK in dashboards/command-center.html from live APIs.
 *
 *   node dashboards/pull/apply-constants.mjs
 *
 * Sources: Pipedrive (activities, deals, leads, persons, orgs, users),
 * Smartlead (campaigns + analytics, master inbox, email accounts),
 * HeyReach (LinkedIn campaign + per-lead status).
 *
 * Credentials are read from ~/pipedrive-api-client/.env and ~/smartlead-api-client/.env.
 */
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const HOME = os.homedir();
const PD_DIR = path.join(HOME, "pipedrive-api-client");
const SL_DIR = path.join(HOME, "smartlead-api-client");
const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const DASH = path.join(ROOT, "command-center.html");

/* ---------- env ---------- */
function loadEnv(dir) {
  const f = path.join(dir, ".env");
  if (!fs.existsSync(f)) return;
  for (const line of fs.readFileSync(f, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
  }
}
loadEnv(PD_DIR);
loadEnv(SL_DIR);

const { SmartleadClient } = await import(path.join(ROOT, "pull/vendor/smartlead-client.js"));
const { HeyReachClient } = await import(path.join(ROOT, "pull/vendor/heyreach-client.js"));
const sl = new SmartleadClient();
const hr = new HeyReachClient();

/* ---------- helpers ---------- */
const TZ = "America/New_York";
const ymd = (d, tz = TZ) =>
  new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
const TODAY = ymd(new Date());
const daysBetween = (a, b) => Math.round((Date.parse(b + "T12:00:00Z") - Date.parse(a + "T12:00:00Z")) / 864e5);
const num = (v) => (v == null ? 0 : Number(v) || 0);
const rate = (n, d) => (d ? Math.round((n / d) * 1000) / 10 : 0);

async function pool(items, size, fn) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(
    Array.from({ length: Math.min(size, items.length) }, async () => {
      for (;;) {
        const idx = i++;
        if (idx >= items.length) return;
        out[idx] = await fn(items[idx], idx);
      }
    })
  );
  return out;
}

/* ---------- Pipedrive raw (paginated; the shared client drops the cursor) ---------- */
const PD_TOKEN = process.env.PIPEDRIVE_API_TOKEN;
const PD_BASE = `https://${process.env.PIPEDRIVE_COMPANY_DOMAIN}.pipedrive.com/api`;

async function pdFetch(version, p, query = {}) {
  const url = new URL(`${PD_BASE}/${version}${p}`);
  url.searchParams.set("api_token", PD_TOKEN);
  for (const [k, v] of Object.entries(query)) if (v != null) url.searchParams.set(k, v);
  for (let attempt = 0; ; attempt++) {
    const res = await fetch(url, { headers: { "x-api-token": PD_TOKEN } });
    if (res.status === 429 && attempt < 4) {
      await new Promise((r) => setTimeout(r, (Number(res.headers.get("retry-after")) || 2 ** attempt) * 1000));
      continue;
    }
    if (!res.ok) throw new Error(`Pipedrive ${version}${p} -> ${res.status} ${await res.text()}`);
    return res.json();
  }
}

/** v2 cursor pagination */
async function pdAllV2(p, query = {}) {
  const out = [];
  let cursor;
  do {
    const j = await pdFetch("v2", p, { ...query, limit: 500, cursor });
    out.push(...(j.data || []));
    cursor = j.additional_data?.next_cursor || null;
  } while (cursor);
  return out;
}

/** v1 start/limit pagination */
async function pdAllV1(p, query = {}) {
  const out = [];
  let start = 0;
  for (;;) {
    const j = await pdFetch("v1", p, { ...query, limit: 500, start });
    out.push(...(j.data || []));
    const more = j.additional_data?.pagination?.more_items_in_collection;
    if (!more) break;
    start = j.additional_data.pagination.next_start;
  }
  return out;
}

/* ================= PULL ================= */
console.error("pulling Pipedrive…");
const [pdUsers, pdStages, pdDeals, pdPersons, pdOrgs, pdActivities, pdLeads] = await Promise.all([
  pdFetch("v1", "/users").then((j) => j.data || []),
  pdAllV2("/stages"),
  pdAllV2("/deals"),
  pdAllV2("/persons"),
  pdAllV2("/organizations"),
  pdAllV2("/activities", { done: false }),
  pdAllV1("/leads", { archived_status: "not_archived" }),
]);

const stageName = new Map(pdStages.map((s) => [s.id, s.name]));
const personName = new Map(pdPersons.map((p) => [p.id, p.name]));
const orgName = new Map(pdOrgs.map((o) => [o.id, o.name]));

/** email -> person id, for the inbox sync check */
const personByEmail = new Map();
for (const p of pdPersons) {
  for (const e of p.emails || []) {
    const v = (e.value || "").toLowerCase().trim();
    if (v && !personByEmail.has(v)) personByEmail.set(v, p.id);
  }
}

console.error("pulling Smartlead…");
const slCampaignsRaw = await sl.listCampaigns();
const slCampaigns = slCampaignsRaw.data || slCampaignsRaw;
const slAnalytics = await pool(slCampaigns, 5, (c) => sl.getCampaignAnalytics(c.id).catch(() => null));

const catList = await sl.getLeadCategories();
const catName = new Map((catList.data || catList).map((c) => [c.id, c.name]));

/** every sending inbox, fully paginated */
const emailAccounts = [];
for (let offset = 0; ; offset += 100) {
  const page = await sl.listEmailAccounts({ offset, limit: 100 });
  const arr = page.data || page;
  emailAccounts.push(...arr);
  if (arr.length < 100) break;
}

/** master inbox, trailing 7 days */
const now = new Date();
const windowStart = new Date(now.getTime() - 7 * 864e5);
const replies = [];
const INBOX_PAGE = 20; // master-inbox caps limit at 20
for (let offset = 0; offset < 5000; offset += INBOX_PAGE) {
  const page = await sl.getMasterInboxReplies({
    offset,
    limit: INBOX_PAGE,
    sortBy: "REPLY_TIME_DESC",
    filters: { emailStatus: "Replied", replyTimeBetween: [windowStart.toISOString(), now.toISOString()] },
  });
  const arr = page.data || [];
  replies.push(...arr);
  if (arr.length < INBOX_PAGE) break;
}

/** yesterday's send volume, per campaign that could have sent */
const YDAY = ymd(new Date(Date.parse(TODAY + "T12:00:00Z") - 864e5));
const sendCandidates = slCampaigns.filter((c, i) => num(slAnalytics[i]?.sent_count) > 0);
const ydayStats = await pool(sendCandidates, 5, (c) =>
  sl.getCampaignAnalyticsByDate(c.id, { startDate: YDAY, endDate: YDAY }).catch(() => null)
);

console.error("pulling HeyReach…");
const hrList = await hr.listCampaigns({ offset: 0, limit: 100 });
const hrCampaigns = hrList.items || [];
const hrActive = hrCampaigns.find((c) => c.status !== "DRAFT") || hrCampaigns[0] || null;
let hrDetail = null;
const hrLeads = [];
if (hrActive) {
  hrDetail = await hr.getCampaign(hrActive.id);
  for (let offset = 0; ; offset += 100) {
    const page = await hr.getLeadsFromCampaign({ campaignId: hrActive.id, offset, limit: 100 });
    const arr = page.items || [];
    hrLeads.push(...arr);
    if (arr.length < 100 || hrLeads.length >= (page.totalCount || 0)) break;
  }
}

/* ================= SHAPE ================= */
const activityRow = (a) => ({
  id: a.id,
  subject: a.subject,
  type: a.type,
  due: a.due_date,
  person: a.person_id ?? null,
  personName: a.person_id ? personName.get(a.person_id) ?? null : null,
  org: a.org_id ?? null,
  orgName: a.org_id ? orgName.get(a.org_id) ?? null : null,
  owner: a.owner_id ?? null,
});

const openActs = pdActivities.filter((a) => !a.done && a.due_date);
const byDue = (x, y) => (x.due < y.due ? -1 : x.due > y.due ? 1 : x.id - y.id);

const OVERDUE = openActs
  .filter((a) => a.due_date < TODAY)
  .map((a) => ({ ...activityRow(a), days: daysBetween(a.due_date, TODAY) }))
  .sort(byDue);

const DUE_TODAY = openActs
  .filter((a) => a.due_date === TODAY)
  .map((a) => ({ ...activityRow(a), inDays: 0 }))
  .sort(byDue);

const UPCOMING = openActs
  .filter((a) => a.due_date > TODAY && daysBetween(TODAY, a.due_date) <= 7)
  .map((a) => ({ ...activityRow(a), inDays: daysBetween(TODAY, a.due_date) }))
  .sort(byDue);

const REP_TAGS = new Set(["YONI", "RACHEL", "EIKKO"]);
const CAMPAIGNS = slCampaigns
  .map((c, i) => {
    const a = slAnalytics[i] || {};
    const sent = num(a.sent_count);
    const reply = num(a.reply_count);
    const bounce = num(a.bounce_count);
    const tag = (a.tags || []).map((t) => t.name).find((n) => REP_TAGS.has(String(n).toUpperCase()));
    const prefix = /^([A-Za-z]+)\s+-\s+/.exec(c.name)?.[1];
    return {
      id: c.id,
      name: c.name,
      status: c.status,
      created: (c.created_at || "").slice(0, 10),
      sent,
      reply,
      bounce,
      leads: num(a.total_count),
      interested: num(a.campaign_lead_stats?.interested),
      replyRate: rate(reply, sent),
      bounceRate: rate(bounce, sent),
      rep: tag || (prefix && REP_TAGS.has(prefix.toUpperCase()) ? prefix : null),
    };
  })
  .sort((x, y) => (x.created < y.created ? 1 : x.created > y.created ? -1 : 0));

const DEALS = pdDeals
  .map((d) => ({
    id: d.id,
    title: d.title,
    stage: stageName.get(d.stage_id) ?? null,
    status: d.status,
    value: num(d.value),
    added: (d.add_time || "").slice(0, 10),
    closed: d.close_time ? d.close_time.slice(0, 10) : null,
    owner: d.owner_id ?? d.creator_user_id ?? null,
  }))
  .sort((x, y) => (x.added < y.added ? -1 : x.added > y.added ? 1 : x.id - y.id));

const SYNC_CATEGORIES = ["Interested", "Meeting Request", "Follow Up"];
const INBOX_LOG = replies
  .map((r) => {
    const email = (r.lead_email || "").toLowerCase().trim();
    const cat = r.lead_category_id ? catName.get(r.lead_category_id) ?? null : null;
    const pd = personByEmail.get(email) ?? null;
    const status = !cat ? "uncategorized" : SYNC_CATEGORIES.includes(cat) ? (pd ? "synced" : "gap") : "none";
    const name = [r.lead_first_name, r.lead_last_name].filter(Boolean).join(" ").trim() || "[not provided]";
    return {
      t: r.last_reply_time,
      day: ymd(new Date(r.last_reply_time)),
      name,
      email: r.lead_email,
      campaign: r.email_campaign_name,
      campaignId: r.email_campaign_id,
      cat,
      catId: r.lead_category_id ?? null,
      pd,
      status,
    };
  })
  .sort((a, b) => (a.t < b.t ? 1 : a.t > b.t ? -1 : 0));

/* yesterday */
const ydayReplies = INBOX_LOG.filter((r) => r.day === YDAY);
const mixCounts = {};
for (const r of ydayReplies) {
  const k = r.cat || "Uncategorized";
  mixCounts[k] = (mixCounts[k] || 0) + 1;
}
const YESTERDAY = {
  label: new Date(YDAY + "T12:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" }),
  date: YDAY,
  sent: ydayStats.reduce((s, a) => s + num(a?.sent_count), 0),
  sendingCampaigns: ydayStats.filter((a) => num(a?.sent_count) > 0).length,
  replies: ydayReplies.length,
  interested: ydayReplies.filter((r) => r.cat === "Interested").length,
  replyMix: Object.entries(mixCounts).sort((a, b) => b[1] - a[1]),
};

/* linkedin */
const countBy = (arr, key, val) => arr.filter((l) => l[key] === val).length;
const LINKEDIN = hrDetail
  ? {
      campaigns: hrCampaigns.length,
      campaignName: hrDetail.name,
      status: hrDetail.status.charAt(0) + hrDetail.status.slice(1).toLowerCase(),
      started: (hrDetail.startedAt || hrDetail.creationTime || "").slice(0, 10),
      listName: hrDetail.linkedInUserListName,
      senders: (hrDetail.campaignAccountIds || []).length,
      leads: hrDetail.progressStats?.totalUsers ?? 0,
      processed: hrLeads.length,
      pending: hrDetail.progressStats?.totalUsersPending ?? 0,
      connectionsSent: hrLeads.filter((l) => l.leadConnectionStatus && l.leadConnectionStatus !== "None").length,
      accepted: countBy(hrLeads, "leadConnectionStatus", "ConnectionAccepted"),
      connNone: countBy(hrLeads, "leadConnectionStatus", "None"),
      messagesSent: hrLeads.filter((l) => l.leadMessageStatus && l.leadMessageStatus !== "None").length,
      replies: countBy(hrLeads, "leadMessageStatus", "MessageReply"),
      inSequence: countBy(hrLeads, "leadCampaignStatus", "InSequence"),
      pendingInBatch: countBy(hrLeads, "leadCampaignStatus", "Pending"),
      failed: hrDetail.progressStats?.totalUsersFailed ?? 0,
      finished: hrDetail.progressStats?.totalUsersFinished ?? 0,
    }
  : null;

/* pipedrive meta */
const openTypeCounts = {};
for (const a of openActs) openTypeCounts[a.type] = (openTypeCounts[a.type] || 0) + 1;
const leadsByOwner = {};
for (const l of pdLeads) leadsByOwner[String(l.owner_id)] = (leadsByOwner[String(l.owner_id)] || 0) + 1;

const PD_META = {
  openTotal: openActs.length,
  openTypeCounts,
  leadsByOwner,
  leadsTotal: pdLeads.length,
  leadsUnseen: pdLeads.filter((l) => l.was_seen === false).length,
  personsTotal: pdPersons.length,
  orgsTotal: pdOrgs.length,
};

const INBOXES = {
  total: emailAccounts.length,
  domains: new Set(emailAccounts.map((a) => (a.from_email || "").split("@")[1]).filter(Boolean)).size,
};

const REP_NAME = {};
for (const u of pdUsers) if (u.active_flag) REP_NAME[u.id] = u.name;

/* ================= EMIT ================= */
const rows = (arr) => arr.map((r) => "  " + JSON.stringify(r) + ",").join("\n");
const dataDate = new Date(TODAY + "T12:00:00Z").toLocaleDateString("en-US", {
  month: "short", day: "numeric", year: "numeric", timeZone: "UTC",
});

const block = `/* ===== DATA BLOCK (generated by dashboards/pull/apply-constants.mjs, pulled ${new Date().toISOString()}) ===== */
const DATA_DATE = ${JSON.stringify(dataDate)};
const TODAY = ${JSON.stringify(TODAY)};
const OVERDUE = [
${rows(OVERDUE)}
];
const DUE_TODAY = [
${rows(DUE_TODAY)}
];
const UPCOMING = [
${rows(UPCOMING)}
];
const CAMPAIGNS = [
${rows(CAMPAIGNS)}
];
const DEALS = [
${rows(DEALS)}
];

/* Master Inbox replies, trailing 7 days. \`pd\` is the Pipedrive person id whose email matches the lead (null = no record).
   status: synced = qualifying category and a Pipedrive record exists; gap = qualifying category but NO record;
   uncategorized = no category yet; none = a category the automation does not sync. \`day\` is the reply date in Eastern time. */
const INBOX_LOG = [
${rows(INBOX_LOG)}
];

const YESTERDAY = ${JSON.stringify(YESTERDAY)};
const LINKEDIN = ${JSON.stringify(LINKEDIN)};
const PD_META = ${JSON.stringify(PD_META)};
const INBOXES = ${JSON.stringify(INBOXES)};
/* Pipedrive user id -> display name, for rep attribution. */
const REP_NAME = ${JSON.stringify(REP_NAME)};
/* Categories the Smartlead-to-Pipedrive automation syncs (Interested, Meeting Request, Follow Up). */
const SYNC_CATEGORIES = ${JSON.stringify(SYNC_CATEGORIES)};
/* END DATA BLOCK ===== */`;

const html = fs.readFileSync(DASH, "utf8");
const START = "/* ===== DATA BLOCK";
const END = "/* END DATA BLOCK ===== */";
const s = html.indexOf(START);
const e = html.indexOf(END);
if (s === -1 || e === -1) throw new Error("DATA BLOCK markers not found in command-center.html");
let updated = html.slice(0, s) + block + html.slice(e + END.length);

/* REP_NAME used to be hand-maintained just below the block; it is generated now. */
const tail = updated.slice(updated.indexOf(END) + END.length);
const dedupedTail = tail.replace(/^const REP_NAME = \{[^\n]*\};\n/m, "");
updated = updated.slice(0, updated.indexOf(END) + END.length) + dedupedTail;

fs.writeFileSync(DASH, updated);

console.error(
  [
    "",
    `data date        ${dataDate}`,
    `overdue          ${OVERDUE.length}`,
    `due today        ${DUE_TODAY.length}`,
    `upcoming (7d)    ${UPCOMING.length}`,
    `campaigns        ${CAMPAIGNS.length}`,
    `deals            ${DEALS.length}`,
    `inbox replies    ${INBOX_LOG.length}`,
    `yesterday sent   ${YESTERDAY.sent} across ${YESTERDAY.sendingCampaigns} campaigns`,
    `inboxes          ${INBOXES.total} on ${INBOXES.domains} domains`,
    `linkedin         ${LINKEDIN ? LINKEDIN.campaignName + " (" + LINKEDIN.status + ")" : "none"}`,
    "",
  ].join("\n")
);
