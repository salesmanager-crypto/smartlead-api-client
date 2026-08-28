// Tracks two deliverability signals day over day, since they're the ones that should actually
// move as a result of the 2026-08-28 bounce-pause fix + unsubscribe-link rollout:
//   1. Bounce count/rate on the 8 campaigns flagged in that root-cause review.
//   2. Spam-folder-save counts on the 6 accounts (3 domains) flagged as elevated-risk.
// Appends one dated entry to scripts/bounce-spam-trend-log.json (git-tracked — aggregate counts
// only, no lead-level PII, safe to commit) and prints the delta against the previous entry.
//
// Usage: node scripts/check-bounce-spam-trend.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const envPath = path.join(projectRoot, ".env");
for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#")) continue;
  const eq = t.indexOf("=");
  if (eq === -1) continue;
  const k = t.slice(0, eq).trim();
  const v = t.slice(eq + 1).trim();
  if (!(k in process.env)) process.env[k] = v;
}

const LOG_PATH = path.join(projectRoot, "scripts", "bounce-spam-trend-log.json");

const CAMPAIGNS = [
  { name: "Cosmoprof Follow up", id: 2302690 },
  { name: "Eikko - Tea Expo", id: 3756194 },
  { name: "Eikko - ICAST 2026", id: 3732474 },
  { name: "Rachel - Nordstil", id: 3731861 },
  { name: "Rachel - ISM Cologne", id: 3738501 },
  { name: "Eikko - Cosmoprof 2026", id: 3730127 },
  { name: "Rachel - Spoga+gafa", id: 3738533 },
  { name: "Eikko - Fancy Foods Q4", id: 3792273 },
];

const FLAGGED_ACCOUNTS = [
  { id: 481772, email: "yoni@AlbertScottLLC.com" },
  { id: 481756, email: "ylebovits@AlbertScottLLC.com" },
  { id: 481754, email: "Yoni.Lebovits@AlbertScottLLC.com" },
  { id: 481763, email: "yoni.lebovits@albertscottny.com" },
  { id: 481758, email: "ylebovits@albertscottny.com" },
  { id: 481762, email: "yoni@albertscottny.com" },
];

const client = new SmartleadClient({});

function loadLog() {
  try {
    return JSON.parse(fs.readFileSync(LOG_PATH, "utf8"));
  } catch {
    return [];
  }
}
function saveLog(log) {
  fs.writeFileSync(LOG_PATH, JSON.stringify(log, null, 2) + "\n");
}

async function main() {
  const entry = { date: new Date().toISOString(), campaigns: {}, accounts: {} };

  for (const c of CAMPAIGNS) {
    try {
      const a = await client.getCampaignAnalytics(c.id);
      const sent = Number(a.unique_sent_count) || 0;
      const bounced = Number(a.bounce_count) || 0;
      entry.campaigns[c.name] = { sent, bounced, rate: sent ? +(bounced / sent * 100).toFixed(2) : 0 };
    } catch (err) {
      entry.campaigns[c.name] = { error: err.message };
    }
  }

  const allAccounts = await client.listEmailAccounts();
  const byId = new Map(allAccounts.map((a) => [a.id, a]));
  for (const target of FLAGGED_ACCOUNTS) {
    const acct = byId.get(target.id);
    if (!acct) {
      entry.accounts[target.email] = { error: "missing from account list" };
      continue;
    }
    const lifetimeSpam = acct.warmup_details?.total_spam_count ?? 0;
    let weeklySpamSaves = null;
    try {
      const stats = await client.getEmailAccountWarmupStats(target.id);
      weeklySpamSaves = (stats.stats_by_date || []).reduce((s, d) => s + (d.save_from_spam_count || 0), 0);
    } catch {
      // leave null if unavailable
    }
    entry.accounts[target.email] = { lifetimeSpam, weeklySpamSaves };
  }

  const log = loadLog();
  const prev = log[log.length - 1];
  log.push(entry);
  saveLog(log);

  console.log(`=== Bounce/spam trend — ${entry.date} ===`);
  let totalSent = 0, totalBounced = 0, prevTotalSent = 0, prevTotalBounced = 0;
  for (const [name, c] of Object.entries(entry.campaigns)) {
    if (c.error) { console.log(`${name}: ERROR — ${c.error}`); continue; }
    totalSent += c.sent; totalBounced += c.bounced;
    const p = prev?.campaigns?.[name];
    const delta = p && !p.error ? ` (was ${p.bounced} bounced / ${p.rate}%, ${p.sent} sent)` : " (no prior baseline)";
    if (p && !p.error) { prevTotalSent += p.sent; prevTotalBounced += p.bounced; }
    console.log(`${name}: ${c.bounced} bounced / ${c.sent} sent = ${c.rate}%${delta}`);
  }
  const totalRate = totalSent ? +(totalBounced / totalSent * 100).toFixed(2) : 0;
  const prevTotalRate = prevTotalSent ? +(prevTotalBounced / prevTotalSent * 100).toFixed(2) : null;
  console.log(`\nCombined (8 campaigns): ${totalBounced}/${totalSent} = ${totalRate}%` + (prevTotalRate !== null ? ` (was ${prevTotalRate}%)` : " (no prior baseline)"));

  console.log(`\n-- Flagged accounts (spam-folder saves) --`);
  for (const [email, a] of Object.entries(entry.accounts)) {
    if (a.error) { console.log(`${email}: ERROR — ${a.error}`); continue; }
    const p = prev?.accounts?.[email];
    const delta = p && !p.error ? ` (was lifetime=${p.lifetimeSpam}, weekly=${p.weeklySpamSaves})` : " (no prior baseline)";
    console.log(`${email}: lifetime_spam=${a.lifetimeSpam}, weekly_spam_saves=${a.weeklySpamSaves}${delta}`);
  }
}

main().catch((err) => {
  console.error("ERROR:", err.message);
  process.exit(1);
});
