/**
 * Pure computation core for the campaign analytics report.
 *
 * No network calls live here — everything takes already-fetched Smartlead API
 * payloads (or fixtures shaped like them) and returns numbers/flags. That
 * keeps it testable without an API key and reusable from both the live CLI
 * script and the fixture-based dry run.
 *
 * Field-name mapping below was confirmed against this account's real
 * Smartlead responses on 2026-08-14 (`getCampaign`, `getCampaignAnalyticsByDate`,
 * `getCampaignStatistics`) — every metric read still goes through `pick()`
 * against a candidate list so a future API change degrades gracefully instead
 * of silently reading `undefined`, but these are confirmed, not guesses.
 *
 * IMPORTANT — per-lead statistics rows are one row per *sequence-step send*,
 * not one row per lead: a lead who received 3 follow-ups shows up as 3 rows
 * with the same `lead_email`. There is no per-row send *count* field, so each
 * row counts as exactly one send (see the `|| 1` fallback below). Also,
 * per-row `reply_count`/`email_reply_count` fields don't exist on real rows —
 * the only reply signal is a non-null `reply_time` — so replied-ness is
 * derived from that, not from `LEAD_STAT_FIELDS.replied` alone.
 *
 * IMPORTANT — open/click tracking can be disabled per campaign
 * (`track_settings` containing `"DONT_EMAIL_OPEN"` / `"DONT_LINK_CLICK"`).
 * When disabled, `open_count`/`click_count` are always 0 — that is a tracking
 * setting, not an engagement signal, and must not be treated as "nobody
 * opened." See `getTrackingFlags()` — every open/click-rate computation and
 * flag in this module is gated on it.
 */

// ---- field-name candidates ------------------------------------------------

export const CAMPAIGN_META_FIELDS = {
  id: ["id", "campaign_id"],
  name: ["name", "campaign_name"],
  status: ["status"],
  createdAt: ["created_at", "createdAt", "created", "campaign_created_at"],
  trackSettings: ["track_settings"],
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
  replyTime: ["reply_time"],
  bounced: ["is_bounced", "bounced", "bounce_count"],
};

/** Does this campaign have open and/or click tracking turned off? */
export function getTrackingFlags(campaignRaw) {
  const raw = pick(campaignRaw, CAMPAIGN_META_FIELDS.trackSettings);
  const list = Array.isArray(raw) ? raw : [];
  return {
    openDisabled: list.includes("DONT_EMAIL_OPEN"),
    clickDisabled: list.includes("DONT_LINK_CLICK"),
  };
}

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

/** Turn summed raw totals into rates. openRate/clickRate are `null` (not 0) when tracking is disabled. */
export function computeCampaignMetrics(totals, trackingFlags = {}) {
  const { sent, opened, clicked, replied, bounced, unsubscribed } = totals;
  return {
    ...totals,
    openRate: trackingFlags.openDisabled ? null : rate(opened, sent),
    clickRate: trackingFlags.clickDisabled ? null : rate(clicked, sent),
    replyRate: rate(replied, sent),
    bounceRate: rate(bounced, sent),
    unsubRate: rate(unsubscribed, sent),
    openTrackingDisabled: !!trackingFlags.openDisabled,
    clickTrackingDisabled: !!trackingFlags.clickDisabled,
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
  if (metrics.openRate === null) {
    flags.push({ level: "info", code: "open-tracking-disabled", message: "Open tracking is disabled for this campaign — open rate/non-opener signals aren't available." });
  } else if (metrics.openRate <= thresholds.openRateCritical) {
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
 * @param {Array<{campaignId, campaignName, leads: object[], openTrackingEnabled?: boolean}>} perCampaignLeads
 *   `leads` is the raw array from getAllCampaignStatistics for that campaign.
 *   `openTrackingEnabled` (default true) marks whether that campaign's opens
 *   are real signal — sends from tracking-disabled campaigns still count
 *   toward `sent` but not toward `trackedSent`, so they can't manufacture a
 *   false "never opens" flag on a lead we simply never measured.
 */
export function aggregateLeadStats(perCampaignLeads) {
  const byEmail = new Map();
  for (const { campaignId, campaignName, leads, openTrackingEnabled = true } of perCampaignLeads) {
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
          trackedSent: 0,
          opened: 0,
          clicked: 0,
          replied: 0,
          bouncedCount: 0,
        });
      }
      const entry = byEmail.get(key);
      entry.campaignIds.add(campaignId);
      entry.campaignNames.add(campaignName);
      const sentIncrement = numField(raw, LEAD_STAT_FIELDS.sent) || 1; // fall back to "1 send" — real rows are one-per-sequence-step, no count field
      entry.sent += sentIncrement;
      if (openTrackingEnabled) entry.trackedSent += sentIncrement;
      entry.opened += numField(raw, LEAD_STAT_FIELDS.opened);
      entry.clicked += numField(raw, LEAD_STAT_FIELDS.clicked);
      // real rows have no reply_count field — a reply shows up only as a non-null reply_time
      const repliedFromCount = numField(raw, LEAD_STAT_FIELDS.replied);
      const repliedFromTimestamp = pick(raw, LEAD_STAT_FIELDS.replyTime) ? 1 : 0;
      entry.replied += Math.max(repliedFromCount, repliedFromTimestamp);
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
    // gated on trackedSent, not sent — a lead only ever emailed via tracking-disabled
    // campaigns has trackedSent 0 and can never trip this flag on a false "zero opens"
    if (entry.trackedSent >= thresholds.minSendsForNonOpenerFlag && entry.opened === 0) {
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
    const tracking = getTrackingFlags(c);
    const metrics = computeCampaignMetrics(totals, tracking);
    return {
      id,
      name: pick(c, CAMPAIGN_META_FIELDS.name),
      status: pick(c, CAMPAIGN_META_FIELDS.status),
      createdAt: pick(c, CAMPAIGN_META_FIELDS.createdAt),
      metrics,
      flags: flagCampaign(metrics, thresholds),
    };
  });

  // openRate/clickRate use only the sent volume from campaigns where that
  // tracking is actually on — otherwise tracking-disabled campaigns' sends
  // dilute the denominator and understate the real open/click rate.
  const globalTotals = { sent: 0, opened: 0, clicked: 0, replied: 0, bounced: 0, unsubscribed: 0 };
  let trackedSentForOpen = 0;
  let trackedSentForClick = 0;
  let campaignsWithOpenTrackingOff = 0;
  let campaignsWithClickTrackingOff = 0;
  for (const c of campaignReports) {
    const m = c.metrics;
    for (const key of ["sent", "opened", "clicked", "replied", "bounced", "unsubscribed"]) globalTotals[key] += m[key];
    if (m.openTrackingDisabled) campaignsWithOpenTrackingOff += 1;
    else trackedSentForOpen += m.sent;
    if (m.clickTrackingDisabled) campaignsWithClickTrackingOff += 1;
    else trackedSentForClick += m.sent;
  }
  const globalMetrics = {
    ...globalTotals,
    openRate: rate(globalTotals.opened, trackedSentForOpen),
    clickRate: rate(globalTotals.clicked, trackedSentForClick),
    replyRate: rate(globalTotals.replied, globalTotals.sent),
    bounceRate: rate(globalTotals.bounced, globalTotals.sent),
    unsubRate: rate(globalTotals.unsubscribed, globalTotals.sent),
    campaignsWithOpenTrackingOff,
    campaignsWithClickTrackingOff,
  };

  const leadsByCampaignWithTracking = leadsByCampaign.map((entry) => {
    const campaign = campaigns.find((c) => pick(c, CAMPAIGN_META_FIELDS.id) === entry.campaignId);
    return { ...entry, openTrackingEnabled: campaign ? !getTrackingFlags(campaign).openDisabled : true };
  });
  const leadMap = aggregateLeadStats(leadsByCampaignWithTracking);
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
