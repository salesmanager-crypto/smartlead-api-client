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
    padding: 0 24px 24px;
    max-width: 1180px;
    margin: 0 auto;
  }
  .topbar { height: 3px; background: var(--accent); margin: 0 -24px 24px; border-radius: 0 0 3px 3px; }
  .eyebrow { display: block; font-size: 0.72rem; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--accent); margin-bottom: 6px; }
  h1 { font-size: 1.5rem; margin: 0 0 4px; text-wrap: balance; }
  h2 { font-size: 1.05rem; margin: 0 0 12px; display: flex; align-items: center; gap: 8px; }
  h2::before { content: ""; width: 8px; height: 8px; border-radius: 2px; background: var(--accent); flex: 0 0 auto; }
  .subtitle { color: var(--text-secondary); font-size: 0.9rem; margin: 0 0 24px; }
  .card {
    background: var(--surface-1);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 20px;
  }
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
  .muted { color: var(--text-muted); font-size: 0.8rem; }
  .empty { color: var(--text-muted); font-size: 0.85rem; padding: 8px 0; }
  .footer-note { color: var(--text-muted); font-size: 0.78rem; margin-top: 8px; }
  .source-badge { display: inline-block; background: var(--surface-2); border: 1px solid var(--border); border-radius: 999px; padding: 2px 10px; font-size: 0.72rem; color: var(--text-secondary); margin-left: 8px; }
</style>
<div class="viz-root" id="app"></div>
<script>
  const REPORT = ${dataJson};

  function pct(n) { return (n * 100).toFixed(1) + "%"; }
  function num(n) { return n.toLocaleString(); }
  function esc(s) { return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])); }

  function severityFor(value, warn, critical, higherIsWorse) {
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
    return [
      kpiTile("Emails sent", num(g.sent)),
      kpiTile("Open rate", pct(g.openRate), severityFor(g.openRate, t.openRateWarning, t.openRateCritical, false)),
      kpiTile("Click rate", pct(g.clickRate)),
      kpiTile("Reply rate", pct(g.replyRate)),
      kpiTile("Bounce rate", pct(g.bounceRate), severityFor(g.bounceRate, t.bounceRateWarning, t.bounceRateCritical, true)),
      kpiTile("Unsubscribe rate", pct(g.unsubRate), severityFor(g.unsubRate, t.unsubRateWarning, t.unsubRateCritical, true)),
    ].join("");
  }

  function renderFlags(r) {
    const rows = [];
    for (const c of r.campaigns) {
      for (const f of c.flags) rows.push({ level: f.level, campaign: c.name, message: f.message });
    }
    rows.sort((a, b) => (a.level === b.level ? 0 : a.level === "critical" ? -1 : 1));
    if (!rows.length) return '<div class="empty">No campaign-level flags in this window — every campaign is within the healthy thresholds.</div>';
    return rows
      .map((f) => \`<div class="flag-row"><span class="dot \${f.level}"></span><div><span class="flag-campaign">\${esc(f.campaign)}</span>\${esc(f.message)}</div></div>\`)
      .join("");
  }

  function renderBarChart(r, metricKey, warnKey, criticalKey, higherIsWorse) {
    const rows = [...r.campaigns].sort((a, b) => (higherIsWorse ? b.metrics[metricKey] - a.metrics[metricKey] : a.metrics[metricKey] - b.metrics[metricKey]));
    const max = Math.max(...rows.map((c) => c.metrics[metricKey]), 0.01);
    return rows
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
  }

  function statusBadge(level) {
    return \`<span class="badge \${level}">\${level}</span>\`;
  }

  function renderCampaignTable(r) {
    const rows = r.campaigns
      .map((c) => {
        const m = c.metrics;
        const worst = c.flags.some((f) => f.level === "critical") ? "critical" : c.flags.length ? "warning" : "good";
        return \`<tr>
          <td>\${esc(c.name)}</td>
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

  function leadTable(rows, columns) {
    if (!rows.length) return '<div class="empty">None in this window.</div>';
    const head = columns.map((c) => \`<th>\${esc(c.label)}</th>\`).join("");
    const body = rows
      .map((row) => \`<tr>\${columns.map((c) => \`<td class="\${c.num ? "num" : ""}">\${esc(c.render ? c.render(row) : row[c.key])}</td>\`).join("")}</tr>\`)
      .join("");
    return \`<div class="table-scroll"><table><thead><tr>\${head}</tr></thead><tbody>\${body}</tbody></table></div>\`;
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

      <div class="card">
        <h2>Overview</h2>
        <div class="kpi-grid">\${renderKpis(r)}</div>
      </div>

      <div class="card">
        <h2>Campaigns needing attention</h2>
        \${renderFlags(r)}
      </div>

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

      \${renderLeadSections(r)}

      <div class="card">
        <h2>Sending inbox health</h2>
        \${renderInboxHealth(r)}
      </div>

      <p class="footer-note">Thresholds: bounce warn/critical \${pct(r.thresholds.bounceRateWarning)}/\${pct(r.thresholds.bounceRateCritical)} &middot; open warn/critical \${pct(r.thresholds.openRateWarning)}/\${pct(r.thresholds.openRateCritical)} &middot; unsub warn/critical \${pct(r.thresholds.unsubRateWarning)}/\${pct(r.thresholds.unsubRateCritical)} &middot; non-opener flag at \${r.thresholds.minSendsForNonOpenerFlag}+ sends with 0 opens. All tunable via CLI flags on campaign-analytics-report.mjs.</p>
    \`;
  }

  document.getElementById("app").innerHTML = render(REPORT);
</script>
`;
}
