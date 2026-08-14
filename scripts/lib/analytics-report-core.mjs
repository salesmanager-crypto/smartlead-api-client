/**
 * Pure computation core for the campaign analytics report.
 *
 * No network calls live here — everything takes already-fetched Smartlead API
 * payloads (or fixtures shaped like them) and returns numbers/flags. That
 * keeps it testable without an API key and reusable from both the live CLI
 * script and the fixture-based dry run.
 *
 * ADAPT_ME: field-name mapping. This project's own docs (README/client.js)
 * describe the *shape* of Smartlead's analytics/statistics responses but not
 * the exact key names for every field, and we don't have a live API key in
 * this environment to confirm them against a real response. Every place this
 * module reads a metric off a raw API object goes through `pick()` against a
 * list of candidate key names below — if a real run's numbers look off
 * (e.g. always zero), the fix is almost certainly "add the real key name to
 * the matching list here," not a rewrite.
 */

// ---- field-name candidates (see ADAPT_ME above) ---------------------------

export const CAMPAIGN_META_FIELDS = {
  id: ["id", "campaign_id"],
  name: ["name", "campaign_name"],
  status: ["status"],
  createdAt: ["created_at", "createdAt", "created", "campaign_created_at"],
};

export const CAMPAIGN_ANALYTICS_FIELDS = {
  sent: ["sent_count", "sentCount", "total_sent", "emails_sent", "sent"],
  opened: ["open_count", "openCount", "unique_open_count", "opens", "opened"],
  clicked: ["click_count", "clickCount", "unique_click_count", "clicks", "clicked"],
  replied: ["reply_count", "replyCount", "replied_count", "replies", "replied"],
  bounced: ["bounce_count", "bounceCount", "bounced_count", "bounces", "hard_bounce_count"],
  unsubscribed: ["unsubscribed_count", "unsubscribeCount", "unsubscribe_count", "opt_out_count"],
};

export const LEAD_STAT_FIELDS = {
  email: ["lead_email", "email", "to_email"],
  name: ["lead_name", "first_name", "name"],
  sent: ["sent_count", "email_sent_count", "total_sent", "emails_sent_count"],
  opened: ["open_count", "email_open_count", "opens"],
  clicked: ["click_count", "email_click_count", "clicks"],
  replied: ["reply_count", "email_reply_count", "replies"],
  bounced: ["is_bounced", "bounced", "bounce_count"],
};

// ---- sensible-default thresholds (all tunable via CLI flags) --------------

export const DEFAULT_THRESHOLDS = {
  // cold-email bounce rate should stay well under 5% or sender reputation/deliverability suffers
  bounceRateWarning: 0.03,
  bounceRateCritical: 0.05,
  // cold outreach open rates below ~20% usually signal a subject-line, deliverability, or targeting problem
  openRateWarning: 0.2,
  openRateCritical: 0.1,
  // unsubscribes above ~0.5-1% are a targeting/messaging signal, not just noise
  unsubRateWarning: 0.005,
  unsubRateCritical: 0.01,
  // a lead sent this many emails with zero opens is a targeting miss (bad persona/list/deliverability to that domain)
  minSendsForNonOpenerFlag: 3,
  // opens repeatedly but never clicks/replies across multiple campaigns = interested-looking but not converting
  minOpensForEngagedNonConverter: 3,
  minCampaignsForEngagedNonConverter: 2,
};

// ---- small helpers ---------------------------------------------------------

export function pick(obj, keys) {
  if (!obj) return undefined;
  for (const k of keys) {
    if (obj[k] !== undefined && obj[k] !== null) return obj[k];
  }
  return undefined;
}

export function toNumber(v) {
  if (typeof v === "boolean") return v ? 1 : 0;
  if (v === undefined || v === null || v === "") return 0;
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function numField(obj, keys) {
  return toNumber(pick(obj, keys));
}

export function rate(numerator, denominator) {
  if (!denominator) return 0;
  return numerator / denominator;
}

// ---- date range chunking (Smartlead's analytics-by-date caps at ~30 days) --

/** Split [startDate, endDate] (YYYY-MM-DD) into consecutive <=maxDays windows. */
export function chunkDateRange(startDate, endDate, maxDays = 30) {
  const chunks = [];
  let cursor = new Date(`${startDate}T00:00:00Z`);
  const end = new Date(`${endDate}T00:00:00Z`);
  while (cursor <= end) {
    const chunkEnd = new Date(cursor);
    chunkEnd.setUTCDate(chunkEnd.getUTCDate() + maxDays - 1);
    const boundedEnd = chunkEnd > end ? end : chunkEnd;
    chunks.push({ start: isoDate(cursor), end: isoDate(boundedEnd) });
    cursor = new Date(boundedEnd);
    cursor.setUTCDate(cursor.getUTCDate() + 1);
  }
  return chunks;
}

function isoDate(d) {
  return d.toISOString().slice(0, 10);
}

// ---- per-campaign metrics ---------------------------------------------------

/** Sum a list of raw analytics-by-date responses (one per date chunk) into one totals object. */
export function sumAnalytics(rawResponses) {
  const totals = { sent: 0, opened: 0, clicked: 0, replied: 0, bounced: 0, unsubscribed: 0 };
  for (const raw of rawResponses) {
    if (!raw) continue;
    for (const key of Object.keys(totals)) {
      totals[key] += numField(raw, CAMPAIGN_ANALYTICS_FIELDS[key]);
    }
  }
  return totals;
}

/** Turn summed raw totals into rates. */
export function computeCampaignMetrics(totals) {
  const { sent, opened, clicked, replied, bounced, unsubscribed } = totals;
  return {
    ...totals,
    openRate: rate(opened, sent),
    clickRate: rate(clicked, sent),
    replyRate: rate(replied, sent),
    bounceRate: rate(bounced, sent),
    unsubRate: rate(unsubscribed, sent),
  };
}

export function flagCampaign(metrics, thresholds = DEFAULT_THRESHOLDS) {
  const flags = [];
  if (metrics.sent === 0) {
    flags.push({ level: "warning", code: "no-sends", message: "No emails sent in this window — check schedule/status." });
    return flags;
  }
  if (metrics.bounceRate >= thresholds.bounceRateCritical) {
    flags.push({ level: "critical", code: "high-bounce-rate", message: `Bounce rate ${pct(metrics.bounceRate)} — list quality/deliverability risk.` });
  } else if (metrics.bounceRate >= thresholds.bounceRateWarning) {
    flags.push({ level: "warning", code: "high-bounce-rate", message: `Bounce rate ${pct(metrics.bounceRate)} — above the healthy threshold.` });
  }
  if (metrics.openRate <= thresholds.openRateCritical) {
    flags.push({ level: "critical", code: "low-open-rate", message: `Open rate ${pct(metrics.openRate)} — likely deliverability or subject-line/targeting problem.` });
  } else if (metrics.openRate <= thresholds.openRateWarning) {
    flags.push({ level: "warning", code: "low-open-rate", message: `Open rate ${pct(metrics.openRate)} — below the healthy range.` });
  }
  if (metrics.unsubRate >= thresholds.unsubRateCritical) {
    flags.push({ level: "critical", code: "high-unsub-rate", message: `Unsubscribe rate ${pct(metrics.unsubRate)} — messaging/targeting mismatch.` });
  } else if (metrics.unsubRate >= thresholds.unsubRateWarning) {
    flags.push({ level: "warning", code: "high-unsub-rate", message: `Unsubscribe rate ${pct(metrics.unsubRate)} — worth reviewing targeting/copy.` });
  }
  return flags;
}

function pct(n) {
  return `${(n * 100).toFixed(1)}%`;
}

// ---- cross-campaign, per-lead aggregation ----------------------------------

/**
 * @param {Array<{campaignId, campaignName, leads: object[]}>} perCampaignLeads
 *   `leads` is the raw array from getAllCampaignStatistics for that campaign.
 */
export function aggregateLeadStats(perCampaignLeads) {
  const byEmail = new Map();
  for (const { campaignId, campaignName, leads } of perCampaignLeads) {
    for (const raw of leads) {
      const email = pick(raw, LEAD_STAT_FIELDS.email);
      if (!email) continue;
      const key = String(email).toLowerCase();
      if (!byEmail.has(key)) {
        byEmail.set(key, {
          email,
          name: pick(raw, LEAD_STAT_FIELDS.name) ?? "",
          campaignIds: new Set(),
          campaignNames: new Set(),
          sent: 0,
          opened: 0,
          clicked: 0,
          replied: 0,
          bouncedCount: 0,
        });
      }
      const entry = byEmail.get(key);
      entry.campaignIds.add(campaignId);
      entry.campaignNames.add(campaignName);
      entry.sent += numField(raw, LEAD_STAT_FIELDS.sent) || 1; // fall back to "1 send" if the API only gives a per-row record
      entry.opened += numField(raw, LEAD_STAT_FIELDS.opened);
      entry.clicked += numField(raw, LEAD_STAT_FIELDS.clicked);
      entry.replied += numField(raw, LEAD_STAT_FIELDS.replied);
      const bouncedVal = pick(raw, LEAD_STAT_FIELDS.bounced);
      entry.bouncedCount += typeof bouncedVal === "boolean" ? (bouncedVal ? 1 : 0) : toNumber(bouncedVal);
    }
  }
  return byEmail;
}

export function flagLeads(byEmail, thresholds = DEFAULT_THRESHOLDS) {
  const repeatNonOpeners = [];
  const chronicBouncers = [];
  const engagedNonConverters = [];

  for (const entry of byEmail.values()) {
    const summary = {
      email: entry.email,
      name: entry.name,
      campaigns: [...entry.campaignNames],
      sent: entry.sent,
      opened: entry.opened,
      clicked: entry.clicked,
      replied: entry.replied,
      bounced: entry.bouncedCount,
    };
    if (entry.bouncedCount >= 1) {
      chronicBouncers.push(summary);
      continue; // a bounced address shouldn't also show up as a "non-opener" — it's undeliverable, not disengaged
    }
    if (entry.sent >= thresholds.minSendsForNonOpenerFlag && entry.opened === 0) {
      repeatNonOpeners.push(summary);
    }
    if (
      entry.opened >= thresholds.minOpensForEngagedNonConverter &&
      entry.clicked === 0 &&
      entry.replied === 0 &&
      entry.campaignIds.size >= thresholds.minCampaignsForEngagedNonConverter
    ) {
      engagedNonConverters.push(summary);
    }
  }

  repeatNonOpeners.sort((a, b) => b.sent - a.sent);
  chronicBouncers.sort((a, b) => b.bounced - a.bounced);
  engagedNonConverters.sort((a, b) => b.opened - a.opened);

  return { repeatNonOpeners, chronicBouncers, engagedNonConverters };
}

// ---- top-level report assembly ---------------------------------------------

/**
 * @param {object} opts
 * @param {Array} opts.campaigns - raw campaign objects already filtered to the in-scope set
 * @param {Map<string|number, object>} opts.analyticsByCampaign - campaignId -> summed totals (from sumAnalytics)
 * @param {Array<{campaignId, campaignName, leads}>} opts.leadsByCampaign
 * @param {object} [opts.thresholds]
 * @param {Array} [opts.inboxHealth] - result of client.getAllInboxHealth()
 * @param {{since:string, start:string, end:string}} opts.range
 */
export function buildReport({ campaigns, analyticsByCampaign, leadsByCampaign, thresholds = DEFAULT_THRESHOLDS, inboxHealth = [], range }) {
  const campaignReports = campaigns.map((c) => {
    const id = pick(c, CAMPAIGN_META_FIELDS.id);
    const totals = analyticsByCampaign.get(id) ?? { sent: 0, opened: 0, clicked: 0, replied: 0, bounced: 0, unsubscribed: 0 };
    const metrics = computeCampaignMetrics(totals);
    return {
      id,
      name: pick(c, CAMPAIGN_META_FIELDS.name),
      status: pick(c, CAMPAIGN_META_FIELDS.status),
      createdAt: pick(c, CAMPAIGN_META_FIELDS.createdAt),
      metrics,
      flags: flagCampaign(metrics, thresholds),
    };
  });

  const globalTotals = campaignReports.reduce(
    (acc, c) => {
      for (const key of ["sent", "opened", "clicked", "replied", "bounced", "unsubscribed"]) acc[key] += c.metrics[key];
      return acc;
    },
    { sent: 0, opened: 0, clicked: 0, replied: 0, bounced: 0, unsubscribed: 0 }
  );
  const globalMetrics = computeCampaignMetrics(globalTotals);

  const leadMap = aggregateLeadStats(leadsByCampaign);
  const leadFlags = flagLeads(leadMap, thresholds);

  const inboxFlags = flagInboxHealth(inboxHealth);

  return {
    generatedAt: undefined, // stamped by the CLI after this returns — keeps this function pure/deterministic for testing
    range,
    thresholds,
    global: globalMetrics,
    campaigns: campaignReports.sort((a, b) => b.metrics.bounceRate - a.metrics.bounceRate),
    leadFlags,
    leadCount: leadMap.size,
    inboxHealth: inboxFlags,
  };
}

export function flagInboxHealth(inboxHealth) {
  const flags = [];
  for (const entry of inboxHealth) {
    const acct = entry.account ?? {};
    const email = acct.from_email ?? acct.email ?? String(acct.id ?? "unknown");
    if (acct.is_smtp_success === false || acct.is_imap_success === false) {
      flags.push({ level: "critical", email, message: "SMTP/IMAP connection failure — this inbox may not be sending/receiving at all." });
    }
    const warmupStatus = acct.warmup_details?.status;
    if (warmupStatus && warmupStatus !== "ACTIVE") {
      flags.push({ level: "warning", email, message: `Warmup status is "${warmupStatus}", not ACTIVE.` });
    }
    const stats = entry.warmupStats;
    const spamSaves = Array.isArray(stats?.stats_by_date)
      ? stats.stats_by_date.reduce((s, d) => s + toNumber(d.save_from_spam_count), 0)
      : 0;
    if (spamSaves > 0) {
      flags.push({ level: spamSaves > 3 ? "critical" : "warning", email, message: `${spamSaves} spam-folder save(s) in the trailing week — deliverability risk.` });
    }
  }
  return flags;
}
