#!/usr/bin/env node
// Builds the "Reply Triage" HTML report: every Smartlead Master Inbox reply in the
// trailing N days (default 7), with the category assigned to each lead and the reply
// text itself. Designed to be run standalone by a scheduled routine, then published
// via the Artifact tool to a fixed URL so the link never changes.
//
// Usage: node scripts/daily-inbox-report.mjs [outputPath] [--days=7]
//
// Reads SMARTLEAD_API_KEY / SMARTLEAD_BASE_URL from the environment (via .env if
// present, per src/client.js). Category id -> name is fetched live from
// /leads/fetch-categories on every run rather than hardcoded, so a renamed or new
// category in Smartlead is picked up automatically.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const args = process.argv.slice(2);
const daysArg = args.find((a) => a.startsWith("--days="));
const DAYS = daysArg ? Number(daysArg.split("=")[1]) : 7;
const outputPath =
  args.find((a) => !a.startsWith("--")) ||
  path.join(__dirname, "..", "dist", "reply-triage.html");

function stripHtml(html) {
  if (!html) return "";
  let text = html
    .replace(/<style[\s\S]*?<\/style>/gi, "")
    .replace(/<script[\s\S]*?<\/script>/gi, "")
    .replace(/<br\s*\/?>/gi, "\n")
    .replace(/<\/p>/gi, "\n\n")
    .replace(/<\/div>/gi, "\n")
    .replace(/<[^>]+>/g, "");
  text = text
    .replace(/&nbsp;/g, " ")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&#39;/g, "'")
    .replace(/&quot;/g, '"');
  text = text.replace(/\n{3,}/g, "\n\n").replace(/[ \t]+\n/g, "\n").trim();
  // drop lone surrogates / the replacement character — mangled emoji in source data
  // that would otherwise trip strict UTF-8 re-encoding when the artifact is published.
  text = text.replace(/[\uD800-\uDFFF]/g, "").replace(/�/g, "");
  return text;
}

function cleanReply(text) {
  const markers = [/\nOn .{0,80} wrote:\n/i, /\n-{2,}\s*Original Message\s*-{2,}/i, /\nFrom:\s/i];
  let cut = text;
  for (const m of markers) {
    const idx = cut.search(m);
    if (idx > 20) cut = cut.slice(0, idx);
  }
  return cut.trim();
}

function esc(s) {
  return String(s || "").replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function splitBody(text, limit = 260) {
  if (text.length <= limit) return { preview: text, rest: "" };
  let cut = text.slice(0, limit);
  const lastSpace = cut.lastIndexOf(" ");
  if (lastSpace > limit * 0.6) cut = cut.slice(0, lastSpace);
  return { preview: cut, rest: text.slice(cut.length) };
}

function fmtTime(iso) {
  const d = new Date(iso);
  return (
    d.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      timeZone: "America/New_York",
    }) + " ET"
  );
}

function fmtDateShort(d) {
  return d.toLocaleString("en-US", { month: "short", day: "numeric", timeZone: "America/New_York" });
}

async function main() {
  const client = new SmartleadClient();
  const now = new Date();
  const windowStart = new Date(now.getTime() - DAYS * 24 * 60 * 60 * 1000);

  // ---- category id -> name map, fetched live ----
  const categories = await client.getLeadCategories();
  const CAT_NAME = {};
  const CAT_TONE = {};
  for (const c of categories) {
    CAT_NAME[c.id] = c.name;
    CAT_TONE[c.name] =
      c.sentiment_type === "positive" ? "positive" : c.sentiment_type === "negative" ? "negative" : "neutral";
  }
  // a few labels used by the categorization automation aren't tagged with a
  // sentiment_type in Smartlead's own table — bucket them by known intent.
  const TONE_OVERRIDE = { "Follow Up": "positive", "Meeting Request": "positive", Client: "positive", Unqualified: "negative" };
  Object.assign(CAT_TONE, TONE_OVERRIDE);

  // ---- paginate the Master Inbox for the window ----
  const limit = 20;
  let offset = 0;
  let all = [];
  while (true) {
    const body = {
      offset,
      limit,
      sortBy: "REPLY_TIME_DESC",
      filters: { emailStatus: "Replied", replyTimeBetween: [windowStart.toISOString(), now.toISOString()] },
    };
    const res = await client.getMasterInboxReplies(body, true);
    const items = res.data || [];
    all = all.concat(items);
    if (items.length < limit) break;
    offset += limit;
    if (offset > 5000) break; // sanity backstop
  }

  // ---- shape rows ----
  const rows = all.map((item) => {
    const history = item.email_history || [];
    const replies = history.filter((h) => h.type === "REPLY");
    let target = null;
    for (const r of replies) {
      const t = new Date(r.time);
      if (t >= windowStart && t <= now) {
        if (!target || new Date(r.time) > new Date(target.time)) target = r;
      }
    }
    if (!target && replies.length) target = replies[replies.length - 1];

    const bodyText = target ? cleanReply(stripHtml(target.email_body)) : "";
    const subject = target?.subject || history.find((h) => h.type === "SENT")?.subject || "";
    const categoryName = item.lead_category_id != null ? CAT_NAME[item.lead_category_id] || `Unknown (${item.lead_category_id})` : null;

    return {
      reply_time: item.last_reply_time,
      campaign_name: item.email_campaign_name,
      is_rachel: (item.email_campaign_name || "").startsWith("Rachel -"),
      lead_name: `${item.lead_first_name || ""} ${item.lead_last_name || ""}`.trim(),
      lead_email: item.lead_email,
      category_name: categoryName,
      subject,
      body: bodyText || "(no reply text captured)",
    };
  });
  rows.sort((a, b) => new Date(b.reply_time) - new Date(a.reply_time));

  // ---- summary counts ----
  const counts = {};
  rows.forEach((r) => {
    const key = r.category_name || "Uncategorized";
    counts[key] = (counts[key] || 0) + 1;
  });
  const total = rows.length;
  const catOrder = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  const toneOf = (name) => (name === "Uncategorized" ? "neutral" : CAT_TONE[name] || "neutral");

  const legendHtml = catOrder
    .map(([name, count]) => {
      const tone = toneOf(name);
      return `<button class="chip chip-${tone}" data-cat="${esc(name)}" type="button" aria-pressed="true">
      <span class="chip-dot"></span>${esc(name)} <span class="chip-count">${count}</span>
    </button>`;
    })
    .join("\n");

  const barHtml = catOrder
    .map(([name, count]) => {
      const tone = toneOf(name);
      const pct = total ? (count / total) * 100 : 0;
      return `<div class="bar-seg bar-${tone}" style="flex-basis:${pct}%" title="${esc(name)}: ${count}"></div>`;
    })
    .join("\n");

  const rowsHtml = rows
    .map((r) => {
      const cat = r.category_name || "Uncategorized";
      const tone = toneOf(cat);
      const { preview, rest } = splitBody(r.body);
      const searchBlob = esc(`${r.lead_name} ${r.lead_email} ${r.campaign_name} ${cat} ${r.body}`.toLowerCase());
      return `
    <article class="row" data-cat="${esc(cat)}" data-search="${searchBlob}">
      <div class="row-meta">
        <div class="row-who">
          <span class="who-name">${esc(r.lead_name || r.lead_email)}</span>
          <span class="who-email">${esc(r.lead_email)}</span>
        </div>
        <div class="row-sub">
          <span class="row-campaign">${esc(r.campaign_name)}${r.is_rachel ? '<span class="track-tag">Rachel track</span>' : ""}</span>
          <time class="row-time" datetime="${esc(r.reply_time)}">${fmtTime(r.reply_time)}</time>
        </div>
      </div>
      <div class="row-cat">
        <span class="pill pill-${tone}">${esc(cat)}</span>
      </div>
      <div class="row-body">
        <p class="subject">${esc(r.subject || "(no subject)")}</p>
        <p class="preview">${esc(preview)}${rest ? "…" : ""}</p>
        ${rest ? `<details class="more"><summary>Show full reply</summary><p class="rest">${esc(rest)}</p></details>` : ""}
      </div>
    </article>`;
    })
    .join("\n");

  const refreshedIso = now.toISOString();
  const refreshedLabel =
    now.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      timeZone: "America/New_York",
    }) + " ET";
  const rangeLabel = `${fmtDateShort(windowStart)}–${fmtDateShort(now)}, ${now.getFullYear()}`;

  const html = `<title>Reply Triage</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,500;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #f3f5f4;
    --surface: #ffffff;
    --surface-2: #eceef0;
    --border: #dde1e0;
    --ink: #1c2521;
    --ink-dim: #566058;
    --ink-faint: #8a938c;
    --accent: #2f5d50;
    --accent-soft: #e4ede9;
    --pos: #2f7d5d;
    --pos-soft: #e3f1e9;
    --neg: #b23a48;
    --neg-soft: #f8e6e7;
    --neu: #6b7280;
    --neu-soft: #eceef0;
    --shadow: 0 1px 2px rgba(28, 37, 33, 0.06), 0 1px 1px rgba(28, 37, 33, 0.04);
    --font-display: "Source Serif 4", Georgia, "Times New Roman", serif;
    --font-body: "IBM Plex Sans", -apple-system, "Segoe UI", sans-serif;
    --font-mono: "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #14181a; --surface: #1c2224; --surface-2: #232a2c; --border: #323b3d;
      --ink: #e9ede9; --ink-dim: #a9b2ac; --ink-faint: #77827c; --accent: #7fbaa2;
      --accent-soft: #223330; --pos: #6fbf95; --pos-soft: #1f342a; --neg: #e08d95;
      --neg-soft: #382223; --neu: #99a1a8; --neu-soft: #262d2f; --shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
    }
  }
  :root[data-theme="dark"] {
    --bg: #14181a; --surface: #1c2224; --surface-2: #232a2c; --border: #323b3d;
    --ink: #e9ede9; --ink-dim: #a9b2ac; --ink-faint: #77827c; --accent: #7fbaa2;
    --accent-soft: #223330; --pos: #6fbf95; --pos-soft: #1f342a; --neg: #e08d95;
    --neg-soft: #382223; --neu: #99a1a8; --neu-soft: #262d2f; --shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  }

  * { box-sizing: border-box; }
  body {
    margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-body);
    font-size: 15px; line-height: 1.55; -webkit-font-smoothing: antialiased;
  }
  .wrap { max-width: 920px; margin: 0 auto; padding: 48px 24px 80px; }
  header.page { margin-bottom: 32px; }
  .eyebrow-row { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin: 0 0 10px; }
  .eyebrow { font-family: var(--font-mono); font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase; color: var(--accent); margin: 0; }
  .refreshed { font-family: var(--font-mono); font-size: 11.5px; color: var(--ink-faint); }
  h1 { font-family: var(--font-display); font-weight: 600; font-size: 34px; line-height: 1.15; margin: 0 0 10px; text-wrap: balance; color: var(--ink); }
  .dek { color: var(--ink-dim); max-width: 62ch; margin: 0; font-size: 15.5px; }
  .dek strong { color: var(--ink); font-weight: 600; }

  .summary { background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 22px 24px; margin: 28px 0 30px; box-shadow: var(--shadow); }
  .summary-top { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; flex-wrap: wrap; margin-bottom: 16px; }
  .summary-total { font-family: var(--font-mono); font-size: 13px; color: var(--ink-faint); }
  .summary-total b { font-size: 20px; color: var(--ink); font-weight: 600; font-variant-numeric: tabular-nums; }
  .bar { display: flex; width: 100%; height: 10px; border-radius: 6px; overflow: hidden; background: var(--surface-2); margin-bottom: 16px; }
  .bar-seg { height: 100%; }
  .bar-positive { background: var(--pos); }
  .bar-negative { background: var(--neg); }
  .bar-neutral { background: var(--neu); }

  .chips { display: flex; flex-wrap: wrap; gap: 8px; }
  .chip { display: inline-flex; align-items: center; gap: 6px; font-family: var(--font-body); font-size: 13px; font-weight: 500; padding: 6px 12px 6px 10px; border-radius: 999px; border: 1px solid var(--border); background: var(--surface-2); color: var(--ink-dim); cursor: pointer; transition: opacity 0.15s ease, background 0.15s ease; }
  .chip-dot { width: 7px; height: 7px; border-radius: 50%; background: var(--neu); flex: none; }
  .chip-positive .chip-dot { background: var(--pos); }
  .chip-negative .chip-dot { background: var(--neg); }
  .chip-count { font-family: var(--font-mono); color: var(--ink-faint); font-variant-numeric: tabular-nums; }
  .chip[aria-pressed="false"] { opacity: 0.4; }
  .chip:hover { background: var(--accent-soft); }
  .chip:focus-visible, .search:focus-visible, summary:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }

  .controls { display: flex; gap: 10px; align-items: center; margin-bottom: 20px; }
  .search { flex: 1; font-family: var(--font-body); font-size: 14px; padding: 10px 14px; border-radius: 10px; border: 1px solid var(--border); background: var(--surface); color: var(--ink); }
  .search::placeholder { color: var(--ink-faint); }
  .result-count { font-family: var(--font-mono); font-size: 12px; color: var(--ink-faint); white-space: nowrap; }

  .rows { display: flex; flex-direction: column; gap: 12px; }
  .row { display: grid; grid-template-columns: 1fr auto; gap: 4px 16px; background: var(--surface); border: 1px solid var(--border); border-radius: 12px; padding: 16px 18px; box-shadow: var(--shadow); }
  .row.is-hidden { display: none; }
  .row-meta { grid-column: 1; }
  .row-who { display: flex; align-items: baseline; gap: 8px; flex-wrap: wrap; }
  .who-name { font-weight: 600; color: var(--ink); }
  .who-email { font-family: var(--font-mono); font-size: 12.5px; color: var(--ink-faint); }
  .row-sub { display: flex; align-items: center; gap: 10px; margin-top: 2px; flex-wrap: wrap; }
  .row-campaign { font-size: 12.5px; color: var(--ink-dim); }
  .track-tag { margin-left: 8px; font-family: var(--font-mono); font-size: 10.5px; letter-spacing: 0.04em; text-transform: uppercase; color: var(--ink-faint); border: 1px solid var(--border); border-radius: 4px; padding: 1px 5px; }
  .row-time { font-family: var(--font-mono); font-size: 12px; color: var(--ink-faint); font-variant-numeric: tabular-nums; }
  .row-cat { grid-column: 2; align-self: start; }
  .pill { display: inline-block; font-size: 12px; font-weight: 600; padding: 4px 11px; border-radius: 999px; white-space: nowrap; }
  .pill-positive { background: var(--pos-soft); color: var(--pos); }
  .pill-negative { background: var(--neg-soft); color: var(--neg); }
  .pill-neutral { background: var(--neu-soft); color: var(--neu); }
  .row-body { grid-column: 1 / -1; margin-top: 8px; padding-top: 12px; border-top: 1px solid var(--border); }
  .subject { margin: 0 0 6px; font-size: 12.5px; font-weight: 600; color: var(--ink-dim); }
  .subject::before { content: "Re: "; font-weight: 400; color: var(--ink-faint); }
  .preview, .rest { margin: 0; white-space: pre-wrap; color: var(--ink); font-size: 14.5px; }
  .rest { margin-top: 8px; }
  details.more { margin-top: 6px; }
  details.more summary { cursor: pointer; font-family: var(--font-mono); font-size: 12px; color: var(--accent); list-style: none; display: inline-flex; align-items: center; gap: 4px; }
  details.more summary::-webkit-details-marker { display: none; }
  details.more summary::after { content: "→ show more"; }
  details.more[open] summary::after { content: "← show less"; }
  .empty-state { text-align: center; padding: 48px 0; color: var(--ink-faint); font-family: var(--font-mono); font-size: 13px; display: none; }
  footer.page { margin-top: 40px; padding-top: 20px; border-top: 1px solid var(--border); font-family: var(--font-mono); font-size: 12px; color: var(--ink-faint); }
  @media (max-width: 560px) { .row { grid-template-columns: 1fr; } .row-cat { grid-column: 1; } }
</style>

<div class="wrap">
  <header class="page">
    <div class="eyebrow-row">
      <p class="eyebrow">Smartlead master inbox · ${esc(rangeLabel)}</p>
      <span class="refreshed">refreshed ${esc(refreshedLabel)}</span>
    </div>
    <h1>Reply Triage</h1>
    <p class="dek">Every inbound reply Smartlead logged in the trailing ${DAYS} days, alongside the
      category assigned and the reply text itself. <strong>${total} replies</strong> across all active
      campaigns — click a category chip to isolate it, or search by name, company, or wording. Refreshes
      automatically once a day.</p>
  </header>

  <section class="summary">
    <div class="summary-top">
      <span class="summary-total"><b>${total}</b> replies categorized</span>
      <span class="summary-total">${catOrder.length} categories in use</span>
    </div>
    <div class="bar">${barHtml}</div>
    <div class="chips" id="chips">${legendHtml}</div>
  </section>

  <div class="controls">
    <input class="search" id="search" type="text" placeholder="Search by name, company, or reply text…" autocomplete="off">
    <span class="result-count" id="resultCount"></span>
  </div>

  <section class="rows" id="rows">
    ${rowsHtml}
  </section>
  <p class="empty-state" id="emptyState">No replies match that filter.</p>

  <footer class="page">
    Source: Smartlead <code>master-inbox/inbox-replies</code>, replies with <code>last_reply_time</code>
    in the trailing ${DAYS} days as of this refresh (<time datetime="${esc(refreshedIso)}">${esc(refreshedLabel)}</time>).
    Categories reflect whatever was on the lead at fetch time — either set by the scheduled triage
    automation or Smartlead's own reply handling.
  </footer>
</div>

<script>
  (function () {
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip'));
    var rows = Array.prototype.slice.call(document.querySelectorAll('.row'));
    var search = document.getElementById('search');
    var resultCount = document.getElementById('resultCount');
    var emptyState = document.getElementById('emptyState');
    var activeCats = new Set(chips.map(function (c) { return c.dataset.cat; }));

    function apply() {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      rows.forEach(function (row) {
        var matchesCat = activeCats.has(row.dataset.cat);
        var matchesSearch = !q || row.dataset.search.indexOf(q) !== -1;
        var visible = matchesCat && matchesSearch;
        row.classList.toggle('is-hidden', !visible);
        if (visible) shown++;
      });
      resultCount.textContent = shown + ' / ' + rows.length + ' shown';
      emptyState.style.display = shown === 0 ? 'block' : 'none';
    }

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var cat = chip.dataset.cat;
        if (activeCats.has(cat)) { activeCats.delete(cat); chip.setAttribute('aria-pressed', 'false'); }
        else { activeCats.add(cat); chip.setAttribute('aria-pressed', 'true'); }
        apply();
      });
    });

    search.addEventListener('input', apply);
    apply();
  })();
</script>
`;

  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html);
  console.error(`Wrote ${outputPath} (${Buffer.byteLength(html)} bytes, ${total} replies, ${catOrder.length} categories)`);
}

main().catch((err) => {
  console.error("daily-inbox-report failed:", err);
  process.exit(1);
});
