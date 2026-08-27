import { useMemo, useState } from "react";
import Badge from "../Badge.jsx";
import { useDashboard } from "../../context/DashboardContext.jsx";
import { pipedriveDealUrl } from "../../lib/constants.js";
import { relativeTime } from "../../lib/time.js";

const TAG_COLOR = { Interested: "green", "Not Interested": "red", OutOfOffice: "yellow", "Wrong Person": "gray" };
const STATUS_COLOR = { "Created Deal": "green", Failed: "red", Skipped: "gray", "Lost/Archived": "gray" };

export default function AutomationLogTable() {
  const { snapshot, openDrawer, reRunAutomations } = useDashboard();
  const [failuresOnly, setFailuresOnly] = useState(false);
  const [selected, setSelected] = useState(new Set());
  const [rerunning, setRerunning] = useState(false);

  const rows = useMemo(() => {
    const all = snapshot?.automationLog || [];
    return failuresOnly ? all.filter((r) => r.pipedriveStatus === "Failed") : all;
  }, [snapshot, failuresOnly]);

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
    <section id="card-automation-log" className="mx-5 mb-8 mt-2 md:mx-8">
      <div className="overflow-hidden rounded-2xl border border-line/20 bg-white shadow-card dark:border-white/10 dark:bg-white/[0.04] dark:shadow-card-dark">
        <header className="flex flex-wrap items-center justify-between gap-3 border-b border-line/15 px-4 py-3 dark:border-white/10">
          <h2 className="text-sm font-bold uppercase tracking-wide text-charcoal/80 dark:text-mist/90">
            Smartlead → Pipedrive Automation Log
          </h2>
          <label className="flex items-center gap-2 text-xs font-medium">
            <input
              type="checkbox"
              checked={failuresOnly}
              onChange={(e) => setFailuresOnly(e.target.checked)}
              className="h-3.5 w-3.5 accent-signal"
            />
            Show failures only
          </label>
        </header>

        {selectedFailed.length > 0 && (
          <div className="flex items-center justify-between gap-3 bg-signal/10 px-4 py-2 text-sm">
            <span className="font-semibold text-signal-deep dark:text-signal">
              {selectedFailed.length} failed automation{selectedFailed.length > 1 ? "s" : ""} selected
            </span>
            <button
              onClick={handleRerun}
              disabled={rerunning}
              className="rounded-lg bg-signal px-3 py-1.5 text-xs font-bold text-white transition-opacity hover:opacity-90 disabled:opacity-50"
            >
              {rerunning ? "Re-running…" : `Re-Run ${selectedFailed.length} Failed Automation${selectedFailed.length > 1 ? "s" : ""}`}
            </button>
          </div>
        )}

        <div className="thin-scroll overflow-x-auto">
          <table className="w-full min-w-[760px] text-sm">
            <thead className="bg-mist/60 text-left text-[11px] uppercase tracking-wide text-charcoal/50 dark:bg-white/[0.06] dark:text-mist/50">
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
            <tbody className="divide-y divide-line/10 dark:divide-white/5">
              {rows.map((row) => (
                <tr
                  key={row.id}
                  className={`cursor-pointer hover:bg-mist/50 dark:hover:bg-white/5 ${
                    selected.has(row.id) ? "bg-signal/5" : ""
                  }`}
                  onClick={() => openDrawer("automation", row)}
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
                    <p className="text-[11px] text-charcoal/50 dark:text-mist/50">
                      {row.company} · {relativeTime(row.timestamp)}
                    </p>
                  </td>
                  <td className="px-3 py-2">
                    <Badge color={TAG_COLOR[row.smartleadTag] || "gray"}>{row.smartleadTag}</Badge>
                  </td>
                  <td className="px-3 py-2 text-xs text-charcoal/70 dark:text-mist/70">{row.ruleExecuted}</td>
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
                        className="text-signal underline hover:text-signal-deep"
                      >
                        Deal #{row.dealId}
                      </a>
                    ) : (
                      <span className="line-clamp-2 text-charcoal/60 dark:text-mist/60">{row.note}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 && (
            <p className="p-6 text-center text-xs text-charcoal/40 dark:text-mist/40">No automation runs match this filter.</p>
          )}
        </div>
      </div>
    </section>
  );
}
