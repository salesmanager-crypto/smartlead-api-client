import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";
import Badge from "../components/Badge.jsx";
import QuickReplyPanel from "../components/QuickReplyPanel.jsx";
import { useDashboard } from "../context/DashboardContext.jsx";
import { pipedriveDealUrl } from "../lib/constants.js";
import { relativeTime } from "../lib/time.js";

const TAG_COLOR = { Interested: "green", "Not Interested": "red", OutOfOffice: "yellow", "Wrong Person": "gray" };
const STATUS_COLOR = { "Created Deal": "green", Failed: "red", Skipped: "gray", "Lost/Archived": "gray" };

function replySnippetFor(row) {
  if (row.smartleadTag === "Interested") return "“This looks interesting, tell me more about US market entry.”";
  if (row.smartleadTag === "OutOfOffice") return "“I'm currently out of office and will respond when I return.”";
  return "“Not the right fit for us right now, please remove me from this list.”";
}

// Dedicated Smartlead → Pipedrive Triaging & Log Hub — a full transactional
// database view (every automation run, filterable) with a master-detail layout:
// the left list drives a center reading pane with an inline quick-reply editor,
// so triaging a reply never leaves this page. The resizable SidebarDrawer (the
// global "third layer") is reserved here specifically for raw API debug/error
// payloads — opened deliberately from a failed run, not on every row click.
export default function InboxPage() {
  const { snapshot, reRunAutomations, openDrawer } = useDashboard();
  const [searchParams, setSearchParams] = useSearchParams();
  const [failuresOnly, setFailuresOnly] = useState(false);
  const [tagFilter, setTagFilter] = useState("All");
  const [query, setQuery] = useState("");
  const [rerunning, setRerunning] = useState(false);

  const rows = snapshot?.automationLog || [];

  const filtered = useMemo(() => {
    return rows.filter((r) => {
      if (failuresOnly && r.pipedriveStatus !== "Failed") return false;
      if (tagFilter !== "All" && r.smartleadTag !== tagFilter) return false;
      if (query && !`${r.leadName} ${r.company}`.toLowerCase().includes(query.toLowerCase())) return false;
      return true;
    });
  }, [rows, failuresOnly, tagFilter, query]);

  const selectedId = searchParams.get("log");
  const selected = filtered.find((r) => r.id === selectedId) || filtered[0] || null;

  useEffect(() => {
    if (filtered.length && (!selectedId || !filtered.some((r) => r.id === selectedId))) {
      const next = new URLSearchParams(searchParams);
      next.set("log", filtered[0].id);
      setSearchParams(next, { replace: true });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filtered, selectedId]);

  const select = (id) => {
    const next = new URLSearchParams(searchParams);
    next.set("log", id);
    setSearchParams(next);
  };

  if (!snapshot) return <div className="mx-4 my-4 text-sm text-charcoal/40 dark:text-slate-500 md:mx-6">Loading…</div>;

  return (
    <div className="mx-4 my-4 md:mx-6">
      <header className="mb-3">
        <h1 className="text-lg font-semibold tracking-tight">Smartlead → Pipedrive Triaging &amp; Log Hub</h1>
        <p className="text-xs text-charcoal/50 dark:text-slate-500">
          {filtered.length} of {rows.length} automation runs
        </p>
      </header>

      <div className="flex h-[calc(100vh-190px)] min-h-[440px] gap-4">
        {/* Left — filterable, scrollable log of every automation run */}
        <aside className="flex w-full max-w-sm shrink-0 flex-col overflow-hidden rounded-2xl border border-line/20 bg-white shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          <div className="shrink-0 space-y-2 border-b border-line/15 p-3 dark:border-slate-800/60">
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search lead or company…"
              className="focus-ring w-full rounded-md border border-line/25 bg-transparent px-2 py-1.5 text-xs transition-colors focus:border-signal dark:border-slate-700/60"
            />
            <div className="flex flex-wrap items-center gap-2">
              <select
                value={tagFilter}
                onChange={(e) => setTagFilter(e.target.value)}
                className="focus-ring rounded-md border border-line/25 bg-transparent px-2 py-1 text-xs transition-colors dark:border-slate-700/60"
              >
                <option value="All">All tags</option>
                {Object.keys(TAG_COLOR).map((t) => (
                  <option key={t}>{t}</option>
                ))}
              </select>
              <label className="flex items-center gap-1.5 text-xs font-medium">
                <input
                  type="checkbox"
                  checked={failuresOnly}
                  onChange={(e) => setFailuresOnly(e.target.checked)}
                  className="h-3.5 w-3.5 accent-signal"
                />
                Failures only
              </label>
            </div>
          </div>
          <ul className="thin-scroll min-h-0 flex-1 divide-y divide-line/10 overflow-auto dark:divide-slate-800/60">
            {filtered.map((row) => (
              <li key={row.id}>
                <button
                  onClick={() => select(row.id)}
                  className={`focus-ring flex w-full flex-col gap-1 px-3 py-2.5 text-left transition-colors hover:bg-mist/60 dark:hover:bg-slate-800/40 ${
                    selected?.id === row.id ? "bg-signal/5" : ""
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm font-medium">{row.leadName}</span>
                    <Badge color={STATUS_COLOR[row.pipedriveStatus] || "gray"} dot>
                      {row.pipedriveStatus}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-[11px] text-charcoal/50 dark:text-slate-500">{row.company}</span>
                    <span className="shrink-0 text-[11px] text-charcoal/40 dark:text-slate-500">{relativeTime(row.timestamp)}</span>
                  </div>
                  <Badge color={TAG_COLOR[row.smartleadTag] || "gray"}>{row.smartleadTag}</Badge>
                </button>
              </li>
            ))}
            {filtered.length === 0 && (
              <li className="p-6 text-center text-xs text-charcoal/40 dark:text-slate-500">No runs match this filter.</li>
            )}
          </ul>
        </aside>

        {/* Center — selected run's content, automation properties, inline quick reply */}
        <main className="thin-scroll min-w-0 flex-1 overflow-auto rounded-2xl border border-line/20 bg-white p-5 shadow-card dark:border-slate-800/60 dark:bg-slate-900 dark:shadow-card-dark">
          {!selected ? (
            <p className="text-sm text-charcoal/40 dark:text-slate-500">Select a run from the list.</p>
          ) : (
            <div className="space-y-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold">{selected.leadName}</h2>
                  <p className="text-sm text-charcoal/60 dark:text-slate-400">{selected.company}</p>
                  <p className="mt-1 font-mono text-xs text-charcoal/45 dark:text-slate-500">{selected.leadEmail}</p>
                </div>
                <div className="flex flex-wrap items-center gap-1.5">
                  <Badge color={TAG_COLOR[selected.smartleadTag] || "gray"}>{selected.smartleadTag}</Badge>
                  <Badge color={STATUS_COLOR[selected.pipedriveStatus] || "gray"} dot>
                    {selected.pipedriveStatus}
                  </Badge>
                  <Badge color="blue">Rule: {selected.ruleExecuted}</Badge>
                  <Badge color="gray">Campaign #{selected.campaignId}</Badge>
                </div>
              </div>

              <div>
                <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-charcoal/45 dark:text-slate-500">
                  Reply content
                </p>
                <p className="rounded-lg bg-mist/60 p-3 text-sm italic dark:bg-slate-800/50">{replySnippetFor(selected)}</p>
              </div>

              {selected.pipedriveStatus === "Created Deal" && selected.dealId && (
                <a
                  href={pipedriveDealUrl(selected.dealId)}
                  target="_blank"
                  rel="noreferrer"
                  className="focus-ring inline-block rounded text-xs font-semibold text-signal underline transition-colors hover:text-signal-deep"
                >
                  Open Deal #{selected.dealId} in Pipedrive ↗
                </a>
              )}

              {selected.pipedriveStatus === "Failed" && (
                <div className="flex flex-wrap items-center gap-2">
                  <button
                    onClick={() => openDrawer("automation", selected)}
                    className="press focus-ring rounded-lg border border-signal/30 bg-signal/10 px-3 py-1.5 text-xs font-semibold text-signal-deep transition-colors hover:bg-signal/20 dark:text-signal"
                  >
                    View raw API debug payload ↗
                  </button>
                  <button
                    onClick={async () => {
                      setRerunning(true);
                      try {
                        await reRunAutomations([selected.id]);
                      } finally {
                        setRerunning(false);
                      }
                    }}
                    disabled={rerunning}
                    className="press focus-ring rounded-lg bg-charcoal px-3 py-1.5 text-xs font-semibold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-mist dark:text-charcoal"
                  >
                    {rerunning ? "Re-running…" : "Re-Run This Automation"}
                  </button>
                </div>
              )}

              <div className="border-t border-line/15 pt-4 dark:border-slate-800/60">
                <QuickReplyPanel row={selected} />
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
