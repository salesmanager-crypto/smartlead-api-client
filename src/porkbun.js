/**
 * Minimal, dependency-free client for the Porkbun API (v3).
 *
 * Docs: https://porkbun.com/api/json/v3/documentation
 *
 * Auth: unlike most REST APIs, Porkbun takes credentials in the JSON *body* of every
 * request (`apikey` / `secretapikey`), not a header — and every endpoint is POST, even
 * pure reads like `/ping` and `/domain/listAll`. Verified directly against the live API
 * rather than assumed, since public summaries of this API commonly get both of those
 * wrong (describing header auth and GET reads instead).
 *
 * Requires Node.js 18+ (uses the built-in `fetch`).
 *
 * ⚠️ Per-domain endpoints (`/dns/retrieve`, `/domain/getNs`, `/ssl/retrieve`, etc.) fail
 * with a "Domain is not opted in to API access" error until API access is turned on for
 * that domain (or globally) in Porkbun's account settings. That's a Porkbun account
 * setting, not a client bug — `listDomains()` still works regardless, since it's
 * account-level rather than per-domain.
 */

const DEFAULT_BASE_URL = "https://api.porkbun.com/api/json/v3";

export class PorkbunError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "PorkbunError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class PorkbunClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiKey] - defaults to process.env.PORKBUN_API_KEY
   * @param {string} [opts.secretApiKey] - defaults to process.env.PORKBUN_SECRET_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.PORKBUN_BASE_URL or the public API
   */
  constructor({ apiKey, secretApiKey, baseUrl } = {}) {
    this.apiKey = apiKey || process.env.PORKBUN_API_KEY;
    this.secretApiKey = secretApiKey || process.env.PORKBUN_SECRET_API_KEY;
    this.baseUrl = (baseUrl || process.env.PORKBUN_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");

    if (!this.apiKey || !this.secretApiKey) {
      throw new Error(
        "Missing Porkbun credentials. Set PORKBUN_API_KEY and PORKBUN_SECRET_API_KEY in your " +
          "environment/.env, or pass { apiKey, secretApiKey } to `new PorkbunClient()`."
      );
    }
  }

  async _post(path, body = {}) {
    const url = `${this.baseUrl}${path}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ apikey: this.apiKey, secretapikey: this.secretApiKey, ...body }),
    });

    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;

    if (!res.ok || data?.status === "ERROR") {
      throw new PorkbunError(`Porkbun POST ${path} failed: ${data?.message ?? res.statusText}`, {
        status: res.status,
        body: data ?? text,
        url,
      });
    }
    return data;
  }

  /** Verify credentials + connectivity. */
  ping() {
    return this._post("/ping");
  }

  /** All domains in the account: status, tld, createDate, expireDate, autoRenew, whoisPrivacy,
   * securityLock, apiAccess. Account-level — works even for domains with API access disabled. */
  async listDomains() {
    const { domains } = await this._post("/domain/listAll");
    return domains;
  }

  /** DNS records for a domain. Requires that domain to be opted in to API access
   * (Porkbun account setting), or throws a PorkbunError with a clear message. */
  getDnsRecords(domain) {
    return this._post(`/dns/retrieve/${domain}`);
  }

  /** Current nameservers for a domain. Same API-access opt-in requirement as above. */
  getNameservers(domain) {
    return this._post(`/domain/getNs/${domain}`);
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default PorkbunClient;
