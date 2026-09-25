#!/usr/bin/env node
/**
 * Semrush -> semrush.json (plain). Needs SEMRUSH_API_KEY; SEMRUSH_SITE_AUDIT_ID optional.
 *
 *   node scripts/pull/semrush.mjs
 *   SEMRUSH_FORCE=1 node scripts/pull/semrush.mjs   # pull again even if already pulled today
 *
 * Semrush API units cost money, so this runs one fixed call set, at most once per
 * Eastern day:
 *   1. domain_ranks for albertscott.com (1 row) to learn how many keywords it ranks for
 *   2. domain_organic for albertscott.com, capped at SEMRUSH_DOMAIN_LIMIT rows (default 100)
 *      -> our position, URL and volume for each tracked keyword
 *   3. phrase_organic with display_limit=1 for each keyword in docs/data/seo_keywords.json
 *      -> the #1 result (refuses to run above SEMRUSH_MAX_KEYWORDS, default 30)
 *   4. Site Audit snapshot info, only when SEMRUSH_SITE_AUDIT_ID is set
 * The unit balance is read before and after (that endpoint is free) to report unitsUsed.
 * GEO checks are not Semrush data: they are copied from seo_geo.json.
 */
import path from "node:path";
import { DATA_DIR, fetchRetry, readJson, today as todayFn, ymd, numOrNull } from "./lib.mjs";
import { runStandalone, isMain } from "./write.mjs";

const API = "https://api.semrush.com/";
const DOMAIN = "albertscott.com";
const DATABASE = "us";

async function call(key, params, label) {
  const url = new URL(API);
  for (const [k, v] of Object.entries({ ...params, key })) url.searchParams.set(k, v);
  const res = await fetchRetry(url, {}, { label: `Semrush ${label}` });
  const text = (await res.text()).trim();
  if (/^ERROR 50 ::/.test(text)) return []; // NOTHING FOUND
  if (!res.ok || /^ERROR \d+/.test(text)) throw new Error(`Semrush ${label}: ${res.status} ${text.slice(0, 120)}`);
  // rows are keyed by the export codes requested (Ph, Po, ...), read by position,
  // so a change in Semrush's human-readable header names cannot break the mapping
  const codes = String(params.export_columns).split(",");
  const [, ...lines] = text.split(/\r?\n/);
  return lines.filter(Boolean).map((l) => Object.fromEntries(l.split(";").map((v, i) => [codes[i], v])));
}

async function unitsLeft(key) {
  try {
    const res = await fetchRetry(`https://www.semrush.com/users/countapiunits.html?key=${encodeURIComponent(key)}`, {}, { label: "Semrush unit balance" });
    const n = Number((await res.text()).trim());
    return res.ok && Number.isFinite(n) ? n : null;
  } catch { return null; }
}

async function siteAudit(key, projectId) {
  const url = `${API}reports/v1/projects/${encodeURIComponent(projectId)}/siteaudit/info?key=${encodeURIComponent(key)}`;
  const res = await fetchRetry(url, {}, { label: "Semrush Site Audit" });
  const j = await res.json().catch(() => null);
  if (!res.ok || !j) throw new Error(`Semrush Site Audit: ${res.status}`);
  const q = numOrNull(j.quality?.value ?? j.quality);
  const delta = numOrNull(j.quality?.delta);
  const errors = numOrNull(j.errors), warnings = numOrNull(j.warnings), notices = numOrNull(j.notices);
  const when = j.last_audit ? ymd(new Date(Number(j.last_audit) || j.last_audit)) : null;
  const items = [
    { item: "Site Health score (Semrush Site Audit)", status: q != null && q >= 80 ? "good" : "bad",
      note: q == null ? "Score not returned." : `${q}%${delta != null ? ` (${delta >= 0 ? "+" : ""}${delta} since the previous audit)` : ""}${j.pages_crawled != null ? `, ${j.pages_crawled} pages crawled` : ""}${when ? `, audited ${when}` : ""}.` },
    { item: "Errors", status: errors ? "bad" : "good", note: errors == null ? "Not returned." : `${errors} error${errors === 1 ? "" : "s"} in the latest crawl.` },
    { item: "Warnings", status: warnings ? "bad" : "good", note: warnings == null ? "Not returned." : `${warnings} warning${warnings === 1 ? "" : "s"}${notices != null ? `, ${notices} notices` : ""}.` },
  ];
  return { source: "semrush", checkedAt: when || new Date().toISOString().slice(0, 10), items };
}

export async function pull(env, ctx = {}) {
  const prev = readJson(path.join(DATA_DIR, "semrush.json"));
  const geo = readJson(path.join(DATA_DIR, "seo_geo.json"), { checkedAt: null, baselineAt: null, sources: [] });
  const manualHealth = readJson(path.join(DATA_DIR, "seo_health_manual.json"), { checkedAt: null, items: [] });
  const tracked = readJson(path.join(DATA_DIR, "seo_keywords.json"), []);

  // one call set per Eastern day
  if (prev?.pulledAt && ymd(new Date(prev.pulledAt)) === todayFn() && env.SEMRUSH_FORCE !== "1") {
    ctx.records = prev.keywords?.length ?? null;
    ctx.note = "already pulled today; kept this morning's data (SEMRUSH_FORCE=1 to pull again)";
    ctx.skipped = true;
    return null;
  }

  if (!env.SEMRUSH_API_KEY) throw new Error("SEMRUSH_API_KEY not set");
  const key = env.SEMRUSH_API_KEY;
  const maxKw = Number(env.SEMRUSH_MAX_KEYWORDS || 30);
  if (tracked.length > maxKw) throw new Error(`seo_keywords.json has ${tracked.length} keywords, above the ${maxKw} cap (SEMRUSH_MAX_KEYWORDS). Each costs about 10 units a day.`);

  const before = await unitsLeft(key);

  const ranks = await call(key, { type: "domain_ranks", domain: DOMAIN, database: DATABASE, export_columns: "Dn,Or" }, "domain_ranks");
  const rankedCount = numOrNull(ranks[0]?.Or) ?? 0;
  const limit = Math.min(rankedCount, Number(env.SEMRUSH_DOMAIN_LIMIT || 100));
  const ours = limit
    ? await call(key, { type: "domain_organic", domain: DOMAIN, database: DATABASE, display_limit: limit, display_sort: "po_asc", export_columns: "Ph,Po,Ur,Nq" }, "domain_organic")
    : [];
  const byPhrase = new Map(ours.map((r) => [String(r.Ph || "").toLowerCase(), r]));

  const keywords = [];
  for (const k of tracked) {
    const top = await call(key, { type: "phrase_organic", phrase: k.q, database: DATABASE, display_limit: 1, export_columns: "Dn,Ur" }, `phrase_organic "${k.q}"`);
    const mine = byPhrase.get(k.q.toLowerCase());
    keywords.push({
      q: k.q,
      pos: mine ? numOrNull(mine.Po) : null,
      top: top[0]?.Dn || null,
      branded: !!k.branded,
      url: mine?.Ur || null,
      volume: mine ? numOrNull(mine.Nq) : null,
    });
  }

  const health = env.SEMRUSH_SITE_AUDIT_ID
    ? await siteAudit(key, env.SEMRUSH_SITE_AUDIT_ID)
    : { source: "manual", checkedAt: manualHealth.checkedAt, items: manualHealth.items };

  const after = await unitsLeft(key);
  const estimated = 10 * (ranks.length + ours.length + keywords.filter((k) => k.top).length);
  ctx.records = keywords.length;
  ctx.note = health.source === "manual" ? "site health from seo_health_manual.json (no SEMRUSH_SITE_AUDIT_ID)" : null;

  return {
    pulledAt: new Date().toISOString(),
    baselineAt: prev?.baselineAt || geo.baselineAt || null,
    domain: DOMAIN,
    database: DATABASE,
    rankedKeywords: rankedCount,
    unitsUsed: before != null && after != null ? before - after : estimated,
    unitsLeft: after,
    keywords,
    geo,
    health,
  };
}

if (isMain(import.meta.url)) await runStandalone("semrush", pull);
