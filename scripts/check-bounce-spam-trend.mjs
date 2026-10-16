// Tracks two deliverability signals day over day, since they're the ones that should actually
// move as a result of the 2026-08-28 bounce-pause fix + unsubscribe-link rollout:
//   1. Bounce count/rate on the 8 campaigns flagged in that root-cause review.
//   2. Spam-folder-save counts on the 6 accounts (3 domains) flagged as elevated-risk.
//
// Appends today's rows to the "Bounce Spam Trend" tab of the Google Sheet configured by
// GOOGLE_SHEETS_SPREADSHEET_ID (see src/googlesheets.js) and prints the delta against the
// previous entry. Sheets, not git, because this runs unattended on a schedule and a direct
// `git push` to `main` from an auto-mode session is blocked by design (see PR #12) — Sheets
// writes aren't subject to that, and a shared sheet is easier to chart than raw JSON anyway.
// The tab is created on first run and seeded with the one historical snapshot that predates
// this migration (2026-08-28, previously the sole entry in the now-removed
// scripts/bounce-spam-trend-log.json).
//
// Usage: node scripts/check-bounce-spam-trend.mjs

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import { GoogleSheetsClient } from "../src/googlesheets.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const envPath = path.join(projectRoot, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq === -1) continue;
    const k = t.slice(0, eq).trim();
    const v = t.slice(eq + 1).trim();
    if (!(k in process.env)) process.env[k] = v;
  }
}

const TAB = "Bounce Spam Trend";
const RANGE = `'${TAB}'!A:I`;
const HEADER = ["Date", "Type", "Name", "Sent", "Bounced", "Rate %", "Lifetime Spam", "Weekly Spam Saves", "Error"];

// The one entry that lived in scripts/bounce-spam-trend-log.json before this migration —
// carried forward so the tab doesn't start blank. Not re-derived from a live query: these
// are the real 2026-08-28 numbers, frozen at the time they were captured.
const SEED_ENTRY = {
  date: "2026-08-28T17:53:12.623Z",
  campaigns: {
    "Cosmoprof Follow up": { sent: 1483, bounced: 127, rate: 8.56 },
    "Eikko - Tea Expo": { sent: 72, bounced: 7, rate: 9.72 },
    "Eikko - ICAST 2026": { sent: 358, bounced: 37, rate: 10.34 },
    "Rachel - Nordstil": { sent: 386, bounced: 69, rate: 17.88 },
    "Rachel - ISM Cologne": { sent: 1226, bounced: 121, rate: 9.87 },
    "Eikko - Cosmoprof 2026": { sent: 411, bounced: 38, rate: 9.25 },
    "Rachel - Spoga+gafa": { sent: 348, bounced: 65, rate: 18.68 },
    "Eikko - Fancy Foods Q4": { sent: 2379, bounced: 221, rate: 9.29 },
  },
  accounts: {
    "yoni@AlbertScottLLC.com": { lifetimeSpam: 37, weeklySpamSaves: 0 },
    "ylebovits@AlbertScottLLC.com": { lifetimeSpam: 29, weeklySpamSaves: 0 },
    "Yoni.Lebovits@AlbertScottLLC.com": { lifetimeSpam: 40, weeklySpamSaves: 0 },
    "yoni.lebovits@albertscottny.com": { lifetimeSpam: 14, weeklySpamSaves: 0 },
    "ylebovits@albertscottny.com": { lifetimeSpam: 13, weeklySpamSaves: 0 },
    "yoni@albertscottny.com": { lifetimeSpam: 11, weeklySpamSaves: 0 },
  },
};

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
const gs = new GoogleSheetsClient({});

function campaignRow(date, name, c) {
  return c.error
    ? [date, "campaign", name, "", "", "", "", "", c.error]
    : [date, "campaign", name, c.sent, c.bounced, c.rate, "", "", ""];
}
function accountRow(date, email, a) {
  return a.error
    ? [date, "account", email, "", "", "", "", "", a.error]
    : [date, "account", email, "", "", "", a.lifetimeSpam, a.weeklySpamSaves ?? "", ""];
}

/** Creates the tab (with header) if missing. Returns true when it just created it. */
async function ensureTab() {
  const meta = await gs.getSpreadsheetMeta();
  const exists = (meta.sheets || []).some((s) => s.properties.title === TAB);
  if (exists) return false;
  await gs.addSheet(TAB);
  await gs.updateRange(`'${TAB}'!A1:I1`, [HEADER]);
  return true;
}

async function seedHistoricalRows() {
  for (const [name, c] of Object.entries(SEED_ENTRY.campaigns)) {
    await gs.appendRow(RANGE, campaignRow(SEED_ENTRY.date, name, c));
  }
  for (const [email, a] of Object.entries(SEED_ENTRY.accounts)) {
    await gs.appendRow(RANGE, accountRow(SEED_ENTRY.date, email, a));
  }
}

/** Last row per campaign/account name, keyed off whichever the sheet actually has so far. */
function buildPrev(dataRows) {
  const campaigns = new Map();
  const accounts = new Map();
  for (const r of dataRows) {
    const [date, type, name, sent, bounced, rate, lifetimeSpam, weeklySpamSaves, error] = r;
    if (error) continue;
    if (type === "campaign") campaigns.set(name, { date, sent: Number(sent), bounced: Number(bounced), rate: Number(rate) });
    else if (type === "account")
      accounts.set(name, {
        date,
        lifetimeSpam: Number(lifetimeSpam),
        weeklySpamSaves: weeklySpamSaves === "" || weeklySpamSaves == null ? null : Number(weeklySpamSaves),
      });
  }
  return { campaigns, accounts };
}

async function main() {
  const justCreated = await ensureTab();
  let prev;
  if (justCreated) {
    await seedHistoricalRows();
    prev = buildPrev([
      ...Object.entries(SEED_ENTRY.campaigns).map(([n, c]) => campaignRow(SEED_ENTRY.date, n, c)),
      ...Object.entries(SEED_ENTRY.accounts).map(([e, a]) => accountRow(SEED_ENTRY.date, e, a)),
    ]);
  } else {
    const res = await gs.getValues(RANGE, { valueRenderOption: "UNFORMATTED_VALUE" });
    prev = buildPrev((res.values || []).slice(1));
  }

  const date = new Date().toISOString();
  const campaignResults = {};
  const accountResults = {};

  for (const c of CAMPAIGNS) {
    try {
      const a = await client.getCampaignAnalytics(c.id);
      const sent = Number(a.unique_sent_count) || 0;
      const bounced = Number(a.bounce_count) || 0;
      campaignResults[c.name] = { sent, bounced, rate: sent ? +((bounced / sent) * 100).toFixed(2) : 0 };
    } catch (err) {
      campaignResults[c.name] = { error: err.message };
    }
    await gs.appendRow(RANGE, campaignRow(date, c.name, campaignResults[c.name]));
  }

  const allAccounts = await client.listEmailAccounts();
  const byId = new Map(allAccounts.map((a) => [a.id, a]));
  for (const target of FLAGGED_ACCOUNTS) {
    const acct = byId.get(target.id);
    if (!acct) {
      accountResults[target.email] = { error: "missing from account list" };
    } else {
      const lifetimeSpam = acct.warmup_details?.total_spam_count ?? 0;
      let weeklySpamSaves = null;
      try {
        const stats = await client.getEmailAccountWarmupStats(target.id);
        weeklySpamSaves = (stats.stats_by_date || []).reduce((s, d) => s + (d.save_from_spam_count || 0), 0);
      } catch {
        // leave null if unavailable
      }
      accountResults[target.email] = { lifetimeSpam, weeklySpamSaves };
    }
    await gs.appendRow(RANGE, accountRow(date, target.email, accountResults[target.email]));
  }

  console.log(`=== Bounce/spam trend — ${date} ===`);
  let totalSent = 0, totalBounced = 0, prevTotalSent = 0, prevTotalBounced = 0;
  for (const [name, c] of Object.entries(campaignResults)) {
    if (c.error) { console.log(`${name}: ERROR — ${c.error}`); continue; }
    totalSent += c.sent; totalBounced += c.bounced;
    const p = prev.campaigns.get(name);
    const delta = p ? ` (was ${p.bounced} bounced / ${p.rate}%, ${p.sent} sent)` : " (no prior baseline)";
    if (p) { prevTotalSent += p.sent; prevTotalBounced += p.bounced; }
    console.log(`${name}: ${c.bounced} bounced / ${c.sent} sent = ${c.rate}%${delta}`);
  }
  const totalRate = totalSent ? +((totalBounced / totalSent) * 100).toFixed(2) : 0;
  const prevTotalRate = prevTotalSent ? +((prevTotalBounced / prevTotalSent) * 100).toFixed(2) : null;
  console.log(`\nCombined (8 campaigns): ${totalBounced}/${totalSent} = ${totalRate}%` + (prevTotalRate !== null ? ` (was ${prevTotalRate}%)` : " (no prior baseline)"));

  console.log(`\n-- Flagged accounts (spam-folder saves) --`);
  for (const [email, a] of Object.entries(accountResults)) {
    if (a.error) { console.log(`${email}: ERROR — ${a.error}`); continue; }
    const p = prev.accounts.get(email);
    const delta = p ? ` (was lifetime=${p.lifetimeSpam}, weekly=${p.weeklySpamSaves})` : " (no prior baseline)";
    console.log(`${email}: lifetime_spam=${a.lifetimeSpam}, weekly_spam_saves=${a.weeklySpamSaves}${delta}`);
  }
}

main().catch((err) => {
  console.error("ERROR:", err.message);
  process.exit(1);
});
