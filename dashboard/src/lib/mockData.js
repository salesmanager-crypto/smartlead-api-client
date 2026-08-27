/**
 * Seed / simulated data for the Growth Ops Command Center.
 *
 * This module is imported by BOTH the browser (as a client-side fallback when
 * `server/index.js` isn't running) and the dashboard's Express server (as the
 * seed for services that don't have live credentials configured — see
 * dashboard/README.md for exactly which cards are live vs. simulated).
 *
 * It is intentionally pure JS with no DOM/Node-only APIs so it works in both places.
 * The shapes here match docs/Smartlead-Pipedrive-Automation-Workflow.md (owner,
 * categories, rule names, Pipedrive statuses) so the dashboard reads like Albert
 * Scott's real Smartlead <-> Pipedrive workflow, not a generic demo.
 */

export const OWNER = { id: 26939288, name: "Yoni Lebovits" };

export const PIPELINE_STAGES = [
  "Deal Created",
  "Discovery",
  "Proposal",
  "Negotiation",
  "Closed Won",
  "Closed Lost",
];

export const TASK_CATEGORIES = ["Smartlead", "Pipedrive", "Heyreach", "SEO", "Infrastructure"];
export const TASK_PRIORITIES = ["High", "Medium", "Low"];

// Deterministic-ish pseudo-random helper so refreshes don't flicker unrelated fields.
function seededRandom(seed) {
  let s = seed % 2147483647;
  if (s <= 0) s += 2147483646;
  return () => {
    s = (s * 16807) % 2147483647;
    return (s - 1) / 2147483646;
  };
}
const rand = seededRandom(4271);
const pick = (arr) => arr[Math.floor(rand() * arr.length)];
const daysAgo = (n) => new Date(Date.now() - n * 86400000).toISOString();
const hoursAgo = (n) => new Date(Date.now() - n * 3600000).toISOString();

// ---- Outbound performance (Smartlead / HeyReach split-screen) -------------

export function buildOutreachTrend(days = 14, base = 40) {
  const out = [];
  for (let i = days - 1; i >= 0; i--) {
    out.push({
      date: daysAgo(i).slice(0, 10),
      sent: Math.round(base + rand() * 25),
      replies: Math.round(4 + rand() * 8),
    });
  }
  return out;
}

export const smartleadSnapshot = {
  totalEmailsSent: 18420,
  openRate: 61.4,
  replyRate: 8.9,
  trend: buildOutreachTrend(14, 260),
};

export const heyreachSnapshot = {
  connectionsSent: 3120,
  acceptRate: 38.2,
  responseRate: 14.6,
  trend: buildOutreachTrend(14, 45),
};

export const inboxInfra = {
  activeInboxes: 46,
  deadInboxes: 3,
};

// ---- Domain asset ledger (also feeds the SEO card + deliverability alerts) --

export const domains = [
  { id: "dom_1", domain: "albertscott-outbound.com", status: "active", deliverability: 97.8, blacklists: [] },
  { id: "dom_2", domain: "as-marketplace.io", status: "active", deliverability: 96.1, blacklists: [] },
  { id: "dom_3", domain: "acme-outbound.com", status: "active", deliverability: 58.2, blacklists: ["Spamhaus DBL"] },
  { id: "dom_4", domain: "asgrowth.co", status: "warming", deliverability: 82.4, blacklists: [] },
  { id: "dom_5", domain: "as-reach.net", status: "warming", deliverability: 90.6, blacklists: [] },
  { id: "dom_6", domain: "legacy-outbound.org", status: "dormant", deliverability: 0, blacklists: [] },
];

// ---- SEO / technical health ------------------------------------------------

export const seoHealth = {
  coreWebVitals: { lcpMs: 2180, inpMs: 148, cls: 0.06, status: "good" },
  brokenLinks: 7,
  crawlErrors: 3,
};

// ---- CRM pipeline deals -----------------------------------------------------

const COMPANIES = [
  "Bukit Sari Organic Plantation",
  "Harborline Outdoor Co.",
  "Northfield Pet Supply",
  "Solace Home Goods",
  "Verdant Kitchenware",
  "Trueform Fitness",
  "Cascade Coffee Roasters",
  "Milele Skincare",
  "Ridgeback Tools",
  "Aurora Baby Co.",
  "Ironclad Auto Parts",
  "Bloomfield Textiles",
];

export function buildDeals() {
  let id = 4200;
  const deals = [];
  const perStage = { "Deal Created": 9, Discovery: 6, Proposal: 4, Negotiation: 3, "Closed Won": 5, "Closed Lost": 2 };
  for (const stage of PIPELINE_STAGES) {
    for (let i = 0; i < perStage[stage]; i++) {
      id += 1;
      const staleHours = Math.round(rand() * 140);
      deals.push({
        id,
        title: `${pick(COMPANIES)} — Amazon US Growth`,
        stage,
        value: Math.round(4000 + rand() * 22000),
        ownerId: OWNER.id,
        lastActivity: hoursAgo(staleHours),
        staleHours,
      });
    }
  }
  return deals;
}

export const dealSummary = () => {
  const deals = buildDeals();
  const byStage = PIPELINE_STAGES.map((stage) => {
    const inStage = deals.filter((d) => d.stage === stage);
    return { stage, count: inStage.length, value: inStage.reduce((s, d) => s + d.value, 0) };
  });
  const staleOpen = deals.filter((d) => !stage_is_closed(d.stage) && d.staleHours >= 48);
  return { deals, byStage, staleOpen };
};

function stage_is_closed(stage) {
  return stage === "Closed Won" || stage === "Closed Lost";
}

// ---- Automation log (Smartlead -> Pipedrive) --------------------------------
// Tag/status enums follow the spec table in section 5 of the dashboard brief.

const LEADS = [
  { name: "Ronald Goenawan", company: "Bukit Sari Organic Plantation" },
  { name: "Priya Shah", company: "Harborline Outdoor Co." },
  { name: "Marcus Webb", company: "Northfield Pet Supply" },
  { name: "Elena Cho", company: "Solace Home Goods" },
  { name: "Dominic Farrell", company: "Verdant Kitchenware" },
  { name: "Anika Patel", company: "Trueform Fitness" },
  { name: "Jules Bergmann", company: "Cascade Coffee Roasters" },
  { name: "Naledi Khumalo", company: "Milele Skincare" },
  { name: "Tom Radley", company: "Ridgeback Tools" },
  { name: "Sofia Marchetti", company: "Aurora Baby Co." },
];

const RULES = ["Auto-Triage", "Auto-Pause", "Unsubscribe"];
const TAGS = ["Interested", "Not Interested", "OutOfOffice", "Wrong Person"];

export function buildAutomationLog(count = 22) {
  const rows = [];
  // Guarantee the first few rows are Interested + Failed so the "Re-Run Failed
  // Automations" bulk-sync feature always has something to demonstrate on load,
  // rather than depending on the seeded RNG happening to land there.
  const minFailed = Math.min(3, count);
  for (let i = 0; i < count; i++) {
    const lead = pick(LEADS);
    const tag = i < minFailed ? "Interested" : pick(TAGS);
    const rule = tag === "Interested" ? "Auto-Triage" : pick(RULES);
    let pipedriveStatus;
    let note;
    let dealId = null;
    if (tag === "Interested") {
      const roll = i < minFailed ? 0.8 : rand();
      if (roll < 0.72) {
        pipedriveStatus = "Created Deal";
        dealId = 4200 + Math.floor(rand() * 400);
        note = `Deal #${dealId}`;
      } else if (roll < 0.88) {
        pipedriveStatus = "Failed";
        note = JSON.stringify({
          error: "PipedriveError",
          status: 400,
          body: { success: false, error: "person_id is read-only on activities; use participants[]" },
        });
      } else {
        pipedriveStatus = "Skipped";
        note = "Duplicate person — already synced 2026-08-19";
      }
    } else if (tag === "Wrong Person" || tag === "OutOfOffice") {
      pipedriveStatus = rand() < 0.5 ? "Skipped" : "Lost/Archived";
      note = tag === "OutOfOffice" ? "Ignore Reply — colleague contact listed" : "No qualifying contact found";
    } else {
      pipedriveStatus = "Lost/Archived";
      note = "Domain blocked (email + domain)";
    }
    rows.push({
      id: `auto_${i + 1}`,
      timestamp: hoursAgo(Math.round(rand() * 96)),
      leadName: lead.name,
      company: lead.company,
      smartleadTag: tag,
      ruleExecuted: rule,
      pipedriveStatus,
      note,
      dealId,
      campaignId: 100000 + Math.floor(rand() * 900),
      leadEmail: `${lead.name.toLowerCase().replace(/[^a-z]+/g, ".")}@${lead.company
        .toLowerCase()
        .replace(/[^a-z]+/g, "")}.com`,
    });
  }
  return rows.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
}

// ---- Tasks ------------------------------------------------------------------

const TASK_SEED = [
  { title: "Re-run failed Pipedrive syncs from Bukit Sari thread", category: "Pipedrive", priority: "High", status: "To Do", daysDue: 0 },
  { title: "Validate SPF/DKIM on acme-outbound.com", category: "Infrastructure", priority: "High", status: "To Do", daysDue: -1 },
  { title: "Warm asgrowth.co another 5 days before adding to rotation", category: "Smartlead", priority: "Medium", status: "In Progress", daysDue: 3 },
  { title: "Book discovery call — Harborline Outdoor Co.", category: "Pipedrive", priority: "High", status: "In Progress", daysDue: 1 },
  { title: "Fix 7 broken links flagged in crawl report", category: "SEO", priority: "Medium", status: "To Do", daysDue: 4 },
  { title: "Review HeyReach acceptance rate drop on LinkedIn campaign #3", category: "Heyreach", priority: "Medium", status: "To Do", daysDue: 2 },
  { title: "Weekly Master Inbox backlog scan", category: "Smartlead", priority: "High", status: "To Do", daysDue: 0 },
  { title: "Retire 3 dead inboxes and provision replacements", category: "Infrastructure", priority: "Low", status: "To Do", daysDue: 6 },
  { title: "Draft Q3 outbound sequence v2", category: "Smartlead", priority: "Low", status: "In Progress", daysDue: 8 },
  { title: "Confirm Calendly -> Pipedrive lead sync for Aurora Baby Co.", category: "Pipedrive", priority: "Medium", status: "Done", daysDue: -6, completedDaysAgo: 1 },
  { title: "Resolve crawl errors on /amazon-us landing page", category: "SEO", priority: "High", status: "Done", daysDue: -9, completedDaysAgo: 9 },
  { title: "Rotate warmup settings on 5 aging inboxes", category: "Infrastructure", priority: "Low", status: "Done", daysDue: -11, completedDaysAgo: 11 },
  { title: "Sync Verdant Kitchenware deal notes into activity log", category: "Pipedrive", priority: "Medium", status: "Done", daysDue: -3, completedDaysAgo: 3 },
];

// ---- Per-account technical SEO audit score --------------------------------
// Feeds the "SEO Audit & Diagnostic Score" widget inline on each deal card in
// the /pipeline workspace — deterministic per company name (not random per
// render) so the same deal shows the same score/issues across polls.

const AUDIT_ISSUES_POOL = [
  "Missing meta descriptions on 4 product pages",
  "Core Web Vitals: LCP above 2.5s on mobile",
  "3 broken outbound links in blog content",
  "No canonical tag on duplicate category pages",
  "Sitemap missing 12 recently added URLs",
  "robots.txt blocking a crawled asset directory",
  "Thin content on 2 collection pages (<300 words)",
  "Missing alt text on 9 product images",
];

function hashString(str) {
  let h = 0;
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i);
    h |= 0;
  }
  return Math.abs(h);
}

export function seoScoreFor(companyName) {
  const h = hashString(companyName || "");
  const score = 42 + (h % 57); // 42–98
  const band = score >= 85 ? "good" : score >= 65 ? "needs-improvement" : "poor";
  const issueCount = score >= 85 ? 1 : score >= 65 ? 2 : 3;
  const start = h % AUDIT_ISSUES_POOL.length;
  const issues = Array.from({ length: issueCount }, (_, i) => AUDIT_ISSUES_POOL[(start + i) % AUDIT_ISSUES_POOL.length]);
  return { score, band, issues };
}

export function buildTasks() {
  return TASK_SEED.map((t, i) => {
    const completedAt = t.status === "Done" ? daysAgo(t.completedDaysAgo ?? 2) : null;
    const isArchived = t.status === "Done" && (t.completedDaysAgo ?? 0) >= 7;
    return {
      id: `task_${i + 1}`,
      title: t.title,
      category: t.category,
      priority: t.priority,
      status: t.status,
      dueDate: new Date(Date.now() + t.daysDue * 86400000).toISOString().slice(0, 10),
      completedAt,
      isArchived,
      description: "",
    };
  });
}
