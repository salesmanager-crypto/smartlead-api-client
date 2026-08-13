import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import { GoogleDriveClient } from "../src/google-drive-client.js";
import { GoogleSheetsClient, extractSpreadsheetId } from "../src/google-sheets-client.js";
import { buildMasterList, buildDedupedTab } from "../src/master-list.js";
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

// Full "fancy food"-style pipeline for a new campaign, from scratch:
//   1. Export matching Smartlead campaigns' leads into a merged CSV.
//   2. Find the matching lead file in a Drive folder (by name, or pass a direct URL/ID).
//      Pass "none" for <drive file> to skip this step (no matching file on Drive) —
//      Tab 2 then becomes the de-duplicated list of Tab 1 alone.
//   3. Create a brand-new spreadsheet with: Tab 1 = Smartlead export, Tab 2 = copy of the
//      Drive file's first tab (if any), Tab 3 = de-duplicated master list combining both
//      (or, with no Drive file, Tab 2 IS the de-duplicated master list).
//
// Usage:
//   node scripts/new-campaign-sheet.mjs "<campaign name filter>" "<drive file name filter or URL/ID>" <driveFolderId> ["<spreadsheet title>"]
//   node scripts/new-campaign-sheet.mjs "<campaign name filter>" none ["<spreadsheet title>"]
const [campaignFilter, driveFileArg, ...rest] = process.argv.slice(2);
const skipDrive = driveFileArg === "none";
const [driveFolderId, titleArgIfDrive] = rest;
const titleArg = skipDrive ? rest[0] : titleArgIfDrive;
if (!campaignFilter || !driveFileArg || (!skipDrive && !driveFolderId)) {
  console.error(
    'Usage: node scripts/new-campaign-sheet.mjs "<campaign name filter>" "<drive file name filter or URL/ID>" <driveFolderId> ["<spreadsheet title>"]\n' +
      '   or: node scripts/new-campaign-sheet.mjs "<campaign name filter>" none ["<spreadsheet title>"]'
  );
  process.exit(1);
}

const smartlead = new SmartleadClient({});
const drive = new GoogleDriveClient({});
const sheets = new GoogleSheetsClient({});

// --- 1. Export matching Smartlead campaigns -------------------------------------------------
console.error(`Finding Smartlead campaigns matching "${campaignFilter}"...`);
const campaigns = await smartlead.listCampaigns();
const needle = campaignFilter.toLowerCase();
const matches = campaigns.filter((c) => (c.name || "").toLowerCase().includes(needle));
if (matches.length === 0) {
  console.error(`No campaigns found matching "${campaignFilter}".`);
  process.exit(1);
}
console.error(`Found ${matches.length} matching campaign(s):`);
for (const c of matches) console.error(`  #${c.id}  ${c.name}  (${c.status})`);

let leadsHeader = null;
const leadsRows = [];
const exportErrors = [];
for (const c of matches) {
  try {
    const csv = await smartlead.exportCampaignLeads(c.id);
    const text = typeof csv === "string" ? csv : JSON.stringify(csv);
    const parsed = parseCSV(text);
    if (parsed.length === 0) continue;
    const [header, ...rows] = parsed;
    if (!leadsHeader) leadsHeader = ["campaign_id", "campaign_name", ...header];
    for (const row of rows) leadsRows.push([String(c.id), c.name || "", ...row]);
  } catch (err) {
    exportErrors.push({ campaignId: c.id, campaignName: c.name, error: err.message });
  }
}
if (!leadsHeader) {
  console.error("No lead rows were returned for the matching campaign(s).");
  if (exportErrors.length) console.error(JSON.stringify(exportErrors, null, 2));
  process.exit(1);
}
console.error(`Exported ${leadsRows.length} lead row(s) from ${matches.length} campaign(s).`);
if (exportErrors.length) console.error(`${exportErrors.length} campaign(s) failed:`, JSON.stringify(exportErrors));

// --- 2. Find (or accept) the Drive file -----------------------------------------------------
let driveFile = null;
if (!skipDrive) {
  if (/^https?:\/\//.test(driveFileArg) || /^[a-zA-Z0-9-_]{15,}$/.test(driveFileArg)) {
    const fileId = extractSpreadsheetId(driveFileArg);
    driveFile = await drive.getFile(fileId, { fields: "id,name,mimeType" });
  } else {
    console.error(`Searching Drive folder ${driveFolderId} for a file matching "${driveFileArg}"...`);
    const escaped = driveFileArg.replace(/'/g, "\\'");
    const res = await drive.listFiles({
      query: `'${driveFolderId}' in parents and name contains '${escaped}'`,
      fields: "files(id,name,mimeType)",
    });
    if (!res.files || res.files.length === 0) {
      console.error(`No file matching "${driveFileArg}" found in that folder.`);
      process.exit(1);
    }
    driveFile = res.files[0];
    if (res.files.length > 1) {
      console.error(`Multiple matches, using the first: ${res.files.map((f) => f.name).join(", ")}`);
    }
  }
  if (driveFile.mimeType !== "application/vnd.google-apps.spreadsheet") {
    console.error(`"${driveFile.name}" isn't a Google Sheet (${driveFile.mimeType}) — this script only merges Sheets tabs.`);
    process.exit(1);
  }
  console.error(`Using Drive file: "${driveFile.name}" (${driveFile.id})`);
} else {
  console.error("Skipping Drive merge (none) — Tab 2 will be the de-duplicated Tab 1 list.");
}

// --- 3. Build the new spreadsheet ------------------------------------------------------------
const slug = campaignFilter.trim().replace(/\s+/g, " ");
const titleCased = slug.replace(/\w\S*/g, (w) => w[0].toUpperCase() + w.slice(1).toLowerCase());
const title = titleArg || `${titleCased} Leads`;
console.error(`Creating spreadsheet "${title}"...`);
const created = await sheets.createSpreadsheet(title);
const spreadsheetId = created.spreadsheetId;
const tab1SheetId = created.sheets[0].properties.sheetId;
const tab1Title = `${slug.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "")}-leads`;

await sheets.updateSheetProperties(spreadsheetId, tab1SheetId, { title: tab1Title });
await sheets.updateValues(spreadsheetId, tab1Title, [leadsHeader, ...leadsRows]);
console.error(`Wrote ${leadsRows.length} row(s) to Tab 1 ("${tab1Title}").`);

let result;
if (driveFile) {
  const sourceMeta = await sheets.getSpreadsheet(driveFile.id, { fields: "sheets.properties" });
  const sourceSheet = sourceMeta.sheets[0];
  const copied = await sheets.copySheetTo(driveFile.id, sourceSheet.properties.sheetId, spreadsheetId);
  await sheets.updateSheetProperties(spreadsheetId, copied.sheetId, { title: "Tab 2", index: 1 });
  console.error(`Copied "${sourceSheet.properties.title}" from "${driveFile.name}" into Tab 2.`);

  await sheets.addSheet(spreadsheetId, { title: "Tab 3", index: 2 });
  result = await buildMasterList(sheets, spreadsheetId);
  console.error(
    `Tab 3 master list: ${result.tab1.rows} (Tab 1) + ${result.tab2.rows} (Tab 2) -> ${result.tab3.rows} unique ` +
      `(${result.duplicatesRemoved} duplicate(s) removed).`
  );
} else {
  // No Drive file to merge — Tab 2 is just the de-duplicated Tab 1 list.
  await sheets.addSheet(spreadsheetId, { title: "Tab 2", index: 1 });
  const deduped = await buildDedupedTab(sheets, spreadsheetId, { sourceTitles: [tab1Title], targetTitle: "Tab 2" });
  result = { tab1: deduped.sources[0], tab2: deduped.target, duplicatesRemoved: deduped.duplicatesRemoved };
  console.error(
    `Tab 2 de-duplicated list: ${result.tab1.rows} (Tab 1) -> ${result.tab2.rows} unique ` +
      `(${result.duplicatesRemoved} duplicate(s) removed).`
  );
}

const url = `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`;
console.error(`\nDone: ${url}`);
console.log(JSON.stringify({ spreadsheetId, url, title, tab1Title, ...result }, null, 2));
