import { Line, LineChart, ResponsiveContainer, Tooltip } from "recharts";
import CardShell from "./CardShell.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";

function Stat({ label, value, accent }) {
  return (
    <div className="min-w-0">
      <p
        className="truncate text-lg font-semibold tabular-nums leading-tight sm:text-xl"
        style={accent ? { color: accent } : undefined}
        title={value}
      >
        {value}
      </p>
      <p className="truncate text-[11px] text-charcoal/55 dark:text-slate-400">{label}</p>
    </div>
  );
}

function Sparkline({ data, dataKey, color }) {
  return (
    <div className="h-14 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 4, right: 0, left: 0, bottom: 0 }}>
          <Tooltip
            contentStyle={{ fontSize: 11, borderRadius: 8, border: "1px solid #A6A6A644" }}
            labelFormatter={(v) => v}
          />
          <Line type="monotone" dataKey={dataKey} stroke={color} strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

function Feed({ title, logo, children }) {
  return (
    <div className="min-w-0 flex-1 rounded-xl border border-line/15 p-3 dark:border-slate-800/60">
      <p className="mb-2 flex items-center gap-1.5 text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
        <span aria-hidden>{logo}</span> {title}
      </p>
      {children}
    </div>
  );
}

export default function OutreachPerformanceCard() {
  const { snapshot } = useDashboard();
  if (!snapshot) return <CardShell id="outreach" title="Outbound Performance">Loading…</CardShell>;

  const { smartlead, heyreach, inboxes } = snapshot;

  return (
    <CardShell id="outreach" title="Outbound Performance" icon="📨">
      <div className="flex h-full flex-col gap-3">
        <div className="flex flex-1 flex-col gap-3 sm:flex-row">
          <Feed title="Smartlead" logo="✉️">
            <div className="grid grid-cols-3 gap-1.5">
              <Stat label="Sent" value={smartlead.totalEmailsSent.toLocaleString()} />
              <Stat label="Open %" value={`${smartlead.openRate}%`} />
              <Stat label="Reply %" value={`${smartlead.replyRate}%`} accent="#E51958" />
            </div>
            <Sparkline data={smartlead.trend} dataKey="sent" color="#E51958" />
          </Feed>
          <Feed title="Heyreach" logo="🔗">
            <div className="grid grid-cols-3 gap-1.5">
              <Stat label="Sent" value={heyreach.connectionsSent.toLocaleString()} />
              <Stat label="Accept %" value={`${heyreach.acceptRate}%`} />
              <Stat label="Reply %" value={`${heyreach.responseRate}%`} accent="#7EC1EE" />
            </div>
            <Sparkline data={heyreach.trend} dataKey="sent" color="#7EC1EE" />
          </Feed>
        </div>

        <div className="flex shrink-0 items-center justify-between rounded-xl bg-mist/60 px-3 py-2 dark:bg-slate-800/50">
          <p className="text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
            Infrastructure
          </p>
          <div className="flex items-center gap-4 text-sm font-medium">
            <span className="inline-flex items-center gap-2 text-emerald-700 dark:text-emerald-400">
              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" aria-hidden />
              {inboxes.activeInboxes} active
            </span>
            <span className="inline-flex items-center gap-2 text-charcoal/50 dark:text-slate-500">
              <span className="h-2 w-2 rounded-full bg-slate-400 dark:bg-slate-600" aria-hidden />
              {inboxes.deadInboxes} dead/disconnected
            </span>
          </div>
        </div>
      </div>
    </CardShell>
  );
}
