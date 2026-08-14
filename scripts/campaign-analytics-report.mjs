#!/usr/bin/env node
/**
 * Global campaign analytics + targeting-refinement report.
 *
 * Pulls every in-scope campaign's performance over a date range, aggregates
 * per-lead engagement *across* those campaigns, and flags what's worth acting
 * on: high-bounce campaigns, low open rates, leads who never open after
 * repeated sends, addresses that bounce, "opens but never converts" leads,
 * and unhealthy sending inboxes.
 *
 * Usage:
 *   node scripts/campaign-analytics-report.mjs [options]
 *
 * Options:
 *   --since=YYYY-MM-DD       only include campaigns created on/after this date
 *                            (default: 2026-07-01)
 *   --start=YYYY-MM-DD       analytics window start (default: --since)
 *   --end=YYYY-MM-DD         analytics window end (default: today)
 *   --status=ACTIVE|ALL      campaign status filter (default: ALL)
 *   --exclude-ids=1,2,3      comma-separated campaign IDs to drop from scope (test campaigns, etc.)
 *   --out=path.json          where to write the JSON report
 *                            (default: scripts/output/<start>_<end>-campaign-report.json)
 *   --fixture                use bundled synthetic sample data instead of
 *                            calling the live Smartlead API (no API key needed)
 *   --skip-inbox-health      skip the inbox/deliverability health section
 *
 * Reads SMARTLEAD_API_KEY (and optional SMARTLEAD_BASE_URL) from .env, same
 * as the rest of this repo's scripts.
 *
 * Output feeds scripts/build-analytics-dashboard.mjs to render an HTML report.
 */

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import {
  CAMPAIGN_META_FIELDS,
  DEFAULT_THRESHOLDS,
  buildReport,
  chunkDateRange,
  pick,
  sumAnalytics,
} from "./lib/analytics-report-core.mjs";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const args = parseArgs(process.argv.slice(2));

const SINCE = args.since || "2026-07-01";
const START = args.start || SINCE;
const END = args.end || todayIso();
const STATUS_FILTER = (args.status || "ALL").toUpperCase();
const EXCLUDE_IDS = new Set((args.excludeIds || "").split(",").map((s) => s.trim()).filter(Boolean).map(Number));

async function main() {
  loadDotEnv();

  const client = args.fixture ? await loadFixtureClient() : new SmartleadClient({});

  console.error(`Fetching campaigns${args.fixture ? " (fixture mode)" : ""}...`);
  const allCampaigns = normalizeList(await client.listCampaigns());

  const inScope = allCampaigns.filter((c) => {
    const id = pick(c, CAMPAIGN_META_FIELDS.id);
    if (EXCLUDE_IDS.has(Number(id))) return false;
    const createdAt = pick(c, CAMPAIGN_META_FIELDS.createdAt);
    const createdDate = createdAt ? String(createdAt).slice(0, 10) : null;
    if (createdDate && createdDate < SINCE) return false;
    if (STATUS_FILTER !== "ALL") {
      const status = String(pick(c, CAMPAIGN_META_FIELDS.status) || "").toUpperCase();
      if (status !== STATUS_FILTER) return false;
    }
    return true;
  });

  console.error(`${inScope.length}/${allCampaigns.length} campaigns in scope (created >= ${SINCE}${STATUS_FILTER !== "ALL" ? `, status=${STATUS_FILTER}` : ""}).`);
  console.error(`Analytics window: ${START} .. ${END}`);

  const dateChunks = chunkDateRange(START, END, 30);
  const analyticsByCampaign = new Map();
  const leadsByCampaign = [];

  for (const c of inScope) {
    const id = pick(c, CAMPAIGN_META_FIELDS.id);
    const name = pick(c, CAMPAIGN_META_FIELDS.name);
    console.error(`  - ${name} (#${id})`);
    try {
      const rawChunks = await Promise.all(
        dateChunks.map((chunk) => client.getCampaignAnalyticsByDate(id, { startDate: chunk.start, endDate: chunk.end }))
      );
      analyticsByCampaign.set(id, sumAnalytics(rawChunks));
    } catch (err) {
      console.error(`    analytics failed: ${err.message}`);
      analyticsByCampaign.set(id, sumAnalytics([]));
    }

    try {
      const leads = await client.getAllCampaignStatistics(id);
      leadsByCampaign.push({ campaignId: id, campaignName: name, leads });
    } catch (err) {
      console.error(`    per-lead statistics failed: ${err.message}`);
      leadsByCampaign.push({ campaignId: id, campaignName: name, leads: [] });
    }
  }

  let inboxHealth = [];
  if (!args.skipInboxHealth) {
    console.error("Fetching inbox/deliverability health...");
    try {
      inboxHealth = await client.getAllInboxHealth();
    } catch (err) {
      console.error(`  inbox health fetch failed: ${err.message}`);
    }
  }

  const thresholds = { ...DEFAULT_THRESHOLDS, ...parseThresholdOverrides(args) };

  const report = buildReport({
    campaigns: inScope,
    analyticsByCampaign,
    leadsByCampaign,
    thresholds,
    inboxHealth,
    range: { since: SINCE, start: START, end: END },
  });
  report.generatedAt = new Date().toISOString();
  report.source = args.fixture ? "fixture-sample" : "live";

  const outPath = path.resolve(args.out || defaultOutPath());
  fs.mkdirSync(path.dirname(outPath), { recursive: true });
  fs.writeFileSync(outPath, JSON.stringify(report, null, 2));

  printSummary(report, outPath);
}

function printSummary(report, outPath) {
  const g = report.global;
  console.error("");
  console.error(`=== Campaign analytics report (${report.range.start} .. ${report.range.end}) ===`);
  console.error(`Campaigns: ${report.campaigns.length}  |  Leads touched: ${report.leadCount}`);
  console.error(
    `Sent: ${g.sent}  Open: ${pctStr(g.openRate)}  Click: ${pctStr(g.clickRate)}  Reply: ${pctStr(g.replyRate)}  Bounce: ${pctStr(g.bounceRate)}  Unsub: ${pctStr(g.unsubRate)}`
  );
  const critical = report.campaigns.flatMap((c) => c.flags.filter((f) => f.level === "critical").map((f) => `${c.name}: ${f.message}`));
  if (critical.length) {
    console.error(`\nCritical campaign flags (${critical.length}):`);
    for (const line of critical) console.error(`  ! ${line}`);
  }
  console.error(`\nRepeat non-openers: ${report.leadFlags.repeatNonOpeners.length}`);
  console.error(`Chronic bouncers (invalid addresses): ${report.leadFlags.chronicBouncers.length}`);
  console.error(`Engaged-but-not-converting leads: ${report.leadFlags.engagedNonConverters.length}`);
  if (report.inboxHealth.length) console.error(`Inbox health flags: ${report.inboxHealth.length}`);
  console.error(`\nWrote ${outPath}`);
  console.error(`Next: node scripts/build-analytics-dashboard.mjs ${path.relative(projectRoot, outPath)}`);
}

function pctStr(n) {
  return `${(n * 100).toFixed(1)}%`;
}

function defaultOutPath() {
  return path.join(projectRoot, "scripts", "output", `${START}_${END}-campaign-report.json`);
}

function normalizeList(res) {
  return Array.isArray(res) ? res : res?.data ?? [];
}

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function parseArgs(argv) {
  const out = {};
  for (const arg of argv) {
    if (!arg.startsWith("--")) continue;
    const [rawKey, rawVal] = arg.slice(2).split(/=(.*)/s);
    const key = rawKey.replace(/-([a-z])/g, (_, c) => c.toUpperCase());
    out[key] = rawVal === undefined ? true : rawVal;
  }
  return out;
}

function parseThresholdOverrides(args) {
  const overrides = {};
  const map = {
    bounceWarn: "bounceRateWarning",
    bounceCritical: "bounceRateCritical",
    openWarn: "openRateWarning",
    openCritical: "openRateCritical",
    unsubWarn: "unsubRateWarning",
    unsubCritical: "unsubRateCritical",
    minSends: "minSendsForNonOpenerFlag",
  };
  for (const [flag, key] of Object.entries(map)) {
    if (args[flag] !== undefined) overrides[key] = Number(args[flag]);
  }
  return overrides;
}

async function loadFixtureClient() {
  const { createFixtureClient } = await import("./fixtures/fixture-client.mjs");
  return createFixtureClient();
}

function loadDotEnv() {
  const envPath = path.join(projectRoot, ".env");
  if (!fs.existsSync(envPath)) return;
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq === -1) continue;
    const k = t.slice(0, eq).trim();
    let v = t.slice(eq + 1).trim();
    if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) v = v.slice(1, -1);
    if (!(k in process.env)) process.env[k] = v;
  }
}

main().catch((err) => {
  console.error(err.stack || err.message);
  process.exit(1);
});
