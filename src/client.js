/**
 * Minimal, dependency-free client for the Smartlead.ai REST API.
 *
 * Docs: https://api.smartlead.ai/reference
 *       https://helpcenter.smartlead.ai/en/articles/125-full-api-documentation
 *
 * Auth: every request carries `api_key` as a query parameter.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const DEFAULT_BASE_URL = "https://server.smartlead.ai/api/v1";

export class SmartleadError extends Error {
  constructor(message, { status, body, url, method } = {}) {
    super(message);
    this.name = "SmartleadError";
    this.status = status;
    this.body = body;
    this.url = url;
    this.method = method;
  }
}

export class SmartleadClient {
  /**
   * @param {object} opts
   * @param {string} [opts.apiKey] - defaults to process.env.SMARTLEAD_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.SMARTLEAD_BASE_URL or the public API
   * @param {number} [opts.maxRetries] - retries on 429 with exponential backoff (default 3)
   */
  constructor({ apiKey, baseUrl, maxRetries = 3 } = {}) {
    this.apiKey = apiKey || process.env.SMARTLEAD_API_KEY;
    this.baseUrl = (baseUrl || process.env.SMARTLEAD_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.maxRetries = maxRetries;

    if (!this.apiKey) {
      throw new Error(
        "Missing Smartlead API key. Set SMARTLEAD_API_KEY in your environment/.env, " +
          "or pass { apiKey } to `new SmartleadClient()`."
      );
    }
  }

  // ---- low-level request helper ------------------------------------------

  async _request(method, path, { query = {}, body } = {}) {
    const url = new URL(this.baseUrl + path);
    url.searchParams.set("api_key", this.apiKey);
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, v);
    }

    let attempt = 0;
    for (;;) {
      const res = await fetch(url, {
        method,
        headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
        body: body !== undefined ? JSON.stringify(body) : undefined,
      });

      if (res.status === 429 && attempt < this.maxRetries) {
        const retryAfter = Number(res.headers.get("retry-after")) || 2 ** attempt;
        await new Promise((r) => setTimeout(r, retryAfter * 1000));
        attempt += 1;
        continue;
      }

      const text = await res.text();
      const data = text ? safeJsonParse(text) : null;

      if (!res.ok) {
        throw new SmartleadError(
          `Smartlead API ${method} ${path} failed: ${res.status} ${res.statusText}`,
          { status: res.status, body: data ?? text, url: url.toString(), method }
        );
      }
      return data;
    }
  }

  get(path, opts) {
    return this._request("GET", path, opts);
  }
  post(path, body, opts = {}) {
    return this._request("POST", path, { ...opts, body });
  }
  patch(path, body, opts = {}) {
    return this._request("PATCH", path, { ...opts, body });
  }
  delete(path, opts) {
    return this._request("DELETE", path, opts);
  }

  // ---- Campaigns -----------------------------------------------------------

  /** List all campaigns. */
  listCampaigns({ clientId, includeTags } = {}) {
    return this.get("/campaigns/", { query: { client_id: clientId, include_tags: includeTags } });
  }

  /** Fetch a single campaign's details. */
  getCampaign(campaignId) {
    return this.get(`/campaigns/${campaignId}`);
  }

  /**
   * Create a new campaign (starts in DRAFTED status).
   * @param {object} payload e.g. { name: "Q3 Outreach" }
   */
  createCampaign(payload) {
    return this.post("/campaigns/create", payload);
  }

  /** Delete a campaign permanently. */
  deleteCampaign(campaignId) {
    return this.delete(`/campaigns/${campaignId}`);
  }

  /**
   * Change a campaign's status.
   * @param {"START"|"PAUSED"|"STOPPED"} status
   */
  updateCampaignStatus(campaignId, status) {
    return this.post(`/campaigns/${campaignId}/status`, { status });
  }
  startCampaign(campaignId) {
    return this.updateCampaignStatus(campaignId, "START");
  }
  pauseCampaign(campaignId) {
    return this.updateCampaignStatus(campaignId, "PAUSED");
  }
  stopCampaign(campaignId) {
    return this.updateCampaignStatus(campaignId, "STOPPED");
  }

  /** Configure sending schedule/timing for a campaign. */
  setCampaignSchedule(campaignId, schedule) {
    return this.post(`/campaigns/${campaignId}/schedule`, schedule);
  }

  /** Update tracking, stop conditions, unsubscribe text, etc. */
  updateCampaignSettings(campaignId, settings) {
    return this.post(`/campaigns/${campaignId}/settings`, settings);
  }

  /** Get email sequences/variants for a campaign. */
  getCampaignSequences(campaignId) {
    return this.get(`/campaigns/${campaignId}/sequences`);
  }

  /** Create/update email sequences for a campaign. */
  upsertCampaignSequences(campaignId, sequences) {
    return this.post(`/campaigns/${campaignId}/sequences`, sequences);
  }

  /** Aggregate performance metrics (sent/open/click/reply/bounce/unsubscribe). */
  getCampaignAnalytics(campaignId) {
    return this.get(`/campaigns/${campaignId}/analytics`);
  }

  /** Detailed per-lead engagement/statistics, paginated. */
  getCampaignStatistics(campaignId, { offset, limit } = {}) {
    return this.get(`/campaigns/${campaignId}/statistics`, { query: { offset, limit } });
  }

  /** Analytics for a specific date range (max 30 days). */
  getCampaignAnalyticsByDate(campaignId, { startDate, endDate }) {
    return this.get(`/campaigns/${campaignId}/analytics-by-date`, {
      query: { start_date: startDate, end_date: endDate },
    });
  }

  /** Global metrics across all campaigns. */
  getAnalyticsOverview(params = {}) {
    return this.get("/analytics/overview", { query: params });
  }

  // ---- Campaign <-> Email account assignment -------------------------------

  listCampaignEmailAccounts(campaignId) {
    return this.get(`/campaigns/${campaignId}/email-accounts`);
  }
  addEmailAccountsToCampaign(campaignId, emailAccountIds) {
    return this.post(`/campaigns/${campaignId}/email-accounts`, { email_account_ids: emailAccountIds });
  }
  removeEmailAccountsFromCampaign(campaignId, emailAccountIds) {
    return this.delete(`/campaigns/${campaignId}/email-accounts`, { body: { email_account_ids: emailAccountIds } });
  }

  // ---- Email accounts (sending inboxes) + warmup/deliverability ------------

  /** List all connected sending email accounts. */
  listEmailAccounts({ offset, limit } = {}) {
    return this.get("/email-accounts/", { query: { offset, limit } });
  }

  /** Connect a new email account (SMTP/IMAP config). */
  createEmailAccount(payload) {
    return this.post("/email-accounts/save", payload);
  }

  /** Update settings/limits for an existing email account. */
  updateEmailAccount(emailAccountId, payload) {
    return this.post(`/email-accounts/${emailAccountId}`, payload);
  }

  /** Get full details (incl. warmup config) for one email account. */
  getEmailAccount(emailAccountId) {
    return this.get(`/email-accounts/${emailAccountId}/`);
  }

  /**
   * Enable/update warmup for an email account.
   * @param {object} settings e.g. { warmup_enabled: true, total_warmup_per_day: 35, daily_rampup: 2, reply_rate_percentage: 30 }
   */
  setEmailAccountWarmup(emailAccountId, settings) {
    return this.post(`/email-accounts/${emailAccountId}/warmup`, settings);
  }

  /** 7-day warmup performance / health data for one email account. */
  getEmailAccountWarmupStats(emailAccountId) {
    return this.get(`/email-accounts/${emailAccountId}/warmup-stats`);
  }

  /** Convenience: warmup + deliverability health across every connected inbox. */
  async getAllInboxHealth() {
    const accounts = await this.listEmailAccounts();
    const list = Array.isArray(accounts) ? accounts : accounts?.data ?? [];
    return Promise.all(
      list.map(async (acct) => {
        const id = acct.id ?? acct.email_account_id;
        const warmupStats = await this.getEmailAccountWarmupStats(id).catch((err) => ({ error: err.message }));
        return { account: acct, warmupStats };
      })
    );
  }

  // ---- Leads ----------------------------------------------------------------

  listCampaignLeads(campaignId, { offset, limit } = {}) {
    return this.get(`/campaigns/${campaignId}/leads`, { query: { offset, limit } });
  }
  getLeadByEmail(email) {
    return this.get("/leads/", { query: { email } });
  }
  getLeadCategories() {
    return this.get("/leads/fetch-categories");
  }
  /** Bulk add leads to a campaign (max 400 per request). */
  addLeadsToCampaign(campaignId, leadList, settings = {}) {
    return this.post(`/campaigns/${campaignId}/leads`, { lead_list: leadList, ...settings });
  }
  updateLead(campaignId, leadId, payload) {
    return this.post(`/campaigns/${campaignId}/leads/${leadId}`, payload);
  }
  pauseLead(campaignId, leadId) {
    return this.post(`/campaigns/${campaignId}/leads/${leadId}/pause`);
  }
  resumeLead(campaignId, leadId) {
    return this.post(`/campaigns/${campaignId}/leads/${leadId}/resume`);
  }
  deleteLead(campaignId, leadId) {
    return this.delete(`/campaigns/${campaignId}/leads/${leadId}`);
  }
  unsubscribeLeadFromCampaign(campaignId, leadId) {
    return this.post(`/campaigns/${campaignId}/leads/${leadId}/unsubscribe`);
  }
  unsubscribeLeadGlobally(leadId) {
    return this.post(`/leads/${leadId}/unsubscribe`);
  }
  /** @param {object} payload e.g. { domain_block_list: ["competitor.com"], client_id: null } */
  blockDomainOrEmail(payload) {
    return this.post("/leads/add-domain-block-list", payload);
  }
  /** Check the block list before re-blocking (per standing rule). */
  getDomainBlockList({ offset, limit, filterClientId, filterEmailOrDomain, filterEmailWithDomain } = {}) {
    return this.get("/leads/get-domain-block-list", {
      query: {
        offset,
        limit,
        filter_client_id: filterClientId,
        filter_email_or_domain: filterEmailOrDomain,
        filter_email_with_domain: filterEmailWithDomain,
      },
    });
  }
  deleteDomainBlockListEntry(id) {
    return this.delete("/leads/delete-domain-block-list", { query: { id } });
  }
  getLeadMessageHistory(campaignId, leadId) {
    return this.get(`/campaigns/${campaignId}/leads/${leadId}/message-history`);
  }
  replyToLeadThread(campaignId, payload) {
    return this.post(`/campaigns/${campaignId}/reply-email-thread`, payload);
  }
  exportCampaignLeads(campaignId, params = {}) {
    return this.get(`/campaigns/${campaignId}/leads-export`, { query: params });
  }
  getCampaignsForLead(leadId) {
    return this.get(`/leads/${leadId}/campaigns`);
  }

  /**
   * Update a lead's category within a specific campaign (e.g. "Interested", "Not Interested").
   * @param {object} [opts]
   * @param {boolean} [opts.pauseLead] - also pause the lead's outreach in this campaign.
   */
  updateLeadCategory(campaignId, leadId, categoryId, { pauseLead } = {}) {
    return this.post(`/campaigns/${campaignId}/leads/${leadId}/category`, {
      category_id: categoryId,
      pause_lead: pauseLead,
    });
  }

  // ---- Master inbox ----------------------------------------------------------

  /**
   * Fetch replies across all campaigns from the unified Master Inbox.
   * @param {object} [filters] e.g. { emailStatus: "Replied", campaignId, leadCategories, offset, limit }
   * @param {boolean} [fetchMessageHistory] - true for full thread, false for latest message only.
   */
  getMasterInboxReplies(filters = {}, fetchMessageHistory = false) {
    return this.post("/master-inbox/inbox-replies", filters, {
      query: { fetch_message_history: fetchMessageHistory },
    });
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default SmartleadClient;
