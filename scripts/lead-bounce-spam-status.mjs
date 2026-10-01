// Looks up a list of lead emails across every Smartlead campaign and reports which ones have
// bounced, been marked spam, or are otherwise unsafe to email again (unsubscribed, Do Not
// Contact, or on the global block list). Built for checking a re-engagement upload list before
// it goes into a new campaign, so the sheet owner can filter out leads that would hurt sender
// reputation. Read-only: nothing in Smartlead is changed.
//
// Input is a text/CSV file: either one email per line, or a CSV with an "email" header column.
// Output is a CSV (email, smartlead_status, do_not_use, campaigns, detail) written to
// .private/ by default, since it is lead-level data and this repository is public.
//
// Usage:
//   node scripts/lead-bounce-spam-status.mjs leads.csv
//   node scripts/lead-bounce-spam-status.mjs leads.csv --out /some/path/status.csv

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

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

const args = process.argv.slice(2);
const outIdx = args.indexOf("--out");
const outPath = outIdx !== -1 ? args[outIdx + 1] : path.join(projectRoot, ".private", "lead-bounce-spam-status.csv");
const inputPath = args.find((a, i) => !a.startsWith("--") && (outIdx === -1 || i !== outIdx + 1));
if (!inputPath) {
  console.error("Usage: node scripts/lead-bounce-spam-status.mjs <emails.csv> [--out status.csv]");
  process.exit(1);
}

function readEmails(file) {
  const lines = fs.readFileSync(file, "utf8").split(/\r?\n/).filter((l) => l.trim());
  const header = lines[0].split(",").map((h) => h.trim().toLowerCase());
  const col = header.indexOf("email");
  const rows = col === -1 ? lines : lines.slice(1);
  return [...new Set(rows.map((l) => (col === -1 ? l : l.split(",")[col] || "").trim().toLowerCase()).filter((e) => e.includes("@")))];
}

const client = new SmartleadClient({});

async function fetchAllStats(campaignId) {
  const limit = 500;
  let offset = 0;
  let all = [];
  while (true) {
    const page = await client.getCampaignStatistics(campaignId, { offset, limit });
    const data = page.data || [];
    all = all.concat(data);
    if (data.length < limit) break;
    offset += limit;
    if (offset > 50000) break; // safety valve
  }
  return all;
}

async function fetchBlockList() {
  const limit = 500;
  let offset = 0;
  const entries = new Set();
  while (true) {
    const page = await client.getDomainBlockList({ offset, limit });
    const data = Array.isArray(page) ? page : page?.data || [];
    for (const row of data) {
      const v = (row.email_or_domain || row.domain || row.email || "").trim().toLowerCase();
      if (v) entries.add(v);
    }
    if (data.length < limit) break;
    offset += limit;
  }
  return entries;
}

function csvCell(v) {
  const s = String(v ?? "");
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}

async function main() {
  const emails = readEmails(inputPath);
  const wanted = new Set(emails);
  console.log(`Checking ${emails.length} unique email(s) against Smartlead...`);

  // email -> { campaigns:Set, bounced:Set, spam:Set, unsubscribed:Set, dnc:Set, categories:Set }
  const found = new Map();
  const campaigns = await client.listCampaigns();
  let failedCampaigns = 0;

  for (const c of campaigns) {
    let stats;
    try {
      stats = await fetchAllStats(c.id);
    } catch (err) {
      failedCampaigns += 1;
      console.warn(`WARN: ${c.name} (${c.id}): could not fetch statistics, ${err.message}`);
      continue;
    }
    for (const s of stats) {
      const email = (s.lead_email || "").trim().toLowerCase();
      if (!wanted.has(email)) continue;
      if (!found.has(email)) {
        found.set(email, { campaigns: new Set(), bounced: new Set(), spam: new Set(), unsubscribed: new Set(), dnc: new Set(), categories: new Set() });
      }
      const f = found.get(email);
      const category = (s.lead_category || "").trim();
      f.campaigns.add(c.name);
      if (category) f.categories.add(category);
      if (s.is_bounced || /bounce/i.test(category)) f.bounced.add(c.name);
      if (/spam/i.test(category)) f.spam.add(c.name);
      if (s.is_unsubscribed) f.unsubscribed.add(c.name);
      if (/do not contact/i.test(category)) f.dnc.add(c.name);
    }
  }

  let blockList = new Set();
  try {
    blockList = await fetchBlockList();
  } catch (err) {
    console.warn(`WARN: could not fetch the global block list, ${err.message}`);
  }

  const counts = {};
  const lines = ["email,smartlead_status,do_not_use,campaigns,detail"];
  for (const email of emails) {
    const f = found.get(email);
    const domain = email.split("@")[1];
    const blocked = blockList.has(email) || blockList.has(domain);
    let status;
    const detail = [];
    if (f?.bounced.size) {
      status = "Bounced";
      detail.push(`bounced in: ${[...f.bounced].join("; ")}`);
    } else if (f?.spam.size) {
      status = "Spam";
      detail.push(`marked spam in: ${[...f.spam].join("; ")}`);
    } else if (blocked) {
      status = "Blocklisted";
    } else if (f?.dnc.size) {
      status = "Do Not Contact";
    } else if (f?.unsubscribed.size) {
      status = "Unsubscribed";
    } else if (f) {
      status = "OK";
    } else {
      status = "Not in Smartlead";
    }
    if (blocked && status !== "Blocklisted") detail.push(blockList.has(email) ? "email on block list" : "domain on block list");
    if (f?.categories.size) detail.push(`categories: ${[...f.categories].join("; ")}`);
    counts[status] = (counts[status] || 0) + 1;
    const doNotUse = ["Bounced", "Spam", "Blocklisted", "Do Not Contact", "Unsubscribed"].includes(status) ? "Yes" : "No";
    lines.push([email, status, doNotUse, f ? [...f.campaigns].join("; ") : "", detail.join(" | ")].map(csvCell).join(","));
  }

  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, lines.join("\n") + "\n");
  console.log(`Scanned ${campaigns.length} campaign(s)${failedCampaigns ? `, ${failedCampaigns} failed` : ""}.`);
  console.log(Object.entries(counts).map(([k, v]) => `${k}: ${v}`).join(", "));
  console.log(`Wrote ${outPath}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
