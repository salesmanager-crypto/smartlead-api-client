#!/usr/bin/env node
/**
 * Validates docs/data/tradeshows.json (the trade show calendar, maintained outside
 * this pipeline, no API) and records the result in the manifest. The file is left
 * exactly as it is: this only checks it.
 *
 *   node scripts/pull/tradeshows.mjs
 *
 * Shape: an array of shows (see docs/data/SCHEMA.md), or { shows: [...] }. Each show
 * is identified by showId(show) = slug of showName + startDate, which is also the key
 * the attendance notes in tradeshow_notes.json use.
 */
import path from "node:path";
import { DATA_DIR, readJson } from "./lib.mjs";
import { isMain, runStandalone } from "./write.mjs";

const DATE = /^\d{4}-\d{2}-\d{2}$/;
const validDate = (s) => DATE.test(s || "") && !Number.isNaN(Date.parse(s + "T12:00:00Z"));

export const showsOf = (doc) => (Array.isArray(doc) ? doc : Array.isArray(doc?.shows) ? doc.shows : null);
export const showId = (s) =>
  `${String(s.showName || "").normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "")}-${s.startDate}`;

export function validate(doc) {
  const shows = showsOf(doc);
  if (!shows) return ["file must be an array of shows (or an object with a shows array)"];
  const errors = [];
  const seen = new Set();
  shows.forEach((s, i) => {
    const at = `#${i + 1}${s?.showName ? ` (${s.showName})` : ""}`;
    if (!s?.showName) errors.push(`${at}: missing showName`);
    if (!validDate(s?.startDate)) errors.push(`${at}: startDate missing or not YYYY-MM-DD`);
    if (s?.endDate && !validDate(s.endDate)) errors.push(`${at}: endDate not YYYY-MM-DD`);
    if (validDate(s?.startDate) && validDate(s?.endDate) && s.endDate < s.startDate) errors.push(`${at}: endDate before startDate`);
    if (s?.sourceUrls != null && !Array.isArray(s.sourceUrls)) errors.push(`${at}: sourceUrls must be an array`);
    if (s?.showName && validDate(s?.startDate)) {
      const id = showId(s);
      if (seen.has(id)) errors.push(`${at}: listed twice with the same start date`);
      seen.add(id);
    }
  });
  return errors;
}

export async function pull(env, ctx = {}) {
  const doc = readJson(path.join(DATA_DIR, "tradeshows.json"));
  if (doc == null) throw new Error("tradeshows.json is missing or is not valid JSON");
  const errors = validate(doc);
  if (errors.length) throw new Error(`${errors.length} problem(s): ${errors.slice(0, 3).join("; ")}`);
  const shows = showsOf(doc);
  ctx.records = shows.length;
  if (!shows.length) ctx.note = "no shows entered yet";
  ctx.unchanged = true;
  return doc;
}

if (isMain(import.meta.url)) await runStandalone("tradeshows", pull);
