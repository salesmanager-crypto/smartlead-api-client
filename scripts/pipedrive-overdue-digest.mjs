#!/usr/bin/env node
// Builds the Pipedrive overdue-activity alert that goes to yoni@albertscott.com: every
// open activity assigned to one owner whose due date has passed, oldest first, plus
// anything that looks like a duplicate (the same person with the same open subject
// more than once). Writes an HTML email body and a plain-text alternative, and prints
// a one-line JSON summary on stdout for the routine's report.
//
// Two ways to feed it:
//   live      PIPEDRIVE_API_TOKEN + PIPEDRIVE_COMPANY_DOMAIN set (env or .env): pulls
//             open activities, persons, organizations and leads itself.
//   from MCP  the Pipedrive connector's raw responses saved to files:
//               --activities getActivities({owner_id, done:false, limit:500}) output
//               --persons    getPersons({ids:[...]}) output        (optional, names)
//               --orgs       getOrganizations({ids:[...]}) output  (optional, names)
//               --leads      getLeads({owner_id, limit:500}) output (optional, titles)
//
// Usage:
//   node scripts/pipedrive-overdue-digest.mjs --out dist/overdue [--owner 25109251]
//        [--today YYYY-MM-DD] [--domain albertscott]
//        [--activities a.json --persons p.json --orgs o.json --leads l.json]
// Writes dist/overdue.html and dist/overdue.txt.

import fs from "node:fs";
import path from "node:path";
import { PipedriveClient } from "../src/pipedrive.js";
import { loadEnv, today as todayNY, daysBetween, fmtDate } from "./pull/lib.mjs";

const YONI = 25109251;

function parseArgs(argv) {
  const out = {};
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (!a.startsWith("--")) continue;
    const [k, inline] = a.slice(2).split("=", 2);
    out[k] = inline ?? (argv[i + 1] && !argv[i + 1].startsWith("--") ? argv[++i] : true);
  }
  return out;
}

/** Accepts a bare array, {data:[...]}, or {data:{items:[...]}} as the connector returns. */
function rowsOf(file) {
  if (!file) return [];
  const j = JSON.parse(fs.readFileSync(file, "utf8"));
  if (Array.isArray(j)) return j;
  if (Array.isArray(j?.data)) return j.data;
  if (Array.isArray(j?.data?.items)) return j.data.items.map((x) => x.item ?? x);
  return [];
}

const esc = (s) =>
  String(s ?? "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const plain = (html) =>
  String(html || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/\s+/g, " ")
    .trim();

const clip = (s, n) => (s.length > n ? s.slice(0, n - 1).trimEnd() + "…" : s);

export function bucketOf(days) {
  if (days <= 7) return "1 to 7 days";
  if (days <= 30) return "8 to 30 days";
  return "Over 30 days";
}
const BUCKETS = ["Over 30 days", "8 to 30 days", "1 to 7 days"];

/**
 * Pure: turns raw rows into the digest model. Exported so it can be checked without
 * touching the network.
 */
export function buildDigest({ activities, persons = [], orgs = [], leads = [], owner, today }) {
  const personName = new Map(persons.map((p) => [p.id, p.name]));
  const orgName = new Map(orgs.map((o) => [o.id, o.name]));
  const leadTitle = new Map(leads.map((l) => [l.id, l.title]));

  const open = activities.filter(
    (a) => !a.done && !a.is_deleted && (owner == null || a.owner_id === owner || a.user_id === owner),
  );
  const rows = open
    .filter((a) => a.due_date && a.due_date < today)
    .map((a) => {
      const personId = a.person_id ?? a.participants?.find((p) => p.primary)?.person_id ?? null;
      const days = daysBetween(a.due_date, today);
      return {
        id: a.id,
        subject: a.subject || "(no subject)",
        type: a.type || "",
        due: a.due_date,
        dueTime: a.due_time || null,
        days,
        bucket: bucketOf(days),
        personId,
        person: personId ? personName.get(personId) || a.person_name || `Person #${personId}` : null,
        orgId: a.org_id ?? null,
        org: a.org_id ? orgName.get(a.org_id) || a.org_name || `Org #${a.org_id}` : null,
        lead: a.lead_id ? leadTitle.get(a.lead_id) || null : null,
        dealId: a.deal_id ?? null,
        note: clip(plain(a.note), 160),
      };
    })
    .sort((x, y) => y.days - x.days || x.id - y.id);

  // The same person carrying the same open subject twice is how a duplicate sync shows up.
  const seen = new Map();
  for (const a of open) {
    const personId = a.person_id ?? a.participants?.find((p) => p.primary)?.person_id;
    if (!personId) continue;
    const key = `${personId}|${(a.subject || "").trim().toLowerCase()}`;
    if (!seen.has(key)) seen.set(key, []);
    seen.get(key).push(a);
  }
  const duplicates = [...seen.values()]
    .filter((list) => list.length > 1)
    .map((list) => ({
      personId: list[0].person_id ?? list[0].participants?.find((p) => p.primary)?.person_id,
      person:
        personName.get(list[0].person_id) || `Person #${list[0].person_id ?? list[0].participants?.[0]?.person_id}`,
      subject: list[0].subject,
      activityIds: list.map((a) => a.id),
      dueDates: list.map((a) => a.due_date),
    }));

  const byBucket = Object.fromEntries(BUCKETS.map((b) => [b, rows.filter((r) => r.bucket === b).length]));
  return {
    today,
    owner,
    openCount: open.length,
    dueToday: open.filter((a) => a.due_date === today).length,
    overdue: rows,
    byBucket,
    oldestDays: rows[0]?.days ?? 0,
    duplicates,
  };
}

function link(domain, kind, id, text) {
  if (!domain || !id) return esc(text);
  return `<a href="https://${esc(domain)}.pipedrive.com/${kind}/${id}" style="color:#1a56db;text-decoration:none">${esc(text)}</a>`;
}

export function renderHtml(d, { domain } = {}) {
  const head = `<p style="margin:0 0 12px">You have <b>${d.overdue.length}</b> overdue Pipedrive ${
    d.overdue.length === 1 ? "activity" : "activities"
  } as of ${esc(fmtDate(d.today))}. The oldest is ${d.oldestDays} days past due. ${d.dueToday} more ${
    d.dueToday === 1 ? "is" : "are"
  } due today.</p>
<p style="margin:0 0 16px">${BUCKETS.map((b) => `${esc(b)}: <b>${d.byBucket[b]}</b>`).join(" &nbsp;|&nbsp; ")}</p>`;

  const th = (t) =>
    `<th align="left" style="padding:6px 8px;border-bottom:2px solid #ddd;font-size:12px;color:#555">${t}</th>`;
  const td = (t, extra = "") => `<td style="padding:6px 8px;border-bottom:1px solid #eee;font-size:13px;vertical-align:top${extra}">${t}</td>`;

  const sections = BUCKETS.filter((b) => d.byBucket[b]).map((b) => {
    const rows = d.overdue
      .filter((r) => r.bucket === b)
      .map((r) => {
        const who = [
          r.person ? link(domain, "person", r.personId, r.person) : "",
          r.org ? `<span style="color:#777">${link(domain, "organization", r.orgId, r.org)}</span>` : "",
        ]
          .filter(Boolean)
          .join("<br>");
        return `<tr>${td(`<b>${r.days}d</b>`, ";white-space:nowrap")}${td(esc(fmtDate(r.due, { month: "short", day: "numeric" })), ";white-space:nowrap")}${td(
          esc(r.type),
        )}${td(`${esc(r.subject)}${r.lead ? `<br><span style="color:#777">Lead: ${esc(r.lead)}</span>` : ""}${
          r.note ? `<br><span style="color:#999;font-size:12px">${esc(r.note)}</span>` : ""
        }`)}${td(who || "<span style=\"color:#999\">no contact linked</span>")}</tr>`;
      })
      .join("");
    return `<h3 style="margin:20px 0 6px;font-size:15px">${esc(b)} (${d.byBucket[b]})</h3>
<table cellspacing="0" cellpadding="0" style="border-collapse:collapse;width:100%">
<tr>${th("Late")}${th("Due")}${th("Type")}${th("Subject")}${th("Contact")}</tr>${rows}</table>`;
  });

  const dups = d.duplicates.length
    ? `<h3 style="margin:24px 0 6px;font-size:15px">Possible duplicates (${d.duplicates.length})</h3>
<p style="margin:0 0 6px;font-size:13px">Same contact, same open subject more than once. Usually one can be closed.</p>
<ul style="margin:0;padding-left:18px;font-size:13px">${d.duplicates
        .map(
          (x) =>
            `<li>${link(domain, "person", x.personId, x.person)}: "${esc(x.subject)}" x${x.activityIds.length} (activity ids ${x.activityIds.join(", ")}; due ${x.dueDates.join(", ")})</li>`,
        )
        .join("")}</ul>`
    : "";

  const empty = `<p>No overdue Pipedrive activities as of ${esc(fmtDate(d.today))}. ${d.dueToday} due today.</p>`;
  return `<div style="font-family:Arial,Helvetica,sans-serif;color:#222;max-width:860px">${
    d.overdue.length ? head + sections.join("") : empty
  }${dups}<p style="margin:24px 0 0;font-size:11px;color:#999">Open activities assigned to user ${d.owner}. Generated by scripts/pipedrive-overdue-digest.mjs.</p></div>`;
}

export function renderText(d) {
  if (!d.overdue.length) return `No overdue Pipedrive activities as of ${fmtDate(d.today)}. ${d.dueToday} due today.`;
  const lines = [
    `${d.overdue.length} overdue Pipedrive activities as of ${fmtDate(d.today)}. Oldest: ${d.oldestDays} days. Due today: ${d.dueToday}.`,
    BUCKETS.map((b) => `${b}: ${d.byBucket[b]}`).join(" | "),
  ];
  for (const b of BUCKETS) {
    const rows = d.overdue.filter((r) => r.bucket === b);
    if (!rows.length) continue;
    lines.push("", `${b.toUpperCase()} (${rows.length})`);
    for (const r of rows)
      lines.push(
        `- ${r.days}d late, due ${r.due}: ${r.type} "${r.subject}"${r.person ? `, ${r.person}` : ""}${r.org ? ` (${r.org})` : ""}`,
      );
  }
  if (d.duplicates.length) {
    lines.push("", `POSSIBLE DUPLICATES (${d.duplicates.length})`);
    for (const x of d.duplicates)
      lines.push(`- ${x.person}: "${x.subject}" x${x.activityIds.length} (ids ${x.activityIds.join(", ")})`);
  }
  return lines.join("\n");
}

async function loadLive(owner) {
  const pd = new PipedriveClient();
  const [activities, persons, orgs, leads] = await Promise.all([
    pd.listAllV2("/activities", { done: false, owner_id: owner }),
    pd.persons(),
    pd.organizations(),
    pd.leads(),
  ]);
  return { activities, persons, orgs, leads };
}

async function main() {
  loadEnv();
  const args = parseArgs(process.argv.slice(2));
  const owner = args.owner ? Number(args.owner) : YONI;
  const today = typeof args.today === "string" ? args.today : todayNY();
  const domain = typeof args.domain === "string" ? args.domain : process.env.PIPEDRIVE_COMPANY_DOMAIN || null;
  const outBase = typeof args.out === "string" ? args.out : "dist/overdue";

  const input = args.activities
    ? {
        activities: rowsOf(args.activities),
        persons: rowsOf(args.persons),
        orgs: rowsOf(args.orgs),
        leads: rowsOf(args.leads),
      }
    : await loadLive(owner);

  if (!input.activities.length) throw new Error("no activities in the input; refusing to send an empty alert");

  const digest = buildDigest({ ...input, owner, today });
  fs.mkdirSync(path.dirname(path.resolve(outBase)), { recursive: true });
  fs.writeFileSync(`${outBase}.html`, renderHtml(digest, { domain }));
  fs.writeFileSync(`${outBase}.txt`, renderText(digest) + "\n");
  console.log(
    JSON.stringify({
      today,
      owner,
      open: digest.openCount,
      overdue: digest.overdue.length,
      dueToday: digest.dueToday,
      oldestDays: digest.oldestDays,
      byBucket: digest.byBucket,
      duplicates: digest.duplicates.length,
      subject: `Pipedrive overdue activities - ${fmtDate(today)} (${digest.overdue.length})`,
      html: `${outBase}.html`,
      text: `${outBase}.txt`,
    }),
  );
}

if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((err) => {
    console.error(`overdue digest failed: ${err.message}`);
    process.exit(1);
  });
}
