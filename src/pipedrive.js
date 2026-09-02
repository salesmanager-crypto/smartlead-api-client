// Minimal, dependency-free Pipedrive REST client (API v2 with v1 for leads).
// Auth: PIPEDRIVE_API_TOKEN from the environment. Get it from Pipedrive under
// Personal preferences -> API. Never commit the token; keep it in .env or the environment.
//
// Responses are returned as Pipedrive sends them: { success, data, additional_data }.
// That is the same shape the Pipedrive connector returns, so files saved from either
// source are interchangeable for dashboards/pull/build-constants.mjs.

const DEFAULT_BASE_URL = "https://api.pipedrive.com";

export class PipedriveError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "PipedriveError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class PipedriveClient {
  constructor({ apiToken, baseUrl } = {}) {
    this.apiToken = apiToken || process.env.PIPEDRIVE_API_TOKEN;
    this.baseUrl = (baseUrl || process.env.PIPEDRIVE_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");
    if (!this.apiToken) throw new PipedriveError("PIPEDRIVE_API_TOKEN is not set");
  }

  async get(path, query = {}) {
    const url = new URL(this.baseUrl + path);
    for (const [k, v] of Object.entries(query)) if (v !== undefined && v !== null && v !== "") url.searchParams.set(k, String(v));
    let lastErr;
    for (let attempt = 0; attempt < 4; attempt++) {
      const res = await fetch(url, { headers: { "x-api-token": this.apiToken, accept: "application/json" } });
      const text = await res.text();
      let body; try { body = JSON.parse(text); } catch { body = text; }
      if (res.ok) return body;
      lastErr = new PipedriveError(`Pipedrive GET ${path} failed: ${res.status} ${res.statusText}`, { status: res.status, body, url: url.toString() });
      if (res.status === 429 || res.status >= 500) { await new Promise((r) => setTimeout(r, 1500 * (attempt + 1))); continue; }
      throw lastErr;
    }
    throw lastErr;
  }

  /** v2 cursor pagination. Returns every page's raw response, in order. */
  async pages(path, query = {}, { max = 50 } = {}) {
    const out = [];
    let cursor;
    for (let i = 0; i < max; i++) {
      const page = await this.get(path, { ...query, cursor });
      out.push(page);
      cursor = page.additional_data && page.additional_data.next_cursor;
      if (!cursor) break;
    }
    return out;
  }

  activities(query = {}) { return this.pages("/api/v2/activities", { limit: 500, sort_by: "due_date", sort_direction: "asc", ...query }); }
  deals(query = {}) { return this.pages("/api/v2/deals", { limit: 500, ...query }); }
  persons(query = {}) { return this.pages("/api/v2/persons", { limit: 500, sort_by: "id", sort_direction: "desc", ...query }); }
  organizations(query = {}) { return this.pages("/api/v2/organizations", { limit: 500, sort_by: "id", sort_direction: "desc", ...query }); }
  stages(query = {}) { return this.get("/api/v2/stages", query); }

  /** Leads are v1 only: offset pagination via start/limit. Returns every page's raw response. */
  async leads(query = {}, { max = 50 } = {}) {
    const out = [];
    const limit = query.limit || 500;
    for (let i = 0, start = 0; i < max; i++, start += limit) {
      const page = await this.get("/v1/leads", { ...query, limit, start });
      out.push(page);
      const more = page.additional_data && page.additional_data.pagination && page.additional_data.pagination.more_items_in_collection;
      if (!more) break;
    }
    return out;
  }
}

export default PipedriveClient;
