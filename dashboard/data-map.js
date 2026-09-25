/**
 * The one mapping from docs/data/*.json to the constants the dashboard code reads.
 *
 * Used twice, so the two dashboards cannot drift:
 *  - GitHub Pages: scripts/build-pages.mjs inlines this function into the page, which
 *    fetches the data files after sign-in and calls it;
 *  - Claude artifact: scripts/build-artifact.mjs imports it in Node and writes each
 *    constant into the artifact's DATA BLOCK.
 *
 * Plain ES5-style function, no imports, no DOM: it must run unchanged in both places.
 * Every input may be null (a source that has never succeeded); every constant then
 * gets an empty value of the right shape, and the source's status pill explains why.
 *
 * `files` = { manifest, smartlead, pipedrive, heyreach, semrush, seoIssues, seoGeo,
 *             smartscout, tradeshows, tradeshowNotes, resources }
 */
function mapDashboardData(files) {
  var f = files || {};
  var man = f.manifest || { generatedAt: null, today: null, sources: {} };
  var sl = f.smartlead || {};
  var pd = f.pipedrive || {};
  var hr = f.heyreach || {};
  var sem = f.semrush || {};
  var iss = f.seoIssues || {};
  var geo = f.seoGeo || {};
  var ss = f.smartscout || { pulledAt: null, watchlist: [], brands: [] };
  var res = f.resources || {};
  var shows = Array.isArray(f.tradeshows) ? f.tradeshows : (f.tradeshows && f.tradeshows.shows) || [];
  var notes = f.tradeshowNotes || { updatedAt: null, people: [], notes: {} };

  function fmtDate(iso, withYear) {
    if (!iso) return null;
    var d = new Date(String(iso).slice(0, 10) + "T12:00:00Z");
    if (isNaN(d)) return null;
    var o = { month: "short", day: "numeric", timeZone: "UTC" };
    if (withYear !== false) o.year = "numeric";
    return d.toLocaleDateString("en-US", o);
  }
  function arr(v) { return Array.isArray(v) ? v : []; }

  var today = man.today || sl.today || pd.today || new Date().toISOString().slice(0, 10);
  var emptyLinkedIn = { campaigns: 0, campaignName: "", status: "", started: "", listName: "", senders: 0, leads: 0, processed: 0,
    pending: 0, connectionsSent: 0, accepted: 0, connNone: 0, messagesSent: 0, replies: 0, inSequence: 0, pendingInBatch: 0, failed: 0, finished: 0 };
  var li = hr.linkedin || emptyLinkedIn;
  var linkedin = {};
  for (var k in emptyLinkedIn) linkedin[k] = li[k] == null ? emptyLinkedIn[k] : li[k];

  return {
    DATA_DATE: fmtDate(today) || "Not pulled",
    TODAY: today,
    OVERDUE: arr(pd.overdue),
    DUE_TODAY: arr(pd.dueToday),
    UPCOMING: arr(pd.upcoming),
    CAMPAIGNS: arr(sl.campaigns),
    DEALS: arr(pd.deals),
    INBOX_LOG: arr(sl.inboxLog),
    YESTERDAY: sl.yesterday || { label: "", date: "", sent: 0, sendingCampaigns: 0, replies: 0, interested: 0, replyMix: [] },
    LINKEDIN: linkedin,
    LINKEDIN_CAMPAIGNS: arr(hr.campaigns),
    PD_META: pd.meta || { openTotal: 0, openTypeCounts: {}, leadsByOwner: {}, leadsTotal: 0, leadsUnseen: 0, personsTotal: 0, orgsTotal: 0 },
    INBOXES: sl.inboxes || { total: 0, domains: 0 },
    REP_NAME: pd.repNames || {},
    SYNC_CATEGORIES: arr(sl.syncCategories).length ? sl.syncCategories : ["Interested", "Meeting Request", "Follow Up"],
    SEO_PULLED: fmtDate(sem.pulledAt) || "Not pulled",
    SEO_BASELINE: fmtDate(sem.baselineAt || geo.baselineAt) || "",
    SEO_SOURCE: sem.source || null,
    SEO_KEYWORDS: arr(sem.keywords),
    SEO_GEO: arr(geo.sources),
    SEO_GEO_SOURCES: arr(geo.sources),
    SEO_HEALTH: arr(sem.health && sem.health.items),
    SEO_ISSUES: arr(iss.issues),
    SEO_SOURCE_UPDATED: fmtDate(iss.sourceUpdated) || "",
    TOOL_CHECKED: res.checkedAt || "",
    PLATFORM_TOOLS: arr(res.platformTools),
    VENDORS: arr(res.vendors),
    DOMAIN_WAVES: arr(res.domainWaves),
    OTHER_TOOLS: arr(res.otherTools),
    META_ADS: res.metaAds || { charges: 0, total: 0, from: "", to: "", since: "" },
    SMARTSCOUT: { pulledAt: ss.pulledAt || null, watchlist: arr(ss.watchlist), brands: arr(ss.brands) },
    TRADESHOWS: shows,
    TRADESHOW_NOTES: { updatedAt: notes.updatedAt || null, people: arr(notes.people).length ? notes.people : ["Yoni", "Maria", "Rachel"], notes: notes.notes || {} },
    MANIFEST: man
  };
}

/** Names of every constant mapDashboardData returns, in DATA BLOCK order. */
var DASHBOARD_CONSTANTS = Object.keys(mapDashboardData({}));

if (typeof module !== "undefined") module.exports = { mapDashboardData: mapDashboardData, DASHBOARD_CONSTANTS: DASHBOARD_CONSTANTS };
