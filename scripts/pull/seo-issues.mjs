#!/usr/bin/env node
/**
 * Shared SEO issue tracker (Google Sheet) -> seo_issues.json (plain). Needs
 * GOOGLE_SERVICE_ACCOUNT_JSON and SEO_TRACKER_FILE_ID; SEO_TRACKER_TAB optional.
 *
 *   node scripts/pull/seo-issues.mjs
 *
 * Without the Google secrets it leaves the current file (the Sep 11 snapshot) in
 * place and the manifest shows it as stale, not as an error. Same reading rules as
 * dashboard/pull/pull-seo-tracker.mjs: native Google Sheets only, the sheet must be
 * shared with the service account, and a read that returns under half of the
 * current issue count is refused (ALLOW_SHRINK=1 overrides).
 */
import path from "node:path";
import { GoogleAuth } from "../../src/google-auth.js";
import { DATA_DIR, readJson, ymd } from "./lib.mjs";
import { runStandalone, isMain } from "./write.mjs";

const NATIVE_SHEET = "application/vnd.google-apps.spreadsheet";

export async function pull(env, ctx = {}) {
  const current = readJson(path.join(DATA_DIR, "seo_issues.json"), { issues: [] });
  if (!env.GOOGLE_SERVICE_ACCOUNT_JSON || !env.SEO_TRACKER_FILE_ID) {
    ctx.skipped = true;
    ctx.records = current.issues.length;
    ctx.note = `Google secrets not set; showing the ${current.sourceUpdated || "last"} snapshot`;
    return null;
  }

  const FILE_ID = env.SEO_TRACKER_FILE_ID;
  const auth = new GoogleAuth(["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/spreadsheets.readonly"]);
  let meta;
  try {
    meta = await auth.get(`https://www.googleapis.com/drive/v3/files/${FILE_ID}`, { fields: "id,name,mimeType,modifiedTime", supportsAllDrives: true });
  } catch (err) {
    if (err.status === 404) throw new Error(`Drive cannot see the tracker as ${auth.clientEmail}; share the sheet with that address (Viewer)`);
    throw err;
  }
  if (meta.mimeType !== NATIVE_SHEET) throw new Error(`"${meta.name}" is an uploaded ${meta.mimeType}, not a Google Sheet; use File > Save as Google Sheets`);

  const range = env.SEO_TRACKER_TAB ? `${env.SEO_TRACKER_TAB}!A1:Z100000` : "A1:Z100000";
  const sheet = await auth.get(`https://sheets.googleapis.com/v4/spreadsheets/${FILE_ID}/values/${encodeURIComponent(range)}`, {
    majorDimension: "ROWS", valueRenderOption: "UNFORMATTED_VALUE",
  });
  const values = sheet.values || [];
  if (values.length < 2) throw new Error(`the tracker returned ${values.length} row(s)`);

  const header = values[0].map((h) => String(h || "").trim());
  const col = (name) => {
    const i = header.findIndex((h) => h.toLowerCase() === name.toLowerCase());
    if (i === -1) throw new Error(`the tracker has no "${name}" column`);
    return i;
  };
  const IDX = { id: col("ID"), cat: col("Category"), page: col("Page"), url: col("URL"), issue: col("Issue"),
    desc: col("Description"), fix: col("Fix"), pri: col("Priority"), ref: col("Roadmap ref"), st: col("Status") };
  const cell = (row, i) => String(row[i] == null ? "" : row[i]).replace(/\s+/g, " ").trim();
  const issues = values.slice(1).filter((row) => cell(row, IDX.id)).map((row) => ({
    id: cell(row, IDX.id), pri: cell(row, IDX.pri) || "P3", ref: cell(row, IDX.ref) || "new", cat: cell(row, IDX.cat),
    page: cell(row, IDX.page), url: cell(row, IDX.url), issue: cell(row, IDX.issue), desc: cell(row, IDX.desc),
    fix: cell(row, IDX.fix), st: cell(row, IDX.st) || "Open",
  }));
  if (!issues.length) throw new Error("parsed 0 issues");
  const prevCount = current.issues.length;
  if (prevCount && issues.length < prevCount * 0.5 && env.ALLOW_SHRINK !== "1") {
    throw new Error(`refusing to write ${issues.length} issues over ${prevCount}; looks like a failed read (ALLOW_SHRINK=1 if genuine)`);
  }

  ctx.records = issues.length;
  return { sourceUpdated: ymd(new Date(meta.modifiedTime)), source: `Google Sheet "${meta.name}"`, issues };
}

if (isMain(import.meta.url)) await runStandalone("seoIssues", pull);
