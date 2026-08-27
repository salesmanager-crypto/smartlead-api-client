/**
 * Minimal, dependency-free client for the Pipedrive REST API (v1).
 *
 * Docs: https://developers.pipedrive.com/docs/api/v1
 *
 * Auth: `api_token` query parameter on every request, scoped to a company domain
 * (`https://{yourCompany}.pipedrive.com/api/v1`).
 *
 * This client only wraps the endpoints the CRM dashboard and the Smartlead-to-Pipedrive
 * automation (see docs/Smartlead-Pipedrive-Automation-Workflow.md) actually use — deal
 * pipeline/stage reads, organization/person/activity search + create, and note creation.
 * Extend it with `client.get/post/put/delete` for anything else in the Pipedrive API.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const DEFAULT_API_VERSION = "v1";

export class PipedriveError extends Error {
  constructor(message, { status, body, url, method } = {}) {
    super(message);
    this.name = "PipedriveError";
    this.status = status;
    this.body = body;
    this.url = url;
    this.method = method;
  }
}

export class PipedriveClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiToken] - defaults to process.env.PIPEDRIVE_API_TOKEN
   * @param {string} [opts.companyDomain] - e.g. "albertscott"; defaults to process.env.PIPEDRIVE_COMPANY_DOMAIN
   * @param {string} [opts.baseUrl] - overrides the derived company-domain URL entirely
   */
  constructor({ apiToken, companyDomain, baseUrl } = {}) {
    this.apiToken = apiToken || process.env.PIPEDRIVE_API_TOKEN;
    this.companyDomain = companyDomain || process.env.PIPEDRIVE_COMPANY_DOMAIN;
    this.baseUrl = (
      baseUrl ||
      process.env.PIPEDRIVE_BASE_URL ||
      (this.companyDomain ? `https://${this.companyDomain}.pipedrive.com/api/${DEFAULT_API_VERSION}` : null)
    )?.replace(/\/+$/, "");

    if (!this.apiToken) {
      throw new Error(
        "Missing Pipedrive API token. Set PIPEDRIVE_API_TOKEN in your environment/.env " +
          "(Pipedrive: Settings -> Personal preferences -> API), or pass { apiToken } to `new PipedriveClient()`."
      );
    }
    if (!this.baseUrl) {
      throw new Error(
        "Missing Pipedrive company domain. Set PIPEDRIVE_COMPANY_DOMAIN=albertscott (the subdomain in " +
          "https://albertscott.pipedrive.com), or pass { companyDomain } / { baseUrl } to `new PipedriveClient()`."
      );
    }
  }

  // ---- low-level request helper ------------------------------------------

  async _request(method, path, { query = {}, body } = {}) {
    const url = new URL(this.baseUrl + path);
    url.searchParams.set("api_token", this.apiToken);
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, v);
    }

    const res = await fetch(url, {
      method,
      headers: body !== undefined ? { "Content-Type": "application/json" } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;

    if (!res.ok) {
      throw new PipedriveError(`Pipedrive API ${method} ${path} failed: ${res.status} ${res.statusText}`, {
        status: res.status,
        body: data ?? text,
        url: url.toString(),
        method,
      });
    }
    // Pipedrive wraps every payload as { success, data, additional_data }.
    return data;
  }

  get(path, opts) {
    return this._request("GET", path, opts);
  }
  post(path, body, opts = {}) {
    return this._request("POST", path, { ...opts, body });
  }
  put(path, body, opts = {}) {
    return this._request("PUT", path, { ...opts, body });
  }
  delete(path, opts) {
    return this._request("DELETE", path, opts);
  }

  // ---- Pipelines & stages ----------------------------------------------

  getPipelines() {
    return this.get("/pipelines");
  }

  getStages(pipelineId) {
    return this.get("/stages", { query: { pipeline_id: pipelineId } });
  }

  // ---- Deals --------------------------------------------------------------

  getDeals({ status = "open", stageId, ownerId, start, limit = 500 } = {}) {
    return this.get("/deals", {
      query: { status, stage_id: stageId, owner_id: ownerId, start, limit, sort: "update_time DESC" },
    });
  }

  getDeal(dealId) {
    return this.get(`/deals/${dealId}`);
  }

  addDeal(payload) {
    return this.post("/deals", payload);
  }

  updateDeal(dealId, payload) {
    return this.put(`/deals/${dealId}`, payload);
  }

  /** Deals whose last activity/update is older than `hours` and still open — used for the
   * "unaddressed opportunity" alert threshold (spec: 48h). */
  async getStaleOpenDeals({ hours = 48, ownerId } = {}) {
    const res = await this.getDeals({ status: "open", ownerId });
    const deals = res?.data || [];
    const cutoff = Date.now() - hours * 60 * 60 * 1000;
    return deals.filter((d) => {
      const last = d.update_time ? Date.parse(d.update_time.replace(" ", "T") + "Z") : 0;
      return last < cutoff;
    });
  }

  // ---- Organizations, Persons, Activities, Notes ---------------------------
  // Mirrors docs/Smartlead-Pipedrive-Automation-Workflow.md: always search before creating.

  searchOrganization(term) {
    return this.get("/organizations/search", { query: { term, exact_match: false } });
  }

  addOrganization(payload) {
    return this.post("/organizations", payload);
  }

  searchPersons(term, { fields = "email" } = {}) {
    return this.get("/persons/search", { query: { term, fields, exact_match: false } });
  }

  addPerson(payload) {
    // Per workflow rule 4: omit job_title, notes, postal_address, im, birthday — the
    // account's contact sync isn't enabled and Pipedrive 403s on those fields.
    const { job_title, notes, postal_address, im, birthday, ...safePayload } = payload;
    return this.post("/persons", safePayload);
  }

  addActivity({ personId, leadId, ...payload }) {
    // Per workflow rule 5: person_id is read-only on activities; pass it via `participants`.
    const body = { ...payload };
    if (personId) body.participants = [{ person_id: personId, primary: true }];
    if (leadId) body.lead_id = leadId;
    return this.post("/activities", body);
  }

  addNote(payload) {
    return this.post("/notes", payload);
  }

  addLead(payload) {
    return this.post("/leads", payload);
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}
