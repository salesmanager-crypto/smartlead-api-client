import { useState } from "react";
import { useNavigate } from "react-router-dom";
import CardShell from "./CardShell.jsx";
import Badge from "../Badge.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";

const STATUS_COLOR = { active: "green", warming: "yellow", dormant: "gray" };
const CWV_LABEL = { good: "green", "needs-improvement": "yellow", poor: "red" };

// Exported so the full /seo diagnostics page reuses the identical row instead of
// duplicating the cooldown-toggle logic. `onOpen`, when passed (overview card
// only), makes the row itself a click-through link to /seo — the toggle keeps its
// own stopPropagation so pausing/warming a domain from the glance view still works.
export function DomainRow({ domain, onToggle, busy, onOpen }) {
  const cooling = domain.coolingDown || domain.status === "warming";
  return (
    <li
      onClick={onOpen}
      role={onOpen ? "link" : undefined}
      tabIndex={onOpen ? 0 : undefined}
      onKeyDown={onOpen ? (e) => (e.key === "Enter" ? onOpen() : undefined) : undefined}
      className={`flex items-center justify-between gap-2 rounded-lg px-2 py-1.5 transition-colors hover:bg-mist/60 dark:hover:bg-slate-800/40 ${onOpen ? "focus-ring cursor-pointer" : ""}`}
    >
      <div className="min-w-0 flex-1">
        <p className="truncate text-sm font-medium">{domain.domain}</p>
        <div className="mt-0.5 flex items-center gap-1.5">
          <Badge color={STATUS_COLOR[domain.status]}>{domain.status}</Badge>
          <span
            className={`text-[11px] font-semibold ${domain.deliverability < 95 ? "text-signal" : "text-charcoal/50 dark:text-slate-400"}`}
          >
            {domain.deliverability}% deliverable
          </span>
          {domain.blacklists?.length > 0 && (
            <span className="text-[11px] font-semibold text-signal">{domain.blacklists.join(", ")}</span>
          )}
        </div>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onToggle(domain.id, !cooling);
        }}
        disabled={busy || domain.status === "dormant"}
        role="switch"
        aria-checked={cooling}
        aria-busy={busy}
        title={cooling ? "Cooling down in warm-up mode" : "Toggle Cool-Down (pause + warm up)"}
        className={`press focus-ring relative h-6 w-11 shrink-0 rounded-full transition-colors disabled:cursor-not-allowed disabled:opacity-30 disabled:active:scale-100 ${
          busy ? "animate-pulse" : ""
        } ${cooling ? "bg-division-listing" : "bg-line/40 dark:bg-slate-800/60"}`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all duration-200 ease-out ${cooling ? "left-5" : "left-0.5"}`}
        />
      </button>
    </li>
  );
}

export default function SeoHealthCard() {
  const { snapshot, setDomainCooldown } = useDashboard();
  const navigate = useNavigate();
  const [busyId, setBusyId] = useState(null);

  if (!snapshot) return <CardShell id="seo" title="Technical SEO & Asset Health">Loading…</CardShell>;
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
    <CardShell id="seo" title="Technical SEO & Asset Health" icon="🌐" openTo="/seo">
      <div className="flex h-full flex-col gap-4">
        <div>
          <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
            SEO Diagnostics <span className="font-normal normal-case text-charcoal/30 dark:text-slate-500">(simulated — wire up Semrush)</span>
          </p>
          <div className="grid grid-cols-3 gap-2 text-center">
            <div className="rounded-lg bg-mist/60 p-2 dark:bg-slate-800/50">
              <p className="text-lg font-semibold">{seo.coreWebVitals.lcpMs}ms</p>
              <p className="text-[11px] text-charcoal/50 dark:text-slate-400">
                LCP <Badge color={CWV_LABEL[seo.coreWebVitals.status]}>{seo.coreWebVitals.status}</Badge>
              </p>
            </div>
            <div className="rounded-lg bg-mist/60 p-2 dark:bg-slate-800/50">
              <p className="text-lg font-semibold text-signal">{seo.brokenLinks}</p>
              <p className="text-[11px] text-charcoal/50 dark:text-slate-400">Broken links</p>
            </div>
            <div className="rounded-lg bg-mist/60 p-2 dark:bg-slate-800/50">
              <p className="text-lg font-semibold text-signal">{seo.crawlErrors}</p>
              <p className="text-[11px] text-charcoal/50 dark:text-slate-400">Crawl errors</p>
            </div>
          </div>
        </div>

        <div className="min-h-0 flex-1">
          <div className="mb-1 flex items-center justify-between">
            <p className="text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">Domain Asset Ledger</p>
            <p className="text-[11px] text-charcoal/45 dark:text-slate-500">
              {counts.active} active · {counts.warming} warming · {counts.dormant} dormant
            </p>
          </div>
          <ul className="thin-scroll max-h-full space-y-0.5 overflow-auto">
            {domains.map((d) => (
              <DomainRow key={d.id} domain={d} onToggle={handleToggle} busy={busyId === d.id} onOpen={() => navigate("/seo")} />
            ))}
          </ul>
        </div>
      </div>
    </CardShell>
  );
}
