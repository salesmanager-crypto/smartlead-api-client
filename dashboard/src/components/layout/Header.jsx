import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useDashboard } from "../../context/DashboardContext.jsx";
import { useTheme } from "../../context/ThemeContext.jsx";
import { greetingFor, hourInTimezone } from "../../lib/time.js";

function initials(profile) {
  return `${profile.firstName?.[0] || ""}${profile.lastName?.[0] || ""}`.toUpperCase() || "?";
}

const LIST_VARIANTS = { hidden: {}, show: { transition: { staggerChildren: 0.04 } } };
const ITEM_VARIANTS = {
  hidden: { opacity: 0, y: -4 },
  show: { opacity: 1, y: 0, transition: { duration: 0.18, ease: "easeOut" } },
};

export default function Header() {
  const { profile, snapshot, setProfileOpen, openDrawer } = useDashboard();
  const { theme, toggleTheme } = useTheme();
  const [summaryOpen, setSummaryOpen] = useState(false);

  const greeting = useMemo(
    () => greetingFor(hourInTimezone(profile.timezone), profile.firstName || "there"),
    [profile.timezone, profile.firstName]
  );

  const recommendations = useMemo(() => {
    if (!snapshot) return [];
    const recs = [];
    const unbooked = snapshot.automationLog.find(
      (r) => r.smartleadTag === "Interested" && r.pipedriveStatus === "Failed"
    );
    if (unbooked) {
      recs.push({
        id: `rec_${unbooked.id}`,
        text: `${unbooked.leadName} replied "Interested" but the Pipedrive sync failed.`,
        cta: "Open the log entry to re-run it or reply directly",
        action: () => openDrawer("automation", unbooked),
      });
    }
    const worstDomain = [...snapshot.domains]
      .filter((d) => d.status !== "dormant")
      .sort((a, b) => a.deliverability - b.deliverability)[0];
    if (worstDomain && worstDomain.deliverability < 95) {
      recs.push({
        id: `rec_${worstDomain.id}`,
        text: `${worstDomain.domain} deliverability dropped to ${worstDomain.deliverability}%.`,
        cta: "Run an SPF/DKIM diagnostic",
        action: () => openDrawer("alert", { type: "domain", domain: worstDomain }),
      });
    }
    const staleDeal = snapshot.pipeline.staleOpen[0];
    if (staleDeal) {
      recs.push({
        id: `rec_deal_${staleDeal.id}`,
        text: `${staleDeal.title} has sat untouched for ${Math.floor(staleDeal.staleHours)}h.`,
        cta: "Open the deal in the pipeline drawer",
        action: () => openDrawer("deal", staleDeal),
      });
    }
    return recs;
  }, [snapshot, openDrawer]);

  const summary = snapshot
    ? `You have ${snapshot.meetingsToday} meetings on the radar, but ${snapshot.hotRepliesUnsynced} hot ${
        snapshot.hotRepliesUnsynced === 1 ? "response" : "responses"
      } failed to sync to Pipedrive, and ${snapshot.domains.filter((d) => d.status !== "dormant" && d.deliverability < 95).length} sending domains need attention.`
    : "Loading your day…";

  return (
    <header className="sticky top-0 z-30 border-b border-line/20 bg-paper/90 backdrop-blur dark:bg-canvas/90">
      <div className="flex items-center justify-between gap-4 px-5 py-3 md:px-8">
        <div className="min-w-0">
          <h1 className="flex items-baseline gap-2 text-xl font-semibold tracking-tight md:text-2xl">
            <span>{greeting.text}</span>
            <span aria-hidden>{greeting.emoji}</span>
          </h1>
          <button
            onClick={() => setSummaryOpen((o) => !o)}
            aria-expanded={summaryOpen}
            className="focus-ring mt-1 max-w-3xl rounded text-left text-sm text-charcoal/70 transition-colors hover:text-signal dark:text-slate-400 dark:hover:text-signal"
          >
            Here is what you have today: <span className="font-medium underline decoration-dotted underline-offset-2">{summary}</span>
          </button>

          <AnimatePresence initial={false}>
            {summaryOpen && recommendations.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0, transition: { duration: 0.16, ease: "easeIn" } }}
                transition={{ duration: 0.22, ease: "easeOut" }}
                className="max-w-2xl overflow-hidden"
              >
                <div className="mt-3 rounded-xl border border-line/30 bg-white p-3 shadow-card dark:border-slate-800/60 dark:bg-slate-800/40 dark:shadow-card-dark">
                  <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-charcoal/50 dark:text-slate-400">
                    Suggested next actions
                  </p>
                  <motion.ul variants={LIST_VARIANTS} initial="hidden" animate="show" className="space-y-2">
                    {recommendations.map((r) => (
                      <motion.li key={r.id} variants={ITEM_VARIANTS} className="text-sm">
                        <span>{r.text} </span>
                        <button
                          onClick={() => {
                            r.action();
                            setSummaryOpen(false);
                          }}
                          className="focus-ring rounded font-semibold text-signal transition-colors hover:text-signal-deep"
                        >
                          [{r.cta}]
                        </button>
                      </motion.li>
                    ))}
                  </motion.ul>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <div className="flex shrink-0 items-center gap-3">
          <button
            onClick={toggleTheme}
            role="switch"
            aria-checked={theme === "dark"}
            aria-label="Toggle dark mode"
            className="press focus-ring relative h-7 w-14 shrink-0 rounded-full bg-mist transition-colors dark:bg-slate-800/60"
          >
            <span
              className={`absolute top-0.5 flex h-6 w-6 items-center justify-center rounded-full bg-white text-xs shadow transition-all duration-200 ease-out dark:bg-slate-700 ${
                theme === "dark" ? "left-7" : "left-0.5"
              }`}
            >
              {theme === "dark" ? "🌙" : "☀️"}
            </span>
          </button>

          <button
            onClick={() => setProfileOpen(true)}
            className="press focus-ring flex h-9 w-9 items-center justify-center rounded-full bg-charcoal text-sm font-semibold text-white transition-opacity hover:opacity-90 dark:bg-mist dark:text-charcoal"
            title={`${profile.firstName} ${profile.lastName}`}
          >
            {profile.avatar ? (
              <img src={profile.avatar} alt="" className="h-9 w-9 rounded-full object-cover" />
            ) : (
              initials(profile)
            )}
          </button>
        </div>
      </div>
    </header>
  );
}
