#!/usr/bin/env node
/**
 * Renders a campaign-analytics-report.mjs JSON output into a single
 * self-contained HTML dashboard (no external CSS/JS/fonts — safe to open
 * directly or publish as a Claude Artifact).
 *
 * Usage:
 *   node scripts/build-analytics-dashboard.mjs <report.json> [out.html]
 */

import fs from "node:fs";
import path from "node:path";

const [, , inPath, outPathArg] = process.argv;
if (!inPath) {
  console.error("Usage: node scripts/build-analytics-dashboard.mjs <report.json> [out.html]");
  process.exit(1);
}

const report = JSON.parse(fs.readFileSync(path.resolve(inPath), "utf8"));
const outPath = path.resolve(outPathArg || inPath.replace(/\.json$/, ".html"));

fs.writeFileSync(outPath, renderHtml(report));
console.error(`Wrote ${outPath}`);

// ---------------------------------------------------------------------------

function renderHtml(report) {
  const dataJson = JSON.stringify(report).replace(/</g, "\\u003c");
  return `<title>Campaign Analytics Report</title>
<style>
  .viz-root {
    color-scheme: light;
    --surface-1: #fcfcfb;
    --surface-2: #f9f9f7;
    --text-primary: #0b0b0b;
    --text-secondary: #52514e;
    --text-muted: #898781;
    --gridline: #e1e0d9;
    --baseline: #c3c2b7;
    --border: rgba(11,11,11,0.10);
    --good: #0ca30c;
    --warning: #fab219;
    --serious: #ec835a;
    --critical: #d03b3b;
    --accent: #2a78d6;
  }
  @media (prefers-color-scheme: dark) {
    :root:where(:not([data-theme="light"])) .viz-root {
      color-scheme: dark;
      --surface-1: #1a1a19;
      --surface-2: #0d0d0d;
      --text-primary: #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted: #898781;
      --gridline: #2c2c2a;
      --baseline: #383835;
      --border: rgba(255,255,255,0.10);
      --good: #0ca30c;
      --warning: #fab219;
      --serious: #ec835a;
      --critical: #e66767;
      --accent: #3987e5;
    }
  }
  :root[data-theme="dark"] .viz-root {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --surface-2: #0d0d0d;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted: #898781;
    --gridline: #2c2c2a;
    --baseline: #383835;
    --border: rgba(255,255,255,0.10);
    --good: #0ca30c;
    --warning: #fab219;
    --serious: #ec835a;
    --critical: #e66767;
    --accent: #3987e5;
  }

  * { box-sizing: border-box; }
  body { margin: 0; background: var(--surface-2); }
  .viz-root {
    font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
    background: var(--surface-2);
    color: var(--text-primary);
    padding: 0 24px 40px;
    max-width: 1180px;
    margin: 0 auto;
  }
  .topbar { height: 3px; background: var(--accent); margin: 0 -24px 24px; border-radius: 0 0 3px 3px; }
  .eyebrow { display: block; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }
  h1 { font-size: 1.6rem; margin: 0 0 4px; text-wrap: balance; }
  h2 { font-size: 1.05rem; margin: 0 0 12px; display: flex; align-items: center; gap: 8px; }
  h2::before { content: ""; width: 8px; height: 8px; border-radius: 2px; background: var(--accent); flex: 0 0 auto; }
  .subtitle { color: var(--text-secondary); font-size: 0.9rem; margin: 0 0 20px; }

  .nav { display: flex; flex-wrap: wrap; gap: 4px 18px; margin: 0 0 28px; padding: 10px 0; border-top: 1px solid var(--gridline); border-bottom: 1px solid var(--gridline); }
  .nav a { color: var(--text-secondary); text-decoration: none; font-size: 0.82rem; font-weight: 500; }
  .nav a:hover, .nav a:focus-visible { color: var(--accent); }

  section { margin-bottom: 32px; }
  section:last-of-type { margin-bottom: 0; }
  .section-title { font-size: 0.78rem; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; color: var(--text-muted); margin: 0 0 12px; }

  .card {
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
  }
  .card:last-child { margin-bottom: 0; }

  .summary-card {
    background: color-mix(in srgb, var(--accent) 7%, var(--surface-1));
    border: 1px solid color-mix(in srgb, var(--accent) 25%, var(--border));
    border-radius: 12px;
    padding: 18px 22px;
    margin-bottom: 16px;
  }
  .summary-list { margin: 0; padding: 0; list-style: none; display: flex; flex-direction: column; gap: 10px; }
  .summary-list li { display: flex; gap: 10px; align-items: baseline; font-size: 0.95rem; line-height: 1.45; }
  .summary-list li::before { content: "→"; color: var(--accent); font-weight: 700; flex: 0 0 auto; }
  .summary-list strong { font-variant-numeric: tabular-nums; }
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
  .kpi-tile { background: var(--surface-1); border: 1px solid var(--border); border-radius: 12px; padding: 14px 16px; }
  .kpi-label { font-size: 0.78rem; color: var(--text-secondary); margin-bottom: 6px; }
  .kpi-value { font-size: 1.7rem; font-weight: 600; }
  .kpi-value.status-warning { color: var(--warning); }
  .kpi-value.status-critical { color: var(--critical); }

  .flag-row { display: flex; align-items: flex-start; gap: 10px; padding: 8px 0; border-bottom: 1px solid var(--gridline); font-size: 0.9rem; }
  .flag-row:last-child { border-bottom: none; }
  .dot { width: 10px; height: 10px; border-radius: 50%; margin-top: 4px; flex: 0 0 auto; }
  .dot.critical { background: var(--critical); }
  .dot.warning { background: var(--warning); }
  .dot.good { background: var(--good); }
  .dot.info { background: var(--text-muted); }
  .flag-campaign { font-weight: 600; margin-right: 6px; }

  .bar-row { display: grid; grid-template-columns: 220px 1fr 60px; align-items: center; gap: 10px; padding: 6px 0; font-size: 0.85rem; }
  .bar-name { color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .bar-track { background: var(--gridline); border-radius: 4px; height: 20px; position: relative; overflow: hidden; }
  .bar-fill { height: 100%; border-radius: 4px; min-width: 3px; }
  .bar-fill.good { background: var(--good); }
  .bar-fill.warning { background: var(--warning); }
  .bar-fill.critical { background: var(--critical); }
  .bar-value { text-align: right; font-variant-numeric: tabular-nums; color: var(--text-primary); }

  .legend { display: flex; gap: 18px; font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 14px; }
  .legend-item { display: flex; align-items: center; gap: 6px; }

  table { border-collapse: collapse; width: 100%; font-size: 0.85rem; }
  th, td { text-align: left; padding: 7px 10px; border-bottom: 1px solid var(--gridline); white-space: nowrap; }
  th { color: var(--text-muted); font-weight: 600; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.02em; }
  td.num { text-align: right; font-variant-numeric: tabular-nums; }
  tr:hover td { background: var(--surface-2); }
  .table-scroll { overflow-x: auto; }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 999px; font-size: 0.72rem; font-weight: 600; }
  .badge.critical { background: color-mix(in srgb, var(--critical) 18%, transparent); color: var(--critical); }
  .badge.warning { background: color-mix(in srgb, var(--warning) 22%, transparent); color: var(--text-primary); }
  .badge.good { background: color-mix(in srgb, var(--good) 16%, transparent); color: var(--good); }
  .badge.info { background: var(--surface-2); color: var(--text-secondary); }
  .muted { color: var(--text-muted); font-size: 0.8rem; }
  .empty { color: var(--text-muted); font-size: 0.85rem; padding: 8px 0; }
  .footer-note { color: var(--text-muted); font-size: 0.78rem; margin-top: 8px; }
  .source-badge { display: inline-block; background: var(--surface-2); border: 1px solid var(--border); border-radius: 999px; padding: 2px 10px; font-size: 0.72rem; color: var(--text-secondary); margin-left: 8px; }

  @media print {
    .nav { display: none; }
    .card, .summary-card { break-inside: avoid; border: 1px solid #ccc; }
    section { break-inside: avoid-page; }
    body { background: #fff; }
  }
</style>
<div class="viz-root" id="app"></div>
<script>
  const REPORT = ${dataJson};

  function pct(n) { return n === null || n === undefined ? "—" : (n * 100).toFixed(1) + "%"; }
  function num(n) { return n.toLocaleString(); }
  function esc(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  function severityFor(value, warn, critical, higherIsWorse) {
    if (value === null || value === undefined) return null;
    if (higherIsWorse) {
      if (value >= critical) return "critical";
      if (value >= warn) return "warning";
      return "good";
    }
    if (value <= critical) return "critical";
    if (value <= warn) return "warning";
    return "good";
  }

  function kpiTile(label, value, status) {
    return \`<div class="kpi-tile"><div class="kpi-label">\${esc(label)}</div><div class="kpi-value\${status ? " status-" + status : ""}">\${esc(value)}</div></div>\`;
  }

  function renderKpis(r) {
    const g = r.global;
    const t = r.thresholds;
    const openLabel = g.campaignsWithOpenTrackingOff ? \`Open rate (\${g.campaignsWithOpenTrackingOff} campaign\${g.campaignsWithOpenTrackingOff === 1 ? "" : "s"} untracked)\` : "Open rate";
    const clickLabel = g.campaignsWithClickTrackingOff ? \`Click rate (\${g.campaignsWithClickTrackingOff} untracked)\` : "Click rate";
    return [
      kpiTile("Emails sent", num(g.sent)),
      kpiTile(openLabel, pct(g.openRate), severityFor(g.openRate, t.openRateWarning, t.openRateCritical, false)),
      kpiTile(clickLabel, pct(g.clickRate)),
      kpiTile("Reply rate", pct(g.replyRate)),
      kpiTile("Bounce rate", pct(g.bounceRate), severityFor(g.bounceRate, t.bounceRateWarning, t.bounceRateCritical, true)),
      kpiTile("Unsubscribe rate", pct(g.unsubRate), severityFor(g.unsubRate, t.unsubRateWarning, t.unsubRateCritical, true)),
    ].join("");
  }

  function renderExecSummary(r) {
    const flagged = r.campaigns.filter((c) => c.flags.some((f) => f.level !== "info"));
    const bullets = [];
    bullets.push(\`<strong>\${flagged.length} of \${r.campaigns.length}</strong> campaigns are flagged for bounce rate, open rate, or unsubscribe issues.\`);
    const worstBounce = [...r.campaigns].filter((c) => c.metrics.sent > 0).sort((a, b) => b.metrics.bounceRate - a.metrics.bounceRate)[0];
    if (worstBounce && worstBounce.metrics.bounceRate >= r.thresholds.bounceRateWarning) {
      bullets.push(\`<strong>\${esc(worstBounce.name)}</strong> has the highest bounce rate at <strong>\${pct(worstBounce.metrics.bounceRate)}</strong> — active sender-reputation risk.\`);
    }
    const nonOpeners = r.leadFlags.repeatNonOpeners.length;
    if (nonOpeners) {
      const share = r.leadCount ? nonOpeners / r.leadCount : 0;
      bullets.push(\`<strong>\${num(nonOpeners)} leads</strong> (\${pct(share)} of everyone contacted) have been emailed \${r.thresholds.minSendsForNonOpenerFlag}+ times with zero opens — the largest targeting-refinement opportunity in this window.\`);
    }
    const bouncers = r.leadFlags.chronicBouncers.length;
    if (bouncers) bullets.push(\`<strong>\${num(bouncers)} addresses</strong> are bouncing and still active in campaigns — block-list candidates.\`);
    if (r.inboxHealth.length) bullets.push(\`<strong>\${r.inboxHealth.length} sending inbox\${r.inboxHealth.length === 1 ? "" : "es"}</strong> need attention (see Inbox Health).\`);
    if (!bullets.length) bullets.push("Nothing flagged this window — every campaign is within the healthy thresholds.");
    return \`<ul class="summary-list">\${bullets.map((b) => \`<li>\${b}</li>\`).join("")}</ul>\`;
  }

  const FLAG_LABELS = {
    "high-bounce-rate": "Bounce",
    "low-open-rate": "Open",
    "high-unsub-rate": "Unsub",
    "no-sends": "No sends",
  };

  function renderAtRiskTable(r) {
    const order = { critical: 0, warning: 1 };
    const flagged = r.campaigns
      .filter((c) => c.flags.some((f) => f.level !== "info"))
      .sort((a, b) => {
        const aw = Math.min(...a.flags.filter((f) => f.level !== "info").map((f) => order[f.level] ?? 2));
        const bw = Math.min(...b.flags.filter((f) => f.level !== "info").map((f) => order[f.level] ?? 2));
        return aw - bw || b.metrics.bounceRate - a.metrics.bounceRate;
      });
    if (!flagged.length) return '<div class="empty">No campaign-level flags in this window — every campaign is within the healthy thresholds.</div>';
    const rows = flagged
      .map((c) => {
        const badges = c.flags
          .filter((f) => f.level !== "info")
          .map((f) => \`<span class="badge \${f.level}" title="\${esc(f.message)}">\${esc(FLAG_LABELS[f.code] ?? f.code)}</span>\`)
          .join(" ");
        return \`<tr>
          <td>\${esc(c.name)}</td>
          <td class="num">\${num(c.metrics.sent)}</td>
          <td class="num">\${pct(c.metrics.bounceRate)}</td>
          <td class="num">\${pct(c.metrics.openRate)}</td>
          <td class="num">\${pct(c.metrics.unsubRate)}</td>
          <td>\${badges}</td>
        </tr>\`;
      })
      .join("");
    return \`<div class="table-scroll"><table>
      <thead><tr><th>Campaign</th><th>Sent</th><th>Bounce</th><th>Open</th><th>Unsub</th><th>Flagged for</th></tr></thead>
      <tbody>\${rows}</tbody>
    </table></div>\`;
  }

  function renderBarChart(r, metricKey, warnKey, criticalKey, higherIsWorse) {
    const all = r.campaigns;
    const untracked = all.filter((c) => c.metrics[metricKey] === null);
    const rows = all
      .filter((c) => c.metrics[metricKey] !== null)
      .sort((a, b) => (higherIsWorse ? b.metrics[metricKey] - a.metrics[metricKey] : a.metrics[metricKey] - b.metrics[metricKey]));
    const max = Math.max(...rows.map((c) => c.metrics[metricKey]), 0.01);
    const bars = rows
      .map((c) => {
        const v = c.metrics[metricKey];
        const status = severityFor(v, r.thresholds[warnKey], r.thresholds[criticalKey], higherIsWorse);
        const widthPct = Math.max((v / max) * 100, 1.5);
        return \`<div class="bar-row" title="\${esc(c.name)}: \${pct(v)} (\${num(c.metrics.sent)} sent)">
          <div class="bar-name">\${esc(c.name)}</div>
          <div class="bar-track"><div class="bar-fill \${status}" style="width:\${widthPct}%"></div></div>
          <div class="bar-value">\${pct(v)}</div>
        </div>\`;
      })
      .join("");
    const note = untracked.length
      ? \`<p class="muted">\${untracked.length} campaign\${untracked.length === 1 ? "" : "s"} excluded — tracking disabled: \${untracked.map((c) => esc(c.name)).join(", ")}</p>\`
      : "";
    return bars + note;
  }

  function statusBadge(level) {
    return \`<span class="badge \${level}">\${level}</span>\`;
  }

  function renderCampaignTable(r) {
    const rows = r.campaigns
      .map((c) => {
        const m = c.metrics;
        const actionable = c.flags.filter((f) => f.level !== "info");
        const worst = actionable.some((f) => f.level === "critical") ? "critical" : actionable.length ? "warning" : "good";
        const trackingNote = m.openTrackingDisabled || m.clickTrackingDisabled
          ? \`<span class="muted" title="Open/click tracking disabled for this campaign"> (untracked)</span>\`
          : "";
        return \`<tr>
          <td>\${esc(c.name)}\${trackingNote}</td>
          <td>\${esc(c.status)}</td>
          <td class="num">\${num(m.sent)}</td>
          <td class="num">\${pct(m.openRate)}</td>
          <td class="num">\${pct(m.clickRate)}</td>
          <td class="num">\${pct(m.replyRate)}</td>
          <td class="num">\${pct(m.bounceRate)}</td>
          <td class="num">\${pct(m.unsubRate)}</td>
          <td>\${statusBadge(worst)}</td>
        </tr>\`;
      })
      .join("");
    return \`<div class="table-scroll"><table>
      <thead><tr><th>Campaign</th><th>Status</th><th>Sent</th><th>Open</th><th>Click</th><th>Reply</th><th>Bounce</th><th>Unsub</th><th>Health</th></tr></thead>
      <tbody>\${rows}</tbody>
    </table></div>\`;
  }

  const LEAD_TABLE_CAP = 50;

  function leadTable(rows, columns) {
    if (!rows.length) return '<div class="empty">None in this window.</div>';
    const shown = rows.slice(0, LEAD_TABLE_CAP);
    const head = columns.map((c) => \`<th>\${esc(c.label)}</th>\`).join("");
    const body = shown
      .map((row) => \`<tr>\${columns.map((c) => \`<td class="\${c.num ? "num" : ""}">\${esc(c.render ? c.render(row) : row[c.key])}</td>\`).join("")}</tr>\`)
      .join("");
    const truncNote = rows.length > LEAD_TABLE_CAP
      ? \`<p class="muted">Showing top \${LEAD_TABLE_CAP} of \${num(rows.length)}, sorted worst-first. Full list is in the underlying JSON report.</p>\`
      : "";
    return \`<div class="table-scroll"><table><thead><tr>\${head}</tr></thead><tbody>\${body}</tbody></table></div>\${truncNote}\`;
  }

  function renderLeadSections(r) {
    const lf = r.leadFlags;
    const nonOpenerCols = [
      { key: "email", label: "Email" },
      { key: "campaigns", label: "Campaigns", render: (row) => row.campaigns.join(", ") },
      { key: "sent", label: "Sent", num: true },
    ];
    const bouncerCols = [
      { key: "email", label: "Email" },
      { key: "campaigns", label: "Bounced in", render: (row) => row.campaigns.join(", ") },
      { key: "bounced", label: "Bounces", num: true },
    ];
    const engagedCols = [
      { key: "email", label: "Email" },
      { key: "campaigns", label: "Campaigns", render: (row) => row.campaigns.join(", ") },
      { key: "opened", label: "Opens", num: true },
      { key: "sent", label: "Sent", num: true },
    ];
    return \`
      <div class="card">
        <h2>Repeat non-openers — \${lf.repeatNonOpeners.length}</h2>
        <p class="muted">Sent \${r.thresholds.minSendsForNonOpenerFlag}+ emails, zero opens, address not bouncing. Likely wrong persona/list fit or a deliverability problem specific to that domain — candidates to suppress or move to a different sequence/offer.</p>
        \${leadTable(lf.repeatNonOpeners, nonOpenerCols)}
      </div>
      <div class="card">
        <h2>Chronic bouncers — \${lf.chronicBouncers.length}</h2>
        <p class="muted">Bounced at least once; several bounced in more than one campaign. Remove from active lists and add to the domain/email block list — every additional send to these risks sender reputation.</p>
        \${leadTable(lf.chronicBouncers, bouncerCols)}
      </div>
      <div class="card">
        <h2>Engaged but never converting — \${lf.engagedNonConverters.length}</h2>
        <p class="muted">Opens repeatedly across multiple campaigns but never clicks or replies. Interested-looking without converting — good candidates for a different subject line, offer, or a direct follow-up instead of another sequence step.</p>
        \${leadTable(lf.engagedNonConverters, engagedCols)}
      </div>
    \`;
  }

  function renderInboxHealth(r) {
    if (!r.inboxHealth.length) return '<div class="empty">All sending inboxes healthy — no flags.</div>';
    return r.inboxHealth
      .map((f) => \`<div class="flag-row"><span class="dot \${f.level}"></span><div><span class="flag-campaign">\${esc(f.email)}</span>\${esc(f.message)}</div></div>\`)
      .join("");
  }

  function render(r) {
    const generated = new Date(r.generatedAt);
    return \`
      <div class="topbar"></div>
      <span class="eyebrow">Albert Scott &middot; Sales Ops</span>
      <h1>Campaign Analytics Report\${r.source === "fixture-sample" ? '<span class="source-badge">sample data</span>' : ""}</h1>
      <p class="subtitle">Campaigns created on/after \${esc(r.range.since)} &middot; window \${esc(r.range.start)} → \${esc(r.range.end)} &middot; \${r.campaigns.length} campaigns &middot; \${num(r.leadCount)} leads &middot; generated \${generated.toLocaleString()}</p>

      <nav class="nav">
        <a href="#overview">Overview</a>
        <a href="#at-risk">Where to focus</a>
        <a href="#performance">Campaign performance</a>
        <a href="#targeting">Targeting opportunities</a>
        <a href="#inbox-health">Inbox health</a>
      </nav>

      <section id="overview">
        <p class="section-title">Overview</p>
        <div class="summary-card">\${renderExecSummary(r)}</div>
        <div class="card">
          <div class="kpi-grid">\${renderKpis(r)}</div>
        </div>
      </section>

      <section id="at-risk">
        <p class="section-title">Where to focus</p>
        <div class="card">
          <h2>Campaigns needing attention</h2>
          \${renderAtRiskTable(r)}
        </div>
      </section>

      <section id="performance">
        <p class="section-title">Campaign performance</p>
        <div class="card">
          <h2>Bounce rate by campaign</h2>
          <div class="legend">
            <span class="legend-item"><span class="dot good"></span>healthy (&lt; \${pct(r.thresholds.bounceRateWarning)})</span>
            <span class="legend-item"><span class="dot warning"></span>warning (≥ \${pct(r.thresholds.bounceRateWarning)})</span>
            <span class="legend-item"><span class="dot critical"></span>critical (≥ \${pct(r.thresholds.bounceRateCritical)})</span>
          </div>
          \${renderBarChart(r, "bounceRate", "bounceRateWarning", "bounceRateCritical", true)}
        </div>

        <div class="card">
          <h2>Open rate by campaign</h2>
          <div class="legend">
            <span class="legend-item"><span class="dot good"></span>healthy (&gt; \${pct(r.thresholds.openRateWarning)})</span>
            <span class="legend-item"><span class="dot warning"></span>warning (≤ \${pct(r.thresholds.openRateWarning)})</span>
            <span class="legend-item"><span class="dot critical"></span>critical (≤ \${pct(r.thresholds.openRateCritical)})</span>
          </div>
          \${renderBarChart(r, "openRate", "openRateWarning", "openRateCritical", false)}
        </div>

        <div class="card">
          <h2>All campaigns</h2>
          \${renderCampaignTable(r)}
        </div>
      </section>

      <section id="targeting">
        <p class="section-title">Targeting refinement opportunities</p>
        \${renderLeadSections(r)}
      </section>

      <section id="inbox-health">
        <p class="section-title">Sending infrastructure</p>
        <div class="card">
          <h2>Sending inbox health</h2>
          \${renderInboxHealth(r)}
        </div>
      </section>

      <p class="footer-note">Thresholds: bounce warn/critical \${pct(r.thresholds.bounceRateWarning)}/\${pct(r.thresholds.bounceRateCritical)} &middot; open warn/critical \${pct(r.thresholds.openRateWarning)}/\${pct(r.thresholds.openRateCritical)} &middot; unsub warn/critical \${pct(r.thresholds.unsubRateWarning)}/\${pct(r.thresholds.unsubRateCritical)} &middot; non-opener flag at \${r.thresholds.minSendsForNonOpenerFlag}+ tracked sends with 0 opens (sends from tracking-disabled campaigns don't count toward that threshold). All tunable via CLI flags on campaign-analytics-report.mjs.\${r.global.campaignsWithOpenTrackingOff ? \` \${r.global.campaignsWithOpenTrackingOff} of \${r.campaigns.length} campaigns have open tracking disabled (Smartlead's "Don't track email opens" setting) — shown as "—" throughout.\` : ""}</p>
    \`;
  }

  document.getElementById("app").innerHTML = render(REPORT);
</script>
`;
}
