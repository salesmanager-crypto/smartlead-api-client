#!/usr/bin/env node
/**
 * Records a source refreshed outside the GitHub workflow (by the daily Claude task)
 * in docs/data/manifest.json, and updates today's history file to match.
 *
 *   node scripts/pull/record.mjs smartscout ok            # after writing smartscout.json
 *   node scripts/pull/record.mjs smartscout error "why"   # when the pull failed
 *   node scripts/pull/record.mjs tradeshowNotes ok        # after writing tradeshow_notes.json
 *
 * Sources: smartscout, semrush, tradeshowNotes. `tradeshowNotes` only stamps
 * tradeshow_notes.json's updatedAt; it has no manifest entry.
 */
import path from "node:path";
import fs from "node:fs";
import { DATA_DIR, readJson, today as todayFn } from "./lib.mjs";
import { readManifest, recordAttempt, saveManifest, writeJsonFile, HISTORY_DIR } from "./write.mjs";

const [source, outcome, ...rest] = process.argv.slice(2);
const now = new Date().toISOString();
if (!["smartscout", "semrush", "tradeshowNotes"].includes(source) || !["ok", "error"].includes(outcome)) {
  console.error("usage: node scripts/pull/record.mjs <smartscout|semrush|tradeshowNotes> <ok|error> [message]");
  process.exit(2);
}

if (source === "tradeshowNotes") {
  const file = path.join(DATA_DIR, "tradeshow_notes.json");
  const doc = readJson(file, { people: ["Yoni", "Maria", "Rachel"], notes: {} });
  doc.updatedAt = now;
  writeJsonFile(file, doc);
  console.error(`tradeshow_notes.json stamped ${now} (${Object.keys(doc.notes || {}).length} shows with notes)`);
  process.exit(0);
}

const file = path.join(DATA_DIR, `${source}.json`);
const data = readJson(file);
let records = null;
if (outcome === "ok") {
  if (!data) { console.error(`${source}.json is missing or not valid JSON; not recording success`); process.exit(1); }
  records = source === "smartscout" ? (data.brands || []).length : (data.keywords || []).length;
}
const manifest = readManifest();
const entry = recordAttempt(manifest, source, outcome === "ok"
  ? { ok: true, records, note: source === "smartscout" ? `${(data.brands || []).filter((b) => b.error).length} not found` : null }
  : { ok: false, error: (rest.join(" ") || "failed").slice(0, 300) }, now);
saveManifest(manifest, { generatedAt: manifest.generatedAt || now, today: manifest.today || todayFn() });

// today's history: the SmartScout watchlist revenue total
if (source === "smartscout" && outcome === "ok") {
  const hfile = path.join(HISTORY_DIR, `${todayFn()}.json`);
  const h = readJson(hfile, { date: todayFn(), generatedAt: now, sent: null, replies: null, interested: null, overdue: null, dealsOpen: null, linkedinAccepted: null });
  const rev = (data.brands || []).map((b) => b.monthlyRevenue).filter((v) => typeof v === "number");
  h.smartscoutWatchlistRevenue = rev.length ? Math.round(rev.reduce((a, b) => a + b, 0) * 100) / 100 : null;
  fs.mkdirSync(HISTORY_DIR, { recursive: true });
  writeJsonFile(hfile, h);
}
console.error(`${source}: ${entry.status}${entry.error ? " (" + entry.error + ")" : ""}, last success ${entry.lastSuccess || "never"}`);
