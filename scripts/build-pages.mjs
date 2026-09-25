#!/usr/bin/env node
/**
 * Builds the GitHub Pages dashboard: docs/index.html.
 *
 *   DASHBOARD_CONTENT_KEY=... node scripts/build-pages.mjs
 *
 * 1. Takes the dashboard code (dashboard/command-center.html) and fills its DATA BLOCK
 *    with a loader: after sign-in the page fetches docs/data/*.json (relative URLs),
 *    decrypts the two .enc files with the content key, and maps everything through
 *    dashboard/data-map.js (the same mapping the artifact builder uses).
 * 2. Encrypts that page under the content key and wraps it in the existing sign-in
 *    page (dashboard/signin.html): same look, same accounts, same passwords.
 *
 * The built page holds no data at all: data lives in docs/data/ and changes daily
 * without a rebuild. Rebuild only when the dashboard code or sign-in page changes
 * (the daily workflow rebuilds every run anyway; it is cheap).
 *
 * Testing without the real accounts: --test-user name:password wraps the key for a
 * throwaway account instead of the real ones, and --out writes somewhere else.
 */
import fs from "node:fs";
import path from "node:path";
import { webcrypto as crypto } from "node:crypto";
import { ROOT, loadEnv, encryptString } from "./pull/lib.mjs";

const APP = path.join(ROOT, "dashboard", "command-center.html");
const SIGNIN = path.join(ROOT, "dashboard", "signin.html");
const MAPPER = path.join(ROOT, "dashboard", "data-map.js");
const START = "/* ===== DATA BLOCK";
const END = "/* END DATA BLOCK ===== */";
const ITER = 600000; // same PBKDF2 work factor as the existing accounts

/** The DASHBOARD_CONSTANTS list, read by evaluating data-map.js the way the browser will. */
export function loadMapper() {
  const src = fs.readFileSync(MAPPER, "utf8");
  const mod = { exports: {} };
  new Function("module", src)(mod);
  return { src, ...mod.exports };
}

/** The declarations the source DATA BLOCK already has (the `let` list), reused as-is. */
function sourceBlock(app) {
  const s = app.indexOf(START), e = app.indexOf(END);
  if (s === -1 || e === -1) throw new Error("DATA BLOCK markers not found in dashboard/command-center.html");
  return { s, e, body: app.slice(s, e) };
}

export function pagesDataBlock(app) {
  const { DASHBOARD_CONSTANTS, src } = loadMapper();
  const { body } = sourceBlock(app);
  const declared = new Set([...body.matchAll(/(?:let|,)\s*([A-Z][A-Z0-9_]+)\s*=/g)].map((m) => m[1]));
  const missing = DASHBOARD_CONSTANTS.filter((n) => !declared.has(n));
  if (missing.length) throw new Error(`the DATA BLOCK in command-center.html does not declare: ${missing.join(", ")}`);

  const assign = DASHBOARD_CONSTANTS.map((n) => `  ${n} = d.${n};`).join("\n");
  const loader = `
/* GitHub Pages: data is fetched after sign-in. The sign-in page replaces the token
   below with the content key it unwrapped, which decrypts the .enc data files. */
const CONTENT_KEY_B64 = "%%CONTENT_KEY%%";
${src.replace(/if \(typeof module !== "undefined"\)[^\n]*\n?/, "")}
const DATA_FILES = { smartlead: "smartlead.json.enc", pipedrive: "pipedrive.json.enc", heyreach: "heyreach.json", semrush: "semrush.json",
  seoIssues: "seo_issues.json", seoGeo: "seo_geo.json", smartscout: "smartscout.json", tradeshows: "tradeshows.json",
  tradeshowNotes: "tradeshow_notes.json", resources: "resources.json" };
async function decryptEnc(env) {
  const raw = Uint8Array.from(atob(CONTENT_KEY_B64), function (c) { return c.charCodeAt(0); });
  const key = await crypto.subtle.importKey("raw", raw, "AES-GCM", false, ["decrypt"]);
  const u8 = function (b) { return Uint8Array.from(atob(b), function (c) { return c.charCodeAt(0); }); };
  return JSON.parse(new TextDecoder().decode(await crypto.subtle.decrypt({ name: "AES-GCM", iv: u8(env.iv) }, key, u8(env.ct))));
}
async function getJson(url, opts) {
  const res = await fetch(url, opts);
  if (res.status === 404) return null;
  if (!res.ok) throw new Error(url + ": HTTP " + res.status);
  return res.json();
}
async function loadData() {
  const manifest = await getJson("data/manifest.json", { cache: "no-store" });
  const v = encodeURIComponent((manifest && manifest.generatedAt) || Date.now());
  const files = { manifest: manifest };
  await Promise.all(Object.keys(DATA_FILES).map(async function (k) {
    try {
      const j = await getJson("data/" + DATA_FILES[k] + "?v=" + v);
      files[k] = j && /\\.enc$/.test(DATA_FILES[k]) ? await decryptEnc(j) : j;
    } catch (err) {
      files[k] = null; // one unreadable file must not blank the dashboard; its status pill shows the source
      console.warn("dashboard data: " + DATA_FILES[k] + " not loaded:", err);
    }
  }));
  const d = mapDashboardData(files);
${assign}
}
`;
  return body + loader;
}

/** Throws if any inline <script> in the page does not parse, so a typo never ships. */
export function checkScripts(html, label) {
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map((m) => m[1]);
  scripts.forEach((code, i) => {
    try { new Function(code); } catch (err) { throw new Error(`${label}: inline script ${i + 1} does not parse: ${err.message}`); }
  });
  return scripts.length;
}

export function buildPagesHtml(app) {
  const { s, e } = sourceBlock(app);
  const html = app.slice(0, s) + pagesDataBlock(app) + app.slice(e);
  checkScripts(html, "dashboard page");
  return html;
}

async function wrapKey(user, pass, rawKey) {
  const salt = crypto.getRandomValues(new Uint8Array(16));
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const base = await crypto.subtle.importKey("raw", new TextEncoder().encode(user + "\0" + pass), "PBKDF2", false, ["deriveKey"]);
  const kek = await crypto.subtle.deriveKey({ name: "PBKDF2", salt, iterations: ITER, hash: "SHA-256" }, base, { name: "AES-GCM", length: 256 }, false, ["encrypt"]);
  const w = new Uint8Array(await crypto.subtle.encrypt({ name: "AES-GCM", iv }, kek, rawKey));
  const b = (u) => Buffer.from(u).toString("base64");
  return { s: b(salt), i: b(iv), w: b(w) };
}

async function main() {
  loadEnv();
  const args = process.argv.slice(2);
  const opt = (name) => { const i = args.indexOf(name); return i === -1 ? null : args[i + 1]; };
  const key = process.env.DASHBOARD_CONTENT_KEY;
  if (!key) {
    console.error("DASHBOARD_CONTENT_KEY not set: docs/index.html left as it is. Recover it with: node scripts/recover-content-key.mjs");
    process.exitCode = 1;
    return;
  }
  const out = path.resolve(ROOT, opt("--out") || "docs/index.html");
  const app = buildPagesHtml(fs.readFileSync(APP, "utf8"));
  const env = await encryptString(app, key);
  let signin = fs.readFileSync(SIGNIN, "utf8");
  const payload = `{iv:"${env.iv}",ct:"${env.ct}",iter:${ITER}}`;
  const testUser = opt("--test-user");
  if (testUser) {
    const [u, p] = testUser.split(":");
    const rec = await wrapKey(u.toLowerCase(), p, Buffer.from(key, "base64"));
    signin = signin.replace(/var U=\{.*?\};\n/, `var U=${JSON.stringify({ [u.toLowerCase()]: rec })};\n`);
  }
  if (!signin.includes("/*%%PAYLOAD%%*/null")) throw new Error("payload marker not found in dashboard/signin.html");
  const html = signin.replace("/*%%PAYLOAD%%*/null", payload);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, html);
  console.error(`wrote ${path.relative(ROOT, out)}  ${(html.length / 1024).toFixed(0)} KB (dashboard code ${(app.length / 1024).toFixed(0)} KB, encrypted; no data inside)${testUser ? "  [test account only]" : ""}`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === new URL(import.meta.url).pathname) await main();
