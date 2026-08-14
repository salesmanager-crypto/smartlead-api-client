/**
 * A drop-in stand-in for SmartleadClient, shaped like the real API's
 * responses, so the report pipeline can be exercised end-to-end (and the
 * dashboard demoed) without a live API key. Used via `--fixture` on
 * scripts/campaign-analytics-report.mjs.
 *
 * The synthetic data intentionally includes: one high-bounce campaign, one
 * low-open-rate campaign, one high-unsubscribe campaign, a couple of healthy
 * campaigns, leads who repeat-non-open, leads whose address bounces in more
 * than one campaign, leads who open repeatedly but never click/reply, and one
 * unhealthy sending inbox — so every flag category in the report has at
 * least one real example to show.
 */

const CAMPAIGNS = [
  { id: 1001, name: "Amazon US - Tea Importers Q3", status: "ACTIVE", created_at: "2026-07-02" },
  { id: 1002, name: "Amazon US - Specialty Foods Outreach", status: "ACTIVE", created_at: "2026-07-08" },
  { id: 1003, name: "Amazon US - Organic Snacks Follow-up", status: "ACTIVE", created_at: "2026-07-15" },
  { id: 1004, name: "Amazon US - Beverage Brands Cold", status: "ACTIVE", created_at: "2026-07-20" },
  { id: 1005, name: "Amazon US - Supplement Brands", status: "PAUSED", created_at: "2026-07-25" },
  { id: 1006, name: "Amazon US - Pet Food Distributors", status: "ACTIVE", created_at: "2026-08-05" },
  // out of scope for a --since=2026-07-01 run — proves the date filter works
  { id: 899, name: "Legacy Q2 Outreach", status: "COMPLETED", created_at: "2026-05-01" },
];

// campaignId -> summed analytics-by-date totals for the whole requested window
const ANALYTICS_TOTALS = {
  1001: { sent_count: 1450, open_count: 520, click_count: 95, reply_count: 38, bounce_count: 22, unsubscribed_count: 4 },
  1002: { sent_count: 980, open_count: 210, click_count: 30, reply_count: 9, bounce_count: 68, unsubscribed_count: 3 },
  1003: { sent_count: 610, open_count: 275, click_count: 61, reply_count: 25, bounce_count: 9, unsubscribed_count: 2 },
  1004: { sent_count: 1120, open_count: 95, click_count: 8, reply_count: 2, bounce_count: 31, unsubscribed_count: 6 },
  1005: { sent_count: 740, open_count: 190, click_count: 22, reply_count: 5, bounce_count: 15, unsubscribed_count: 11 },
  1006: { sent_count: 180, open_count: 61, click_count: 9, reply_count: 3, bounce_count: 2, unsubscribed_count: 0 },
};

const LEADS_BY_CAMPAIGN = {
  1001: [
    row("priya.patel@himalayanteaco.com", 3, 2, 1, 1),
    row("sarah.chen@brewhouseimports.com", 2, 0, 0, 0), // -> repeat non-opener (cross-campaign with 1003)
    row("mkline@tealeafwholesale.com", 4, 0, 0, 0), // -> repeat non-opener
    row("orders@goldenleaftea.com", 3, 1, 0, 0),
    row("purchasing@driftwoodbeverages.com", 3, 2, 0, 0), // -> engaged non-converter (cross-campaign with 1004)
    row("j.oconnor@coastalteahouse.com", 2, 1, 1, 0),
    row("hello@leafandbloomtea.com", 3, 0, 0, 0), // -> repeat non-opener
    row("buyer@spiceroutetea.com", 2, 1, 0, 0),
  ],
  1002: [
    row("info@snackdistro.co", 2, 0, 0, 0, true), // -> chronic bouncer (cross-campaign with 1004)
    row("orders@pantryfinefoods.com", 2, 0, 0, 0, true), // -> chronic bouncer
    row("contact@harvesttablefoods.com", 2, 0, 0, 0, true), // -> chronic bouncer
    row("buying@urbanpantryco.com", 3, 1, 0, 0),
    row("procurement@finemarketfoods.com", 2, 0, 0, 0), // below min-sends threshold, not flagged
    row("hello@artisanpantry.com", 3, 2, 1, 1),
    row("purchasing@gourmetgoodsco.com", 2, 1, 0, 0),
    row("team@freshfoodsdistribution.com", 2, 0, 0, 0, true), // -> chronic bouncer
  ],
  1003: [
    row("sarah.chen@brewhouseimports.com", 3, 0, 0, 0),
    row("buyer@puresnackco.com", 2, 2, 1, 1),
    row("orders@wholesomebitesco.com", 2, 1, 0, 0),
    row("procurement@naturesnackdistro.com", 3, 2, 1, 0),
    row("hello@crunchyharvestfoods.com", 2, 2, 0, 1),
    row("buying@greenfieldsnacks.com", 2, 1, 0, 0),
  ],
  1004: [
    row("purchasing@driftwoodbeverages.com", 2, 2, 0, 0),
    row("info@snackdistro.co", 2, 0, 0, 0, true),
    row("orders@springwaterco.com", 3, 0, 0, 0), // -> repeat non-opener
    row("buyer@craftsodaworks.com", 3, 0, 0, 0), // -> repeat non-opener
    row("procurement@coldbrewimports.com", 2, 0, 0, 0), // below threshold
    row("hello@nitrofusionbev.com", 3, 1, 0, 0),
    row("materials@bluepeakwholesale.com", 2, 2, 0, 0), // -> engaged non-converter (cross-campaign with 1006)
  ],
  1005: [
    row("buyer@peakvitalitysupps.com", 2, 1, 0, 0),
    row("orders@puresourcenutra.com", 2, 1, 1, 1),
    row("procurement@ironwillsupplements.com", 3, 0, 0, 0), // -> repeat non-opener
    row("hello@vitalrootsnutrition.com", 2, 1, 0, 0),
    row("buying@summitsportnutrition.com", 3, 0, 0, 0), // -> repeat non-opener
  ],
  1006: [
    row("buyer@wildtrailpetfood.com", 2, 1, 1, 1),
    row("orders@happytailpetsupply.com", 2, 1, 0, 0),
    row("procurement@naturalpawsdistro.com", 2, 0, 0, 0), // below threshold
    row("hello@pettreatpantry.com", 1, 1, 0, 0),
    row("materials@bluepeakwholesale.com", 2, 2, 0, 0),
  ],
};

const INBOX_HEALTH = [
  {
    account: { id: 1, from_email: "yoni@albertscottco.com", is_smtp_success: true, is_imap_success: true, warmup_details: { status: "ACTIVE", total_spam_count: 1 } },
    warmupStats: { stats_by_date: [{ date: "2026-08-10", save_from_spam_count: 0 }] },
  },
  {
    account: { id: 2, from_email: "sales@albertscottllc.com", is_smtp_success: true, is_imap_success: true, warmup_details: { status: "PAUSED", total_spam_count: 6 } },
    warmupStats: { stats_by_date: [{ date: "2026-08-10", save_from_spam_count: 2 }, { date: "2026-08-11", save_from_spam_count: 3 }] },
  },
  {
    account: { id: 3, from_email: "outreach@albertscottny.com", is_smtp_success: false, is_imap_success: true, warmup_details: { status: "ACTIVE", total_spam_count: 0 } },
    warmupStats: { stats_by_date: [] },
  },
  {
    account: { id: 4, from_email: "hello@albertscottco.com", is_smtp_success: true, is_imap_success: true, warmup_details: { status: "ACTIVE", total_spam_count: 0 } },
    warmupStats: { stats_by_date: [{ date: "2026-08-10", save_from_spam_count: 0 }] },
  },
];

function row(email, sent, opened, clicked, replied, bounced = false) {
  return { lead_email: email, sent_count: sent, open_count: opened, click_count: clicked, reply_count: replied, is_bounced: bounced };
}

export function createFixtureClient() {
  const servedAnalytics = new Set();
  return {
    async listCampaigns() {
      return CAMPAIGNS;
    },
    async getCampaignAnalyticsByDate(campaignId, _range) {
      // Return the campaign's full totals exactly once (on the first date
      // chunk requested) and zeros after, so summing across chunks doesn't
      // double-count — mirrors "all the activity happened somewhere in this
      // window," which is all the fixture needs to demonstrate.
      if (servedAnalytics.has(campaignId)) {
        return { sent_count: 0, open_count: 0, click_count: 0, reply_count: 0, bounce_count: 0, unsubscribed_count: 0 };
      }
      servedAnalytics.add(campaignId);
      return ANALYTICS_TOTALS[campaignId] ?? { sent_count: 0, open_count: 0, click_count: 0, reply_count: 0, bounce_count: 0, unsubscribed_count: 0 };
    },
    async getCampaignStatistics(campaignId, { offset = 0 } = {}) {
      if (offset > 0) return [];
      return LEADS_BY_CAMPAIGN[campaignId] ?? [];
    },
    async getAllCampaignStatistics(campaignId) {
      return LEADS_BY_CAMPAIGN[campaignId] ?? [];
    },
    async getAllInboxHealth() {
      return INBOX_HEALTH;
    },
  };
}
