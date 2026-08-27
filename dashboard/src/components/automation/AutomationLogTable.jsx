import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Badge from "../Badge.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";
import { pipedriveDealUrl } from "../../lib/constants.js";
import { relativeTime } from "../../lib/time.js";

const TAG_COLOR = { Interested: "green", "Not Interested": "red", OutOfOffice: "yellow", "Wrong Person": "gray" };
const STATUS_COLOR = { "Created Deal": "green", Failed: "red", Skipped: "gray", "Lost/Archived": "gray" };

// Keep this to a glance on the main dashboard — a handful of the most recent runs,
// not the whole log. "Show all" expands it inline for anyone who needs the full list.
const VISIBLE_LIMIT = 5;

export default function AutomationLogTable() {
  const { snapshot, openDrawer, reRunAutomations } = useDashboard();
  const [failuresOnly, setFailuresOnly] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [selected, setSelected] = useState(new Set());
  const [rerunning, setRerunning] = useState(false);

  const filteredRows = useMemo(() => {
    const all = snapshot?.automationLog || [];
    return failuresOnly ? all.filter((r) => r.pipedriveStatus === "Failed") : all;
  }, [snapshot, failuresOnly]);

  const rows = expanded ? filteredRows : filteredRows.slice(0, VISIBLE_LIMIT);
  const hiddenCount = filteredRows.length - rows.length;

  const selectedFailed = useMemo(() => {
    const all = snapshot?.automationLog || [];
    return all.filter((r) => selected.has(r.id) && r.pipedriveStatus === "Failed");
  }, [snapshot, selected]);

  const toggleRow = (id) =>
    setSelected((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

  const toggleAll = () => {
    setSelected((prev) => (prev.size === rows.length ? new Set() : new Set(rows.map((r) => r.id))));
  };

  const handleRerun = async () => {
    setRerunning(true);
    try {
      await reRunAutomations(selectedFailed.map((r) => r.id));
      setSelected(new Set());
    } finally {
      setRerunning(false);
    }
  };

  if (!snapshot) return null;

  return (
    <section id="card-automation-log" className="mx-4 mb-6 mt-2 md:mx-6">
      <div className="overflow-hidden rounded-2xl border border-line/20 bg-white shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line/15 px-3 py-2 dark:border-slate-800/60">
          <div className="flex items-baseline gap-2">
            <h2 className="text-sm font-semibold uppercase tracking-wide text-charcoal/80 dark:text-slate-50">
              Smartlead → Pipedrive Automation Log
            </h2>
            <span className="text-[11px] font-medium text-charcoal/40 dark:text-slate-500">
              {expanded ? filteredRows.length : `${rows.length} of ${filteredRows.length}`}
            </span>
          </div>
          <label className="focus-within:ring-2 focus-within:ring-signal/50 flex items-center gap-2 rounded text-xs font-medium">
            <input
              type="checkbox"
              checked={failuresOnly}
              onChange={(e) => setFailuresOnly(e.target.checked)}
              className="h-3.5 w-3.5 accent-signal"
            />
            Show failures only
          </label>
        </header>

        <AnimatePresence initial={false}>
          {selectedFailed.length > 0 && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0, transition: { duration: 0.15, ease: "easeIn" } }}
              transition={{ duration: 0.2, ease: "easeOut" }}
              className="overflow-hidden"
            >
              <div className="flex items-center justify-between gap-3 bg-signal/10 px-4 py-2 text-sm">
                <span className="font-semibold text-signal-deep dark:text-signal">
                  {selectedFailed.length} failed automation{selectedFailed.length > 1 ? "s" : ""} selected
                </span>
                <button
                  onClick={handleRerun}
                  disabled={rerunning}
                  className="press focus-ring rounded-lg bg-signal px-3 py-1.5 text-xs font-bold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 disabled:active:scale-100"
                >
                  {rerunning ? (
                    <span className="inline-flex items-center gap-1.5">
                      <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden />
                      Re-running…
                    </span>
                  ) : (
                    `Re-Run ${selectedFailed.length} Failed Automation${selectedFailed.length > 1 ? "s" : ""}`
                  )}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="thin-scroll overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="bg-mist/60 text-left text-[11px] uppercase tracking-wide text-charcoal/50 dark:bg-slate-800/50 dark:text-slate-400">
              <tr>
                <th className="w-8 px-3 py-2">
                  <input
                    type="checkbox"
                    checked={rows.length > 0 && selected.size === rows.length}
                    onChange={toggleAll}
                    className="h-3.5 w-3.5 accent-signal"
                  />
                </th>
                <th className="px-3 py-2 font-semibold">Timestamp / Lead</th>
                <th className="px-3 py-2 font-semibold">Smartlead Tag</th>
                <th className="px-3 py-2 font-semibold">Rule Executed</th>
                <th className="px-3 py-2 font-semibold">Pipedrive Status</th>
                <th className="px-3 py-2 font-semibold">Action / Error Note</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line/10 dark:divide-slate-800/60">
              {rows.map((row) => (
                <tr
                  key={row.id}
                  tabIndex={0}
                  role="button"
                  aria-label={`Open automation log entry for ${row.leadName}`}
                  className={`focus-ring cursor-pointer transition-colors hover:bg-mist/50 dark:hover:bg-slate-800/40 ${
                    selected.has(row.id) ? "bg-signal/5" : ""
                  }`}
                  onClick={() => openDrawer("automation", row)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      openDrawer("automation", row);
                    }
                  }}
                >
                  <td className="px-3 py-2" onClick={(e) => e.stopPropagation()}>
                    <input
                      type="checkbox"
                      checked={selected.has(row.id)}
                      onChange={() => toggleRow(row.id)}
                      className="h-3.5 w-3.5 accent-signal"
                    />
                  </td>
                  <td className="px-3 py-2">
                    <p className="font-medium">{row.leadName}</p>
                    <p className="text-[11px] text-charcoal/50 dark:text-slate-400">
                      {row.company} · {relativeTime(row.timestamp)}
                    </p>
                  </td>
                  <td className="px-3 py-2">
                    <Badge color={TAG_COLOR[row.smartleadTag] || "gray"}>{row.smartleadTag}</Badge>
                  </td>
                  <td className="px-3 py-2 text-xs text-charcoal/70 dark:text-slate-400">{row.ruleExecuted}</td>
                  <td className="px-3 py-2">
                    <Badge color={STATUS_COLOR[row.pipedriveStatus] || "gray"} dot>
                      {row.pipedriveStatus}
                    </Badge>
                  </td>
                  <td className="max-w-[260px] px-3 py-2 font-mono text-[11px]">
                    {row.pipedriveStatus === "Created Deal" && row.dealId ? (
                      <a
                        href={pipedriveDealUrl(row.dealId)}
                        target="_blank"
                        rel="noreferrer"
                        onClick={(e) => e.stopPropagation()}
                        className="focus-ring rounded text-signal underline transition-colors hover:text-signal-deep"
                      >
                        Deal #{row.dealId}
                      </a>
                    ) : (
                      <span className="line-clamp-2 text-charcoal/60 dark:text-slate-400">{row.note}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && (
            <p className="p-6 text-center text-xs text-charcoal/40 dark:text-slate-500">No automation runs match this filter.</p>
          )}
        </div>

        {(hiddenCount > 0 || expanded) && filteredRows.length > VISIBLE_LIMIT && (
          <div className="border-t border-line/15 px-3 py-2 dark:border-slate-800/60">
            <button
              onClick={() => setExpanded((e) => !e)}
              className="press focus-ring w-full rounded-lg py-1 text-center text-xs font-semibold text-charcoal/60 transition-colors hover:bg-mist/60 hover:text-charcoal dark:text-slate-400 dark:hover:bg-slate-800/50 dark:hover:text-slate-200"
            >
              {expanded ? "Show fewer ↑" : `Show all ${filteredRows.length} runs ↓`}
            </button>
          </div>
        )}
      </div>
    </section>
  );
}
