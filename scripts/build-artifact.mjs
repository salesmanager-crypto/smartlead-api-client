#!/usr/bin/env node
/**
 * Builds the Claude artifact "Alberscott Dashboard" from the same page code as GitHub
 * Pages (dashboard/command-center.html) with every constant written inline, so the page
 * is fully self-contained: no fetches, no external scripts (Google Fonts only).
 *
 *   DASHBOARD_CONTENT_KEY=... node scripts/build-artifact.mjs
 *     -> docs/artifact/alberscott-dashboard.html.enc   (committed; same .enc format as the data)
 *     -> .private/artifact/alberscott-dashboard.html   (plaintext, gitignored)
 *   node scripts/build-artifact.mjs --plain-out /tmp/alberscott-dashboard.html
 *     -> just the plaintext page, for the Claude task to publish
 *   --data-dir <dir>  read the data files from another folder (testing)
 *
 * The DATA BLOCK holds one `const NAME = <json>;` line per constant in
 * dashboard/data-map.js (DATA_DATE, TODAY, OVERDUE, DUE_TODAY, UPCOMING, CAMPAIGNS,
 * DEALS, INBOX_LOG, YESTERDAY, LINKEDIN, PD_META, INBOXES, REP_NAME, SYNC_CATEGORIES,
 * SEO_*, VENDORS, DOMAIN_WAVES, PLATFORM_TOOLS, OTHER_TOOLS, META_ADS, TOOL_CHECKED,
 * SMARTSCOUT, TRADESHOWS, TRADESHOW_NOTES, MANIFEST), plus TRADESHOW_STORE, which saves
 * trade show attendance notes to the artifact's shared `db` store (publish with
 * capabilities: { db: {} }).
 */
import fs from "node:fs";
import path from "node:path";
import { ROOT, DATA_DIR, loadEnv, readJson, decryptEnvelope, encryptString } from "./pull/lib.mjs";
import { loadMapper, checkScripts } from "./build-pages.mjs";

const APP = path.join(ROOT, "dashboard", "command-center.html");
const START = "/* ===== DATA BLOCK";
const END = "/* END DATA BLOCK ===== */";
export const ARTIFACT_TITLE = "Alberscott Dashboard";
export const OUT_ENC = path.join(ROOT, "docs", "artifact", "alberscott-dashboard.html.enc");
export const OUT_PLAIN = path.join(ROOT, ".private", "artifact", "alberscott-dashboard.html");
const MAX_BYTES = 16 * 1024 * 1024;

/** Reads every data file the dashboards use; person-level ones from .private/ or by decrypting. */
export async function readFiles(dir = DATA_DIR, env = process.env) {
  const plainOrEnc = async (name) => {
    const plain = readJson(path.join(dir, `${name}.json`));
    if (plain) return plain;
    const priv = dir === DATA_DIR ? readJson(path.join(ROOT, ".private", "data", `${name}.json`)) : null;
    if (priv) return priv;
    const enc = readJson(path.join(dir, `${name}.json.enc`));
    if (!enc) return null;
    if (!env.DASHBOARD_CONTENT_KEY) throw new Error(`${name}.json.enc needs DASHBOARD_CONTENT_KEY to decrypt`);
    return JSON.parse(await decryptEnvelope(enc, env.DASHBOARD_CONTENT_KEY));
  };
  const j = (n) => readJson(path.join(dir, n));
  return {
    manifest: j("manifest.json"),
    smartlead: await plainOrEnc("smartlead"),
    pipedrive: await plainOrEnc("pipedrive"),
    heyreach: j("heyreach.json"),
    semrush: j("semrush.json"),
    seoIssues: j("seo_issues.json"),
    seoGeo: j("seo_geo.json"),
    smartscout: j("smartscout.json"),
    tradeshows: j("tradeshows.json"),
    tradeshowNotes: j("tradeshow_notes.json"),
    resources: j("resources.json"),
  };
}

/* Saves attendance notes in the artifact's db (one document per show, id = show id).
   Loads the repo copy first and overlays the live store; without db (a view that does
   not serve it, or a viewer who cannot write) the page stays read-only. */
const STORE_JS = `
/* Trade show attendance notes: live in this artifact's shared db store at
   tradeshowNotes/<show id>; the daily Claude task copies them to docs/data/tradeshow_notes.json. */
const TRADESHOW_STORE = (function () {
  let dbp = null;
  function getDb() {
    if (!dbp) dbp = (window.claude && typeof window.claude.use === "function") ? window.claude.use("db").catch(function () { return null; }) : Promise.resolve(null);
    return dbp;
  }
  const store = {
    editable: true,
    load: function () {
      const notes = Object.assign({}, TRADESHOW_NOTES.notes || {});
      return getDb().then(function (db) {
        if (!db) { store.editable = false; return notes; }
        return db.collection("tradeshowNotes").get().then(function (snap) {
          snap.docs.forEach(function (d) { if (d.exists) notes[d.id] = d.data(); });
          return notes;
        }, function () { store.editable = false; return notes; });
      });
    },
    save: function (id, entry) {
      return getDb().then(function (db) {
        if (!db) throw new Error("saving is not available in this view");
        const body = { attending: entry.attending, note: entry.note, updatedAt: entry.updatedAt, updatedBy: null };
        return db.doc("tradeshowNotes/" + id).set(body).then(function () { return body; }, function (e) {
          if (e && e.code === "invalid_argument") { store.editable = false; throw new Error("you have view-only access to this dashboard"); }
          throw new Error((e && e.message) || "save failed");
        });
      });
    }
  };
  return store;
})();
`;

const LS = String.fromCharCode(0x2028), PS = String.fromCharCode(0x2029); // legal in JSON, not in a <script>
const json = (v) => JSON.stringify(v).replace(/<\//g, "<\\/").split(LS).join("\\u2028").split(PS).join("\\u2029");

export function artifactDataBlock(files, pulledAt = new Date().toISOString()) {
  const { mapDashboardData, DASHBOARD_CONSTANTS } = loadMapper();
  const d = mapDashboardData(files);
  const lines = DASHBOARD_CONSTANTS.map((n) => `const ${n} = ${json(d[n])};`);
  return `${START} (generated by scripts/build-artifact.mjs from docs/data/*.json, ${pulledAt}) ===== */\n` +
    lines.join("\n") + "\n" + STORE_JS + END;
}

export function buildArtifactHtml(app, files) {
  const s = app.indexOf(START), e = app.indexOf(END);
  if (s === -1 || e === -1) throw new Error("DATA BLOCK markers not found in dashboard/command-center.html");
  let html = app.slice(0, s) + artifactDataBlock(files) + app.slice(e + END.length);
  html = html.replace(/<title>[^<]*<\/title>/, `<title>${ARTIFACT_TITLE}</title>`);
  checkScripts(html, "artifact");
  // self-contained: nothing loaded from anywhere but Google Fonts
  const external = [...html.matchAll(/<(?:script|link|img|iframe)[^>]+(?:src|href)="(https?:[^"]+)"/g)].map((m) => m[1])
    .filter((u) => !/^https:\/\/fonts\.(googleapis|gstatic)\.com(\/|$)/.test(u));
  if (external.length) throw new Error(`artifact would load external resources: ${external.join(", ")}`);
  if (/function loadData\s*\(/.test(html)) throw new Error("the artifact must not load data at runtime (loadData found)");
  if (Buffer.byteLength(html) > MAX_BYTES) throw new Error(`artifact is ${(Buffer.byteLength(html) / 1048576).toFixed(1)} MB, over the 16 MB limit`);
  return html;
}

async function main() {
  loadEnv();
  const args = process.argv.slice(2);
  const opt = (name) => { const i = args.indexOf(name); return i === -1 ? null : args[i + 1]; };
  const dir = opt("--data-dir") ? path.resolve(opt("--data-dir")) : DATA_DIR;
  const files = await readFiles(dir);
  const html = buildArtifactHtml(fs.readFileSync(APP, "utf8"), files);
  const kb = (Buffer.byteLength(html) / 1024).toFixed(0);

  const plainOut = opt("--plain-out");
  if (plainOut) {
    fs.mkdirSync(path.dirname(path.resolve(plainOut)), { recursive: true });
    fs.writeFileSync(plainOut, html);
    console.error(`wrote ${plainOut}  ${kb} KB (plaintext: contains names and email addresses; do not commit)`);
    return;
  }
  fs.mkdirSync(path.dirname(OUT_PLAIN), { recursive: true });
  fs.writeFileSync(OUT_PLAIN, html);
  const key = process.env.DASHBOARD_CONTENT_KEY;
  if (!key) {
    console.error(`wrote ${path.relative(ROOT, OUT_PLAIN)} (${kb} KB). DASHBOARD_CONTENT_KEY not set, so the committed .enc copy was not updated.`);
    process.exitCode = 1;
    return;
  }
  fs.mkdirSync(path.dirname(OUT_ENC), { recursive: true });
  fs.writeFileSync(OUT_ENC, JSON.stringify(await encryptString(html, key)) + "\n");
  console.error(`wrote ${path.relative(ROOT, OUT_ENC)} (encrypted) and ${path.relative(ROOT, OUT_PLAIN)}  ${kb} KB`);
}

if (process.argv[1] && path.resolve(process.argv[1]) === new URL(import.meta.url).pathname) await main();
