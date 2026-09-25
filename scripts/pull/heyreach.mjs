#!/usr/bin/env node
/**
 * HeyReach -> heyreach.json (plain: campaign-level counts only). Needs HEYREACH_API_KEY
 * (the workspace key; the organization key cannot read campaigns).
 *
 *   node scripts/pull/heyreach.mjs
 *
 * Every campaign with its LinkedIn funnel counts. `linkedin` is the primary
 * campaign (the first one that is not a draft), in the artifact's LINKEDIN shape.
 * Lead-level statuses are counted here and never written out.
 */
import { HeyReachClient } from "../../src/heyreach.js";
import { numOrNull } from "./lib.mjs";
import { runStandalone, isMain } from "./write.mjs";

const PAGE = 100;
const MAX_LEADS = 20000; // safety stop for one campaign

const statusLabel = (s) => {
  const t = String(s || "").replace(/_/g, " ").toLowerCase();
  return t ? t.charAt(0).toUpperCase() + t.slice(1) : null;
};
const countBy = (arr, key, val) => arr.filter((l) => l[key] === val).length;

async function allLeads(hr, campaignId) {
  const out = [];
  for (let offset = 0; offset < MAX_LEADS; offset += PAGE) {
    const page = await hr.getLeadsFromCampaign({ campaignId, offset, limit: PAGE });
    const arr = page?.items || [];
    out.push(...arr);
    if (arr.length < PAGE || out.length >= (page?.totalCount ?? Infinity)) break;
  }
  return out;
}

function shape(detail, leads) {
  const p = detail.progressStats || {};
  const worked = leads != null;
  return {
    id: detail.id,
    campaignName: detail.name ?? null,
    status: statusLabel(detail.status),
    started: String(detail.startedAt || detail.creationTime || "").slice(0, 10) || null,
    listName: detail.linkedInUserListName ?? null,
    senders: (detail.campaignAccountIds || []).length,
    leads: numOrNull(p.totalUsers),
    processed: worked ? leads.length : null,
    pending: numOrNull(p.totalUsersPending),
    connectionsSent: worked ? leads.filter((l) => l.leadConnectionStatus && l.leadConnectionStatus !== "None").length : null,
    accepted: worked ? countBy(leads, "leadConnectionStatus", "ConnectionAccepted") : null,
    connNone: worked ? countBy(leads, "leadConnectionStatus", "None") : null,
    messagesSent: worked ? leads.filter((l) => l.leadMessageStatus && l.leadMessageStatus !== "None").length : null,
    replies: worked ? countBy(leads, "leadMessageStatus", "MessageReply") : null,
    inSequence: worked ? countBy(leads, "leadCampaignStatus", "InSequence") : null,
    pendingInBatch: worked ? countBy(leads, "leadCampaignStatus", "Pending") : null,
    failed: numOrNull(p.totalUsersFailed),
    finished: numOrNull(p.totalUsersFinished),
  };
}

export async function pull(env, ctx = {}) {
  const hr = new HeyReachClient({ apiKey: env.HEYREACH_API_KEY, orgApiKey: env.HEYREACH_ORG_API_KEY });
  const campaigns = [];
  for (let offset = 0; ; offset += PAGE) {
    const page = await hr.listCampaigns({ offset, limit: PAGE });
    const arr = page?.items || [];
    campaigns.push(...arr);
    if (arr.length < PAGE || campaigns.length >= (page?.totalCount ?? Infinity)) break;
  }

  // drafts have no leads worked yet, so their lead-derived counts stay null
  const rows = [];
  for (const c of campaigns) {
    const detail = await hr.getCampaign(c.id);
    const leads = c.status === "DRAFT" ? null : await allLeads(hr, c.id);
    rows.push(shape(detail, leads));
  }

  const primary = rows.find((r, i) => campaigns[i].status !== "DRAFT") || rows[0] || null;
  ctx.records = rows.length;
  const { id: _id, ...primaryFields } = primary || {};
  return {
    pulledAt: new Date().toISOString(),
    primaryCampaignId: primary ? primary.id : null,
    linkedin: primary ? { campaigns: rows.length, ...primaryFields } : null,
    campaigns: rows,
  };
}

if (isMain(import.meta.url)) await runStandalone("heyreach", pull);
