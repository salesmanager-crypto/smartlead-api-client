/**
 * Shared helpers for the dashboard pull scripts. No dependencies beyond Node 18+.
 *
 * Rules every pull script follows:
 *  - never log or throw anything that contains a secret (API keys ride in URLs for
 *    SmartLead and Semrush, so errors carry only method, path and status);
 *  - retry 429 and 5xx up to 3 times with exponential backoff;
 *  - dates are business dates in America/New_York.
 */
import fs from "node:fs";
import path from "node:path";
import { webcrypto as crypto } from "node:crypto";

export const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..", "..");
export const DATA_DIR = path.join(ROOT, "docs", "data");
export const PRIVATE_DIR = path.join(ROOT, ".private", "data");
export const TZ = "America/New_York";

/* ---------- env ---------- */

/** Loads ROOT/.env into process.env without overriding anything already set. */
export function loadEnv(file = path.join(ROOT, ".env")) {
  if (!fs.existsSync(file)) return;
  for (const line of fs.readFileSync(file, "utf8").split("\n")) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
  }
}

export function requireEnv(env, ...names) {
  const missing = names.filter((n) => !env[n]);
  if (missing.length) throw new Error(`${missing.join(", ")} not set`);
}

/* ---------- dates ---------- */

export const ymd = (d, tz = TZ) =>
  new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit" }).format(d);
export const addDays = (iso, n) => {
  const d = new Date(iso + "T12:00:00Z");
  d.setUTCDate(d.getUTCDate() + n);
  return d.toISOString().slice(0, 10);
};
export const daysBetween = (a, b) => Math.round((Date.parse(b + "T12:00:00Z") - Date.parse(a + "T12:00:00Z")) / 864e5);
export const fmtDate = (iso, opts = { month: "short", day: "numeric", year: "numeric" }) =>
  iso ? new Date(iso.slice(0, 10) + "T12:00:00Z").toLocaleDateString("en-US", { ...opts, timeZone: "UTC" }) : null;

/** "Today" for a run. DASHBOARD_TODAY=YYYY-MM-DD overrides it for testing. */
export const today = () => process.env.DASHBOARD_TODAY || ymd(new Date());

/* ---------- numbers ---------- */

export const num = (v) => (v == null || v === "" ? 0 : Number(v) || 0);
export const numOrNull = (v) => (v == null || v === "" || Number.isNaN(Number(v)) ? null : Number(v));
export const rate = (n, d) => (d ? Math.round((n / d) * 1000) / 10 : 0);

/* ---------- concurrency ---------- */

export async function pool(items, size, fn) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(
    Array.from({ length: Math.min(size, items.length) }, async () => {
      for (;;) {
        const idx = i++;
        if (idx >= items.length) return;
        out[idx] = await fn(items[idx], idx);
      }
    })
  );
  return out;
}

export const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

/* ---------- HTTP ---------- */

/**
 * fetch with 3 retries on 429/5xx/network errors. `label` is what appears in
 * errors instead of the URL, so a key in the query string never leaks.
 */
export async function fetchRetry(url, init = {}, { label = "request", retries = 3 } = {}) {
  for (let attempt = 0; ; attempt++) {
    let res;
    try {
      res = await fetch(url, init);
    } catch (err) {
      if (attempt < retries) { await sleep(2 ** attempt * 1000); continue; }
      throw new Error(`${label}: network error (${err.cause?.code || err.name})`);
    }
    if ((res.status === 429 || res.status >= 500) && attempt < retries) {
      await sleep((Number(res.headers.get("retry-after")) || 2 ** attempt) * 1000);
      continue;
    }
    return res;
  }
}

/** A secret-free, one-line description of any thrown error, max 300 chars. */
export function describeError(err) {
  let msg = err?.message || String(err);
  // belt and braces: strip anything that looks like a credential in a URL
  msg = msg.replace(/([?&](api_key|api_token|key|token)=)[^&\s]+/gi, "$1***");
  for (const k of ["SMARTLEAD_API_KEY", "PIPEDRIVE_API_TOKEN", "HEYREACH_API_KEY", "DASHBOARD_CONTENT_KEY"]) {
    const v = process.env[k];
    if (v && v.length > 6) msg = msg.split(v).join("***");
  }
  return msg.replace(/\s+/g, " ").trim().slice(0, 300);
}

/* ---------- encryption (same scheme as the dashboard sign-in page) ---------- */

/**
 * The content key as 32 raw bytes. Forgives the usual paste mistakes in the secret
 * (surrounding spaces or newlines, quotes, the "DASHBOARD_CONTENT_KEY (verified):"
 * label copied along) by taking the one 44-character base64 token in it. On failure
 * the error describes the value's shape, never the value.
 */
export function contentKeyBytes(value) {
  const v = String(value || "");
  const tokens = v.match(/[A-Za-z0-9+/]{43}=/g) || [];
  const raw = tokens.length === 1 ? Buffer.from(tokens[0], "base64") : null;
  if (raw && raw.length === 32) return raw;
  const shape = [
    `${v.length} characters`,
    `${v.split(/\r?\n/).length} line(s)`,
    /\s/.test(v) ? "contains spaces or line breaks" : "no whitespace",
    /["']/.test(v) ? "contains quote marks" : null,
    /:/.test(v) ? "contains a colon (label copied?)" : null,
    `${tokens.length} key-shaped token(s) found`,
  ].filter(Boolean).join(", ");
  throw new Error(`DASHBOARD_CONTENT_KEY is not a 44-character base64 key ending in "=" (${shape}). Re-copy just the key line printed by scripts/recover-content-key.mjs or the browser snippet.`);
}

async function contentKey(value) {
  return crypto.subtle.importKey("raw", contentKeyBytes(value), "AES-GCM", false, ["encrypt", "decrypt"]);
}

/** Encrypts a string into the `.enc` envelope documented in docs/data/SCHEMA.md. */
export async function encryptString(plaintext, keyB64) {
  const key = await contentKey(keyB64);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(plaintext)));
  return { v: 1, alg: "AES-256-GCM", iv: Buffer.from(iv).toString("base64"), ct: Buffer.from(ct).toString("base64") };
}

export async function decryptEnvelope(env, keyB64) {
  const key = await contentKey(keyB64);
  const pt = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: Buffer.from(env.iv, "base64") }, key, Buffer.from(env.ct, "base64")
  );
  return new TextDecoder().decode(pt);
}

/* ---------- reading data files back ---------- */

export function readJson(file, fallback = null) {
  try { return JSON.parse(fs.readFileSync(file, "utf8")); } catch { return fallback; }
}

/**
 * Reads a source's data: plain docs/data/<name>.json, else the local plaintext copy
 * in .private/data/, else decrypts docs/data/<name>.json.enc with the content key.
 */
export async function readSource(name, env = process.env) {
  const plain = readJson(path.join(DATA_DIR, `${name}.json`));
  if (plain) return plain;
  const priv = readJson(path.join(PRIVATE_DIR, `${name}.json`));
  if (priv) return priv;
  const enc = readJson(path.join(DATA_DIR, `${name}.json.enc`));
  if (enc && env.DASHBOARD_CONTENT_KEY) return JSON.parse(await decryptEnvelope(enc, env.DASHBOARD_CONTENT_KEY));
  return null;
}
