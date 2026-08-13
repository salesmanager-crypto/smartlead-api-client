import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import { GoogleDriveClient } from "../src/google-drive-client.js";

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

// Finds every campaign whose name contains the given text (case-insensitive),
// merges their lead exports into one CSV, and uploads it straight to Google Drive.
//
// Usage:
//   node scripts/export-and-upload.mjs "fancy food" [driveFolderId] [localOutputPath]
const [nameFilter, driveFolderId, outputArg] = process.argv.slice(2);
if (!nameFilter) {
  console.error(
    'Usage: node scripts/export-and-upload.mjs "<campaign name filter>" [driveFolderId] [localOutputPath]'
  );
  process.exit(1);
}

const smartlead = new SmartleadClient({});
const campaigns = await smartlead.listCampaigns();

const needle = nameFilter.toLowerCase();
const matches = campaigns.filter((c) => (c.name || "").toLowerCase().includes(needle));

if (matches.length === 0) {
  console.error(`No campaigns found matching "${nameFilter}". Available campaigns:`);
  for (const c of campaigns) console.error(`  #${c.id}  ${c.name}`);
  process.exit(1);
}

console.error(`Found ${matches.length} matching campaign(s):`);
for (const c of matches) console.error(`  #${c.id}  ${c.name}  (${c.status})`);

const rows = [];
let header = null;
const errors = [];

for (const c of matches) {
  try {
    const csv = await smartlead.exportCampaignLeads(c.id);
    const text = typeof csv === "string" ? csv : JSON.stringify(csv);
    const lines = text.split(/\r?\n/).filter((l) => l.length > 0);
    if (lines.length === 0) continue;

    const [csvHeader, ...csvRows] = lines;
    if (!header) header = `campaign_id,campaign_name,${csvHeader}`;

    for (const row of csvRows) {
      rows.push(`${c.id},"${(c.name || "").replace(/"/g, '""')}",${row}`);
    }
  } catch (err) {
    errors.push({ campaignId: c.id, campaignName: c.name, error: err.message, status: err.status });
  }
}

if (!header) {
  console.error("No lead rows were returned for the matching campaign(s).");
  if (errors.length) console.error(JSON.stringify(errors, null, 2));
  process.exit(1);
}

const slug = nameFilter.trim().toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
const outputPath = path.resolve(projectRoot, outputArg || `exports/${slug}-leads.csv`);
const csvContent = [header, ...rows].join("\n") + "\n";
fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, csvContent, "utf8");
console.error(`Wrote ${rows.length} lead row(s) from ${matches.length} campaign(s) to ${outputPath}`);
if (errors.length) {
  console.error(`${errors.length} campaign(s) failed to export:`);
  console.error(JSON.stringify(errors, null, 2));
}

console.error("Uploading to Google Drive...");
const drive = new GoogleDriveClient({});
const uploaded = await drive.uploadFile({
  content: csvContent,
  name: path.basename(outputPath),
  folderId: driveFolderId,
});

console.error(`Uploaded: ${uploaded.webViewLink || uploaded.id}`);
console.log(JSON.stringify({ localPath: outputPath, rows: rows.length, campaigns: matches.length, errors, drive: uploaded }, null, 2));
