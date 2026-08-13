#!/usr/bin/env node
/**
 * Tiny CLI wrapper around GoogleSheetsClient. No dependencies.
 *
 * Usage:
 *   node src/sheets-cli.js sheets:get <spreadsheetIdOrUrl>
 *   node src/sheets-cli.js sheets:add-tab <spreadsheetIdOrUrl> "<title>" [index]
 *   node src/sheets-cli.js sheets:copy-tab <sourceSpreadsheetIdOrUrl> <sheetId> <destSpreadsheetIdOrUrl>
 *   node src/sheets-cli.js sheets:values-get <spreadsheetIdOrUrl> "<range>"
 *   node src/sheets-cli.js sheets:values-update <spreadsheetIdOrUrl> "<range>" '[["a","b"],["c","d"]]'
 *
 * Reads GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN from the environment.
 * Loads a local .env file automatically if present (no dotenv dependency needed).
 * Run `node scripts/google-drive-auth.mjs` once first to obtain a refresh token.
 */

import fs from "node:fs";
import path from "node:path";
import { GoogleSheetsClient, extractSpreadsheetId } from "./google-sheets-client.js";

loadDotEnv();

const [, , cmd, ...args] = process.argv;

let client;

const commands = {
  "sheets:get": (id) => client.getSpreadsheet(extractSpreadsheetId(id)),
  "sheets:add-tab": (id, title, index) =>
    client.addSheet(extractSpreadsheetId(id), { title, index: index !== undefined ? Number(index) : undefined }),
  "sheets:copy-tab": (sourceId, sheetId, destId) =>
    client.copySheetTo(extractSpreadsheetId(sourceId), Number(sheetId), extractSpreadsheetId(destId)),
  "sheets:values-get": (id, range) => client.getValues(extractSpreadsheetId(id), range),
  "sheets:values-update": (id, range, json) => client.updateValues(extractSpreadsheetId(id), range, JSON.parse(json)),
};

async function main() {
  const fn = commands[cmd];
  if (!fn) {
    console.error(`Unknown or missing command: ${cmd ?? "(none)"}\n`);
    console.error("Available commands:\n  " + Object.keys(commands).join("\n  "));
    process.exit(1);
  }
  try {
    client = new GoogleSheetsClient({});
    const result = await fn(...args);
    console.log(JSON.stringify(result, null, 2));
  } catch (err) {
    console.error(err.message);
    if (err.body) console.error(JSON.stringify(err.body, null, 2));
    process.exit(1);
  }
}

function loadDotEnv() {
  const envPath = path.resolve(process.cwd(), ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const trimmed = line.trim();
    if (!trimmed || trimmed.startsWith("#")) continue;
    const eq = trimmed.indexOf("=");
    if (eq === -1) continue;
    const key = trimmed.slice(0, eq).trim();
    let value = trimmed.slice(eq + 1).trim();
    if (
      (value.startsWith('"') && value.endsWith('"')) ||
      (value.startsWith("'") && value.endsWith("'"))
    ) {
      value = value.slice(1, -1);
    }
    if (!(key in process.env)) process.env[key] = value;
  }
}

main();
