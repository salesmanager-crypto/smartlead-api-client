import { useCallback, useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useDashboard } from "../context/DashboardContext.jsx";
import Badge from "./Badge.jsx";
import { pipedriveDealUrl } from "../lib/constants.js";
import { relativeTime } from "../lib/time.js";

const CONTEXT_LABEL = { automation: "Automation Log", alert: "Alert", deal: "CRM Pipeline Deal" };

function useDrawerResize(setDrawerWidth) {
  const draggingRef = useRef(false);

  const onMouseDown = useCallback(() => {
    draggingRef.current = true;
    document.body.style.cursor = "ew-resize";
  }, []);

  useEffect(() => {
    const onMove = (e) => {
      if (!draggingRef.current) return;
      const pct = ((window.innerWidth - e.clientX) / window.innerWidth) * 100;
      setDrawerWidth(pct);
    };
    const onUp = () => {
      draggingRef.current = false;
      document.body.style.cursor = "";
    };
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    return () => {
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
    };
  }, [setDrawerWidth]);

  return onMouseDown;
}

function CodeBlock({ children }) {
  return (
    <pre className="thin-scroll max-h-40 overflow-auto rounded-lg bg-charcoal p-3 font-mono text-[11px] leading-relaxed text-mist">
      {children}
    </pre>
  );
}

function Section({ label, children }) {
  return (
    <div>
      <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-charcoal/45 dark:text-slate-500">{label}</p>
      {children}
    </div>
  );
}

function QuickReplyPanel({ row }) {
  const { sendQuickReply } = useDashboard();
  const [message, setMessage] = useState("");
  const [status, setStatus] = useState("idle");

  const send = async () => {
    if (!message.trim()) return;
    setStatus("sending");
    try {
      await sendQuickReply({
        channel: "smartlead",
        campaignId: row.campaignId,
        leadEmail: row.leadEmail,
        message,
      });
      setStatus("sent");
      setMessage("");
      setTimeout(() => setStatus("idle"), 2500);
    } catch {
      setStatus("error");
    }
  };

  return (
    <Section label="Quick reply · sends via Smartlead, no tab switch">
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={`Reply to ${row.leadName}, or paste a booking link…`}
        rows={3}
        className="focus-ring w-full resize-none rounded-lg border border-line/25 bg-transparent p-2 text-sm transition-colors focus:border-signal dark:border-slate-700/60"
      />
      <div className="mt-1.5 flex items-center justify-between">
        <span aria-live="polite" className="text-[11px] text-charcoal/40 dark:text-slate-500">
          {status === "sent" ? "Sent ✓" : status === "error" ? "Failed to send" : status === "sending" ? "Sending…" : "Thread " + row.campaignId}
        </span>
        <button
          onClick={send}
          disabled={status === "sending" || !message.trim()}
          className="press focus-ring rounded-lg bg-signal px-3 py-1.5 text-xs font-bold text-white transition-opacity hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-40 disabled:active:scale-100"
        >
          {status === "sending" ? (
            <span className="inline-flex items-center gap-1.5">
              <span className="h-3 w-3 animate-spin rounded-full border-2 border-white/40 border-t-white" aria-hidden />
              Sending
            </span>
          ) : (
            "Send Response"
          )}
        </button>
      </div>
    </Section>
  );
}

function AutomationDetail({ row }) {
  return (
    <div className="space-y-4">
      <Section label="Lead">
        <p className="text-base font-semibold">{row.leadName}</p>
        <p className="text-sm text-charcoal/60 dark:text-slate-400">{row.company}</p>
        <p className="mt-1 font-mono text-xs text-charcoal/45 dark:text-slate-500">{row.leadEmail}</p>
      </Section>
      <Section label="Reply snippet">
        <p className="rounded-lg bg-mist/60 p-2.5 text-sm italic dark:bg-slate-800/50">
          {row.smartleadTag === "Interested"
            ? "“This looks interesting, tell me more about US market entry.”"
            : row.smartleadTag === "OutOfOffice"
              ? "“I'm currently out of office and will respond when I return.”"
              : "“Not the right fit for us right now, please remove me from this list.”"}
        </p>
      </Section>
      <Section label="Automation">
        <div className="flex flex-wrap gap-1.5">
          <Badge color="blue">Rule: {row.ruleExecuted}</Badge>
          <Badge color={row.pipedriveStatus === "Failed" ? "red" : row.pipedriveStatus === "Created Deal" ? "green" : "gray"}>
            {row.pipedriveStatus}
          </Badge>
          <Badge color="gray">Campaign #{row.campaignId}</Badge>
        </div>
      </Section>
      {row.pipedriveStatus === "Failed" && (
        <Section label="Raw CRM API failure payload">
          <CodeBlock>{typeof row.note === "string" ? row.note : JSON.stringify(row.note, null, 2)}</CodeBlock>
        </Section>
      )}
      <QuickReplyPanel row={row} />
    </div>
  );
}

function AlertDetail({ alert }) {
  const domain = alert.data?.domain;
  return (
    <div className="space-y-4">
      <Section label="Summary">
        <p className="text-base font-semibold">{alert.title}</p>
        <p className="text-sm text-charcoal/60 dark:text-slate-400">{alert.detail}</p>
      </Section>
      {(domain || alert.type === "domain") && (
        <Section label="Infrastructure">
          <div className="space-y-1 text-sm">
            <p>
              Blacklist hits:{" "}
              <span className="font-semibold text-signal">{domain?.blacklists?.length ? domain.blacklists.join(", ") : "None detected"}</span>
            </p>
            <p>Deliverability: {domain?.deliverability ?? "—"}%</p>
            <a
              className="focus-ring inline-block rounded text-xs font-semibold text-signal underline transition-colors hover:text-signal-deep"
              href={`https://mxtoolbox.com/SuperTool.aspx?action=blacklist%3a${domain?.domain || ""}`}
              target="_blank"
              rel="noreferrer"
            >
              Run blacklist check on MXToolbox ↗
            </a>
            <br />
            <a
              className="focus-ring inline-block rounded text-xs font-semibold text-signal underline transition-colors hover:text-signal-deep"
              href={`https://porkbun.com/account/domainsSpeedy`}
              target="_blank"
              rel="noreferrer"
            >
              Open registrar (Porkbun) ↗
            </a>
          </div>
        </Section>
      )}
    </div>
  );
}

function DealRow({ deal, onOpen }) {
  return (
    <button
      onClick={() => onOpen(deal)}
      className="press focus-ring flex w-full items-center justify-between gap-2 rounded-lg border border-line/15 px-3 py-2 text-left text-sm transition-colors hover:bg-mist/60 dark:border-slate-800/60 dark:hover:bg-slate-800/40"
    >
      <span className="min-w-0 flex-1 truncate">{deal.title}</span>
      <span className="shrink-0 font-semibold">${deal.value.toLocaleString()}</span>
    </button>
  );
}

function DealDetail({ deal, onBack }) {
  return (
    <motion.div
      initial={{ opacity: 0, x: 12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ duration: 0.18, ease: "easeOut" }}
      className="space-y-4"
    >
      {onBack && (
        <button onClick={onBack} className="focus-ring rounded text-xs font-semibold text-signal transition-colors hover:text-signal-deep">
          ← Back to stage list
        </button>
      )}
      <Section label="Deal">
        <p className="text-base font-semibold">{deal.title}</p>
        <p className="text-sm text-charcoal/60 dark:text-slate-400">Stage: {deal.stage}</p>
      </Section>
      <Section label="Expected close value">
        <p className="text-2xl font-semibold text-signal">${deal.value.toLocaleString()}</p>
      </Section>
      <Section label="Activity">
        <p className="text-sm">Last touched {relativeTime(deal.lastActivity)}</p>
        {deal.staleHours >= 48 && <p className="mt-1 text-sm font-semibold text-signal">⚠ Unaddressed for {Math.floor(deal.staleHours)}h</p>}
      </Section>
      <Section label="Client diagnostics">
        <p className="rounded-lg bg-mist/60 p-2.5 text-sm dark:bg-slate-800/50">
          Domain health, SEO crawl status and outreach history for this account are available on the canvas view —
          cross-reference the Outbound Performance and SEO cards for the same client.
        </p>
      </Section>
    </motion.div>
  );
}

function PipelineStageDetail({ data }) {
  const [selectedDeal, setSelectedDeal] = useState(null);
  if (data.deals && data.deals.length && !data.title) {
    if (selectedDeal) return <DealDetail deal={selectedDeal} onBack={() => setSelectedDeal(null)} />;
    return (
      <div className="space-y-3">
        <Section label={`${data.stage} · ${data.deals.length} deals`}>
          <div className="space-y-1.5">
            {data.deals.map((d) => (
              <DealRow key={d.id} deal={d} onOpen={setSelectedDeal} />
            ))}
            {data.deals.length === 0 && <p className="text-sm text-charcoal/40 dark:text-slate-500">No deals in this stage.</p>}
          </div>
        </Section>
      </div>
    );
  }
  return <DealDetail deal={data} />;
}

// Enter with a soft spring (spring-physics feels more natural than linear/cubic-bezier
// per the design system's Animation guidance); exit noticeably faster than enter
// (~65% of the perceived enter duration) so closing feels responsive, not sluggish.
const PANEL_ENTER = { type: "spring", stiffness: 380, damping: 34, mass: 0.9 };
const PANEL_EXIT = { type: "tween", duration: 0.18, ease: [0.4, 0, 1, 1] };
const BACKDROP_ENTER = { duration: 0.22, ease: "easeOut" };
const BACKDROP_EXIT = { duration: 0.15, ease: "easeIn" };

export default function SidebarDrawer() {
  const { drawer, closeDrawer, setDrawerWidth, muteAlert } = useDashboard();
  const onHandleDown = useDrawerResize(setDrawerWidth);

  const { context, data } = drawer;
  const dealIdForTray =
    context === "automation" ? data?.dealId : context === "deal" ? data?.id || data?.deals?.[0]?.id : null;

  return (
    <AnimatePresence>
      {drawer.open && (
        <>
          <motion.div
            key="drawer-backdrop"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={BACKDROP_ENTER}
            className="fixed inset-0 z-40 bg-charcoal/30 backdrop-blur-[1px]"
            onClick={closeDrawer}
          />
          <motion.aside
            key="drawer-panel"
            initial={{ x: "100%" }}
            animate={{ x: 0, transition: PANEL_ENTER }}
            exit={{ x: "100%", transition: PANEL_EXIT }}
            style={{ width: `${drawer.widthPct}vw` }}
            className="fixed right-0 top-0 z-50 flex h-screen flex-col border-l border-line/20 bg-white shadow-2xl dark:border-slate-800/60 dark:bg-slate-900"
          >
            <div
              onMouseDown={onHandleDown}
              className="absolute -left-1.5 top-0 h-full w-3 cursor-ew-resize"
              title="Drag to resize"
            />
        <header className="flex shrink-0 items-center justify-between border-b border-line/15 px-5 py-4 dark:border-slate-800/60">
          <div>
            <p className="text-[11px] font-semibold uppercase tracking-wide text-charcoal/45 dark:text-slate-500">
              {CONTEXT_LABEL[context]}
            </p>
          </div>
          <button
            onClick={closeDrawer}
            className="press focus-ring rounded-lg px-2 py-1 text-lg leading-none text-charcoal/50 transition-colors hover:bg-mist dark:text-slate-400 dark:hover:bg-slate-800/60"
            aria-label="Close"
          >
            ✕
          </button>
        </header>

        <div className="thin-scroll min-h-0 flex-1 overflow-auto px-5 py-4">
          {context === "automation" && <AutomationDetail row={data} />}
          {context === "alert" && <AlertDetail alert={data} />}
          {context === "deal" && <PipelineStageDetail data={data} />}
        </div>

        <footer className="flex shrink-0 flex-wrap items-center gap-2 border-t border-line/15 px-5 py-3 dark:border-slate-800/60">
          {context === "alert" && (
            <button
              onClick={() => {
                muteAlert(data.id);
                closeDrawer();
              }}
              className="press focus-ring rounded-lg border border-line/25 px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-mist dark:border-slate-700/60 dark:hover:bg-slate-800/60"
            >
              Mute Alert
            </button>
          )}
          {dealIdForTray && (
            <a
              href={pipedriveDealUrl(dealIdForTray)}
              target="_blank"
              rel="noreferrer"
              className="press focus-ring rounded-lg bg-charcoal px-3 py-1.5 text-xs font-semibold text-white transition-colors hover:opacity-90 dark:bg-mist dark:text-charcoal"
            >
              Open in Pipedrive
            </a>
          )}
          {context === "automation" && (
            <button className="press focus-ring rounded-lg border border-line/25 px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-mist dark:border-slate-700/60 dark:hover:bg-slate-800/60">
              Override in Smartlead
            </button>
          )}
          {context === "alert" && data.type === "domain" && (
            <button className="press focus-ring rounded-lg border border-line/25 px-3 py-1.5 text-xs font-semibold transition-colors hover:bg-mist dark:border-slate-700/60 dark:hover:bg-slate-800/60">
              Pause Domain
            </button>
          )}
            </footer>
          </motion.aside>
        </>
      )}
    </AnimatePresence>
  );
}
