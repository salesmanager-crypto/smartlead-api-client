/**
 * Minimal, dependency-free client for the Surfe API (contact/company enrichment).
 *
 * Docs: https://developers.surfe.com
 *
 * Auth: `Authorization: Bearer <key>` on every request.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 *
 * Enrichment is async: enrichPeople() returns an enrichment id, then poll
 * getPeopleEnrichment(id) until the status is complete. Enrichment spends credits.
 */

const DEFAULT_BASE_URL = "https://api.surfe.com";

export class SurfeError extends Error {
  constructor(message, { status, body, url, method } = {}) {
    super(message);
    this.name = "SurfeError";
    this.status = status;
    this.body = body;
    this.url = url;
    this.method = method;
  }
}

export class SurfeClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiKey] - defaults to process.env.SURFE_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.SURFE_BASE_URL or the public API
   */
  constructor({ apiKey, baseUrl } = {}) {
    this.apiKey = apiKey || process.env.SURFE_API_KEY;
    this.baseUrl = (baseUrl || process.env.SURFE_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");

    if (!this.apiKey) {
      throw new Error(
        "Missing Surfe API key. Set SURFE_API_KEY in your environment/.env, or pass " +
          "{ apiKey } to `new SurfeClient()`."
      );
    }
  }

  async _request(method, path, body) {
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      method,
      headers: {
        Authorization: `Bearer ${this.apiKey}`,
        Accept: "application/json",
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    const text = await res.text();
    let data;
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = text;
    }
    if (!res.ok) {
      throw new SurfeError(`Surfe ${method} ${path} failed: ${res.status}`, {
        status: res.status,
        body: data,
        url,
        method,
      });
    }
    return data;
  }

  /** Remaining credits: { totalEmail, totalMobile, totalSearch }. Free; doubles as a key check. */
  getCredits() {
    return this._request("GET", "/v1/credits");
  }

  /** Start a people enrichment. `body` per Surfe docs, e.g. { people: [{ firstName, lastName, companyName, linkedinUrl }] }. */
  enrichPeople(body) {
    return this._request("POST", "/v2/people/enrich", body);
  }

  getPeopleEnrichment(id) {
    return this._request("GET", `/v2/people/enrich/${encodeURIComponent(id)}`);
  }

  searchPeople(body) {
    return this._request("POST", "/v2/people/search", body);
  }

  searchCompanies(body) {
    return this._request("POST", "/v2/companies/search", body);
  }
}
