#!/usr/bin/env node
// Pulls everything the command center needs from Pipedrive over REST and writes the raw
// responses under dashboards/pull/out/pipedrive/ in the exact files build-constants.mjs reads.
// Needs PIPEDRIVE_API_TOKEN in the environment or .env. Without it, save the Pipedrive
// connector responses to the same files by hand (see scripts/scheduled-command-center-refresh-prompt.md).

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { PipedriveClient } from "../../src/pipedrive.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const outDir = path.join(here, "out", "pipedrive");

const envPath = path.join(root, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim(); if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("="); if (eq === -1) continue;
    const k = t.slice(0, eq).trim(), v = t.slice(eq + 1).trim();
    if (!(k in process.env)) process.env[k] = v;
  }
}
if (!process.env.PIPEDRIVE_API_TOKEN) { console.error("PIPEDRIVE_API_TOKEN is not set"); process.exit(2); }

// start clean so a shorter pull never leaves stale pages behind
fs.rmSync(outDir, { recursive: true, force: true });
fs.mkdirSync(outDir, { recursive: true });
const write = (name, obj) => fs.writeFileSync(path.join(outDir, name + ".json"), JSON.stringify(obj));
const log = (...a) => console.error(new Date().toISOString().slice(11, 19), ...a);
const pd = new PipedriveClient({});

const acts = await pd.activities({ done: 0 });
acts.forEach((p, i) => write("activities-" + (i + 1), p));
log("activities pages", acts.length, "rows", acts.reduce((n, p) => n + (p.data || []).length, 0));

for (const status of ["open", "won", "lost"]) {
  const pages = await pd.deals({ status, limit: 100 });
  write("deals-" + status, { success: true, data: pages.flatMap((p) => p.data || []), additional_data: { next_cursor: null } });
}
write("stages", await pd.stages());

const leads = await pd.leads({ limit: 500 });
leads.forEach((p, i) => write("leads-" + (i + 1), p));
log("leads pages", leads.length, "rows", leads.reduce((n, p) => n + (p.data || []).length, 0));

const persons = await pd.persons();
persons.forEach((p, i) => write("persons-" + (i + 1), p));
log("persons pages", persons.length, "rows", persons.reduce((n, p) => n + (p.data || []).length, 0));

const orgs = await pd.organizations();
orgs.forEach((p, i) => write("orgs-" + (i + 1), p));
log("orgs pages", orgs.length, "rows", orgs.reduce((n, p) => n + (p.data || []).length, 0));
log("written", outDir);
