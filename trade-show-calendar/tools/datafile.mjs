#!/usr/bin/env node
// Load, validate, report on and save trade-show-calendar/data/shows.js.
//
//   node trade-show-calendar/tools/datafile.mjs validate          # schema checks + report
//   node trade-show-calendar/tools/datafile.mjs export out.json   # {meta, shows} as JSON
//   node trade-show-calendar/tools/datafile.mjs import in.json    # write shows.js from {meta, shows}
//   node trade-show-calendar/tools/datafile.mjs sheet [YYYY-MM]   # rows for the team Google Sheet (>500 exhibitors)

import fs from "node:fs";
import path from "node:path";
import vm from "node:vm";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
export const DATA_FILE = path.join(here, "..", "data", "shows.js");

export const SECTORS = [
  "Food & Beverage", "Coffee & Tea", "Fashion & Apparel", "Footwear", "Lingerie & Swimwear",
  "Kids & Baby", "Accessories & Jewellery", "Gift & Stationery", "Christmas & Seasonal",
  "Home & Interiors", "Housewares & Kitchen", "Garden & DIY", "Beauty & Personal Care",
  "Health & Supplements", "Toys & Games", "Licensing", "Hobby & Crafts", "Sports & Outdoor",
  "Cycling", "Hunting & Fishing", "Automotive Aftermarket", "Consumer Electronics & Tech",
  "Pet Supplies",
];

const ENUMS = {
  audience: ["trade", "trade+consumer", "consumer"],
  exhibitors_status: ["current", "previous", "not_found"],
  amazon_fit: ["strong", "partial"],
  status: ["confirmed", "dates TBC", "postponed", "cancelled"],
};

const REQUIRED = [
  "id", "name", "edition_year", "start_date", "end_date", "months_covered", "city", "country",
  "venue", "organiser", "website", "sectors", "audience", "exhibitors_current",
  "exhibitors_current_source", "exhibitors_previous", "exhibitors_previous_year",
  "exhibitors_previous_source", "exhibitors_status", "sources_checked", "has_app", "app_name",
  "app_platform", "app_source", "amazon_fit", "fit_notes", "status", "added_on", "last_verified",
  "notes",
];

export function load(file = DATA_FILE) {
  const ctx = { window: {} };
  vm.runInNewContext(fs.readFileSync(file, "utf8"), ctx, { filename: file });
  return { meta: ctx.window.META || {}, shows: ctx.window.SHOWS || [] };
}

export function save({ meta, shows }, file = DATA_FILE) {
  shows = [...shows].sort((a, b) =>
    (a.start_date || a.months_covered?.[0] || "9999").localeCompare(b.start_date || b.months_covered?.[0] || "9999") ||
    a.name.localeCompare(b.name));
  const body =
    "// Trade Show Calendar data. Edited by the /research-month and /refresh-all commands.\n" +
    "// Loaded by index.html as a plain script, so the page works from file:// without a server.\n" +
    "window.META = " + JSON.stringify(meta, null, 2) + ";\n\n" +
    "window.SHOWS = [\n" + shows.map((s) => "  " + JSON.stringify(s)).join(",\n") + "\n];\n";
  fs.writeFileSync(file, body);
}

const isoDate = (v) => typeof v === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v) && !isNaN(Date.parse(v));

export function monthsBetween(start, end) {
  const out = [];
  let [y, m] = start.slice(0, 7).split("-").map(Number);
  const [ey, em] = end.slice(0, 7).split("-").map(Number);
  while (y < ey || (y === ey && m <= em)) {
    out.push(`${y}-${String(m).padStart(2, "0")}`);
    if (++m > 12) { m = 1; y++; }
  }
  return out;
}

export function validate({ meta, shows }) {
  const errors = [];
  const warnings = [];
  const ids = new Set();
  for (const s of shows) {
    const tag = s.id || s.name || "(no id)";
    for (const k of REQUIRED) if (!(k in s)) errors.push(`${tag}: missing field ${k}`);
    if (ids.has(s.id)) errors.push(`${tag}: duplicate id`);
    ids.add(s.id);
    for (const [k, vals] of Object.entries(ENUMS))
      if (k in s && !vals.includes(s[k])) errors.push(`${tag}: ${k}="${s[k]}" not in ${vals.join("|")}`);
    if (![true, false, "unknown"].includes(s.has_app)) errors.push(`${tag}: has_app must be true|false|"unknown"`);
    for (const sec of s.sectors || []) if (!SECTORS.includes(sec)) errors.push(`${tag}: unknown sector "${sec}"`);
    if (!s.sectors?.length) errors.push(`${tag}: no sectors`);
    if (!/^https?:\/\//.test(s.website || "")) errors.push(`${tag}: website must be a full URL`);
    if (!s.fit_notes) errors.push(`${tag}: fit_notes empty`);
    if (s.start_date || s.end_date) {
      if (!isoDate(s.start_date) || !isoDate(s.end_date)) errors.push(`${tag}: bad start/end date`);
      else {
        if (s.end_date < s.start_date) errors.push(`${tag}: end_date before start_date`);
        const expect = monthsBetween(s.start_date, s.end_date).join(",");
        if ((s.months_covered || []).join(",") !== expect)
          errors.push(`${tag}: months_covered ${JSON.stringify(s.months_covered)} != ${expect}`);
      }
    } else if (s.status !== "dates TBC") errors.push(`${tag}: no dates but status is not "dates TBC"`);
    if (!(s.months_covered || []).every((m) => /^\d{4}-\d{2}$/.test(m))) errors.push(`${tag}: bad months_covered`);
    if (s.exhibitors_status === "current" && !(Number.isInteger(s.exhibitors_current) && s.exhibitors_current_source))
      errors.push(`${tag}: status current needs exhibitors_current + source`);
    if (s.exhibitors_status === "previous" &&
        !(Number.isInteger(s.exhibitors_previous) && s.exhibitors_previous_year && s.exhibitors_previous_source))
      errors.push(`${tag}: status previous needs exhibitors_previous + year + source`);
    if (s.exhibitors_status === "not_found" && !(s.sources_checked || []).length)
      errors.push(`${tag}: not_found needs sources_checked`);
    if (s.has_app === true && !s.app_name) warnings.push(`${tag}: has_app true but no app_name`);
  }
  if (!isoDate(meta.last_updated)) errors.push("META.last_updated missing or not YYYY-MM-DD");
  return { errors, warnings };
}

export function exhibitorFigure(s) {
  if (s.exhibitors_status === "current") return { n: s.exhibitors_current, year: s.edition_year, current: true };
  if (s.exhibitors_status === "previous") return { n: s.exhibitors_previous, year: s.exhibitors_previous_year, current: false };
  return null;
}

const MON = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
const MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August",
  "September", "October", "November", "December"];

export function sheetDates(s) {
  if (!s.start_date) return `TBC (${s.months_covered.map((m) => MON[+m.slice(5) - 1]).join("/")} ${s.edition_year})`;
  const [sy, sm, sd] = s.start_date.split("-");
  const [ey, em, ed] = s.end_date.split("-");
  if (s.start_date === s.end_date) return `${sd} ${MON[sm - 1]} ${sy}`;
  if (sy !== ey) return `${sd} ${MON[sm - 1]} ${sy}–${ed} ${MON[em - 1]} ${ey}`;
  if (sm !== em) return `${sd} ${MON[sm - 1]}–${ed} ${MON[em - 1]} ${ey}`;
  return `${sd}–${ed} ${MON[sm - 1]} ${ey}`;
}

export function sheetRow(s) {
  const f = exhibitorFigure(s);
  const ex = f ? f.n.toLocaleString("en-GB") + (f.current ? "" : ` (${f.year})`) : "";
  return [s.name, `${s.city} (${s.venue}), ${s.country}`, sheetDates(s), ex, s.sectors.join(", "), s.website];
}

export function startMonth(s) {
  return s.start_date ? s.start_date.slice(0, 7) : s.months_covered[0];
}

export function sheetTabName(month) {
  return MONTH_NAMES[+month.slice(5) - 1];
}

function report({ meta, shows }) {
  const months = [...new Set([...(meta.researched_months || []), ...shows.flatMap((s) => s.months_covered)])].sort();
  console.log("\nShows per month (by months_covered):");
  for (const m of months) {
    const list = shows.filter((s) => s.months_covered.includes(m));
    const c = (st) => list.filter((s) => s.exhibitors_status === st).length;
    console.log(`  ${m}: ${String(list.length).padStart(3)}  current ${c("current")}, previous ${c("previous")}, not_found ${c("not_found")}`);
  }
  const c = (st) => shows.filter((s) => s.exhibitors_status === st).length;
  console.log(`\nTotal ${shows.length}: current ${c("current")}, previous ${c("previous")}, not_found ${c("not_found")}`);
  console.log(`Apps: yes ${shows.filter((s) => s.has_app === true).length}, no ${shows.filter((s) => s.has_app === false).length}, unknown ${shows.filter((s) => s.has_app === "unknown").length}`);
  console.log(`Status: ${Object.entries(shows.reduce((a, s) => ((a[s.status] = (a[s.status] || 0) + 1), a), {})).map(([k, v]) => `${k} ${v}`).join(", ")}`);
  const nf = shows.filter((s) => s.exhibitors_status === "not_found");
  if (nf.length) {
    console.log("\nExhibitor figure not found (check manually):");
    for (const s of nf) console.log(`  - ${s.name} (${s.city}, ${s.start_date || "TBC"}) ${s.website}`);
  }
}

const [, , cmd, arg] = process.argv;
if (cmd && import.meta.url === `file://${process.argv[1]}`) {
  if (cmd === "validate") {
    const data = load();
    const { errors, warnings } = validate(data);
    warnings.forEach((w) => console.log("warn: " + w));
    errors.forEach((e) => console.log("ERROR: " + e));
    report(data);
    console.log(errors.length ? `\n${errors.length} error(s)` : "\nOK: no schema errors");
    process.exit(errors.length ? 1 : 0);
  } else if (cmd === "export") {
    fs.writeFileSync(arg, JSON.stringify(load(), null, 2));
  } else if (cmd === "import") {
    const data = JSON.parse(fs.readFileSync(arg, "utf8"));
    const { errors } = validate(data);
    if (errors.length) { errors.forEach((e) => console.log("ERROR: " + e)); process.exit(1); }
    save(data);
    console.log(`Wrote ${data.shows.length} shows to ${DATA_FILE}`);
  } else if (cmd === "sheet") {
    const { shows } = load();
    const rows = shows
      .filter((s) => s.status !== "cancelled" && (exhibitorFigure(s)?.n || 0) > 500)
      .filter((s) => !arg || startMonth(s) === arg);
    console.log(JSON.stringify(rows.map((s) => ({ id: s.id, tab: sheetTabName(startMonth(s)), month: startMonth(s), row: sheetRow(s) })), null, 2));
  } else {
    console.log("usage: datafile.mjs validate | export <out.json> | import <in.json> | sheet [YYYY-MM]");
    process.exit(2);
  }
}
