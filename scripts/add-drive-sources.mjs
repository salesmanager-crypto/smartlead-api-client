import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { GoogleDriveClient } from "../src/google-drive-client.js";
import { GoogleSheetsClient, extractSpreadsheetId } from "../src/google-sheets-client.js";
import { buildDedupedTab } from "../src/master-list.js";

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

// Adds one or more additional Drive files as new source tabs on an existing campaign
// spreadsheet (one built by scripts/new-campaign-sheet.mjs, or anything with a
// "Master List of <name>" tab), then rebuilds that master tab as the de-duplicated
// union of every other tab in the spreadsheet. Handles native Google Sheets and
// .xlsx files alike (the latter get auto-converted to Sheets first).
//
// Usage:
//   node scripts/add-drive-sources.mjs <spreadsheetUrlOrId> <driveFolderId> "<file name filter or URL/ID>" [more...]
const [spreadsheetArg, driveFolderId, ...fileArgs] = process.argv.slice(2);
if (!spreadsheetArg || !driveFolderId || fileArgs.length === 0) {
  console.error(
    'Usage: node scripts/add-drive-sources.mjs <spreadsheetUrlOrId> <driveFolderId> "<file name filter or URL/ID>" [more...]'
  );
  process.exit(1);
}

const spreadsheetId = extractSpreadsheetId(spreadsheetArg);
const drive = new GoogleDriveClient({});
const sheets = new GoogleSheetsClient({});

const SHEET_MIME = "application/vnd.google-apps.spreadsheet";

function uniqueTitle(base, existingTitles) {
  if (!existingTitles.has(base)) return base;
  let n = 2;
  while (existingTitles.has(`${base} (${n})`)) n++;
  return `${base} (${n})`;
}

const meta = await sheets.getSpreadsheet(spreadsheetId, { fields: "sheets.properties" });
const masterTab = meta.sheets.find((s) => s.properties.title.startsWith("Master List of "));
if (!masterTab) {
  console.error('No tab titled "Master List of ..." found — build the sheet with scripts/new-campaign-sheet.mjs first.');
  process.exit(1);
}
const existingTitles = new Set(meta.sheets.map((s) => s.properties.title));
console.error(`Master tab: "${masterTab.properties.title}". Existing tabs: ${[...existingTitles].join(", ")}`);

const tempCopies = [];
const addedTabs = [];

for (const fileArg of fileArgs) {
  let driveFile;
  if (/^https?:\/\//.test(fileArg) || /^[a-zA-Z0-9-_]{15,}$/.test(fileArg)) {
    driveFile = await drive.getFile(extractSpreadsheetId(fileArg), { fields: "id,name,mimeType" });
  } else {
    console.error(`Searching Drive folder ${driveFolderId} for a file matching "${fileArg}"...`);
    const escaped = fileArg.replace(/'/g, "\\'");
    const res = await drive.listFiles({
      query: `'${driveFolderId}' in parents and name contains '${escaped}'`,
      fields: "files(id,name,mimeType)",
    });
    if (!res.files || res.files.length === 0) {
      console.error(`No file matching "${fileArg}" found in that folder — skipping.`);
      continue;
    }
    driveFile = res.files[0];
    if (res.files.length > 1) {
      console.error(`Multiple matches for "${fileArg}", using the first: ${res.files.map((f) => f.name).join(", ")}`);
    }
  }
  console.error(`Found "${driveFile.name}" (${driveFile.mimeType})`);

  let sourceSpreadsheetId = driveFile.id;
  if (driveFile.mimeType !== SHEET_MIME) {
    console.error(`  Not a native Google Sheet — converting a copy...`);
    const converted = await drive.copyFile(driveFile.id, { name: `${driveFile.name} (converted)`, mimeType: SHEET_MIME });
    sourceSpreadsheetId = converted.id;
    tempCopies.push(converted.id);
  }

  const sourceMeta = await sheets.getSpreadsheet(sourceSpreadsheetId, { fields: "sheets.properties" });
  const sourceSheet = sourceMeta.sheets[0];
  const copied = await sheets.copySheetTo(sourceSpreadsheetId, sourceSheet.properties.sheetId, spreadsheetId);

  const newTitle = uniqueTitle(driveFile.name.trim(), existingTitles);
  existingTitles.add(newTitle);
  await sheets.updateSheetProperties(spreadsheetId, copied.sheetId, { title: newTitle });
  console.error(`  Added as tab "${newTitle}".`);
  addedTabs.push(newTitle);
}

for (const id of tempCopies) {
  await drive.deleteFile(id).catch((err) => console.error(`  (couldn't clean up temp copy ${id}: ${err.message})`));
}

if (addedTabs.length === 0) {
  console.error("No new tabs were added — nothing to rebuild.");
  process.exit(1);
}

// Keep the master tab last, then rebuild it from every other tab in the spreadsheet.
const refreshedMeta = await sheets.getSpreadsheet(spreadsheetId, { fields: "sheets.properties" });
const allTitles = refreshedMeta.sheets.map((s) => s.properties.title);
await sheets.updateSheetProperties(spreadsheetId, masterTab.properties.sheetId, { index: allTitles.length - 1 });

const sourceTitles = allTitles.filter((t) => t !== masterTab.properties.title);
const result = await buildDedupedTab(sheets, spreadsheetId, { sourceTitles, targetTitle: masterTab.properties.title });

console.error(
  `\n"${masterTab.properties.title}" rebuilt from [${sourceTitles.join(", ")}]: ` +
    `${result.sources.map((s) => `${s.rows} (${s.title})`).join(" + ")} -> ${result.target.rows} unique ` +
    `(${result.duplicatesRemoved} duplicate(s) removed).`
);

const url = `https://docs.google.com/spreadsheets/d/${spreadsheetId}/edit`;
console.log(JSON.stringify({ spreadsheetId, url, addedTabs, ...result }, null, 2));
