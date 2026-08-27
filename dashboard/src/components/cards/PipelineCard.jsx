import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import CardShell from "./CardShell.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";

// Monochrome funnel ramp — neutral stages darken as a deal progresses (lightest at
// creation, darkest at negotiation), with the accent budget spent on a single
// semantic color reserved for the one outcome worth calling out: Closed Won.
// Exported so the dedicated /pipeline workspace page can reuse the exact same ramp.
export const STAGE_STYLE = {
  "Deal Created": "bg-slate-300 dark:bg-slate-700",
  Discovery: "bg-slate-400 dark:bg-slate-600",
  Proposal: "bg-slate-500 dark:bg-slate-500",
  Negotiation: "bg-slate-600 dark:bg-slate-400",
  "Closed Won": "bg-emerald-500 dark:bg-emerald-500",
  "Closed Lost": "bg-slate-700 dark:bg-slate-800",
};

// Compact radial gauge for win rate — a real metric (decided deals only, Closed Won
// vs. Closed Lost), not a decorative ring. Sales ops reads win rate as a headline
// number; giving it its own shape earns the one "signature" this card gets. Exported
// so the overview card and the full /pipeline page render the identical widget.
export function WinRateRing({ percent, size = 38, stroke = 4 }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - percent / 100);
  return (
    <div className="relative shrink-0" style={{ width: size, height: size }} aria-hidden>
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size / 2} cy={size / 2} r={r} fill="none" strokeWidth={stroke} className="stroke-line/25 dark:stroke-slate-800" />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={r}
          fill="none"
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={c}
          strokeDashoffset={offset}
          className="stroke-emerald-500 transition-[stroke-dashoffset] duration-700 ease-out"
        />
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-[10px] font-semibold tabular-nums text-charcoal/80 dark:text-slate-200">
        {Math.round(percent)}%
      </span>
    </div>
  );
}

export default function PipelineCard() {
  const { snapshot } = useDashboard();
  const navigate = useNavigate();
  const [hovering, setHovering] = useState(false);

  const correlation = useMemo(() => {
    if (!snapshot) return [];
    const { smartlead, heyreach } = snapshot;
    return smartlead.trend.map((d, i) => ({
      date: d.date.slice(5),
      outreach: d.sent + (heyreach.trend[i]?.sent || 0),
    }));
  }, [snapshot]);

  if (!snapshot) return <CardShell id="pipeline" title="Pipedrive CRM Pipeline">Loading…</CardShell>;

  const { byStage } = snapshot.pipeline;
  const total = Math.max(
    1,
    byStage.reduce((s, x) => s + x.count, 0)
  );
  const won = byStage.find((s) => s.stage === "Closed Won")?.count || 0;
  const lost = byStage.find((s) => s.stage === "Closed Lost")?.count || 0;
  const decided = won + lost;
  const winRate = decided > 0 ? (won / decided) * 100 : 0;

  // Clicking into a stage now deep-links to the dedicated CRM Deals Workspace
  // (pre-filtered to that stage) instead of opening the drawer — the drawer stays
  // reserved for single-deal drill-down from within that workspace.
  const goToStage = (stage) => navigate(`/pipeline?stage=${encodeURIComponent(stage)}`);

  return (
    <CardShell
      id="pipeline"
      title="Pipedrive CRM Pipeline"
      icon="📊"
      openTo="/pipeline"
      headerRight={
        <div className="flex items-center gap-2.5" title={`${won} won / ${lost} lost of ${decided} decided deals`}>
          {decided > 0 && <WinRateRing percent={winRate} />}
          <div className="text-right leading-tight">
            {decided > 0 && <p className="text-xs font-semibold text-charcoal/80 dark:text-slate-200">win rate</p>}
            <p className="text-[11px] text-charcoal/45 dark:text-slate-500">{total} deals</p>
          </div>
        </div>
      }
    >
      <div className="flex h-full flex-col gap-3">
        <div
          className="relative"
          onMouseEnter={() => setHovering(true)}
          onMouseLeave={() => setHovering(false)}
        >
          <div className="flex h-9 w-full overflow-hidden rounded-lg border border-line/20 dark:border-slate-800/60">
            {byStage.map((s) => (
              <button
                key={s.stage}
                onClick={() => goToStage(s.stage)}
                title={`${s.stage}: ${s.count} deals, $${s.value.toLocaleString()} — open in Pipeline Workspace`}
                style={{ width: `${(s.count / total) * 100}%` }}
                className={`press focus-ring group relative h-full min-w-[3%] transition-[filter,transform] duration-200 hover:brightness-110 ${STAGE_STYLE[s.stage]}`}
              >
                {s.count > 0 && (
                  <span className="absolute inset-0 flex items-center justify-center text-[11px] font-medium text-white/90 mix-blend-difference">
                    {s.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          <AnimatePresence>
            {hovering && (
              <motion.div
                initial={{ opacity: 0, y: -4 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -4, transition: { duration: 0.14, ease: "easeIn" } }}
                transition={{ duration: 0.2, ease: "easeOut" }}
                className="absolute left-0 right-0 top-11 z-10 rounded-xl border border-line/20 bg-white/95 p-2 shadow-card backdrop-blur dark:border-slate-800/60 dark:bg-slate-900/95"
              >
                <p className="mb-1 px-1 text-[11px] font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
                  Outreach input · trailing 14 days (funnel health correlation)
                </p>
                <div className="h-20 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <AreaChart data={correlation} margin={{ top: 4, right: 8, left: 8, bottom: 0 }}>
                      <defs>
                        <linearGradient id="corrFill" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#E51958" stopOpacity={0.35} />
                          <stop offset="100%" stopColor="#E51958" stopOpacity={0.02} />
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="date" tick={{ fontSize: 9 }} interval={2} axisLine={false} tickLine={false} />
                      <Tooltip contentStyle={{ fontSize: 11, borderRadius: 8 }} animationDuration={150} />
                      <Area
                        type="monotone"
                        dataKey="outreach"
                        stroke="#E51958"
                        fill="url(#corrFill)"
                        strokeWidth={2}
                        isAnimationActive
                        animationDuration={400}
                        animationEasing="ease-out"
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <ul className="grid flex-1 grid-cols-2 gap-x-4 gap-y-2 content-start overflow-auto pt-2 sm:grid-cols-3">
          {byStage.map((s) => (
            <li key={s.stage}>
              <button
                onClick={() => goToStage(s.stage)}
                className="press focus-ring flex w-full items-center gap-2 rounded-lg px-1.5 py-1 text-left transition-colors hover:bg-mist dark:hover:bg-slate-800/40"
              >
                <span className={`h-2.5 w-2.5 shrink-0 rounded-sm ${STAGE_STYLE[s.stage]}`} aria-hidden />
                <span className="min-w-0 flex-1 truncate text-xs font-medium">{s.stage}</span>
                <span className="shrink-0 text-xs font-medium tabular-nums">{s.count}</span>
              </button>
              <p className="pl-4.5 ml-4 text-[11px] text-charcoal/45 dark:text-slate-500">${s.value.toLocaleString()}</p>
            </li>
          ))}
        </ul>
      </div>
    </CardShell>
  );
}
