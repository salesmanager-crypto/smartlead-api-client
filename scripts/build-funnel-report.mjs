#!/usr/bin/env node
/**
 * Builds "Rachel's Funnel Dashboard" — a cross-tool view of how prospects move
 * through Smartlead outreach -> replies -> Pipedrive leads/deals -> Gmail
 * follow-up, so drop-off at each hop is visible.
 *
 * Usage:
 *   node scripts/build-funnel-report.mjs <pipedrive.json> <gmail.json> <output.html> [generatedLabel]
 *
 * Smartlead data (campaigns named "Rachel - ...", their per-lead statistics) is
 * pulled live inside this script. Pipedrive and Gmail data must be gathered by
 * the caller (via MCP tools, since this script has no MCP access) and passed in
 * as JSON files shaped like:
 *
 *   pipedrive.json: {
 *     "range_start": "2026-02-20", "range_end": "2026-08-20", "owner_id": 25102178,
 *     "persons": [{ "id":123, "name":"...", "email":"...", "org_id":45 }],
 *     "organizations": [{ "id":45, "name":"..." }],
 *     "leads": [{ "id":"uuid", "title":"...", "person_id":123, "add_time":"2026-03-01T00:00:00Z" }],
 *     "deals": [{ "id":1, "title":"...", "person_id":123, "stage_id":5, "status":"open",
 *                 "value":1000, "currency":"USD", "add_time":"2026-03-05T00:00:00Z" }],
 *     "stages": [{ "id":5, "name":"Qualified", "pipeline_id":1 }],
 *     "overdue_activities_count": 7
 *   }
 *
 *   gmail.json: {
 *     "range_start": "2026-02-20", "range_end": "2026-08-20",
 *     "my_email": "rachel.s@albertscott.com",
 *     "threads": [{ "thread_id":"...", "subject":"...", "label":"Pitti Immagine Uomo",
 *                   "messages": [{ "from":"a@b.com", "to":["rachel.s@albertscott.com"], "date":"2026-03-01T12:00:00Z" }] }]
 *   }
 *
 * `label` is the Gmail label the thread was pulled under (used to group the
 * "unmatched Gmail" section below); omit it if unknown and it groups as "Unlabeled".
 *
 * Matching across all three tools is by lower-cased email address. Records that
 * don't match anything are never dropped — they show up in the "Unmatched"
 * sections instead, so nothing silently disappears.
 *
 * Requires SMARTLEAD_API_KEY in the environment (see README.md).
 */

import { readFileSync, writeFileSync } from "node:fs";
import { SmartleadClient } from "../src/client.js";

const [, , pipedrivePath, gmailPath, outPath, generatedLabelArg] = process.argv;
if (!pipedrivePath || !gmailPath || !outPath) {
  console.error("Usage: node scripts/build-funnel-report.mjs <pipedrive.json> <gmail.json> <output.html> [generatedLabel]");
  process.exit(1);
}

const pd = JSON.parse(readFileSync(pipedrivePath, "utf8"));
const gm = JSON.parse(readFileSync(gmailPath, "utf8"));
const generatedLabel = generatedLabelArg || new Date().toISOString().slice(0, 10);
const rangeStart = pd.range_start || gm.range_start || null;
const rangeEnd = pd.range_end || gm.range_end || new Date().toISOString().slice(0, 10);
const myEmail = norm(gm.my_email);

function norm(email) {
  return (email || "").trim().toLowerCase();
}
function inRange(dateStr) {
  if (!dateStr) return false;
  const d = String(dateStr).slice(0, 10);
  return (!rangeStart || d >= rangeStart) && (!rangeEnd || d <= rangeEnd);
}

// ---- Smartlead: pull "Rachel - " campaigns + per-lead statistics ------------

const POSITIVE_CATEGORY_IDS = new Set([1, 2, 5301]); // Interested, Meeting Request, Follow Up

let smartleadError = null;
const campaignReports = [];
const smartleadByEmail = new Map(); // normalized email -> aggregated record

try {
  const client = new SmartleadClient();
  const allCampaigns = await client.listCampaigns();
  const campaignList = Array.isArray(allCampaigns) ? allCampaigns : allCampaigns?.data ?? [];
  const rachelCampaigns = campaignList.filter((c) => (c.name || "").startsWith("Rachel - "));

  for (const camp of rachelCampaigns) {
    const campaignId = camp.id;
    const campaignName = (camp.name || "").replace(/^Rachel - /, "");
    const leadStats = [];
    let offset = 0;
    const limit = 100;
    let pageError = null;

    for (;;) {
      let page;
      try {
        page = await client.getCampaignStatistics(campaignId, { offset, limit });
      } catch (e) {
        pageError = e.message;
        break;
      }
      const items = Array.isArray(page) ? page : page?.data ?? page?.leads ?? [];
      if (!items.length) break;
      leadStats.push(...items);
      if (items.length < limit) break;
      offset += limit;
      if (offset > 5000) break; // sanity cap on a single campaign
    }

    let sent = 0, opened = 0, replied = 0, positive = 0;
    for (const s of leadStats) {
      const email = norm(s.lead_email || s.email);
      if (!email) continue;
      const sentAt = s.sent_time || s.sent_at || s.first_sent_time || null;
      // Scope the whole record to leads actually sent within the report window —
      // otherwise "sent" silently becomes the campaign's all-time cumulative total.
      if (!inRange(sentAt)) continue;
      const openAt = s.open_time || s.first_open_time || s.opened_time || null;
      const replyAt = s.reply_time || s.last_reply_time || s.replied_time || null;
      const categoryId = s.lead_category_id ?? null;
      const hasReplied = Boolean(replyAt) || categoryId != null;
      const isPositive = POSITIVE_CATEGORY_IDS.has(categoryId);

      sent += 1;
      if (openAt) opened += 1;
      if (hasReplied) replied += 1;
      if (isPositive) positive += 1;

      const existing = smartleadByEmail.get(email) || {
        email, campaigns: new Set(), sent: false, replied: false, positive: false,
        replyAt: null, categoryId: null, latestCampaign: null,
      };
      if (sentAt) existing.sent = true;
      if (hasReplied) existing.replied = true;
      if (isPositive) existing.positive = true;
      existing.campaigns.add(campaignName);
      if (replyAt && (!existing.replyAt || replyAt > existing.replyAt)) {
        existing.replyAt = replyAt;
        existing.categoryId = categoryId;
        existing.latestCampaign = campaignName;
      }
      smartleadByEmail.set(email, existing);
    }

    campaignReports.push({
      campaignId, campaignName, sent, opened, replied, positive, error: pageError,
      openRate: sent ? opened / sent : 0,
      replyRate: sent ? replied / sent : 0,
      positiveRate: sent ? positive / sent : 0,
    });
  }
} catch (e) {
  smartleadError = e.message;
}

// ---- Pipedrive: persons/orgs/stages lookups, leads + deals in range ---------

const personById = new Map((pd.persons || []).map((p) => [p.id, p]));
const orgById = new Map((pd.organizations || []).map((o) => [o.id, o]));
const stageById = new Map((pd.stages || []).map((s) => [s.id, s]));

function personEmail(personId) {
  const p = personById.get(personId);
  return p ? norm(p.email) : null;
}
function personLabel(personId) {
  const p = personById.get(personId);
  if (!p) return null;
  const org = p.org_id ? orgById.get(p.org_id) : null;
  return [p.name, org?.name].filter(Boolean).join(" · ");
}

const leadsInRange = (pd.leads || []).filter((l) => !rangeStart || (l.add_time || "") >= rangeStart);
const dealsInRange = (pd.deals || []).filter((d) => !rangeStart || (d.add_time || "") >= rangeStart);

const leadEmailSet = new Set(leadsInRange.map((l) => personEmail(l.person_id)).filter(Boolean));
const dealsByEmail = new Map();
for (const d of dealsInRange) {
  const email = personEmail(d.person_id);
  if (!email) continue;
  if (!dealsByEmail.has(email)) dealsByEmail.set(email, []);
  dealsByEmail.get(email).push(d);
}

const stageDist = new Map(); // stage name -> { count, valueByCurrency }
for (const d of dealsInRange) {
  const stageName = stageById.get(d.stage_id)?.name || `Stage ${d.stage_id ?? "?"}`;
  const entry = stageDist.get(stageName) || { count: 0, value: 0, currency: d.currency || "USD" };
  entry.count += 1;
  entry.value += Number(d.value) || 0;
  stageDist.set(stageName, entry);
}
const totalDealValue = dealsInRange.reduce((sum, d) => sum + (Number(d.value) || 0), 0);
const dealCurrency = dealsInRange[0]?.currency || "USD";
const overdueActivitiesCount = pd.overdue_activities_count ?? null;

// ---- Gmail: normalize threads, direction, response time --------------------

function otherParty(msg) {
  const from = norm(msg.from);
  if (from && from !== myEmail) return from;
  const tos = Array.isArray(msg.to) ? msg.to.map(norm) : [];
  return tos.find((t) => t && t !== myEmail) || null;
}

const gmailThreads = (gm.threads || [])
  .map((t) => {
    const messages = (t.messages || []).slice().sort((a, b) => new Date(a.date) - new Date(b.date));
    const other = messages.map(otherParty).find(Boolean) || null;
    const last = messages[messages.length - 1] || null;
    const lastDirection = last ? (norm(last.from) === myEmail ? "sent" : "received") : null;
    const sentCount = messages.filter((m) => norm(m.from) === myEmail).length;
    const receivedCount = messages.length - sentCount;

    const responseTimesMs = [];
    for (let i = 0; i < messages.length - 1; i++) {
      const cur = messages[i], next = messages[i + 1];
      if (norm(cur.from) !== myEmail && norm(next.from) === myEmail) {
        responseTimesMs.push(new Date(next.date) - new Date(cur.date));
      }
    }

    return {
      threadId: t.thread_id, subject: t.subject, otherEmail: other, label: t.label || null,
      lastDirection, lastDate: last?.date || null, sentCount, receivedCount,
      responseTimesMs, awaitingReply: lastDirection === "received",
    };
  })
  .filter((t) => t.otherEmail);

const gmailByEmail = new Map();
for (const t of gmailThreads) {
  if (!gmailByEmail.has(t.otherEmail)) gmailByEmail.set(t.otherEmail, []);
  gmailByEmail.get(t.otherEmail).push(t);
}

const allResponseTimesMs = gmailThreads.flatMap((t) => t.responseTimesMs);
const avgResponseMs = allResponseTimesMs.length
  ? allResponseTimesMs.reduce((a, b) => a + b, 0) / allResponseTimesMs.length
  : null;
const totalSent = gmailThreads.reduce((s, t) => s + t.sentCount, 0);
const totalReceived = gmailThreads.reduce((s, t) => s + t.receivedCount, 0);
const awaitingReplyThreads = gmailThreads.filter((t) => t.awaitingReply);

// ---- Funnel ------------------------------------------------------------------

const smartleadContacts = [...smartleadByEmail.values()];
const sentContacts = smartleadContacts.filter((c) => c.sent);
const repliedContacts = sentContacts.filter((c) => c.replied);
const becameLead = repliedContacts.filter((c) => leadEmailSet.has(c.email));
const becameDeal = repliedContacts.filter((c) => dealsByEmail.has(c.email));
const followUpSent = repliedContacts.filter((c) => (gmailByEmail.get(c.email) || []).some((t) => t.sentCount > 0));

const funnelStages = [
  { key: "sent", label: "Emails sent", count: sentContacts.length },
  { key: "replied", label: "Replied", count: repliedContacts.length },
  { key: "lead", label: "Became Pipedrive lead", count: becameLead.length },
  { key: "deal", label: "Became Pipedrive deal", count: becameDeal.length },
  { key: "followup", label: "Gmail follow-up sent", count: followUpSent.length },
];
const maxStage = Math.max(1, ...funnelStages.map((s) => s.count));
for (let i = 0; i < funnelStages.length; i++) {
  const prev = i === 0 ? null : funnelStages[i - 1].count;
  funnelStages[i].hopRate = prev ? funnelStages[i].count / prev : i === 0 ? 1 : 0;
  funnelStages[i].cohortRate = funnelStages[0].count ? funnelStages[i].count / funnelStages[0].count : 0;
  funnelStages[i].widthPct = (funnelStages[i].count / maxStage) * 100;
}

// ---- Unmatched ---------------------------------------------------------------

const unmatchedReplies = repliedContacts.filter((c) => !leadEmailSet.has(c.email) && !dealsByEmail.has(c.email));
const unmatchedGmailThreads = gmailThreads.filter((t) => !smartleadByEmail.has(t.otherEmail));

// ---- Formatting helpers -------------------------------------------------------

function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function pct(n) {
  return `${(n * 100).toFixed(1)}%`;
}
function money(amount, currency = "USD") {
  try {
    return new Intl.NumberFormat("en-US", { style: "currency", currency, maximumFractionDigits: 0 }).format(amount);
  } catch {
    return `${amount.toFixed(0)} ${currency}`;
  }
}
function fmtDate(iso) {
  if (!iso) return null;
  try {
    return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "2-digit", year: "numeric" });
  } catch {
    return iso;
  }
}
function fmtDuration(ms) {
  if (ms == null) return "—";
  const hours = ms / 3600000;
  if (hours < 24) return `${hours.toFixed(1)}h`;
  return `${(hours / 24).toFixed(1)}d`;
}
function groupBy(items, keyFn) {
  const map = new Map();
  for (const item of items) {
    const key = keyFn(item) || "Uncategorized";
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(item);
  }
  return [...map.entries()].sort((a, b) => b[1].length - a[1].length);
}

// ---- HTML rendering ------------------------------------------------------------

const funnelRowsHtml = funnelStages
  .map(
    (s, i) => `
    <div class="funnel-row">
      <div class="funnel-label">${esc(s.label)}</div>
      <div class="funnel-bar-track">
        <div class="funnel-bar" style="width:${s.widthPct.toFixed(1)}%"><span class="funnel-count">${s.count}</span></div>
      </div>
      <div class="funnel-rate">${i === 0 ? "" : `${pct(s.hopRate)} of prev &middot; `}${pct(s.cohortRate)} of sent</div>
    </div>`
  )
  .join("\n");

const campaignRowsHtml = campaignReports
  .sort((a, b) => b.sent - a.sent)
  .map(
    (c) => `
    <tr>
      <td>${esc(c.campaignName)}</td>
      <td class="num">${c.sent}</td>
      <td class="num">${pct(c.openRate)}</td>
      <td class="num">${pct(c.replyRate)}</td>
      <td class="num">${pct(c.positiveRate)}</td>
    </tr>`
  )
  .join("\n");

const stageRowsHtml = [...stageDist.entries()]
  .sort((a, b) => b[1].count - a[1].count)
  .map(
    ([name, d]) => `
    <div class="stage-row">
      <div class="stage-name">${esc(name)}</div>
      <div class="stage-bar-track"><div class="stage-bar" style="width:${((d.count / Math.max(1, dealsInRange.length)) * 100).toFixed(1)}%"></div></div>
      <div class="stage-count">${d.count} &middot; ${money(d.value, d.currency)}</div>
    </div>`
  )
  .join("\n");

const unmatchedRepliesByCampaign = groupBy(
  unmatchedReplies,
  (c) => c.latestCampaign || [...c.campaigns][0] || null
);
const unmatchedRepliesHtml = unmatchedRepliesByCampaign
  .map(([campaign, contacts]) => {
    const rows = contacts
      .slice()
      .sort((a, b) => (b.replyAt || "").localeCompare(a.replyAt || ""))
      .map(
        (c) => `
        <tr>
          <td>${esc(c.email)}</td>
          <td>${fmtDate(c.replyAt) || "—"}</td>
        </tr>`
      )
      .join("\n");
    return `
    <details class="group">
      <summary><span class="group-name">${esc(campaign)}</span><span class="group-count">${contacts.length}</span></summary>
      <div class="table-scroll"><table class="data-table"><tr><th>Email</th><th>Last reply</th></tr>${rows}</table></div>
    </details>`;
  })
  .join("\n");

const unmatchedGmailByLabel = groupBy(unmatchedGmailThreads, (t) => t.label);
const unmatchedGmailHtml = unmatchedGmailByLabel
  .map(([label, threads]) => {
    const rows = threads
      .slice()
      .sort((a, b) => (b.lastDate || "").localeCompare(a.lastDate || ""))
      .map(
        (t) => `
        <tr>
          <td>${esc(t.subject || "(no subject)")}</td>
          <td>${esc(t.otherEmail)}</td>
          <td>${fmtDate(t.lastDate) || "—"}</td>
        </tr>`
      )
      .join("\n");
    return `
    <details class="group">
      <summary><span class="group-name">${esc(label)}</span><span class="group-count">${threads.length}</span></summary>
      <div class="table-scroll"><table class="data-table"><tr><th>Subject</th><th>Contact</th><th>Last message</th></tr>${rows}</table></div>
    </details>`;
  })
  .join("\n");

const totalPersons = personById.size;
const smartleadNote = smartleadError
  ? `<div class="err-banner">Smartlead pull failed (${esc(smartleadError)}) — Smartlead-derived numbers below are stale or empty.</div>`
  : "";
const gmailNote = gm.note ? `<div class="err-banner">${esc(gm.note)}</div>` : "";

const html = `<title>Rachel's Funnel Dashboard</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {
    --paper: #EEF1EC; --surface: #FBFBF8; --surface-2: #F3F5F0;
    --ink: #1C231F; --ink-soft: #4B564E; --ink-faint: #7C8A7F; --line: #D8DED2;
    --accent: #1F6F6B; --accent-soft: #E3EFEC; --accent-ink: #0F4B48;
    --pos: #2F6E52; --pos-soft: #DFEEE5; --neg: #A23B2C; --neg-soft: #F4E1DC;
    --warn: #B8862E; --warn-soft: #F6EBD4; --muted: #6B756A; --muted-soft: #E7EAE4;
    --shadow: 0 1px 2px rgba(28,35,31,0.04), 0 6px 16px -8px rgba(28,35,31,0.12);
    --radius: 14px;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #14201C; --surface: #1B2925; --surface-2: #20302A;
      --ink: #EAF0EA; --ink-soft: #B7C4B9; --ink-faint: #7E9186; --line: #2E4038;
      --accent: #4FBBAF; --accent-soft: #1F3833; --accent-ink: #A9E7DE;
      --pos: #6FBE97; --pos-soft: #1E3327; --neg: #E0836B; --neg-soft: #3A241F;
      --warn: #E0B563; --warn-soft: #3A3120; --muted: #91A092; --muted-soft: #263630;
      --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 20px -10px rgba(0,0,0,0.5);
    }
  }
  :root[data-theme="dark"] {
    --paper: #14201C; --surface: #1B2925; --surface-2: #20302A;
    --ink: #EAF0EA; --ink-soft: #B7C4B9; --ink-faint: #7E9186; --line: #2E4038;
    --accent: #4FBBAF; --accent-soft: #1F3833; --accent-ink: #A9E7DE;
    --pos: #6FBE97; --pos-soft: #1E3327; --neg: #E0836B; --neg-soft: #3A241F;
    --warn: #E0B563; --warn-soft: #3A3120; --muted: #91A092; --muted-soft: #263630;
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 20px -10px rgba(0,0,0,0.5);
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif; font-size: 15.5px; line-height: 1.5; }
  .wrap { max-width: 960px; margin: 0 auto; padding: 0 20px 96px; }
  header.masthead { padding: 56px 20px 28px; max-width: 960px; margin: 0 auto; }
  .eyebrow { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.09em; text-transform: uppercase; color: var(--accent); display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
  .eyebrow::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); display: inline-block; }
  h1 { font-family: "Fraunces", ui-serif, Georgia, serif; font-weight: 500; font-size: clamp(32px, 5vw, 46px); line-height: 1.06; letter-spacing: -0.01em; margin: 0 0 14px; text-wrap: balance; }
  .dek { font-size: 16.5px; color: var(--ink-soft); max-width: 64ch; margin: 0; }
  .err-banner { margin: 20px auto 0; max-width: 960px; background: var(--warn-soft); color: var(--warn); border-radius: var(--radius); padding: 12px 16px; font-size: 13.5px; }
  section.block { margin-top: 48px; }
  h2.block-title { font-family: "Fraunces", serif; font-weight: 500; font-size: 22px; margin: 0 0 18px; border-bottom: 1px solid var(--line); padding-bottom: 12px; }
  .funnel { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); padding: 22px 24px; box-shadow: var(--shadow); }
  .funnel-row { display: grid; grid-template-columns: 190px 1fr 190px; align-items: center; gap: 16px; padding: 10px 0; }
  .funnel-label { font-size: 13.5px; font-weight: 600; color: var(--ink-soft); }
  .funnel-bar-track { background: var(--surface-2); border-radius: 8px; height: 30px; position: relative; overflow: hidden; }
  .funnel-bar { background: var(--accent); height: 100%; border-radius: 8px; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; min-width: 34px; transition: width .2s ease; }
  .funnel-count { font-family: "IBM Plex Mono", monospace; font-size: 12.5px; font-weight: 600; color: var(--accent-soft); }
  .funnel-rate { font-size: 12px; color: var(--ink-faint); font-family: "IBM Plex Mono", monospace; text-align: right; }
  .stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
  .stat { background: var(--surface); padding: 16px 16px 14px; }
  .stat-num { font-family: "Fraunces", serif; font-variant-numeric: tabular-nums; font-size: 25px; font-weight: 500; display: block; line-height: 1; }
  .stat-label { display: block; margin-top: 6px; font-size: 11.5px; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.06em; }
  .table-scroll { overflow-x: auto; border-radius: var(--radius); }
  table.data-table { width: 100%; min-width: 480px; border-collapse: collapse; background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; font-size: 13.5px; }
  table.data-table td.num, table.data-table th.num, .funnel-count { font-variant-numeric: tabular-nums; }
  table.data-table th { text-align: left; font-family: "IBM Plex Mono", monospace; font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--ink-faint); padding: 10px 14px; border-bottom: 1px solid var(--line); background: var(--surface-2); }
  table.data-table td { padding: 9px 14px; border-bottom: 1px solid var(--line); color: var(--ink-soft); }
  table.data-table td.num { text-align: right; font-family: "IBM Plex Mono", monospace; }
  table.data-table th.num { text-align: right; }
  table.data-table tr:last-child td { border-bottom: none; }
  .stage-row { display: grid; grid-template-columns: 160px 1fr 190px; align-items: center; gap: 14px; padding: 8px 0; }
  .stage-name { font-size: 13px; color: var(--ink-soft); }
  .stage-bar-track { background: var(--surface-2); border-radius: 6px; height: 16px; overflow: hidden; }
  .stage-bar { background: var(--warn); height: 100%; }
  .stage-count { font-size: 12px; color: var(--ink-faint); font-family: "IBM Plex Mono", monospace; text-align: right; }
  .empty-note { padding: 16px; text-align: center; color: var(--ink-faint); font-size: 13px; border: 1px dashed var(--line); border-radius: var(--radius); }
  .group-list { display: flex; flex-direction: column; gap: 8px; }
  details.group { background: var(--surface); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
  details.group[open] { padding-bottom: 12px; }
  details.group summary { list-style: none; cursor: pointer; padding: 12px 16px; display: flex; align-items: center; justify-content: space-between; gap: 12px; font-size: 13.5px; font-weight: 600; color: var(--ink-soft); }
  details.group summary::-webkit-details-marker { display: none; }
  details.group summary::before { content: "▸"; font-size: 11px; color: var(--ink-faint); margin-right: 10px; transition: transform .15s ease; display: inline-block; }
  details.group[open] summary::before { transform: rotate(90deg); }
  details.group .group-name { flex: 1; }
  details.group .group-count { font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--ink-faint); background: var(--surface-2); border-radius: 999px; padding: 2px 10px; }
  details.group .table-scroll { padding: 0 16px 4px; border-radius: 0; }
  details.group table.data-table { border: none; border-radius: 0; }
  footer.note { max-width: 960px; margin: 56px auto 0; padding-top: 20px; border-top: 1px solid var(--line); font-size: 12.5px; color: var(--ink-faint); }
  @media (max-width: 640px) {
    .funnel-row, .stage-row { grid-template-columns: 1fr; gap: 4px; }
    .funnel-rate, .stage-count { text-align: left; }
  }
</style>

<header class="masthead">
  <div class="eyebrow">Smartlead &times; Pipedrive &times; Gmail &middot; refreshed ${esc(generatedLabel)}</div>
  <h1>Rachel's Funnel Dashboard</h1>
  <p class="dek">How your outreach moves from a sent email to a replied thread to a Pipedrive lead, a deal, and a follow-up in Gmail — and where it drops off along the way. Window: ${esc(fmtDate(rangeStart) || rangeStart)} &ndash; ${esc(fmtDate(rangeEnd) || rangeEnd)}.</p>
</header>
${smartleadNote}
${gmailNote}

<div class="wrap">
  <section class="block">
    <h2 class="block-title">Funnel</h2>
    <div class="funnel">
      ${funnelRowsHtml}
    </div>
  </section>

  <section class="block">
    <h2 class="block-title">Smartlead — by campaign</h2>
    ${campaignReports.length
      ? `<div class="table-scroll"><table class="data-table">
          <tr><th>Campaign</th><th class="num">Sent</th><th class="num">Open rate</th><th class="num">Reply rate</th><th class="num">Positive-reply rate</th></tr>
          ${campaignRowsHtml}
        </table></div>`
      : `<div class="empty-note">No "Rachel - " campaigns with data found.</div>`}
  </section>

  <section class="block">
    <h2 class="block-title">Pipedrive</h2>
    <div class="stat-strip">
      <div class="stat"><span class="stat-num">${leadsInRange.length}</span><span class="stat-label">Leads created</span></div>
      <div class="stat"><span class="stat-num">${dealsInRange.length}</span><span class="stat-label">Deals opened</span></div>
      <div class="stat"><span class="stat-num">${money(totalDealValue, dealCurrency)}</span><span class="stat-label">Total deal value</span></div>
      <div class="stat"><span class="stat-num">${overdueActivitiesCount ?? "—"}</span><span class="stat-label">Overdue activities</span></div>
    </div>
    ${stageDist.size ? `<div style="margin-top:18px">${stageRowsHtml}</div>` : ""}
  </section>

  <section class="block">
    <h2 class="block-title">Gmail follow-up</h2>
    <div class="stat-strip">
      <div class="stat"><span class="stat-num">${gmailThreads.length}</span><span class="stat-label">Matched threads</span></div>
      <div class="stat"><span class="stat-num">${totalSent}</span><span class="stat-label">Messages sent</span></div>
      <div class="stat"><span class="stat-num">${totalReceived}</span><span class="stat-label">Messages received</span></div>
      <div class="stat"><span class="stat-num">${fmtDuration(avgResponseMs)}</span><span class="stat-label">Avg. response time</span></div>
      <div class="stat"><span class="stat-num">${awaitingReplyThreads.length}</span><span class="stat-label">Awaiting your reply</span></div>
    </div>
  </section>

  <section class="block">
    <h2 class="block-title">Unmatched — Smartlead replies with no Pipedrive record (${unmatchedReplies.length})</h2>
    ${unmatchedReplies.length
      ? `<div class="group-list">${unmatchedRepliesHtml}</div>`
      : `<div class="empty-note">Every Smartlead reply in range matches a Pipedrive lead or deal.</div>`}
  </section>

  <section class="block">
    <h2 class="block-title">Unmatched — Gmail threads with no Smartlead record (${unmatchedGmailThreads.length})</h2>
    ${unmatchedGmailThreads.length
      ? `<div class="group-list">${unmatchedGmailHtml}</div>`
      : `<div class="empty-note">Every matched Gmail thread ties back to a Smartlead contact.</div>`}
  </section>

  <footer class="note">
    Matched across tools by lower-cased email address. "Sent" = leads with a recorded send in any "Rachel - " Smartlead campaign; positive-reply = category Interested/Meeting Request/Follow Up. Pipedrive scoped to owner_id ${esc(pd.owner_id ?? "")}. Gmail scoped to the labelled outreach threads only, matched by contact email. Unmatched records are shown, never dropped. Persons resolved: ${totalPersons}.
  </footer>
</div>
`;

writeFileSync(outPath, html);
console.log(
  `Wrote ${outPath} (sent=${sentContacts.length} replied=${repliedContacts.length} leads=${becameLead.length} deals=${becameDeal.length} followup=${followUpSent.length} unmatched_replies=${unmatchedReplies.length} unmatched_gmail=${unmatchedGmailThreads.length})`
);
