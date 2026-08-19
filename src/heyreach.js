/**
 * Minimal, dependency-free client for the HeyReach public API (LinkedIn outreach automation).
 *
 * Docs: https://documenter.getpostman.com/view/23808049/2sA2xb5F75
 *
 * Auth: `X-API-KEY` header on every request — but HeyReach has *two* incompatible key
 * scopes that share that same header name:
 *   - A **workspace-level** key (inside a workspace: Settings → API) is required for the
 *     everyday endpoints below: campaigns, leads, network/connections.
 *   - An **organization-level** key (Organization settings, org-admin only) is required
 *     for the separate "Organization Management API": listing workspaces and minting new
 *     workspace API keys.
 * An org key does NOT work on the everyday endpoints — verified directly against the live
 * API, which responds 200 with the body `"The provided API key is not a workspace-level
 * key."` (not a 401/403) when you pass one where a workspace key is expected. This client
 * takes both keys separately and picks the right one per call so that mistake fails fast
 * with a clear message instead of a confusing 200.
 *
 * Rate limit: 300 requests/minute, tracked *separately* per scope (workspace calls and
 * org-management calls don't share a bucket).
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const DEFAULT_BASE_URL = "https://api.heyreach.io/api/public";

export class HeyReachError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "HeyReachError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class HeyReachClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiKey] - workspace-level key; defaults to process.env.HEYREACH_API_KEY
   * @param {string} [opts.orgApiKey] - organization-level key; defaults to process.env.HEYREACH_ORG_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.HEYREACH_BASE_URL or the public API
   */
  constructor({ apiKey, orgApiKey, baseUrl } = {}) {
    this.apiKey = apiKey || process.env.HEYREACH_API_KEY;
    this.orgApiKey = orgApiKey || process.env.HEYREACH_ORG_API_KEY;
    this.baseUrl = (baseUrl || process.env.HEYREACH_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");

    if (!this.apiKey && !this.orgApiKey) {
      throw new Error(
        "Missing HeyReach credentials. Set HEYREACH_API_KEY (workspace-level, for campaigns/leads/" +
          "network) and/or HEYREACH_ORG_API_KEY (organization-level, for workspace/API-key management) " +
          "in your environment/.env, or pass { apiKey, orgApiKey } to `new HeyReachClient()`."
      );
    }
  }

  _requireApiKey() {
    if (!this.apiKey) {
      throw new Error(
        "This call needs a workspace-level key. Set HEYREACH_API_KEY (inside the workspace: " +
          "Settings → API) — see src/heyreach.js for why the organization key won't work here."
      );
    }
    return this.apiKey;
  }

  _requireOrgApiKey() {
    if (!this.orgApiKey) {
      throw new Error(
        "This call needs an organization-level key. Set HEYREACH_ORG_API_KEY (Organization settings, " +
          "org-admin only) — see src/heyreach.js for why a workspace key won't work here."
      );
    }
    return this.orgApiKey;
  }

  async _request(method, path, { apiKey, query = {}, body } = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, v);
    }

    const res = await fetch(url, {
      method,
      headers: { "X-API-KEY": apiKey, "Content-Type": "application/json" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;

    if (!res.ok) {
      throw new HeyReachError(`HeyReach ${method} ${path} failed: ${res.status} ${res.statusText}`, {
        status: res.status,
        body: data ?? text,
        url: url.toString(),
      });
    }
    return data;
  }

  // ---- Auth -------------------------------------------------------------------

  /** Verify a workspace-level key + connectivity. 200 with no body on success. */
  checkApiKey() {
    return this._request("GET", "/auth/CheckApiKey", { apiKey: this._requireApiKey() });
  }

  // ---- Campaigns ----------------------------------------------------------------

  /** Paginated campaign list, up to 100 per request. `statuses` values: DRAFT,
   * IN_PROGRESS, PAUSED, FINISHED, CANCELED, FAILED, STARTING, SCHEDULED. */
  listCampaigns({ offset = 0, limit = 10, keyword, statuses, accountIds } = {}) {
    return this._request("POST", "/campaign/GetAll", {
      apiKey: this._requireApiKey(),
      body: { offset, limit, keyword, statuses, accountIds },
    });
  }

  getCampaign(campaignId) {
    return this._request("GET", "/campaign/GetById", {
      apiKey: this._requireApiKey(),
      query: { campaignId },
    });
  }

  /** Activate a DRAFT/SCHEDULED campaign. Needs a valid sequence and at least one
   * connected LinkedIn sender account, or HeyReach returns a 400. */
  startCampaign(campaignId) {
    return this._request("POST", "/campaign/StartCampaign", {
      apiKey: this._requireApiKey(),
      query: { campaignId },
    });
  }

  pauseCampaign(campaignId) {
    return this._request("POST", "/campaign/Pause", { apiKey: this._requireApiKey(), query: { campaignId } });
  }

  resumeCampaign(campaignId) {
    return this._request("POST", "/campaign/Resume", { apiKey: this._requireApiKey(), query: { campaignId } });
  }

  /** Full replacement of a campaign's name/lead-list/exclusion settings. Omitted exclusion
   * fields reset to their defaults (false / null) — always send the complete set you want,
   * not a partial diff (HeyReach's own docs flag this). Only allowed while the campaign is
   * DRAFT, SCHEDULED, or PAUSED. */
  updateCampaignSettings(body) {
    return this._request("POST", "/campaign/UpdateSettings", { apiKey: this._requireApiKey(), body });
  }

  /** Add up to 100 leads per request. `resumeFinishedCampaign`/`resumePausedCampaign`
   * control whether a non-IN_PROGRESS campaign gets auto-resumed to run the new leads. */
  addLeadsToCampaign(body) {
    return this._request("POST", "/campaign/AddLeadsToCampaign", { apiKey: this._requireApiKey(), body });
  }

  /** Same request shape as addLeadsToCampaign, but the response reports counts:
   * { addedLeadsCount, updatedLeadsCount, failedLeadsCount }. */
  addLeadsToCampaignV2(body) {
    return this._request("POST", "/campaign/AddLeadsToCampaignV2", { apiKey: this._requireApiKey(), body });
  }

  /** Stop a single lead's progression through a campaign. Identify the lead via
   * `leadMemberId` (the `linkedin_id` from getLeadsFromCampaign) or `leadUrl`. */
  stopLeadInCampaign({ campaignId, leadMemberId, leadUrl }) {
    return this._request("POST", "/campaign/StopLeadInCampaign", {
      apiKey: this._requireApiKey(),
      body: { campaignId, leadMemberId, leadUrl },
    });
  }

  /** The "Lead Analytics" screen: leads pending/in-sequence/finished/etc. in a campaign.
   * `timeFilter` is one of Everywhere (default), CreationTime, LastActionTakenTime,
   * FailedTime, LastActionTakenOrFailedTime — paired with `timeFrom`/`timeTo` (ISO 8601). */
  getLeadsFromCampaign({ campaignId, offset = 0, limit = 100, timeFrom, timeTo, timeFilter } = {}) {
    return this._request("POST", "/campaign/GetLeadsFromCampaign", {
      apiKey: this._requireApiKey(),
      body: { campaignId, offset, limit, timeFrom, timeTo, timeFilter },
    });
  }

  /** Look up which campaigns a lead (by email, linkedinId, or profileUrl) is in. */
  getCampaignsForLead({ email, linkedinId, profileUrl, offset = 0, limit = 100 } = {}) {
    return this._request("POST", "/campaign/GetCampaignsForLead", {
      apiKey: this._requireApiKey(),
      body: { email, linkedinId, profileUrl, offset, limit },
    });
  }

  // ---- Network / connections ------------------------------------------------------

  /** Paginated 1st-degree LinkedIn network for one connected sender account. */
  getMyNetworkForSender({ senderId, pageNumber = 0, pageSize = 100 }) {
    return this._request("POST", "/MyNetwork/GetMyNetworkForSender", {
      apiKey: this._requireApiKey(),
      body: { senderId, pageNumber, pageSize },
    });
  }

  /** Whether a lead is a connection of a sender. Pass leadProfileUrl OR leadLinkedInId,
   * not both — HeyReach errors if both are set. */
  isConnection({ senderAccountId, leadProfileUrl, leadLinkedInId }) {
    return this._request("POST", "/MyNetwork/IsConnection", {
      apiKey: this._requireApiKey(),
      body: { senderAccountId, leadProfileUrl, leadLinkedInId },
    });
  }

  // ---- Organization management (org-admin only; needs HEYREACH_ORG_API_KEY) ----------

  /** All workspaces in the organization. Confirmed live against the real API: GET,
   * returns { totalCount, items: [{ workspaceId, workspaceName, seatsLimit, usedSeats }] }. */
  listWorkspaces() {
    return this._request("GET", "/management/organizations/workspaces", { apiKey: this._requireOrgApiKey() });
  }

  /** ⚠️ Mutating, one-way action — mints a new API/integration key inside a workspace and
   * deactivates any existing key of that same type for the workspace (see the returned
   * `previousKeyStatus`). `apiKeyType` is one of PUBLIC | N8N | MAKE | ZAPIER | MCP. */
  createWorkspaceApiKey(workspaceId, apiKeyType = "PUBLIC") {
    return this._request("POST", `/management/organizations/api-keys/workspaces/${workspaceId}`, {
      apiKey: this._requireOrgApiKey(),
      body: { apiKeyType },
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

export default HeyReachClient;
