import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis } from "recharts";
import CardShell from "./CardShell.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";

const STAGE_COLOR = {
  "Deal Created": "#A6A6A6",
  Discovery: "#7EC1EE",
  Proposal: "#F5A3BC",
  Negotiation: "#E51958",
  "Closed Won": "#0F9D58",
  "Closed Lost": "#0D0D0D",
};

export default function PipelineCard() {
  const { snapshot, openDrawer } = useDashboard();
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

  const { byStage, deals } = snapshot.pipeline;
  const total = Math.max(
    1,
    byStage.reduce((s, x) => s + x.count, 0)
  );

  return (
    <CardShell
      id="pipeline"
      title="Pipedrive CRM Pipeline"
      icon="📊"
      headerRight={
        <span className="text-xs font-medium text-charcoal/50 dark:text-mist/50">
          {byStage.reduce((s, x) => s + x.count, 0)} open + closed deals
        </span>
      }
    >
      <div className="flex h-full flex-col gap-3">
        <div
          className="relative"
          onMouseEnter={() => setHovering(true)}
          onMouseLeave={() => setHovering(false)}
        >
          <div className="flex h-9 w-full overflow-hidden rounded-lg border border-line/20 dark:border-white/10">
            {byStage.map((s) => (
              <button
                key={s.stage}
                onClick={() => openDrawer("deal", { stage: s.stage, deals: deals.filter((d) => d.stage === s.stage) })}
                title={`${s.stage}: ${s.count} deals, $${s.value.toLocaleString()}`}
                style={{ width: `${(s.count / total) * 100}%`, background: STAGE_COLOR[s.stage] }}
                className="press focus-ring group relative h-full min-w-[3%] transition-[filter,transform] duration-200 hover:brightness-110"
              >
                {s.count > 0 && (
                  <span className="absolute inset-0 flex items-center justify-center text-[11px] font-bold text-white/90 mix-blend-difference">
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
                className="absolute left-0 right-0 top-11 z-10 rounded-xl border border-line/20 bg-white/95 p-2 shadow-card backdrop-blur dark:border-white/10 dark:bg-canvas/95"
              >
                <p className="mb-1 px-1 text-[11px] font-semibold uppercase tracking-wide text-charcoal/50 dark:text-mist/50">
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
                onClick={() => openDrawer("deal", { stage: s.stage, deals: deals.filter((d) => d.stage === s.stage) })}
                className="press focus-ring flex w-full items-center gap-2 rounded-lg px-1.5 py-1 text-left transition-colors hover:bg-mist dark:hover:bg-white/5"
              >
                <span className="h-2.5 w-2.5 shrink-0 rounded-sm" style={{ background: STAGE_COLOR[s.stage] }} aria-hidden />
                <span className="min-w-0 flex-1 truncate text-xs font-medium">{s.stage}</span>
                <span className="shrink-0 text-xs font-bold tabular-nums">{s.count}</span>
              </button>
              <p className="pl-4.5 ml-4 text-[11px] text-charcoal/45 dark:text-mist/45">${s.value.toLocaleString()}</p>
            </li>
          ))}
        </ul>
      </div>
    </CardShell>
  );
}
