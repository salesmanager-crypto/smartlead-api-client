import { Router } from "express";
import { smartlead, heyreach, pipedrive, safeLive } from "../lib/liveClients.js";
import { store, runArchiveSweep } from "../data/store.js";
import {
  smartleadSnapshot as mockSmartlead,
  heyreachSnapshot as mockHeyreach,
  inboxInfra as mockInboxInfra,
  seoHealth as mockSeo,
  dealSummary as mockDealSummary,
  PIPELINE_STAGES,
  OWNER,
} from "../../src/lib/mockData.js";

export const router = Router();

async function loadSmartlead() {
  if (!smartlead) return { ...mockSmartlead, live: false };
  const { value, live } = await safeLive(
    "smartlead.getAnalyticsOverview",
    () => smartlead.getAnalyticsOverview(),
    null
  );
  if (!live || !value) return { ...mockSmartlead, live: false };
  // Smartlead's overview shape varies by account/plan — pick out what we recognize
  // and fall back to mock numbers for anything missing, rather than showing zeros.
  return {
    totalEmailsSent: value.sent_count ?? value.total_sent ?? mockSmartlead.totalEmailsSent,
    openRate: value.open_rate ?? value.unique_open_rate ?? mockSmartlead.openRate,
    replyRate: value.reply_rate ?? value.unique_reply_rate ?? mockSmartlead.replyRate,
    trend: mockSmartlead.trend,
    live: true,
  };
}

async function loadHeyreach() {
  if (!heyreach) return { ...mockHeyreach, live: false };
  const { value, live } = await safeLive("heyreach.listCampaigns", () => heyreach.listCampaigns({ limit: 50 }), null);
  if (!live || !value) return { ...mockHeyreach, live: false };
  const campaigns = value.items || value.data || (Array.isArray(value) ? value : []);
  return { ...mockHeyreach, campaignCount: campaigns.length, live: true };
}

async function loadDomainsAndInboxes() {
  if (!smartlead) return { domains: store.domains, inboxes: mockInboxInfra, live: false };
  const { value, live } = await safeLive("smartlead.getAllInboxHealth", () => smartlead.getAllInboxHealth(), null);
  if (!live || !Array.isArray(value)) return { domains: store.domains, inboxes: mockInboxInfra, live: false };

  const domains = value.map((entry, i) => {
    const acct = entry.account || {};
    const stats = entry.warmupStats || {};
    const health = Number(stats.health_score ?? stats.deliverability ?? 100);
    return {
      id: `live_${acct.id ?? i}`,
      domain: acct.from_email?.split("@")[1] || acct.email || `inbox-${i}`,
      status: acct.warmup_details?.status === "active" ? "warming" : acct.is_smtp_success ? "active" : "dormant",
      deliverability: Number.isFinite(health) ? health : 92,
      blacklists: [],
      emailAccountId: acct.id,
    };
  });
  const active = domains.filter((d) => d.status === "active").length;
  const dead = domains.filter((d) => d.status === "dormant").length;
  return { domains: domains.length ? domains : store.domains, inboxes: { activeInboxes: active, deadInboxes: dead }, live: true };
}

async function loadPipeline() {
  if (!pipedrive) return { ...mockDealSummary(), live: false };
  const { value, live } = await safeLive("pipedrive.getDeals", () => pipedrive.getDeals({ status: "all_not_deleted", ownerId: OWNER.id }), null);
  if (!live || !value?.data) return { ...mockDealSummary(), live: false };

  const stages = await safeLive("pipedrive.getStages", () => pipedrive.getStages(), null);
  const stageNameById = new Map((stages.value?.data || []).map((s) => [s.id, s.name]));

  const deals = value.data.map((d) => {
    const stageName = stageNameById.get(d.stage_id) || (d.status === "won" ? "Closed Won" : d.status === "lost" ? "Closed Lost" : "Deal Created");
    const lastActivity = d.update_time ? new Date(d.update_time.replace(" ", "T") + "Z").toISOString() : new Date().toISOString();
    const staleHours = (Date.now() - new Date(lastActivity).getTime()) / 3600000;
    return { id: d.id, title: d.title, stage: stageName, value: d.value || 0, ownerId: d.owner_id?.value, lastActivity, staleHours };
  });
  const byStage = PIPELINE_STAGES.map((stage) => {
    const inStage = deals.filter((d) => d.stage === stage);
    return { stage, count: inStage.length, value: inStage.reduce((s, d) => s + d.value, 0) };
  });
  const staleOpen = deals.filter((d) => d.stage !== "Closed Won" && d.stage !== "Closed Lost" && d.staleHours >= 48);
  return { deals, byStage, staleOpen, live: true };
}

function computeAlerts({ domains, pipeline, tasks }) {
  const alerts = [];
  for (const d of domains) {
    if (d.status !== "dormant" && d.deliverability < 95 && !store.mutedAlerts.has(`alert_domain_${d.id}`)) {
      alerts.push({
        id: `alert_domain_${d.id}`,
        severity: d.deliverability < 70 ? "critical" : "warning",
        type: "domain",
        title: `${d.domain} deliverability at ${d.deliverability}%`,
        detail: d.blacklists?.length ? `Listed on: ${d.blacklists.join(", ")}` : "Below the 95% threshold",
        refId: d.id,
        data: { domain: d },
      });
    }
  }
  for (const deal of pipeline.staleOpen.slice(0, 5)) {
    const id = `alert_deal_${deal.id}`;
    if (store.mutedAlerts.has(id)) continue;
    alerts.push({
      id,
      severity: "warning",
      type: "deal",
      title: `${deal.title} unaddressed for ${Math.floor(deal.staleHours)}h`,
      detail: `Stage: ${deal.stage} · $${deal.value.toLocaleString()}`,
      refId: deal.id,
    });
  }
  const today = new Date().toISOString().slice(0, 10);
  for (const t of tasks.filter((t) => t.status !== "Done" && t.dueDate < today)) {
    const id = `alert_task_${t.id}`;
    if (store.mutedAlerts.has(id)) continue;
    alerts.push({ id, severity: "critical", type: "task", title: `Task overdue: ${t.title}`, detail: `Was due ${t.dueDate}`, refId: t.id });
  }
  return alerts;
}

router.get("/snapshot", async (_req, res) => {
  runArchiveSweep();

  const [sl, hr, di, pipeline] = await Promise.all([loadSmartlead(), loadHeyreach(), loadDomainsAndInboxes(), loadPipeline()]);

  const failedInteresting = store.automationLog.filter((r) => r.smartleadTag === "Interested" && r.pipedriveStatus === "Failed");

  res.json({
    source: {
      smartlead: sl.live ? "live" : "mock",
      heyreach: hr.live ? "live" : "mock",
      domains: di.live ? "live" : "mock",
      pipeline: pipeline.live ? "live" : "mock",
      seo: "mock",
    },
    smartlead: sl,
    heyreach: hr,
    inboxes: di.inboxes,
    domains: di.domains,
    seo: mockSeo,
    pipeline,
    automationLog: store.automationLog,
    tasks: store.tasks,
    alerts: computeAlerts({ domains: di.domains, pipeline, tasks: store.tasks }),
    meetingsToday: 3,
    hotRepliesUnsynced: failedInteresting.length,
  });
});
