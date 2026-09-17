#!/usr/bin/env node
/**
 * Splices the committed dashboard template + page JS with a data JSON file
 * into the final self-contained Command Center HTML.
 *
 * Usage:
 *   node scripts/build-command-center-html.mjs <dashboard-data.json> <output.html>
 */

import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const scriptsDir = path.dirname(fileURLToPath(import.meta.url));
const [, , dataPath, outPath] = process.argv;
if (!dataPath || !outPath) {
  console.error("Usage: node scripts/build-command-center-html.mjs <dashboard-data.json> <output.html>");
  process.exit(1);
}

const template = readFileSync(path.join(scriptsDir, "command-center-template.html"), "utf8");
const pageJs = readFileSync(path.join(scriptsDir, "command-center-page.js"), "utf8");
const data = JSON.parse(readFileSync(dataPath, "utf8"));

const out = template
  .replace("__PAGE_JS__", pageJs)
  .replace("__DATA_JSON__", JSON.stringify(data));

writeFileSync(outPath, out);
console.log(`Wrote ${outPath} (${out.length} bytes)`);
