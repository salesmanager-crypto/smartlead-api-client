#!/usr/bin/env node
/**
 * Builds "Rachel's Overdue Desk" — an HTML report of overdue Pipedrive activities
 * cross-checked against Smartlead lead/conversation data.
 *
 * Usage:
 *   node scripts/build-overdue-report.mjs <rows.json> <output.html> [generatedLabel]
 *
 * <rows.json> is an array of overdue-activity rows, each shaped like:
 *   {
 *     "activity_id": 553,
 *     "subject": "followup",
 *     "due_date": "2026-06-02",
 *     "days_overdue": 77,
 *     "contact_name": "Joe Zhao" | null,
 *     "email": "joe@gozleo.com" | null,
 *     "org_name": "Zleo" | null
 *   }
 *
 * This script looks up each unique email in Smartlead (getLeadByEmail + latest
 * campaign's message history), merges the result onto each row, and writes a
 * complete standalone HTML report to <output.html>.
 *
 * Requires SMARTLEAD_API_KEY in the environment (see README.md).
 */

import { readFileSync, writeFileSync } from "node:fs";
import { SmartleadClient } from "../src/client.js";

const [, , rowsPath, outPath, generatedLabelArg] = process.argv;
if (!rowsPath || !outPath) {
  console.error("Usage: node scripts/build-overdue-report.mjs <rows.json> <output.html> [generatedLabel]");
  process.exit(1);
}

const rows = JSON.parse(readFileSync(rowsPath, "utf8"));
const generatedLabel = generatedLabelArg || new Date().toISOString().slice(0, 10);

const client = new SmartleadClient();

// ---- Smartlead lookups ----------------------------------------------------

function pickLatestCampaign(campaigns) {
  if (!Array.isArray(campaigns) || campaigns.length === 0) return null;
  return [...campaigns].sort((a, b) => {
    const ta = new Date(a.last_activity_at || a.last_sent_at || 0).getTime();
    const tb = new Date(b.last_activity_at || b.last_sent_at || 0).getTime();
    return tb - ta;
  })[0];
}

const categoriesList = await client.getLeadCategories().catch(() => []);
const categories = Object.fromEntries((categoriesList || []).map((c) => [c.id, c.name]));

const uniqueEmails = [...new Set(rows.map((r) => r.email).filter(Boolean))];
const lookup = {};

for (const email of uniqueEmails) {
  try {
    const lead = await client.getLeadByEmail(email);
    if (!lead || !lead.id) {
      lookup[email] = { match: false };
      continue;
    }
    const campaigns = lead.lead_campaign_data || [];
    const latest = pickLatestCampaign(campaigns);
    let history = null;
    if (latest) {
      try {
        history = await client.getLeadMessageHistory(latest.campaign_id, lead.id);
      } catch (e) {
        history = { error: e.message };
      }
    }
    lookup[email] = {
      match: true,
      isUnsubscribed: lead.is_unsubscribed,
      campaignCount: campaigns.length,
      latestCampaign: latest,
      history,
    };
  } catch (e) {
    lookup[email] = { match: false, error: e.message };
  }
}

// ---- Merge + synopsis ------------------------------------------------------

function stripHtml(s) {
  if (!s) return "";
  return s
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/div>/gi, "\n")
    .replace(/<[^>]+>/g, "")
    .replace(/\n{2,}/g, "\n")
    .trim();
}

function fmtDate(iso) {
  if (!iso) return null;
  try {
    return new Date(iso).toLocaleDateString("en-US", { month: "short", day: "2-digit", year: "numeric" });
  } catch {
    return iso;
  }
}

function buildSmartlead(row) {
  if (!row.email) return { status: "no_email" };
  const look = lookup[row.email];
  if (!look || !look.match) return { status: "no_match" };

  const latest = look.latestCampaign || {};
  const catId = latest.lead_category_id;
  const category = catId == null ? "Uncategorized" : categories[catId] || `Unknown (${catId})`;
  const history = look.history || {};
  const msgs = Array.isArray(history.history) ? history.history : Array.isArray(history) ? history : [];
  const lastMsg = msgs.length ? msgs[msgs.length - 1] : null;
  const replies = msgs.filter((m) => m.type === "REPLY");
  const lastReply = replies.length ? replies[replies.length - 1] : null;

  return {
    status: "match",
    campaign_name: latest.campaign_name,
    campaign_count: look.campaignCount,
    category,
    is_unsubscribed: look.isUnsubscribed,
    last_activity_at: fmtDate(latest.last_activity_at),
    last_reply_at: fmtDate(latest.last_reply_at),
    replied: Boolean(latest.last_reply_at),
    last_message_time: lastMsg ? fmtDate(lastMsg.time) : null,
    last_message_snippet: lastMsg ? stripHtml(lastMsg.email_body).slice(0, 400) : null,
    last_reply_snippet: lastReply ? stripHtml(lastReply.email_body).slice(0, 400) : null,
  };
}

const merged = rows
  .map((r) => ({ ...r, smartlead: buildSmartlead(r) }))
  .sort((a, b) => b.days_overdue - a.days_overdue);

// ---- HTML rendering ---------------------------------------------------------

function esc(s) {
  if (s === null || s === undefined) return "";
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

const CAT_CLASS = {
  Interested: "cat-pos",
  "Meeting Request": "cat-pos",
  Client: "cat-pos",
  "Not Interested": "cat-neg",
  "Do Not Contact": "cat-neg",
  Unqualified: "cat-neg",
  "Wrong Person": "cat-neutral",
  "Out Of Office": "cat-neutral",
  Ignore: "cat-neutral",
  "Follow Up": "cat-warn",
  "Action Needed": "cat-warn",
  "Information Request": "cat-warn",
  Unsure: "cat-warn",
  Uncategorized: "cat-muted",
  "Sender Originated Bounce": "cat-bounce",
  "Uncategorizable by Ai": "cat-muted",
};

function renderCard(r, bucketClass) {
  const subj = esc(r.subject);
  const org = r.org_name ? esc(r.org_name) : null;
  const contact = r.contact_name ? esc(r.contact_name) : null;
  const sl = r.smartlead;

  const whoBits = [];
  if (contact) whoBits.push(`<span class="contact-name">${contact}</span>`);
  if (org) whoBits.push(`<span class="org-name">${org}</span>`);
  const whoHtml = whoBits.length
    ? whoBits.join(" &middot; ")
    : '<span class="contact-name unknown">Unlinked activity</span>';

  let slHtml;
  if (sl.status === "no_email") {
    slHtml = `<div class="sl-block sl-none">
      <span class="sl-status-dot dot-none"></span>
      <span class="sl-status-text">No contact linked in Pipedrive &mdash; nothing to check in Smartlead.</span>
    </div>`;
  } else if (sl.status === "no_match") {
    slHtml = `<div class="sl-block sl-none">
      <span class="sl-status-dot dot-none"></span>
      <span class="sl-status-text">No Smartlead lead found for <code>${esc(r.email)}</code>.</span>
    </div>`;
  } else {
    const cat = sl.category;
    const catClass = CAT_CLASS[cat] || "cat-muted";
    const bounced = cat === "Sender Originated Bounce";
    const replied = sl.replied;
    let dot, statusText;
    if (bounced) {
      dot = "dot-bounce";
      statusText = `Bounced &mdash; last send undeliverable (${esc(sl.last_message_time || "")})`;
    } else if (replied) {
      dot = "dot-replied";
      statusText = `Replied ${esc(sl.last_reply_at || "")} &mdash; awaiting your response`;
    } else {
      dot = "dot-sent";
      statusText = `No reply yet &middot; last touch ${esc(sl.last_activity_at || sl.last_message_time || "")}`;
    }

    const campaign = esc(sl.campaign_name || "Unnamed campaign");
    const ccount = sl.campaign_count || 1;
    const extraCamp = ccount > 1 ? ` (+${ccount - 1} more)` : "";

    const snippetLabel = replied && !bounced ? "Their reply" : bounced ? "Bounce notice" : "Last message sent";
    const snippetText = esc((replied || bounced ? sl.last_reply_snippet : sl.last_message_snippet) || "No message body available.");

    let alsoSent = "";
    if ((replied || bounced) && sl.last_message_snippet) {
      alsoSent = `<div class="msg-block">
        <div class="msg-label">Most recent outbound</div>
        <div class="msg-body">${esc(sl.last_message_snippet)}&hellip;</div>
      </div>`;
    }

    slHtml = `<div class="sl-block sl-match">
      <div class="sl-status-row">
        <span class="sl-status-dot ${dot}"></span>
        <span class="sl-status-text">${statusText}</span>
        <span class="cat-chip ${catClass}">${esc(cat)}</span>
      </div>
      <div class="sl-meta">Campaign: <strong>${campaign}</strong>${extraCamp}</div>
      <details class="thread">
        <summary>View last message</summary>
        <div class="msg-block">
          <div class="msg-label">${snippetLabel}</div>
          <div class="msg-body">${snippetText}&hellip;</div>
        </div>
        ${alsoSent}
      </details>
    </div>`;
  }

  return `<article class="card ${bucketClass}">
    <div class="card-top">
      <div class="who">${whoHtml}</div>
      <div class="due-pill ${bucketClass}">
        <span class="due-days">${r.days_overdue}d</span>
        <span class="due-label">overdue</span>
      </div>
    </div>
    <div class="task-row">
      <span class="task-icon">&#9742;</span>
      <span class="task-subject">${subj}</span>
      <span class="task-due">due ${esc(r.due_date)}</span>
    </div>
    ${slHtml}
  </article>`;
}

const buckets = [
  { key: "stale", title: "3+ Weeks Overdue", sub: "Gone quiet the longest — decide whether to re-engage or close out.", min: 21, max: Infinity, rows: [] },
  { key: "aging", title: "1–3 Weeks Overdue", sub: "Still fresh enough to catch before they go cold.", min: 7, max: 20, rows: [] },
  { key: "fresh", title: "Under a Week Overdue", sub: "Just slipped — quickest wins on the list.", min: 0, max: 6, rows: [] },
];

for (const r of merged) {
  const b = buckets.find((b) => r.days_overdue >= b.min && r.days_overdue <= b.max) || buckets[buckets.length - 1];
  b.rows.push(r);
}

const sectionsHtml = buckets
  .map(
    (b) => `
  <section class="bucket" id="${b.key}">
    <div class="bucket-head">
      <h2>${b.title}</h2>
      <p class="bucket-sub">${b.sub}</p>
      <span class="bucket-count">${b.rows.length}</span>
    </div>
    <div class="card-grid">
      ${b.rows.map((r) => renderCard(r, b.key)).join("\n")}
    </div>
  </section>`
  )
  .join("\n");

const total = merged.length;
const matched = merged.filter((r) => r.smartlead.status === "match").length;
const noMatch = merged.filter((r) => r.smartlead.status === "no_match").length;
const replied = merged.filter((r) => r.smartlead.replied).length;
const oldest = merged.length ? Math.max(...merged.map((r) => r.days_overdue)) : 0;

const html = `<title>Rachel's Overdue Desk</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
  :root {
    --paper: #EEF1EC; --surface: #FBFBF8; --surface-2: #F3F5F0;
    --ink: #1C231F; --ink-soft: #4B564E; --ink-faint: #7C8A7F; --line: #D8DED2;
    --accent: #1F6F6B; --accent-soft: #E3EFEC; --accent-ink: #0F4B48;
    --stale: #B5432A; --stale-soft: #F7E4DD; --stale-ink: #7A2C1B;
    --aging: #B8862E; --aging-soft: #F6EBD4; --aging-ink: #7A5A1D;
    --fresh: #2F6E52; --fresh-soft: #DFEEE5; --fresh-ink: #1E4B37;
    --pos: #2F6E52; --pos-soft: #DFEEE5; --neg: #A23B2C; --neg-soft: #F4E1DC;
    --warn: #B8862E; --warn-soft: #F6EBD4; --muted: #6B756A; --muted-soft: #E7EAE4;
    --bounce: #8A2F6B; --bounce-soft: #F1E0EC;
    --dot-replied: #2F6E52; --dot-sent: #9AA398; --dot-none: #C6CCC1; --dot-bounce: #8A2F6B;
    --shadow: 0 1px 2px rgba(28,35,31,0.04), 0 6px 16px -8px rgba(28,35,31,0.12);
    --radius: 14px;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --paper: #14201C; --surface: #1B2925; --surface-2: #20302A;
      --ink: #EAF0EA; --ink-soft: #B7C4B9; --ink-faint: #7E9186; --line: #2E4038;
      --accent: #4FBBAF; --accent-soft: #1F3833; --accent-ink: #A9E7DE;
      --stale: #E08361; --stale-soft: #3A241D; --stale-ink: #F2C3AC;
      --aging: #E0B563; --aging-soft: #3A3120; --aging-ink: #F1DAA6;
      --fresh: #6FBE97; --fresh-soft: #1E3327; --fresh-ink: #B7E6CC;
      --pos: #6FBE97; --pos-soft: #1E3327; --neg: #E0836B; --neg-soft: #3A241F;
      --warn: #E0B563; --warn-soft: #3A3120; --muted: #91A092; --muted-soft: #263630;
      --bounce: #D391BE; --bounce-soft: #362335;
      --dot-replied: #6FBE97; --dot-sent: #6E7D71; --dot-none: #435049; --dot-bounce: #D391BE;
      --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 20px -10px rgba(0,0,0,0.5);
    }
  }
  :root[data-theme="dark"] {
    --paper: #14201C; --surface: #1B2925; --surface-2: #20302A;
    --ink: #EAF0EA; --ink-soft: #B7C4B9; --ink-faint: #7E9186; --line: #2E4038;
    --accent: #4FBBAF; --accent-soft: #1F3833; --accent-ink: #A9E7DE;
    --stale: #E08361; --stale-soft: #3A241D; --stale-ink: #F2C3AC;
    --aging: #E0B563; --aging-soft: #3A3120; --aging-ink: #F1DAA6;
    --fresh: #6FBE97; --fresh-soft: #1E3327; --fresh-ink: #B7E6CC;
    --pos: #6FBE97; --pos-soft: #1E3327; --neg: #E0836B; --neg-soft: #3A241F;
    --warn: #E0B563; --warn-soft: #3A3120; --muted: #91A092; --muted-soft: #263630;
    --bounce: #D391BE; --bounce-soft: #362335;
    --dot-replied: #6FBE97; --dot-sent: #6E7D71; --dot-none: #435049; --dot-bounce: #D391BE;
    --shadow: 0 1px 2px rgba(0,0,0,0.3), 0 8px 20px -10px rgba(0,0,0,0.5);
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--paper); color: var(--ink); font-family: "IBM Plex Sans", ui-sans-serif, system-ui, sans-serif; font-size: 15.5px; line-height: 1.5; }
  .wrap { max-width: 920px; margin: 0 auto; padding: 0 20px 96px; }
  header.masthead { padding: 56px 20px 28px; max-width: 920px; margin: 0 auto; }
  .eyebrow { font-family: "IBM Plex Mono", ui-monospace, monospace; font-size: 12px; letter-spacing: 0.09em; text-transform: uppercase; color: var(--accent); display: flex; align-items: center; gap: 8px; margin-bottom: 14px; }
  .eyebrow::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--accent); display: inline-block; }
  h1 { font-family: "Fraunces", ui-serif, Georgia, serif; font-weight: 500; font-size: clamp(32px, 5vw, 46px); line-height: 1.06; letter-spacing: -0.01em; margin: 0 0 14px; text-wrap: balance; color: var(--ink); }
  .dek { font-size: 16.5px; color: var(--ink-soft); max-width: 62ch; margin: 0; }
  .stat-strip { display: grid; grid-template-columns: repeat(auto-fit, minmax(110px, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; margin: 32px auto 0; max-width: 920px; }
  .stat { background: var(--surface); padding: 16px 16px 14px; }
  .stat-num { font-family: "Fraunces", serif; font-variant-numeric: tabular-nums; font-size: 27px; font-weight: 500; color: var(--ink); display: block; line-height: 1; }
  .stat-num.stale-c { color: var(--stale); }
  .stat-num.pos-c { color: var(--pos); }
  .stat-label { display: block; margin-top: 6px; font-size: 11.5px; color: var(--ink-faint); text-transform: uppercase; letter-spacing: 0.06em; }
  nav.jump { display: flex; gap: 10px; flex-wrap: wrap; margin: 28px auto 0; max-width: 920px; }
  nav.jump a { font-family: "IBM Plex Mono", monospace; font-size: 12.5px; text-decoration: none; color: var(--ink-soft); border: 1px solid var(--line); padding: 7px 12px; border-radius: 999px; background: var(--surface); transition: border-color .15s ease, color .15s ease; }
  nav.jump a:hover, nav.jump a:focus-visible { border-color: var(--accent); color: var(--accent-ink); }
  nav.jump a .n { font-weight: 600; color: var(--ink); margin-left: 5px; }
  section.bucket { margin-top: 52px; scroll-margin-top: 24px; }
  .bucket-head { display: grid; grid-template-columns: 1fr auto; align-items: baseline; column-gap: 16px; border-bottom: 1px solid var(--line); padding-bottom: 14px; margin-bottom: 20px; }
  .bucket-head h2 { font-family: "Fraunces", serif; font-weight: 500; font-size: 24px; margin: 0; grid-column: 1; }
  .bucket-sub { grid-column: 1; margin: 4px 0 0; font-size: 13.5px; color: var(--ink-faint); }
  .bucket-count { grid-column: 2; grid-row: 1 / 3; align-self: center; font-family: "Fraunces", serif; font-size: 30px; color: var(--ink-faint); font-variant-numeric: tabular-nums; }
  #stale .bucket-count { color: var(--stale); }
  #aging .bucket-count { color: var(--aging); }
  #fresh .bucket-count { color: var(--fresh); }
  .card-grid { display: flex; flex-direction: column; gap: 12px; }
  .card { background: var(--surface); border: 1px solid var(--line); border-left: 3px solid var(--line); border-radius: var(--radius); padding: 16px 18px 15px; box-shadow: var(--shadow); }
  .card.stale { border-left-color: var(--stale); }
  .card.aging { border-left-color: var(--aging); }
  .card.fresh { border-left-color: var(--fresh); }
  .card-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
  .who { font-size: 15.5px; }
  .contact-name { font-weight: 600; color: var(--ink); }
  .contact-name.unknown { font-weight: 500; font-style: italic; color: var(--ink-faint); }
  .org-name { color: var(--ink-soft); }
  .due-pill { display: flex; align-items: baseline; gap: 5px; padding: 4px 10px; border-radius: 999px; font-family: "IBM Plex Mono", monospace; white-space: nowrap; flex-shrink: 0; }
  .due-pill.stale { background: var(--stale-soft); color: var(--stale-ink); }
  .due-pill.aging { background: var(--aging-soft); color: var(--aging-ink); }
  .due-pill.fresh { background: var(--fresh-soft); color: var(--fresh-ink); }
  .due-days { font-weight: 600; font-size: 13.5px; }
  .due-label { font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.04em; opacity: 0.85; }
  .task-row { display: flex; align-items: baseline; gap: 8px; margin-top: 10px; padding-top: 10px; border-top: 1px dashed var(--line); font-size: 13.5px; flex-wrap: wrap; }
  .task-icon { color: var(--accent); font-size: 12px; }
  .task-subject { font-weight: 500; color: var(--ink); }
  .task-due { color: var(--ink-faint); font-family: "IBM Plex Mono", monospace; font-size: 12px; margin-left: auto; }
  .sl-block { margin-top: 12px; }
  .sl-none { display: flex; align-items: center; gap: 9px; font-size: 13px; color: var(--ink-faint); background: var(--surface-2); border-radius: 10px; padding: 9px 12px; }
  .sl-none code { font-family: "IBM Plex Mono", monospace; font-size: 12px; color: var(--ink-soft); background: transparent; }
  .sl-status-row { display: flex; align-items: center; gap: 9px; flex-wrap: wrap; }
  .sl-status-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
  .dot-replied { background: var(--dot-replied); box-shadow: 0 0 0 3px var(--pos-soft); }
  .dot-sent { background: var(--dot-sent); }
  .dot-none { background: var(--dot-none); }
  .dot-bounce { background: var(--dot-bounce); box-shadow: 0 0 0 3px var(--bounce-soft); }
  .sl-status-text { font-size: 13.5px; color: var(--ink-soft); }
  .cat-chip { font-family: "IBM Plex Mono", monospace; font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.03em; padding: 2.5px 8px; border-radius: 999px; margin-left: auto; }
  .cat-pos { background: var(--pos-soft); color: var(--pos); }
  .cat-neg { background: var(--neg-soft); color: var(--neg); }
  .cat-warn { background: var(--warn-soft); color: var(--warn); }
  .cat-neutral, .cat-muted { background: var(--muted-soft); color: var(--muted); }
  .cat-bounce { background: var(--bounce-soft); color: var(--bounce); }
  .sl-meta { margin-top: 7px; font-size: 12.5px; color: var(--ink-faint); }
  .sl-meta strong { color: var(--ink-soft); font-weight: 600; }
  details.thread { margin-top: 9px; }
  details.thread summary { cursor: pointer; font-size: 12.5px; color: var(--accent-ink); font-weight: 500; list-style: none; display: inline-flex; align-items: center; gap: 5px; }
  details.thread summary::before { content: "▸"; font-size: 10px; transition: transform .15s ease; }
  details.thread[open] summary::before { transform: rotate(90deg); }
  details.thread summary::-webkit-details-marker { display: none; }
  .msg-block { margin-top: 8px; padding: 10px 12px; background: var(--surface-2); border-radius: 10px; border: 1px solid var(--line); }
  .msg-label { font-family: "IBM Plex Mono", monospace; font-size: 10px; text-transform: uppercase; letter-spacing: 0.05em; color: var(--ink-faint); margin-bottom: 5px; }
  .msg-body { font-size: 13px; color: var(--ink-soft); white-space: pre-line; line-height: 1.55; }
  footer.note { max-width: 920px; margin: 56px auto 0; padding-top: 20px; border-top: 1px solid var(--line); font-size: 12.5px; color: var(--ink-faint); }
  @media (max-width: 560px) { header.masthead { padding-top: 40px; } .task-due { margin-left: 0; } }
</style>

<header class="masthead">
  <div class="eyebrow">Pipedrive &times; Smartlead &middot; refreshed ${esc(generatedLabel)}</div>
  <h1>Rachel's Overdue Desk</h1>
  <p class="dek">Every open Pipedrive activity assigned to you that's past its due date, cross-checked against Smartlead so you know what's already been said before you pick up the phone.</p>
</header>

<div class="stat-strip">
  <div class="stat"><span class="stat-num stale-c">${total}</span><span class="stat-label">Overdue tasks</span></div>
  <div class="stat"><span class="stat-num">${oldest}d</span><span class="stat-label">Oldest one</span></div>
  <div class="stat"><span class="stat-num pos-c">${replied}</span><span class="stat-label">Have replied</span></div>
  <div class="stat"><span class="stat-num">${matched}</span><span class="stat-label">Found in Smartlead</span></div>
  <div class="stat"><span class="stat-num">${noMatch}</span><span class="stat-label">No Smartlead match</span></div>
</div>

<div class="wrap">
  <nav class="jump">
    <a href="#stale">3+ weeks<span class="n">${buckets[0].rows.length}</span></a>
    <a href="#aging">1&ndash;3 weeks<span class="n">${buckets[1].rows.length}</span></a>
    <a href="#fresh">Under a week<span class="n">${buckets[2].rows.length}</span></a>
  </nav>

  ${sectionsHtml}

  <footer class="note">
    Pulled from Pipedrive activities owned by Rachel (done = false, due date before today) and matched to Smartlead by contact email. "No Smartlead match" means the email wasn't found as a lead in Smartlead &mdash; it doesn't mean no outreach ever happened elsewhere. Reply snippets are truncated to the first ~400 characters of the raw message. Refreshes twice daily at 9am and 4pm ET.
  </footer>
</div>
`;

writeFileSync(outPath, html);
console.log(`Wrote ${outPath} (${total} activities, ${matched} matched, ${replied} replied)`);
