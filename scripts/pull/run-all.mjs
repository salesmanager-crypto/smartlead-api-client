#!/usr/bin/env node
/**
 * Daily dashboard refresh: every source in sequence, the manifest, today's history file.
 *
 *   node scripts/pull/run-all.mjs
 *
 * Reads credentials from the environment or ROOT/.env (see .env.example). One
 * failing source never blocks the others; its failure is recorded in
 * docs/data/manifest.json and shown on both dashboards. Exits non-zero only when
 * every API source failed (SmartLead, Pipedrive, HeyReach, Semrush), which is what
 * makes the GitHub workflow fail and email the repo owner.
 *
 * SmartScout is not pulled here: the Claude scheduled task writes smartscout.json.
 */
import path from "node:path";
import { loadEnv, today as todayFn, readJson, DATA_DIR, ymd } from "./lib.mjs";
import { readManifest, runSource, saveManifest, writeHistory } from "./write.mjs";
import * as pipedrive from "./pipedrive.mjs";
import * as smartlead from "./smartlead.mjs";
import * as heyreach from "./heyreach.mjs";
import * as semrush from "./semrush.mjs";
import * as seoIssues from "./seo-issues.mjs";
import * as tradeshows from "./tradeshows.mjs";

loadEnv();
const env = process.env;
const TODAY = todayFn();
const manifest = readManifest();
const ctx = {}; // shared between sources: pipedrive leaves personByEmail for smartlead

console.error(`dashboard refresh for ${TODAY}`);
const results = {};
results.pipedrive = await runSource("pipedrive", pipedrive.pull, env, ctx, manifest);
results.smartlead = await runSource("smartlead", smartlead.pull, env, ctx, manifest);
results.heyreach = await runSource("heyreach", heyreach.pull, env, ctx, manifest);
results.semrush = await runSource("semrush", semrush.pull, env, ctx, manifest);
results.seoIssues = await runSource("seoIssues", seoIssues.pull, env, ctx, manifest);
results.tradeshows = await runSource("tradeshows", tradeshows.pull, env, ctx, manifest);

const generatedAt = new Date().toISOString();
const saved = saveManifest(manifest, { generatedAt, today: TODAY });

/* history: KPI numbers only; a source that failed today records null */
const pd = results.pipedrive.ok ? results.pipedrive.data : null;
const sl = results.smartlead.ok ? results.smartlead.data : null;
const hr = results.heyreach.ok ? results.heyreach.data : null;
const ss = readJson(path.join(DATA_DIR, "smartscout.json"));
const ssToday = ss?.pulledAt && ymd(new Date(ss.pulledAt)) === TODAY;
const revenues = ssToday ? (ss.brands || []).map((b) => b.monthlyRevenue).filter((v) => typeof v === "number") : [];
const pruned = writeHistory({
  date: TODAY,
  generatedAt,
  sent: sl ? sl.yesterday.sent : null,
  replies: sl ? sl.yesterday.replies : null,
  interested: sl ? sl.yesterday.interested : null,
  overdue: pd ? pd.overdue.length : null,
  dealsOpen: pd ? pd.deals.filter((d) => d.status === "open").length : null,
  linkedinAccepted: hr?.linkedin ? hr.linkedin.accepted : null,
  smartscoutWatchlistRevenue: revenues.length ? Math.round(revenues.reduce((a, b) => a + b, 0) * 100) / 100 : null,
});

console.error(`\nmanifest ${saved.generatedAt}`);
for (const [name, s] of Object.entries(saved.sources)) {
  console.error(`  ${name.padEnd(11)} ${s.status.padEnd(6)} last success ${s.lastSuccess || "never"}${s.error ? "  error: " + s.error : s.note ? "  (" + s.note + ")" : ""}`);
}
if (pruned.length) console.error(`history: pruned ${pruned.length} file(s) older than 180 days`);

const API_SOURCES = ["smartlead", "pipedrive", "heyreach", "semrush"];
const allFailed = API_SOURCES.every((s) => !results[s].ok && !results[s].skipped);
if (allFailed) {
  console.error("\nevery API source failed");
  process.exitCode = 1;
}
