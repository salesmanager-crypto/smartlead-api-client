import { AnimatePresence, motion } from "framer-motion";
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
      <AnimatePresence initial={false}>
        {alerts.slice(0, 4).map((alert) => (
          <motion.div
            key={alert.id}
            layout
            initial={{ opacity: 0, y: -8, height: 0, marginBottom: 0 }}
            animate={{ opacity: 1, y: 0, height: "auto", marginBottom: 8 }}
            exit={{ opacity: 0, x: 24, height: 0, marginBottom: 0, transition: { duration: 0.18, ease: "easeIn" } }}
            transition={{ duration: 0.24, ease: "easeOut" }}
            className={`flex items-center justify-between gap-3 overflow-hidden rounded-xl border px-4 py-2.5 text-sm shadow-sm ${SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.warning}`}
          >
            <button
              className="focus-ring flex min-w-0 flex-1 items-center gap-2 rounded text-left"
              onClick={() => openDrawer("alert", alert)}
            >
              <span aria-hidden>{alert.severity === "critical" ? "🚨" : "⚠️"}</span>
              <span className="truncate font-semibold">{alert.title}</span>
              <span className="hidden truncate text-xs opacity-70 sm:inline">— {alert.detail}</span>
            </button>
            <button
              onClick={() => muteAlert(alert.id)}
              className="press focus-ring shrink-0 rounded-md px-2 py-1 text-xs font-medium opacity-70 transition-colors hover:bg-black/5 hover:opacity-100 dark:hover:bg-white/10"
            >
              Mute
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
