import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { GoogleSheetsClient, extractSpreadsheetId } from "../src/google-sheets-client.js";

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

// Copies a tab from a source spreadsheet into a target spreadsheet as a new tab
// ("Tab 2"), then writes a de-duplicated (by contact) copy of it into another new
// tab ("Tab 3").
//
// Usage:
//   node scripts/merge-and-dedupe-sheet.mjs <targetSpreadsheetUrlOrId> <sourceSpreadsheetUrlOrId> [sourceTabName]
const [targetArg, sourceArg, sourceTabName] = process.argv.slice(2);
if (!targetArg || !sourceArg) {
  console.error(
    "Usage: node scripts/merge-and-dedupe-sheet.mjs <targetSpreadsheetUrlOrId> <sourceSpreadsheetUrlOrId> [sourceTabName]"
  );
  process.exit(1);
}

const targetId = extractSpreadsheetId(targetArg);
const sourceId = extractSpreadsheetId(sourceArg);

const sheets = new GoogleSheetsClient({});

console.error(`Reading source spreadsheet ${sourceId}...`);
const sourceMeta = await sheets.getSpreadsheet(sourceId, { fields: "sheets.properties" });
const sourceSheet = sourceTabName
  ? sourceMeta.sheets.find((s) => s.properties.title === sourceTabName)
  : sourceMeta.sheets[0];
if (!sourceSheet) {
  console.error(
    `Couldn't find a tab${sourceTabName ? ` named "${sourceTabName}"` : ""} in the source spreadsheet. Tabs available:`
  );
  for (const s of sourceMeta.sheets) console.error(`  ${s.properties.title}`);
  process.exit(1);
}
console.error(`Copying tab "${sourceSheet.properties.title}" into the target spreadsheet...`);

const targetMeta = await sheets.getSpreadsheet(targetId, { fields: "sheets.properties" });
const existingTitles = new Set(targetMeta.sheets.map((s) => s.properties.title));

const copied = await sheets.copySheetTo(sourceId, sourceSheet.properties.sheetId, targetId);
const tab2Title = uniqueTitle("Tab 2", existingTitles);
await sheets.updateSheetProperties(targetId, copied.sheetId, { title: tab2Title, index: 1 });
console.error(`Created "${tab2Title}" (copied from source).`);

console.error(`Reading values back from "${tab2Title}" to de-duplicate...`);
const rows = await sheets.getValues(targetId, tab2Title);
if (rows.length === 0) {
  console.error("Tab 2 came back empty — nothing to de-duplicate.");
  process.exit(1);
}

const [header, ...dataRows] = rows;
const contactCol = findContactColumn(header);
console.error(
  contactCol >= 0
    ? `De-duplicating on column "${header[contactCol]}" (index ${contactCol}).`
    : "No email/phone/contact column found in the header — de-duplicating on the full row instead."
);

const seen = new Set();
const deduped = [];
let duplicates = 0;
for (const row of dataRows) {
  const key = contactCol >= 0 ? (row[contactCol] || "").trim().toLowerCase() : JSON.stringify(row);
  if (key && seen.has(key)) {
    duplicates++;
    continue;
  }
  if (key) seen.add(key);
  deduped.push(row);
}

console.error(`${dataRows.length} row(s) in Tab 2 -> ${deduped.length} unique (${duplicates} duplicate(s) removed).`);

const tab3Title = uniqueTitle("Tab 3", new Set([...existingTitles, tab2Title]));
const tab3 = await sheets.addSheet(targetId, { title: tab3Title, index: 2 });
await sheets.updateValues(targetId, tab3Title, [header, ...deduped]);
console.error(`Wrote de-duplicated list to "${tab3Title}".`);

console.log(
  JSON.stringify(
    {
      targetSpreadsheetId: targetId,
      tab2: { title: tab2Title, sheetId: copied.sheetId, rows: dataRows.length },
      tab3: { title: tab3Title, sheetId: tab3.sheetId, rows: deduped.length, duplicatesRemoved: duplicates },
      dedupeColumn: contactCol >= 0 ? header[contactCol] : null,
    },
    null,
    2
  )
);

function findContactColumn(header) {
  const patterns = [/^email$/i, /email/i, /^phone/i, /^contact/i];
  for (const pattern of patterns) {
    const idx = header.findIndex((h) => pattern.test((h || "").trim()));
    if (idx >= 0) return idx;
  }
  return -1;
}

function uniqueTitle(base, existingTitles) {
  if (!existingTitles.has(base)) return base;
  let n = 2;
  while (existingTitles.has(`${base} (${n})`)) n++;
  return `${base} (${n})`;
}
