import { useSearchParams } from "react-router-dom";
import Badge from "../components/Badge.jsx";
import { STAGE_STYLE, WinRateRing } from "../components/cards/PipelineCard.jsx";
import { useDashboard } from "../context/DashboardContext.jsx";
import { seoScoreFor } from "../lib/mockData.js";
import { relativeTime } from "../lib/time.js";

const SCORE_COLOR = { good: "green", "needs-improvement": "yellow", poor: "red" };
const CLOSED_STAGES = new Set(["Closed Won", "Closed Lost"]);

function SeoAuditWidget({ company }) {
  const { score, band, issues } = seoScoreFor(company);
  return (
    <div className="mt-3 rounded-lg border border-line/15 bg-mist/40 p-2.5 dark:border-slate-800/60 dark:bg-slate-800/40">
      <div className="mb-1.5 flex items-center justify-between">
        <p className="text-[11px] font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
          SEO Audit &amp; Diagnostic Score
        </p>
        <Badge color={SCORE_COLOR[band]}>{score}/100</Badge>
      </div>
      <ul className="space-y-0.5">
        {issues.map((issue) => (
          <li key={issue} className="text-[11px] leading-snug text-charcoal/60 dark:text-slate-400">
            · {issue}
          </li>
        ))}
      </ul>
    </div>
  );
}

// Dedicated Pipedrive CRM Deals Workspace — expanded deal cards (not the compact
// funnel-bar summary) with a per-deal SEO diagnostic widget baked in, so a rep
// reviewing a deal sees client-site health in the same glance. Deep-linked from
// the overview Pipeline card via ?stage=; opening a card hands off to the
// SidebarDrawer (third layer) for the same single-deal detail view used everywhere
// else — this page is the browse surface, the drawer stays the drill-down.
export default function PipelinePage() {
  const { snapshot, openDrawer } = useDashboard();
  const [searchParams, setSearchParams] = useSearchParams();
  const stageParam = searchParams.get("stage") || "All";

  if (!snapshot) return <div className="mx-4 my-4 text-sm text-charcoal/40 dark:text-slate-500 md:mx-6">Loading…</div>;

  const { byStage, deals } = snapshot.pipeline;
  const won = byStage.find((s) => s.stage === "Closed Won")?.count || 0;
  const lost = byStage.find((s) => s.stage === "Closed Lost")?.count || 0;
  const decided = won + lost;
  const winRate = decided > 0 ? (won / decided) * 100 : 0;
  const totalValue = byStage.reduce((s, x) => s + x.value, 0);
  const filteredDeals = stageParam === "All" ? deals : deals.filter((d) => d.stage === stageParam);

  return (
    <div className="mx-4 my-4 md:mx-6">
      <header className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Pipedrive CRM Deals Workspace</h1>
          <p className="text-xs text-charcoal/50 dark:text-slate-500">
            {filteredDeals.length} of {deals.length} deals · ${totalValue.toLocaleString()} total pipeline value
          </p>
        </div>
        <div className="flex items-center gap-3">
          {decided > 0 && (
            <div className="flex items-center gap-2" title={`${won} won / ${lost} lost of ${decided} decided deals`}>
              <WinRateRing percent={winRate} size={40} />
              <p className="text-xs font-semibold text-charcoal/80 dark:text-slate-200">win rate</p>
            </div>
          )}
          <select
            value={stageParam}
            onChange={(e) => setSearchParams(e.target.value === "All" ? {} : { stage: e.target.value })}
            className="focus-ring rounded-md border border-line/25 bg-transparent px-2 py-1.5 text-xs transition-colors dark:border-slate-700/60"
          >
            <option value="All">All stages</option>
            {byStage.map((s) => (
              <option key={s.stage} value={s.stage}>
                {s.stage} ({s.count})
              </option>
            ))}
          </select>
        </div>
      </header>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
        {filteredDeals.map((deal) => {
          const company = deal.title.split(" — ")[0];
          return (
            <button
              key={deal.id}
              onClick={() => openDrawer("deal", deal)}
              className="press focus-ring flex flex-col rounded-2xl border border-line/20 bg-white p-4 text-left shadow-card transition-colors hover:border-signal/40 dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark"
            >
              <div className="mb-2 flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <p className="truncate text-sm font-semibold">{deal.title}</p>
                  <p className="mt-0.5 truncate text-[11px] text-charcoal/50 dark:text-slate-500">{company}</p>
                </div>
                <span className={`h-2.5 w-2.5 shrink-0 rounded-sm ${STAGE_STYLE[deal.stage]}`} title={deal.stage} aria-hidden />
              </div>
              <p className="text-xl font-semibold tabular-nums text-signal">${deal.value.toLocaleString()}</p>
              <p className="mt-1 text-[11px] text-charcoal/45 dark:text-slate-500">
                {deal.stage} · last touched {relativeTime(deal.lastActivity)}
              </p>
              {deal.staleHours >= 48 && !CLOSED_STAGES.has(deal.stage) && (
                <p className="mt-1 text-[11px] font-semibold text-signal">⚠ Unaddressed for {Math.floor(deal.staleHours)}h</p>
              )}
              <SeoAuditWidget company={company} />
            </button>
          );
        })}
        {filteredDeals.length === 0 && (
          <p className="text-sm text-charcoal/40 dark:text-slate-500">No deals in this stage.</p>
        )}
      </div>
    </div>
  );
}
