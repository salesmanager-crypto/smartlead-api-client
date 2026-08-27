import { useDashboard } from "../../context/DashboardContext.jsx";

const SEVERITY_STYLE = {
  critical: "border-signal/40 bg-signal/10 text-signal-deep dark:text-signal",
  warning: "border-division-retail/50 bg-division-retail/10 text-charcoal dark:text-mist",
};

export default function AlertBanner() {
  const { snapshot, openDrawer, muteAlert } = useDashboard();
  const alerts = snapshot?.alerts || [];
  if (!alerts.length) return null;

  return (
    <div className="mx-5 mt-4 space-y-2 md:mx-8" id="alerts">
      {alerts.slice(0, 4).map((alert) => (
        <div
          key={alert.id}
          className={`flex items-center justify-between gap-3 rounded-xl border px-4 py-2.5 text-sm shadow-sm ${SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.warning}`}
        >
          <button
            className="flex min-w-0 flex-1 items-center gap-2 text-left"
            onClick={() => openDrawer("alert", alert)}
          >
            <span aria-hidden>{alert.severity === "critical" ? "🚨" : "⚠️"}</span>
            <span className="truncate font-semibold">{alert.title}</span>
            <span className="hidden truncate text-xs opacity-70 sm:inline">— {alert.detail}</span>
          </button>
          <button
            onClick={() => muteAlert(alert.id)}
            className="shrink-0 rounded-md px-2 py-1 text-xs font-medium opacity-70 hover:bg-black/5 hover:opacity-100 dark:hover:bg-white/10"
          >
            Mute
          </button>
        </div>
      ))}
    </div>
  );
}
