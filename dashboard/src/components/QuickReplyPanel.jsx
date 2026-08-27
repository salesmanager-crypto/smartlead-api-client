import { useState } from "react";
import { useDashboard } from "../context/DashboardContext.jsx";

// Standalone quick-reply composer — shared by the SidebarDrawer's automation
// detail view (third-layer glance) and InboxPage's master-detail center pane
// (embedded inline, per the Inbox page spec: reply without leaving the page).
export default function QuickReplyPanel({ row, label = "Quick reply · sends via Smartlead, no tab switch" }) {
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
    <div>
      <p className="mb-1.5 text-[11px] font-semibold uppercase tracking-wide text-charcoal/45 dark:text-slate-500">{label}</p>
      <textarea
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder={`Reply to ${row.leadName}, or paste a booking link…`}
        rows={4}
        className="focus-ring w-full resize-none rounded-lg border border-line/25 bg-transparent p-2.5 text-sm transition-colors focus:border-signal dark:border-slate-700/60"
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
    </div>
  );
}
