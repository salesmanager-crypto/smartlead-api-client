/**
 * Writes source data files and keeps docs/data/manifest.json current.
 * Every pull script writes through here; see docs/data/SCHEMA.md for the formats.
 */
import fs from "node:fs";
import path from "node:path";
import { DATA_DIR, PRIVATE_DIR, encryptString, readJson, today as todayFn, addDays, describeError, loadEnv } from "./lib.mjs";

export const MANIFEST = path.join(DATA_DIR, "manifest.json");
export const HISTORY_DIR = path.join(DATA_DIR, "history");
export const SOURCES = ["smartlead", "pipedrive", "heyreach", "semrush", "seoIssues", "smartscout", "tradeshows"];
/** Sources whose files carry person-level data: committed encrypted only. */
export const ENCRYPTED = new Set(["smartlead", "pipedrive"]);
/** File name for each source. */
export const FILE = { seoIssues: "seo_issues" };
export const fileOf = (source) => FILE[source] || source;
export const STALE_HOURS = 36;

function writeAtomic(file, text) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp-${process.pid}`;
  fs.writeFileSync(tmp, text);
  fs.renameSync(tmp, file);
}
export const writeJsonFile = (file, obj) => writeAtomic(file, JSON.stringify(obj, null, 2) + "\n");

/**
 * Writes one source's data. Person-level sources go to docs/data/<file>.json.enc
 * (plus a plaintext copy in the gitignored .private/data/); everything else to
 * docs/data/<file>.json.
 */
export async function writeSource(source, data, env = process.env) {
  const name = fileOf(source);
  if (!ENCRYPTED.has(source)) {
    writeJsonFile(path.join(DATA_DIR, `${name}.json`), data);
    return `docs/data/${name}.json`;
  }
  const text = JSON.stringify(data, null, 2) + "\n";
  writeAtomic(path.join(PRIVATE_DIR, `${name}.json`), text);
  if (!env.DASHBOARD_CONTENT_KEY) {
    throw new Error("DASHBOARD_CONTENT_KEY not set, so the encrypted file was not written (plaintext kept in .private/data/)");
  }
  writeJsonFile(path.join(DATA_DIR, `${name}.json.enc`), await encryptString(text, env.DASHBOARD_CONTENT_KEY));
  // never leave a stale plaintext copy where Pages would serve it
  fs.rmSync(path.join(DATA_DIR, `${name}.json`), { force: true });
  return `docs/data/${name}.json.enc`;
}

/* ---------- manifest ---------- */

export function readManifest() {
  const m = readJson(MANIFEST, null) || {};
  m.sources = m.sources || {};
  for (const s of SOURCES) {
    m.sources[s] = { lastSuccess: null, lastAttempt: null, status: "stale", error: null, records: null, note: null, ...m.sources[s] };
  }
  return m;
}

export function statusOf(entry, now = Date.now()) {
  if (entry.error) return "error";
  if (!entry.lastSuccess || now - Date.parse(entry.lastSuccess) > STALE_HOURS * 3600e3) return "stale";
  return "ok";
}

/**
 * Records one attempt. `result` is { ok: true, records, note }, { skipped: true, note }
 * or { ok: false, error }.
 * A failure keeps the previous lastSuccess, so the dashboards can still say how old
 * the data they are showing is.
 */
export function recordAttempt(manifest, source, result, at = new Date().toISOString()) {
  const prev = manifest.sources[source] || {};
  // a skipped run (nothing to do, or credentials not configured) is neither a success nor a failure
  const entry = {
    lastSuccess: result.ok ? at : prev.lastSuccess ?? null,
    lastAttempt: at,
    error: result.ok || result.skipped ? null : result.error,
    records: result.ok || result.skipped ? result.records ?? prev.records ?? null : prev.records ?? null,
    note: result.note ?? null,
  };
  entry.status = statusOf(entry);
  manifest.sources[source] = entry;
  return entry;
}

export function saveManifest(manifest, { generatedAt = new Date().toISOString(), today = todayFn() } = {}) {
  for (const s of SOURCES) manifest.sources[s].status = statusOf(manifest.sources[s]);
  const out = { generatedAt, today, sources: manifest.sources };
  writeJsonFile(MANIFEST, out);
  return out;
}

/* ---------- history ---------- */

export const HISTORY_DAYS = 180;

export function writeHistory(entry) {
  writeJsonFile(path.join(HISTORY_DIR, `${entry.date}.json`), entry);
  const cutoff = addDays(entry.date, -HISTORY_DAYS);
  const removed = [];
  for (const f of fs.existsSync(HISTORY_DIR) ? fs.readdirSync(HISTORY_DIR) : []) {
    const m = /^(\d{4}-\d{2}-\d{2})\.json$/.exec(f);
    if (m && m[1] < cutoff) { fs.rmSync(path.join(HISTORY_DIR, f)); removed.push(f); }
  }
  return removed;
}

/* ---------- one source, end to end ---------- */

/**
 * Pulls one source, writes its file and records the attempt in the manifest.
 * Never throws: a failure is returned as { ok: false, error } and recorded.
 * `pull(env, ctx)` returns the data object; it may set `ctx.records`, `ctx.note`, and
 * `ctx.skipped = true` to leave the existing file alone (nothing to do this run).
 */
export async function runSource(source, pull, env = process.env, ctx = {}, manifest = readManifest()) {
  const started = Date.now();
  const at = new Date().toISOString();
  const sctx = Object.assign(ctx, { records: null, note: null, skipped: false });
  let result;
  try {
    const data = await pull(env, sctx);
    if (sctx.skipped) {
      result = { ok: false, skipped: true, records: sctx.records, note: sctx.note, wrote: null, data: null };
    } else {
      const wrote = await writeSource(source, data, env);
      result = { ok: true, records: sctx.records, note: sctx.note, wrote, data };
    }
  } catch (err) {
    result = { ok: false, error: describeError(err), note: sctx.note };
  }
  recordAttempt(manifest, source, result, at);
  const secs = ((Date.now() - started) / 1000).toFixed(1);
  console.error(result.ok
    ? `  ${source.padEnd(11)} ok     ${String(result.records ?? "").padStart(5)} records  ${secs}s  -> ${result.wrote}${result.note ? "  (" + result.note + ")" : ""}`
    : result.skipped
      ? `  ${source.padEnd(11)} skip   ${result.note || ""}`
      : `  ${source.padEnd(11)} ERROR  ${result.error}`);
  return result;
}

/** For `node scripts/pull/<source>.mjs`: run one source and save the manifest. */
export async function runStandalone(source, pull) {
  loadEnv();
  const manifest = readManifest();
  const r = await runSource(source, pull, process.env, {}, manifest);
  saveManifest(manifest, { generatedAt: manifest.generatedAt || new Date().toISOString(), today: todayFn() });
  process.exitCode = r.ok || r.skipped ? 0 : 1;
}

export const isMain = (metaUrl) => process.argv[1] && new URL(metaUrl).pathname === path.resolve(process.argv[1]);
