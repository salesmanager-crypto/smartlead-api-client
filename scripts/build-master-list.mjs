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

// Combines the 1st and 2nd tabs of a spreadsheet (by position, regardless of their
// titles/column layouts) into a normalized contact schema, de-duplicates by email,
// and overwrites the 3rd tab with the result — a master list built from both sources.
//
// Usage:
//   node scripts/build-master-list.mjs <spreadsheetUrlOrId>
const [spreadsheetArg] = process.argv.slice(2);
if (!spreadsheetArg) {
  console.error("Usage: node scripts/build-master-list.mjs <spreadsheetUrlOrId>");
  process.exit(1);
}

const spreadsheetId = extractSpreadsheetId(spreadsheetArg);
const sheets = new GoogleSheetsClient({});

const meta = await sheets.getSpreadsheet(spreadsheetId, { fields: "sheets.properties" });
const byIndex = meta.sheets.sort((a, b) => a.properties.index - b.properties.index);
if (byIndex.length < 3) {
  console.error(`Expected at least 3 tabs, found ${byIndex.length}: ${byIndex.map((s) => s.properties.title).join(", ")}`);
  process.exit(1);
}
const [tab1, tab2, tab3] = byIndex;
console.error(`Tab 1: "${tab1.properties.title}"   Tab 2: "${tab2.properties.title}"   Tab 3 (target): "${tab3.properties.title}"`);

// Normalized master schema — every source row gets mapped into this shape.
const MASTER_COLUMNS = ["First Name", "Last Name", "Email", "Phone", "Company", "Website", "Title", "Source", "Status"];
const ALIASES = {
  "First Name": ["first_name", "first name", "firstname"],
  "Last Name": ["last_name", "last name", "lastname"],
  Email: ["email", "email address"],
  Phone: ["phone_number", "phone", "phone number"],
  Company: ["company_name", "company", "company / account", "company/account"],
  Website: ["website", "site", "url"],
  Title: ["title", "job_title", "job title"],
  Source: ["source", "campaign_name", "campaign"],
  Status: ["status", "lead_status", "lead status", "category"],
};

function normalizeKey(h) {
  return (h || "").trim().toLowerCase();
}

function buildColumnMap(header) {
  const normalized = header.map(normalizeKey);
  const map = {};
  for (const [masterCol, aliases] of Object.entries(ALIASES)) {
    const idx = normalized.findIndex((h) => aliases.includes(h));
    if (idx >= 0) map[masterCol] = idx;
  }
  return map;
}

function normalizeRows(header, rows, sourceLabel) {
  const map = buildColumnMap(header);
  return rows.map((row) =>
    MASTER_COLUMNS.map((col) => (col === "Source" && map[col] === undefined ? sourceLabel : row[map[col]] || ""))
  );
}

console.error(`Reading "${tab1.properties.title}" and "${tab2.properties.title}"...`);
const [tab1Values, tab2Values] = await Promise.all([
  sheets.getValues(spreadsheetId, tab1.properties.title),
  sheets.getValues(spreadsheetId, tab2.properties.title),
]);

const [tab1Header, ...tab1Rows] = tab1Values;
const [tab2Header, ...tab2Rows] = tab2Values;

const combined = [
  ...normalizeRows(tab1Header, tab1Rows, tab1.properties.title),
  ...normalizeRows(tab2Header, tab2Rows, tab2.properties.title),
];

const emailCol = MASTER_COLUMNS.indexOf("Email");
const seen = new Set();
const deduped = [];
let duplicates = 0;
for (const row of combined) {
  const key = (row[emailCol] || "").trim().toLowerCase();
  if (key && seen.has(key)) {
    duplicates++;
    continue;
  }
  if (key) seen.add(key);
  deduped.push(row);
}

console.error(
  `${tab1Rows.length} row(s) from "${tab1.properties.title}" + ${tab2Rows.length} row(s) from "${tab2.properties.title}" ` +
    `= ${combined.length} combined -> ${deduped.length} unique by email (${duplicates} duplicate(s) removed).`
);

await sheets.clearValues(spreadsheetId, tab3.properties.title);
await sheets.updateValues(spreadsheetId, tab3.properties.title, [MASTER_COLUMNS, ...deduped]);
console.error(`Wrote master list to "${tab3.properties.title}".`);

console.log(
  JSON.stringify(
    {
      spreadsheetId,
      tab1: { title: tab1.properties.title, rows: tab1Rows.length },
      tab2: { title: tab2.properties.title, rows: tab2Rows.length },
      tab3: { title: tab3.properties.title, rows: deduped.length, duplicatesRemoved: duplicates },
    },
    null,
    2
  )
);
