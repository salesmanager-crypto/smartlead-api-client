/**
 * Minimal, dependency-free, read-side client for the Pipedrive REST API (v1 + v2).
 *
 * Docs: https://developers.pipedrive.com/docs/api/v1
 *       https://developers.pipedrive.com/docs/api/v2
 *
 * Auth: the API token goes in the `x-api-token` header, never in the URL, so it
 * cannot leak through an error message or a log line.
 * Base URL: https://{PIPEDRIVE_COMPANY_DOMAIN}.pipedrive.com/api
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

export class PipedriveError extends Error {
  constructor(message, { status, body, method, path } = {}) {
    super(message);
    this.name = "PipedriveError";
    this.status = status;
    this.body = body;
    this.method = method;
    this.path = path;
  }
}

export class PipedriveClient {
  /**
   * @param {object} opts
   * @param {string} [opts.apiToken] - defaults to process.env.PIPEDRIVE_API_TOKEN
   * @param {string} [opts.companyDomain] - defaults to process.env.PIPEDRIVE_COMPANY_DOMAIN
   * @param {number} [opts.maxRetries] - retries on 429 and 5xx with backoff (default 3)
   */
  constructor({ apiToken, companyDomain, maxRetries = 3 } = {}) {
    this.apiToken = apiToken || process.env.PIPEDRIVE_API_TOKEN;
    const domain = companyDomain || process.env.PIPEDRIVE_COMPANY_DOMAIN;
    this.maxRetries = maxRetries;
    if (!this.apiToken || !domain) {
      throw new Error("Missing Pipedrive credentials. Set PIPEDRIVE_API_TOKEN and PIPEDRIVE_COMPANY_DOMAIN (the part before .pipedrive.com).");
    }
    this.baseUrl = `https://${domain}.pipedrive.com/api`;
  }

  /** GET /api/{version}{path}. Returns the parsed JSON body. */
  async get(version, path, query = {}) {
    const url = new URL(`${this.baseUrl}/${version}${path}`);
    for (const [k, v] of Object.entries(query)) if (v !== undefined && v !== null) url.searchParams.set(k, v);

    for (let attempt = 0; ; attempt++) {
      let res;
      try {
        res = await fetch(url, { headers: { "x-api-token": this.apiToken, accept: "application/json" } });
      } catch (err) {
        if (attempt < this.maxRetries) { await sleep(2 ** attempt * 1000); continue; }
        throw new PipedriveError(`Pipedrive GET ${version}${path}: network error (${err.cause?.code || err.name})`, { method: "GET", path });
      }
      if ((res.status === 429 || res.status >= 500) && attempt < this.maxRetries) {
        await sleep((Number(res.headers.get("retry-after")) || 2 ** attempt) * 1000);
        continue;
      }
      const text = await res.text();
      let body;
      try { body = text ? JSON.parse(text) : null; } catch { body = text; }
      if (!res.ok) {
        const detail = typeof body === "object" && body ? body.error || body.message || "" : "";
        throw new PipedriveError(`Pipedrive GET ${version}${path} failed: ${res.status}${detail ? " " + detail : ""}`, {
          status: res.status, body, method: "GET", path,
        });
      }
      return body;
    }
  }

  /** Every row of a v2 list endpoint (cursor pagination). */
  async listAllV2(path, query = {}) {
    const out = [];
    let cursor;
    do {
      const j = await this.get("v2", path, { ...query, limit: 500, cursor });
      out.push(...(j?.data || []));
      cursor = j?.additional_data?.next_cursor || null;
    } while (cursor);
    return out;
  }

  /** Every row of a v1 list endpoint (start/limit pagination). */
  async listAllV1(path, query = {}) {
    const out = [];
    let start = 0;
    for (;;) {
      const j = await this.get("v1", path, { ...query, limit: 500, start });
      out.push(...(j?.data || []));
      const p = j?.additional_data?.pagination;
      if (!p?.more_items_in_collection) break;
      start = p.next_start;
    }
    return out;
  }

  users() { return this.get("v1", "/users").then((j) => j?.data || []); }
  stages() { return this.listAllV2("/stages"); }
  /** v2 without a status filter returns open, won and lost deals (not deleted). */
  deals() { return this.listAllV2("/deals"); }
  persons() { return this.listAllV2("/persons"); }
  organizations() { return this.listAllV2("/organizations"); }
  openActivities() { return this.listAllV2("/activities", { done: false }); }
  leads() { return this.listAllV1("/leads", { archived_status: "not_archived" }); }
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

export default PipedriveClient;
