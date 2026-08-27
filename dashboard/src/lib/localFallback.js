// In-browser fallback data layer — used only when `server/index.js` isn't reachable.
// Mirrors the shape (and mutation behavior) of the real Express API in
// dashboard/server/, so the dashboard is still fully interactive as a standalone
// static preview. Nothing here persists across a page reload; run `npm run dev:all`
// for a real backing store.
import {
  smartleadSnapshot,
  heyreachSnapshot,
  inboxInfra,
  domains as seedDomains,
  seoHealth,
  dealSummary,
  buildAutomationLog,
  buildTasks,
} from "./mockData.js";

const state = {
  domains: seedDomains.map((d) => ({ ...d })),
  automationLog: buildAutomationLog(24),
  tasks: buildTasks(),
  mutedAlerts: new Set(),
};

const wait = (ms = 220) => new Promise((r) => setTimeout(r, ms));

function computeAlerts() {
  const alerts = [];
  for (const d of state.domains) {
    if (d.status !== "dormant" && d.deliverability < 95) {
      alerts.push({
        id: `alert_domain_${d.id}`,
        severity: d.deliverability < 70 ? "critical" : "warning",
        type: "domain",
        title: `${d.domain} deliverability at ${d.deliverability}%`,
        detail: d.blacklists.length ? `Listed on: ${d.blacklists.join(", ")}` : "Below the 95% threshold",
        refId: d.id,
      });
    }
  }
  const { staleOpen } = dealSummary();
  for (const deal of staleOpen.slice(0, 5)) {
    alerts.push({
      id: `alert_deal_${deal.id}`,
      severity: "warning",
      type: "deal",
      title: `${deal.title} unaddressed for ${Math.floor(deal.staleHours)}h`,
      detail: `Stage: ${deal.stage} · $${deal.value.toLocaleString()}`,
      refId: deal.id,
    });
  }
  const overdue = state.tasks.filter((t) => t.status !== "Done" && t.dueDate < new Date().toISOString().slice(0, 10));
  for (const t of overdue) {
    alerts.push({
      id: `alert_task_${t.id}`,
      severity: "critical",
      type: "task",
      title: `Task overdue: ${t.title}`,
      detail: `Was due ${t.dueDate}`,
      refId: t.id,
    });
  }
  return alerts.filter((a) => !state.mutedAlerts.has(a.id));
}

function runArchiveSweep() {
  const now = Date.now();
  for (const t of state.tasks) {
    if (t.status === "Done" && t.completedAt && !t.isArchived) {
      const ageDays = (now - new Date(t.completedAt).getTime()) / 86400000;
      if (ageDays >= 7) t.isArchived = true;
    }
  }
}

export async function getSnapshot() {
  await wait();
  runArchiveSweep();
  const { byStage, deals, staleOpen } = dealSummary();
  const failedInteresting = state.automationLog.filter(
    (r) => r.smartleadTag === "Interested" && r.pipedriveStatus === "Failed"
  );
  return {
    source: "local-fallback",
    smartlead: smartleadSnapshot,
    heyreach: heyreachSnapshot,
    inboxes: inboxInfra,
    domains: state.domains,
    seo: seoHealth,
    pipeline: { byStage, deals, staleOpen },
    automationLog: state.automationLog,
    tasks: state.tasks,
    alerts: computeAlerts(),
    meetingsToday: 3,
    hotRepliesUnsynced: failedInteresting.length,
  };
}

export async function reRunAutomations(ids) {
  await wait(500);
  const updated = [];
  for (const row of state.automationLog) {
    if (!ids.includes(row.id)) continue;
    if (row.pipedriveStatus === "Failed") {
      const succeeded = Math.random() > 0.25;
      row.pipedriveStatus = succeeded ? "Created Deal" : "Failed";
      row.dealId = succeeded ? row.dealId || 4200 + Math.floor(Math.random() * 400) : row.dealId;
      row.note = succeeded
        ? `Deal #${row.dealId} (re-synced)`
        : JSON.stringify({ error: "PipedriveError", status: 429, body: { success: false, error: "rate_limited" } });
    }
    updated.push({ ...row });
  }
  return updated;
}

export async function setDomainCooldown(domainId, cooldown) {
  await wait(400);
  const d = state.domains.find((x) => x.id === domainId);
  if (!d) throw new Error("Domain not found");
  d.status = cooldown ? "warming" : "active";
  d.coolingDown = cooldown;
  return { ...d };
}

export async function sendQuickReply(payload) {
  await wait(500);
  return { ok: true, sentAt: new Date().toISOString(), echo: payload };
}

export async function updateTask(id, patch) {
  await wait(150);
  const t = state.tasks.find((x) => x.id === id);
  if (!t) throw new Error("Task not found");
  Object.assign(t, patch);
  if (patch.status === "Done" && !t.completedAt) t.completedAt = new Date().toISOString();
  if (patch.status && patch.status !== "Done") {
    t.completedAt = null;
    t.isArchived = false;
  }
  return { ...t };
}

export async function createTask(task) {
  await wait(150);
  const newTask = {
    id: `task_${Date.now()}`,
    status: "To Do",
    priority: "Medium",
    category: "Smartlead",
    dueDate: new Date(Date.now() + 3 * 86400000).toISOString().slice(0, 10),
    completedAt: null,
    isArchived: false,
    description: "",
    ...task,
  };
  state.tasks.unshift(newTask);
  return newTask;
}

export async function muteAlert(id) {
  await wait(120);
  state.mutedAlerts.add(id);
  return { ok: true };
}

export async function resetLayout() {
  await wait(80);
  return { ok: true };
}
