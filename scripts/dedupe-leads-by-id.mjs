import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parseCSV } from "../src/csv.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

// De-duplicates a merged leads CSV (e.g. from export-all-leads-csv.mjs) by Smartlead's
// own lead `id` column — NOT by email. A lead is Smartlead's real unit of identity;
// the same email can legitimately appear on more than one lead record (re-added over
// time, etc.), so deduping by email undercounts vs. Smartlead's own "total contacts".
// Keeps the first campaign membership row seen for each lead id.
//
// Usage:
//   node scripts/dedupe-leads-by-id.mjs <inputCsvPath> [outputCsvPath]
const [inputArg, outputArg] = process.argv.slice(2);
if (!inputArg) {
  console.error("Usage: node scripts/dedupe-leads-by-id.mjs <inputCsvPath> [outputCsvPath]");
  process.exit(1);
}

const inputPath = path.resolve(process.cwd(), inputArg);
const text = fs.readFileSync(inputPath, "utf8");
const rows = parseCSV(text);
if (rows.length === 0) {
  console.error("Input CSV is empty.");
  process.exit(1);
}

const [header, ...dataRows] = rows;
const idCol = header.indexOf("id");
if (idCol === -1) {
  console.error(`No "id" column found in the header: ${header.join(", ")}`);
  process.exit(1);
}

const seen = new Set();
const deduped = [];
let duplicates = 0;
for (const row of dataRows) {
  const id = row[idCol];
  if (id && seen.has(id)) {
    duplicates++;
    continue;
  }
  if (id) seen.add(id);
  deduped.push(row);
}

const emailCol = header.indexOf("email");
const uniqueEmails = emailCol >= 0 ? new Set(deduped.map((r) => (r[emailCol] || "").trim().toLowerCase()).filter(Boolean)).size : null;

const outputPath = path.resolve(process.cwd(), outputArg || inputPath.replace(/\.csv$/i, "-deduped-by-id.csv"));
const csvContent = [header, ...deduped].map((r) => r.map(csvEscape).join(",")).join("\n") + "\n";
fs.writeFileSync(outputPath, csvContent, "utf8");

console.error(
  `${dataRows.length} row(s) -> ${deduped.length} unique lead id(s) (${duplicates} duplicate membership row(s) removed)` +
    (uniqueEmails !== null ? `, ${uniqueEmails} unique email(s) among them` : "")
);
console.error(`Wrote ${outputPath}`);

function csvEscape(field) {
  const s = String(field ?? "");
  return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
}
