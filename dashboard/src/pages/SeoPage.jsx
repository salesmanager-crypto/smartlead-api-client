import { useState } from "react";
import Badge from "../components/Badge.jsx";
import { DomainRow } from "../components/cards/SeoHealthCard.jsx";
import { useDashboard } from "../context/DashboardContext.jsx";

const CWV_LABEL = { good: "green", "needs-improvement": "yellow", poor: "red" };

// Dedicated Website Diagnostics & Audit Ledger page — the same live/simulated SEO
// data and cooldown-toggle domain rows as the overview card, laid out with the
// room a compact card can't spare: bigger stat tiles and a two-column ledger
// instead of a scroll-capped list.
export default function SeoPage() {
  const { snapshot, setDomainCooldown } = useDashboard();
  const [busyId, setBusyId] = useState(null);

  if (!snapshot) return <div className="mx-4 my-4 text-sm text-charcoal/40 dark:text-slate-500 md:mx-6">Loading…</div>;
  const { seo, domains } = snapshot;
  const counts = domains.reduce(
    (acc, d) => ({ ...acc, [d.status]: (acc[d.status] || 0) + 1 }),
    { active: 0, warming: 0, dormant: 0 }
  );

  const handleToggle = async (id, cooldown) => {
    setBusyId(id);
    try {
      await setDomainCooldown(id, cooldown);
    } finally {
      setBusyId(null);
    }
  };

  return (
    <div className="mx-4 my-4 md:mx-6">
      <header className="mb-4">
        <h1 className="text-lg font-semibold tracking-tight">Website Diagnostics &amp; Asset Health</h1>
        <p className="text-xs text-charcoal/50 dark:text-slate-500">
          {counts.active} active · {counts.warming} warming · {counts.dormant} dormant sending domains
        </p>
      </header>

      <div className="mb-5 grid grid-cols-2 gap-3 sm:grid-cols-5">
        <div className="rounded-2xl border border-line/20 bg-white p-4 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          <p className="text-2xl font-semibold tabular-nums">{seo.coreWebVitals.lcpMs}ms</p>
          <p className="mt-1 text-xs text-charcoal/50 dark:text-slate-400">
            LCP <Badge color={CWV_LABEL[seo.coreWebVitals.status]}>{seo.coreWebVitals.status}</Badge>
          </p>
        </div>
        <div className="rounded-2xl border border-line/20 bg-white p-4 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          <p className="text-2xl font-semibold tabular-nums">{seo.coreWebVitals.inpMs}ms</p>
          <p className="mt-1 text-xs text-charcoal/50 dark:text-slate-400">INP</p>
        </div>
        <div className="rounded-2xl border border-line/20 bg-white p-4 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          <p className="text-2xl font-semibold tabular-nums">{seo.coreWebVitals.cls}</p>
          <p className="mt-1 text-xs text-charcoal/50 dark:text-slate-400">CLS</p>
        </div>
        <div className="rounded-2xl border border-line/20 bg-white p-4 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          <p className="text-2xl font-semibold tabular-nums text-signal">{seo.brokenLinks}</p>
          <p className="mt-1 text-xs text-charcoal/50 dark:text-slate-400">Broken links</p>
        </div>
        <div className="rounded-2xl border border-line/20 bg-white p-4 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          <p className="text-2xl font-semibold tabular-nums text-signal">{seo.crawlErrors}</p>
          <p className="mt-1 text-xs text-charcoal/50 dark:text-slate-400">Crawl errors</p>
        </div>
      </div>

      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
        Domain Asset Ledger <span className="font-normal normal-case text-charcoal/30 dark:text-slate-500">(simulated — wire up Semrush)</span>
      </p>
      <ul className="grid grid-cols-1 gap-1 rounded-2xl border border-line/20 bg-white p-2 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark md:grid-cols-2">
        {domains.map((d) => (
          <DomainRow key={d.id} domain={d} onToggle={handleToggle} busy={busyId === d.id} />
        ))}
      </ul>
    </div>
  );
}
