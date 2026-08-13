import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { GoogleSheetsClient, extractSpreadsheetId } from "../src/google-sheets-client.js";
import { buildMasterList } from "../src/master-list.js";

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

// Usage:
//   node scripts/build-master-list.mjs <spreadsheetUrlOrId> ["<campaign name>"]
// With a campaign name given, the 3rd tab is renamed to "Master List of <campaign name>".
const [spreadsheetArg, campaignName] = process.argv.slice(2);
if (!spreadsheetArg) {
  console.error('Usage: node scripts/build-master-list.mjs <spreadsheetUrlOrId> ["<campaign name>"]');
  process.exit(1);
}

const spreadsheetId = extractSpreadsheetId(spreadsheetArg);
const sheets = new GoogleSheetsClient({});

const result = await buildMasterList(sheets, spreadsheetId);

if (campaignName) {
  const titleCased = campaignName
    .trim()
    .replace(/\s+/g, " ")
    .replace(/\w\S*/g, (w) => w[0].toUpperCase() + w.slice(1).toLowerCase());
  const masterTitle = `Master List of ${titleCased}`;
  const meta = await sheets.getSpreadsheet(spreadsheetId, { fields: "sheets.properties" });
  const tab3 = meta.sheets.find((s) => s.properties.title === result.tab3.title);
  await sheets.updateSheetProperties(spreadsheetId, tab3.properties.sheetId, { title: masterTitle });
  result.tab3.title = masterTitle;
}

console.error(
  `Tab 1: "${result.tab1.title}" (${result.tab1.rows}) + Tab 2: "${result.tab2.title}" (${result.tab2.rows}) ` +
    `-> "${result.tab3.title}" (${result.tab3.rows} unique, ${result.duplicatesRemoved} duplicate(s) removed)`
);
console.log(JSON.stringify({ spreadsheetId, ...result }, null, 2));
