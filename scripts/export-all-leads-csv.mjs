import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import { parseCSV } from "../src/csv.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

// minimal .env loader (mirrors src/cli.js)
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

// Exports every lead from every campaign in the account (Smartlead has no single
// "list all leads" endpoint — leads-export is per-campaign, so this fans out across
// all of them) into one merged CSV.
//
// Usage:
//   node scripts/export-all-leads-csv.mjs [outputPath]
const [outputArg] = process.argv.slice(2);

const client = new SmartleadClient({});
const campaigns = await client.listCampaigns();
console.error(`Exporting leads from all ${campaigns.length} campaigns...`);

const CONCURRENCY = 8;
let idx = 0;
let done = 0;
let header = null;
const rows = [];
const errors = [];

async function worker() {
  while (idx < campaigns.length) {
    const c = campaigns[idx++];
    try {
      const csv = await client.exportCampaignLeads(c.id);
      const text = typeof csv === "string" ? csv : JSON.stringify(csv);
      const parsed = parseCSV(text);
      if (parsed.length === 0) continue;
      const [csvHeader, ...csvRows] = parsed;
      if (!header) header = ["campaign_id", "campaign_name", ...csvHeader];
      for (const row of csvRows) rows.push([String(c.id), c.name || "", ...row]);
    } catch (err) {
      errors.push({ campaignId: c.id, campaignName: c.name, error: err.message, status: err.status });
    } finally {
      done++;
      if (done % 25 === 0 || done === campaigns.length) {
        console.error(`  ${done}/${campaigns.length} campaigns exported, ${rows.length} lead rows so far`);
      }
    }
  }
}

await Promise.all(Array.from({ length: CONCURRENCY }, worker));

if (!header) {
  console.error("No lead rows were returned from any campaign.");
  if (errors.length) console.error(JSON.stringify(errors, null, 2));
  process.exit(1);
}

const uniqueEmails = new Set(rows.map((r) => (r[header.indexOf("email")] || "").trim().toLowerCase()).filter(Boolean));

const outputPath = path.resolve(projectRoot, outputArg || "exports/all-leads.csv");
const csvContent = [header, ...rows].map((r) => r.map(csvEscape).join(",")).join("\n") + "\n";
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, csvContent, "utf8");

console.error(
  `\nWrote ${rows.length} lead row(s) (${uniqueEmails.size} unique emails) from ${campaigns.length} campaign(s) to ${outputPath}`
);
if (errors.length) {
  console.error(`${errors.length} campaign(s) failed to export:`);
  console.error(JSON.stringify(errors, null, 2));
}

function csvEscape(field) {
  const s = String(field ?? "");
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
