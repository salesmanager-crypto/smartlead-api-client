#!/usr/bin/env node
/**
 * Validates docs/data/tradeshows.json (hand-edited, no API) and records the result
 * in the manifest. Rewrites the file only to normalise it (sorted by startDate).
 *
 *   node scripts/pull/tradeshows.mjs
 */
import path from "node:path";
import { DATA_DIR, readJson } from "./lib.mjs";
import { runStandalone, isMain } from "./write.mjs";

const DATE = /^\d{4}-\d{2}-\d{2}$/;
const validDate = (s) => DATE.test(s) && !Number.isNaN(Date.parse(s + "T12:00:00Z"));

export function validate(doc) {
  const errors = [];
  if (!doc || typeof doc !== "object" || !Array.isArray(doc.shows)) return ["file must be an object with a shows array"];
  if (doc.updatedAt != null && !validDate(doc.updatedAt)) errors.push("updatedAt is not YYYY-MM-DD");
  const seen = new Set();
  doc.shows.forEach((s, i) => {
    const at = `shows[${i}]${s?.id ? ` (${s.id})` : ""}`;
    if (!s?.id) errors.push(`${at}: missing id`);
    else if (seen.has(s.id)) errors.push(`${at}: duplicate id`);
    else seen.add(s.id);
    if (!s?.name) errors.push(`${at}: missing name`);
    if (!validDate(s?.startDate)) errors.push(`${at}: startDate is missing or not YYYY-MM-DD`);
    if (s?.endDate != null && !validDate(s.endDate)) errors.push(`${at}: endDate is not YYYY-MM-DD`);
    if (validDate(s?.startDate) && validDate(s?.endDate) && s.endDate < s.startDate) errors.push(`${at}: endDate is before startDate`);
    if (s?.campaignIds != null && (!Array.isArray(s.campaignIds) || s.campaignIds.some((n) => !Number.isInteger(n)))) errors.push(`${at}: campaignIds must be an array of numbers`);
  });
  return errors;
}

export async function pull(env, ctx = {}) {
  const doc = readJson(path.join(DATA_DIR, "tradeshows.json"));
  if (!doc) throw new Error("tradeshows.json is missing or is not valid JSON");
  const errors = validate(doc);
  if (errors.length) throw new Error(`${errors.length} problem(s): ${errors.slice(0, 3).join("; ")}`);
  ctx.records = doc.shows.length;
  if (!doc.shows.length) ctx.note = "no shows entered yet";
  return { ...doc, shows: [...doc.shows].sort((a, b) => (a.startDate < b.startDate ? -1 : a.startDate > b.startDate ? 1 : 0)) };
}

if (isMain(import.meta.url)) await runStandalone("tradeshows", pull);
