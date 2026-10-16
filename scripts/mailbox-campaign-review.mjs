#!/usr/bin/env node
// Twice-monthly mailbox + campaign review for SmartLead. Every connected inbox is
// checked for connection, warmup and spam-placement problems and for a broken
// tracking domain; every ACTIVE campaign is checked for bounce rate, reply rate,
// stalled sending, missing mailboxes and a sequence that is about to run dry. The
// window is the trailing 14 days, so two runs a month cover the whole month.
//
// Writes an HTML email body and a plain-text alternative and prints a one-line JSON
// summary on stdout. Exits 1 only when SmartLead itself can't be reached; findings
// are reported, not treated as failures.
//
// Usage: node scripts/mailbox-campaign-review.mjs [--out dist/mailbox-review] [--days 14]
// Needs SMARTLEAD_API_KEY (env or .env). Read-only: changes nothing in SmartLead.

import fs from "node:fs";
import path from "node:path";
import { SmartleadClient } from "../src/client.js";
import { auditTrackingDomains, listAllEmailAccounts, trackingDomainFlags } from "../src/trackingdomains.js";
import { loadEnv, today as todayNY, addDays, fmtDate, num, numOrNull, rate, pool } from "./pull/lib.mjs";

// Thresholds. Bounce lines match the inbox-health artifact (5%) with an earlier
// warning at 3%; the spam-save line is the worst week seen historically (see
// daily-deliverability-check.mjs).
const BOUNCE_WARN = 3;
const BOUNCE_BAD = 5;
const MIN_SENT_TO_JUDGE = 100;
const LOW_REPLY_RATE = 0.5;
const MIN_SENT_FOR_REPLY_RATE = 500;
const REPUTATION_WARN = 95;
const WEEKLY_SPAM_SAVES_BAD = 4;
const NEARLY_DONE = 0.9;
const CONCURRENCY = 5;

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const [k, inline] = a.slice(2).split("=", 2);
    out[k] = inline ?? (argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true);
  }
  return out;
}

const esc = (s) => String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
const pct = (s) => numOrNull(String(s ?? "").replace("%", ""));

/** Warmup-stats totals for the trailing week the endpoint returns. */
function warmupTotals(stats) {
  const days = stats?.stats_by_date || [];
  const spamSaves = days.reduce((s, d) => s + num(d.save_from_spam_count), 0);
  const inbox = numOrNull(stats?.inbox_count);
  const spam = numOrNull(stats?.spam_count);
  const placed = inbox != null && spam != null ? inbox + spam : null;
  return { spamSaves, inboxRate: placed ? rate(inbox, placed) : null };
}

export function reviewMailboxes(accounts, warmup, campaignsByAccount) {
  return accounts.map((a, i) => {
    const w = warmup[i];
    const problems = [];
    const warnings = [];
    if (!a.is_smtp_success) problems.push("SMTP connection failing");
    if (!a.is_imap_success) problems.push("IMAP connection failing");
    const status = a.warmup_details?.status ?? null;
    if (status !== "ACTIVE") problems.push(`warmup ${status ? status.toLowerCase() : "not set up"}`);
    const reputation = pct(a.warmup_details?.warmup_reputation);
    if (reputation != null && reputation < REPUTATION_WARN) warnings.push(`warmup reputation ${reputation}%`);
    if (w?.error) warnings.push(`warmup stats unavailable (${w.error})`);
    else if (w && w.spamSaves > WEEKLY_SPAM_SAVES_BAD) problems.push(`${w.spamSaves} warmup emails pulled from spam this week`);
    const campaigns = campaignsByAccount.get(a.id) || [];
    return {
      id: a.id,
      email: a.from_email,
      domain: String(a.from_email || "").split("@")[1]?.toLowerCase() || "",
      status,
      reputation,
      sentToday: num(a.daily_sent_count),
      dailyLimit: num(a.message_per_day),
      spamSaves: w?.spamSaves ?? null,
      inboxRate: w?.inboxRate ?? null,
      activeCampaigns: campaigns.length,
      problems,
      warnings,
    };
  });
}

export function reviewCampaigns(campaigns, analytics, windowed, mailboxCounts, days) {
  return campaigns.map((c, i) => {
    const a = analytics[i] || {};
    const w = windowed[i] || {};
    const sent = num(a.sent_count);
    const bounce = num(a.bounce_count);
    const wSent = num(w.sent_count);
    const wReply = num(w.reply_count);
    const wBounce = num(w.bounce_count);
    const total = num(a.total_count);
    const completed = num(a.campaign_lead_stats?.completed);
    const problems = [];
    const warnings = [];

    const mailboxes = mailboxCounts[i];
    if (mailboxes === 0) problems.push("no mailboxes attached");
    if (!wSent) problems.push(`sent nothing in the last ${days} days`);

    const wBounceRate = rate(wBounce, wSent);
    const bounceRate = rate(bounce, sent);
    if (wSent >= MIN_SENT_TO_JUDGE && wBounceRate >= BOUNCE_BAD) problems.push(`bounce rate ${wBounceRate}% in the window`);
    else if (wSent >= MIN_SENT_TO_JUDGE && wBounceRate >= BOUNCE_WARN) warnings.push(`bounce rate ${wBounceRate}% in the window`);
    else if (sent >= MIN_SENT_TO_JUDGE && bounceRate >= BOUNCE_BAD) warnings.push(`lifetime bounce rate ${bounceRate}%`);

    const wReplyRate = rate(wReply, wSent);
    if (wSent >= MIN_SENT_FOR_REPLY_RATE && wReplyRate < LOW_REPLY_RATE)
      warnings.push(`reply rate ${wReplyRate}% on ${wSent} sends`);

    if (total && completed / total >= NEARLY_DONE)
      warnings.push(`${Math.round((completed / total) * 100)}% of leads have finished the sequence`);

    return {
      id: c.id,
      name: c.name,
      mailboxes,
      sent,
      bounceRate,
      leads: total,
      interested: num(a.campaign_lead_stats?.interested),
      window: { sent: wSent, replies: wReply, bounces: wBounce, replyRate: wReplyRate, bounceRate: wBounceRate },
      problems,
      warnings,
    };
  });
}

export function renderHtml(r) {
  const li = (s) => `<li style="margin:2px 0">${s}</li>`;
  const th = (t) => `<th align="left" style="padding:5px 8px;border-bottom:2px solid #ddd;font-size:12px;color:#555">${t}</th>`;
  const td = (t) => `<td style="padding:5px 8px;border-bottom:1px solid #eee;font-size:13px;vertical-align:top">${t}</td>`;
  const tag = (bad) =>
    `<span style="display:inline-block;padding:1px 6px;border-radius:3px;font-size:11px;color:#fff;background:${bad ? "#c0392b" : "#d68910"}">${bad ? "fix" : "watch"}</span>`;

  const mbFlagged = r.mailboxes.filter((m) => m.problems.length || m.warnings.length);
  const cFlagged = r.campaigns.filter((c) => c.problems.length || c.warnings.length);

  const summary = `<p style="margin:0 0 12px">Review of <b>${r.mailboxes.length}</b> mailboxes and <b>${r.campaigns.length}</b> active campaigns for ${esc(
    fmtDate(r.from),
  )} to ${esc(fmtDate(r.to))}.</p>
<ul style="margin:0 0 16px;padding-left:18px;font-size:14px">
${li(`Mailboxes needing a fix: <b>${r.totals.mailboxProblems}</b>, to watch: <b>${r.totals.mailboxWarnings}</b>, idle (in no active campaign): <b>${r.totals.idleMailboxes}</b>`)}
${li(`Campaigns needing a fix: <b>${r.totals.campaignProblems}</b>, to watch: <b>${r.totals.campaignWarnings}</b>`)}
${li(`Last ${r.days} days across active campaigns: <b>${r.totals.sent}</b> sent, <b>${r.totals.replies}</b> replies (${r.totals.replyRate}%), <b>${r.totals.bounces}</b> bounces (${r.totals.bounceRate}%)`)}
${li(`Tracking domains: ${r.tracking.length ? `<b>${r.tracking.length}</b> issue(s)` : "clean"}`)}
</ul>`;

  const campaignTable = r.campaigns.length
    ? `<h3 style="margin:20px 0 6px;font-size:15px">Active campaigns, last ${r.days} days</h3>
<table cellspacing="0" cellpadding="0" style="border-collapse:collapse;width:100%"><tr>${th("Campaign")}${th("Sent")}${th("Replies")}${th("Reply %")}${th("Bounce %")}${th("Mailboxes")}${th("Interested")}${th("Notes")}</tr>${r.campaigns
        .map(
          (c) =>
            `<tr>${td(esc(c.name))}${td(c.window.sent)}${td(c.window.replies)}${td(c.window.replyRate)}${td(c.window.bounceRate)}${td(c.mailboxes ?? "n/a")}${td(
              c.interested,
            )}${td([...c.problems.map((p) => `${tag(true)} ${esc(p)}`), ...c.warnings.map((p) => `${tag(false)} ${esc(p)}`)].join("<br>"))}</tr>`,
        )
        .join("")}</table>`
    : `<p>No ACTIVE campaigns.</p>`;

  const mbTable = mbFlagged.length
    ? `<h3 style="margin:20px 0 6px;font-size:15px">Mailboxes that need attention (${mbFlagged.length})</h3>
<table cellspacing="0" cellpadding="0" style="border-collapse:collapse;width:100%"><tr>${th("Mailbox")}${th("Warmup")}${th("Reputation")}${th("Spam saves (7d)")}${th("Active campaigns")}${th("Issue")}</tr>${mbFlagged
        .map(
          (m) =>
            `<tr>${td(esc(m.email))}${td(esc(m.status ?? "none"))}${td(m.reputation != null ? m.reputation + "%" : "n/a")}${td(m.spamSaves ?? "n/a")}${td(m.activeCampaigns)}${td(
              [...m.problems.map((p) => `${tag(true)} ${esc(p)}`), ...m.warnings.map((p) => `${tag(false)} ${esc(p)}`)].join("<br>"),
            )}</tr>`,
        )
        .join("")}</table>`
    : `<p style="margin:16px 0">Every mailbox is connected, warming and clear of spam-placement flags.</p>`;

  const idle = r.mailboxes.filter((m) => !m.activeCampaigns && !m.problems.length);
  const idleBlock = idle.length
    ? `<h3 style="margin:20px 0 6px;font-size:15px">Healthy but idle mailboxes (${idle.length})</h3>
<p style="margin:0 0 6px;font-size:13px">Warm and connected, but attached to no active campaign. Spare sending capacity.</p>
<p style="margin:0;font-size:12px;color:#555">${idle.map((m) => esc(m.email)).join(", ")}</p>`
    : "";

  const tracking = r.tracking.length
    ? `<h3 style="margin:20px 0 6px;font-size:15px">Tracking domains</h3><ul style="margin:0;padding-left:18px;font-size:13px">${r.tracking
        .map((t) => li(esc(t)))
        .join("")}</ul>`
    : "";

  const errors = r.errors.length
    ? `<h3 style="margin:20px 0 6px;font-size:15px;color:#c0392b">Checks that could not run</h3><ul style="margin:0;padding-left:18px;font-size:13px">${r.errors
        .map((e) => li(esc(e)))
        .join("")}</ul>`
    : "";

  return `<div style="font-family:Arial,Helvetica,sans-serif;color:#222;max-width:900px">${summary}${campaignTable}${mbTable}${idleBlock}${tracking}${errors}<p style="margin:24px 0 0;font-size:11px;color:#999">Read-only review. Generated by scripts/mailbox-campaign-review.mjs. Fix = act now; watch = check again next review. ${
    cFlagged.length + mbFlagged.length
  } items flagged.</p></div>`;
}

export function renderText(r) {
  const lines = [
    `SmartLead review ${r.from} to ${r.to}: ${r.mailboxes.length} mailboxes, ${r.campaigns.length} active campaigns.`,
    `Last ${r.days} days: ${r.totals.sent} sent, ${r.totals.replies} replies (${r.totals.replyRate}%), ${r.totals.bounces} bounces (${r.totals.bounceRate}%).`,
    `Mailboxes: ${r.totals.mailboxProblems} to fix, ${r.totals.mailboxWarnings} to watch, ${r.totals.idleMailboxes} idle. Campaigns: ${r.totals.campaignProblems} to fix, ${r.totals.campaignWarnings} to watch.`,
  ];
  for (const c of r.campaigns.filter((c) => c.problems.length || c.warnings.length))
    lines.push(`- Campaign "${c.name}": ${[...c.problems.map((p) => "FIX " + p), ...c.warnings.map((p) => "watch " + p)].join("; ")}`);
  for (const m of r.mailboxes.filter((m) => m.problems.length || m.warnings.length))
    lines.push(`- ${m.email}: ${[...m.problems.map((p) => "FIX " + p), ...m.warnings.map((p) => "watch " + p)].join("; ")}`);
  for (const t of r.tracking) lines.push(`- Tracking: ${t}`);
  for (const e of r.errors) lines.push(`- Could not run: ${e}`);
  return lines.join("\n");
}

async function main() {
  loadEnv();
  const args = parseArgs(process.argv.slice(2));
  const days = Number(args.days) || 14;
  const outBase = typeof args.out === "string" ? args.out : "dist/mailbox-review";
  const to = todayNY();
  const from = addDays(to, -(days - 1));
  const errors = [];

  const sl = new SmartleadClient();
  const accounts = await listAllEmailAccounts(sl);
  const campaigns = (await sl.listCampaigns()).filter((c) => c.status === "ACTIVE");

  const [analytics, windowed, campaignAccounts, warmup] = await Promise.all([
    pool(campaigns, CONCURRENCY, (c) => sl.getCampaignAnalytics(c.id).catch((e) => (errors.push(`analytics for "${c.name}" (${e.status ?? e.message})`), null))),
    pool(campaigns, CONCURRENCY, (c) =>
      sl.getCampaignAnalyticsByDate(c.id, { startDate: from, endDate: to }).catch((e) => (errors.push(`${days}-day analytics for "${c.name}" (${e.status ?? e.message})`), null)),
    ),
    pool(campaigns, CONCURRENCY, (c) => sl.listCampaignEmailAccounts(c.id).catch((e) => (errors.push(`mailbox list for "${c.name}" (${e.status ?? e.message})`), null))),
    pool(accounts, CONCURRENCY, (a) =>
      sl.getEmailAccountWarmupStats(a.id).then(warmupTotals).catch((e) => ({ error: String(e.status ?? e.message) })),
    ),
  ]);

  const campaignsByAccount = new Map();
  const mailboxCounts = campaignAccounts.map((list, i) => {
    if (!Array.isArray(list)) return null;
    for (const a of list) {
      const id = a.id ?? a.email_account_id;
      if (!campaignsByAccount.has(id)) campaignsByAccount.set(id, []);
      campaignsByAccount.get(id).push(campaigns[i].id);
    }
    return list.length;
  });

  let tracking = [];
  try {
    tracking = trackingDomainFlags(await auditTrackingDomains(accounts));
  } catch (err) {
    errors.push(`tracking-domain audit (${err.message})`);
  }

  const mailboxes = reviewMailboxes(accounts, warmup, campaignsByAccount);
  const campaignRows = reviewCampaigns(campaigns, analytics, windowed, mailboxCounts, days);
  const sent = campaignRows.reduce((s, c) => s + c.window.sent, 0);
  const replies = campaignRows.reduce((s, c) => s + c.window.replies, 0);
  const bounces = campaignRows.reduce((s, c) => s + c.window.bounces, 0);
  const report = {
    from,
    to,
    days,
    mailboxes,
    campaigns: campaignRows,
    tracking,
    errors,
    totals: {
      sent,
      replies,
      bounces,
      replyRate: rate(replies, sent),
      bounceRate: rate(bounces, sent),
      mailboxProblems: mailboxes.filter((m) => m.problems.length).length,
      mailboxWarnings: mailboxes.filter((m) => !m.problems.length && m.warnings.length).length,
      idleMailboxes: mailboxes.filter((m) => !m.activeCampaigns && !m.problems.length).length,
      campaignProblems: campaignRows.filter((c) => c.problems.length).length,
      campaignWarnings: campaignRows.filter((c) => !c.problems.length && c.warnings.length).length,
    },
  };

  fs.mkdirSync(path.dirname(path.resolve(outBase)), { recursive: true });
  fs.writeFileSync(`${outBase}.html`, renderHtml(report));
  fs.writeFileSync(`${outBase}.txt`, renderText(report) + "\n");
  console.log(
    JSON.stringify({
      from,
      to,
      mailboxes: mailboxes.length,
      activeCampaigns: campaignRows.length,
      ...report.totals,
      trackingIssues: tracking.length,
      checksFailed: errors.length,
      subject: `SmartLead mailbox and campaign review - ${fmtDate(to)}`,
      html: `${outBase}.html`,
      text: `${outBase}.txt`,
    }),
  );
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((err) => {
    console.error(`mailbox review failed: ${err.message}`);
    process.exit(1);
  });
}
