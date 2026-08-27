// In-memory store for the pieces of dashboard state that are the dashboard's own
// (not owned by Smartlead/Pipedrive/HeyReach): the automation log's local mirror,
// tasks, and muted-alert acknowledgements. Resets on server restart — swap for a
// real database when this moves past a single-instance dev/demo deployment.
import { buildAutomationLog, buildTasks, domains as seedDomains } from "../../src/lib/mockData.js";

export const store = {
  automationLog: buildAutomationLog(24),
  tasks: buildTasks(),
  domains: seedDomains.map((d) => ({ ...d })),
  mutedAlerts: new Set(),
};

export function runArchiveSweep() {
  const now = Date.now();
  for (const t of store.tasks) {
    if (t.status === "Done" && t.completedAt && !t.isArchived) {
      const ageDays = (now - new Date(t.completedAt).getTime()) / 86400000;
      if (ageDays >= 7) t.isArchived = true;
    }
  }
}
