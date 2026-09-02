#!/usr/bin/env node
// Turns the raw pulls in dashboards/pull/out/ into the constants the dashboard renders from,
// written to dashboards/pull/out/data-constants.json. Then run apply-constants.mjs.
//
// Inputs (all under dashboards/pull/out/):
//   smartlead-pull.json               from pull-smartlead.mjs
//   heyreach-pull.json                from pull-heyreach.mjs (optional: previous LINKEDIN carried forward if missing)
//   pipedrive/activities-*.json       raw connector responses, getActivities done=false, any page count
//   pipedrive/deals-*.json            raw getDeals responses (one file per status is fine)
//   pipedrive/leads-*.json            raw getLeads responses
//   pipedrive/persons-*.json          raw getPersons responses, every page
//   pipedrive/orgs-*.json             raw getOrganizations responses, every page
//   pipedrive/stages.json             raw getStages response (optional)
//
// Usage: node dashboards/pull/build-constants.mjs [--today=YYYY-MM-DD] [--previous=path/to/yoni-command-center.html]
// --previous lets a section be carried forward when its pull is missing (HeyReach without a key, for example).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const outDir = path.join(here, "out");
const pdDir = path.join(outDir, "pipedrive");
const arg = (name) => { const a = process.argv.find((x) => x.startsWith("--" + name + "=")); return a ? a.split("=").slice(1).join("=") : null; };

const ET = "America/New_York";
const etDate = (d) => new Intl.DateTimeFormat("en-CA", { timeZone: ET, year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date(d));
const shiftDay = (iso, n) => { const d = new Date(iso + "T12:00:00Z"); d.setUTCDate(d.getUTCDate() + n); return d.toISOString().slice(0, 10); };
const shortDate = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", timeZone: "UTC" });
const longDate = (iso) => new Date(iso + "T12:00:00Z").toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric", timeZone: "UTC" });
const readJson = (p) => JSON.parse(fs.readFileSync(p, "utf8"));
const listFiles = (dir, prefix) => fs.existsSync(dir) ? fs.readdirSync(dir).filter((f) => f.startsWith(prefix) && f.endsWith(".json")).sort().map((f) => path.join(dir, f)) : [];
const rowsOf = (files) => files.flatMap((f) => { const j = readJson(f); return Array.isArray(j) ? j : j.data || []; });
const warn = [];

// ---- previous constants, for carry-forward ----
let previous = {};
const prevPath = arg("previous") || path.join(here, "..", "yoni-command-center.html");
if (fs.existsSync(prevPath)) {
  const html = fs.readFileSync(prevPath, "utf8");
  const grab = (name) => { const m = html.match(new RegExp("\\nconst " + name + " = (\\{[^\\n]*\\});\\n")); return m ? JSON.parse(m[1]) : null; };
  previous = { LINKEDIN: grab("LINKEDIN"), INBOXES: grab("INBOXES"), YESTERDAY: grab("YESTERDAY") };
}

// ---- SmartLead ----
const slPath = path.join(outDir, "smartlead-pull.json");
if (!fs.existsSync(slPath)) { console.error("missing " + slPath + " (run pull-smartlead.mjs first)"); process.exit(2); }
const S = readJson(slPath);
const TODAY = arg("today") || S.today || etDate(new Date());
const YDAY = shiftDay(TODAY, -1);

const REPS = ["Rachel", "Eikko", "John", "Yoni"];
function repOf(name) {
  const m = name.match(/^\s*([A-Za-z]+)\s*-\s*/);
  if (m) { const r = m[1].charAt(0).toUpperCase() + m[1].slice(1).toLowerCase(); if (REPS.includes(r)) return r; }
  if (/\byoni\b/i.test(name)) return "Yoni";
  return null;
}
const CAMPAIGNS = S.campaigns.map((c) => {
  const a = c.analytics || {}; const ls = a.campaign_lead_stats || {};
  const sent = Number(a.sent_count || 0), reply = Number(a.reply_count || 0), bounce = Number(a.bounce_count || 0);
  return { id: c.id, name: c.name.trim(), status: c.status, created: (c.created || "").slice(0, 10), sent, reply, bounce, leads: Number(a.total_count || 0), interested: Number(ls.interested || 0),
    replyRate: sent ? Math.round(reply / sent * 1000) / 10 : 0, bounceRate: sent ? Math.round(bounce / sent * 1000) / 10 : 0, rep: repOf(c.name) };
}).sort((x, y) => x.created.localeCompare(y.created));

const CAT = Object.fromEntries((S.categories || []).map((c) => [c.id, c.name]));
const SYNC_IDS = new Set(Object.entries(CAT).filter(([, n]) => ["Interested", "Meeting Request", "Follow Up"].includes(n)).map(([id]) => Number(id)));

// ---- Pipedrive persons: email -> person id (the sync check) ----
const persons = rowsOf(listFiles(pdDir, "persons-"));
const orgs = rowsOf(listFiles(pdDir, "orgs-"));
if (!persons.length) warn.push("no pipedrive/persons-*.json: sync check will mark everything unsynced");
const personName = Object.fromEntries(persons.map((p) => [String(p.id), p.name]));
const orgName = Object.fromEntries(orgs.map((o) => [String(o.id), o.name]));
const emailToPerson = {};
for (const p of persons) for (const e of p.emails || []) { const v = (e.value || "").trim().toLowerCase(); if (v && !(v in emailToPerson)) emailToPerson[v] = p.id; }

const INBOX_LOG = S.replies7d.map((r) => {
  const email = (r.lead_email || "").trim().toLowerCase(); const cat = r.category_id; const pd = emailToPerson[email] || null;
  const qual = cat != null && SYNC_IDS.has(Number(cat));
  const status = qual && pd ? "synced" : qual ? "gap" : cat == null ? "uncategorized" : "none";
  return { t: r.time, day: etDate(r.time), name: [r.first_name, r.last_name].filter(Boolean).join(" ").trim(), email, campaign: r.campaign, campaignId: r.campaign_id, cat: cat != null ? CAT[cat] || ("Category " + cat) : null, catId: cat, pd, status };
}).sort((a, b) => b.t.localeCompare(a.t));

const yRows = INBOX_LOG.filter((r) => r.day === YDAY);
const mix = {}; for (const r of yRows) { const k = r.cat || "Uncategorized"; mix[k] = (mix[k] || 0) + 1; }
const ySent = S.yesterdayByCampaign.map((y) => Number((y.data || {}).sent_count || 0));
const YESTERDAY = { label: shortDate(YDAY), date: YDAY, sent: ySent.reduce((a, b) => a + b, 0), sendingCampaigns: ySent.filter((n) => n > 0).length,
  replies: yRows.length, interested: yRows.filter((r) => r.cat === "Interested").length, replyMix: Object.entries(mix).sort((a, b) => b[1] - a[1]) };
const INBOXES = { total: S.emailAccounts.length, domains: new Set(S.emailAccounts.map((e) => (e.email || "").split("@")[1]).filter(Boolean)).size };

// ---- HeyReach ----
let LINKEDIN = previous.LINKEDIN;
const hrPath = path.join(outDir, "heyreach-pull.json");
if (fs.existsSync(hrPath)) {
  const H = readJson(hrPath);
  const hc = H.campaigns[0];
  if (hc) {
    const hl = H.leadsByCampaign[String(hc.id)] || { total: 0, byConnection: {}, byMessage: {}, byCampaignStatus: {} };
    const conn = hl.byConnection || {}, msg = hl.byMessage || {}, cs = hl.byCampaignStatus || {};
    LINKEDIN = { campaigns: H.campaigns.length, campaignName: hc.name, status: hc.status.charAt(0) + hc.status.slice(1).toLowerCase(), started: (hc.startedAt || hc.creationTime || "").slice(0, 10), listName: hc.linkedInUserListName, senders: (hc.campaignAccountIds || []).length,
      leads: hc.progressStats.totalUsers, processed: hl.total, pending: hc.progressStats.totalUsersPending,
      connectionsSent: (conn.ConnectionSent || 0) + (conn.ConnectionAccepted || 0), accepted: conn.ConnectionAccepted || 0, connNone: conn.None || 0,
      messagesSent: (msg.MessageSent || 0) + (msg.MessageReply || 0), replies: msg.MessageReply || 0,
      inSequence: cs.InSequence || 0, pendingInBatch: cs.Pending || 0, failed: cs.Failed || 0, finished: cs.Finished || 0 };
  }
} else { warn.push("no heyreach-pull.json: LINKEDIN carried forward from the previous page"); }
if (!LINKEDIN) { console.error("no HeyReach data and nothing to carry forward"); process.exit(2); }

// ---- Pipedrive activities, deals, leads ----
const acts = rowsOf(listFiles(pdDir, "activities-")).filter((a) => !a.done);
if (!acts.length) warn.push("no pipedrive/activities-*.json: OVERDUE/DUE_TODAY/UPCOMING will be empty");
const row = (x, kind) => {
  const delta = Math.round((Date.parse(TODAY + "T00:00:00Z") - Date.parse(x.due_date + "T00:00:00Z")) / 86400000);
  const r = { id: x.id, subject: x.subject || "", type: x.type, due: x.due_date, person: x.person_id ?? null, personName: x.person_id ? personName[String(x.person_id)] || null : null,
    org: x.org_id ?? null, orgName: x.org_id ? orgName[String(x.org_id)] || null : null, owner: x.owner_id };
  if (kind === "over") r.days = delta; else r.inDays = -delta;
  return r;
};
const byDue = (a, b) => a.due_date.localeCompare(b.due_date) || a.id - b.id;
const OVERDUE = acts.filter((a) => a.due_date < TODAY).sort(byDue).map((a) => row(a, "over"));
const DUE_TODAY = acts.filter((a) => a.due_date === TODAY).sort(byDue).map((a) => row(a, "today"));
const UPCOMING = acts.filter((a) => a.due_date > TODAY && a.due_date <= shiftDay(TODAY, 7)).sort(byDue).map((a) => row(a, "up"));
const openTypeCounts = {}; for (const a of acts) openTypeCounts[a.type] = (openTypeCounts[a.type] || 0) + 1;

const stagesFile = path.join(pdDir, "stages.json");
const stageName = fs.existsSync(stagesFile) ? Object.fromEntries(rowsOf([stagesFile]).map((s) => [String(s.id), s.name])) : {};
const dealRows = rowsOf(listFiles(pdDir, "deals-"));
const seen = new Set();
const DEALS = dealRows.filter((d) => !seen.has(d.id) && seen.add(d.id)).map((d) => ({ id: d.id, title: d.title, stage: stageName[String(d.stage_id)] || ("Stage #" + d.stage_id), status: d.status, value: Number(d.value || 0),
  added: (d.add_time || "").slice(0, 10), closed: d.close_time ? d.close_time.slice(0, 10) : null, owner: d.owner_id })).sort((a, b) => a.id - b.id);
if (!DEALS.length) warn.push("no pipedrive/deals-*.json: DEALS empty");

const leads = rowsOf(listFiles(pdDir, "leads-"));
const leadsByOwner = {}; for (const l of leads) leadsByOwner[l.owner_id] = (leadsByOwner[l.owner_id] || 0) + 1;
const PD_META = { openTotal: acts.length, openTypeCounts, leadsByOwner, leadsTotal: leads.length, leadsUnseen: leads.filter((l) => l.was_seen === false).length, personsTotal: persons.length, orgsTotal: orgs.length };

const constants = { DATA_DATE: longDate(TODAY), TODAY, OVERDUE, DUE_TODAY, UPCOMING, CAMPAIGNS, DEALS, INBOX_LOG, YESTERDAY, LINKEDIN, PD_META, INBOXES, pulledAt: S.pulledAt, warnings: warn };
const outFile = path.join(outDir, "data-constants.json");
fs.writeFileSync(outFile, JSON.stringify(constants));
console.error(JSON.stringify({ today: TODAY, campaigns: CAMPAIGNS.length, inboxLog: INBOX_LOG.length, gaps: INBOX_LOG.filter((r) => r.status === "gap").length, overdue: OVERDUE.length, dueToday: DUE_TODAY.length, upcoming: UPCOMING.length, deals: DEALS.length, persons: persons.length, orgs: orgs.length, warnings: warn }, null, 1));
console.error("written", outFile);
