import { AnimatePresence, motion } from "framer-motion";
import { useDashboard } from "../../context/DashboardContext.jsx";

// Single consolidated row instead of stacked blocks — deep, low-opacity tints and a
// small dot indicator rather than heavy bordered bars or emoji (ui-ux-pro-max Style
// Specification Override, section 3A: "anti-childish" alert restructuring).
const SEVERITY_STYLE = {
  critical: "bg-red-500/10 text-red-600 dark:text-red-400",
  warning: "bg-amber-500/5 text-amber-700 dark:text-amber-400",
};
const SEVERITY_DOT = {
  critical: "bg-red-500",
  warning: "bg-amber-500",
};

export default function AlertBanner() {
  const { snapshot, openDrawer, muteAlert } = useDashboard();
  const alerts = snapshot?.alerts || [];
  if (!alerts.length) return null;

  return (
    <div
      id="alerts"
      className="mx-5 mt-4 flex flex-wrap items-center gap-x-1.5 gap-y-1.5 rounded-md border border-line/20 bg-white px-3 py-2 dark:border-slate-800/60 dark:bg-slate-900/60 md:mx-8"
    >
      <AnimatePresence initial={false}>
        {alerts.slice(0, 6).map((alert) => (
          <motion.div
            key={alert.id}
            layout
            initial={{ opacity: 0, scale: 0.92 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.92, transition: { duration: 0.15, ease: "easeIn" } }}
            transition={{ duration: 0.2, ease: "easeOut" }}
            className={`group inline-flex items-center gap-1.5 rounded-md py-1 pl-2 pr-1 text-xs ${SEVERITY_STYLE[alert.severity] || SEVERITY_STYLE.warning}`}
          >
            <span className={`h-1.5 w-1.5 shrink-0 rounded-full ${SEVERITY_DOT[alert.severity] || SEVERITY_DOT.warning}`} aria-hidden />
            <button
              className="focus-ring max-w-[20rem] truncate rounded text-left font-medium"
              onClick={() => openDrawer("alert", alert)}
              title={alert.detail}
            >
              {alert.title}
            </button>
            <button
              onClick={() => muteAlert(alert.id)}
              aria-label={`Mute alert: ${alert.title}`}
              className="press focus-ring shrink-0 rounded px-1 text-[11px] leading-none opacity-40 transition-opacity hover:opacity-100 focus-visible:opacity-100 group-hover:opacity-70"
            >
              ✕
            </button>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}
