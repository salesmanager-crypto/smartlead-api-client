/**
 * Minimal, dependency-free client for the Namecheap XML API.
 *
 * Docs: https://www.namecheap.com/support/api/methods/
 *
 * Namecheap's API is XML over HTTP GET, authenticated via query params
 * (`ApiUser`, `ApiKey`, `UserName`, `ClientIp`) rather than a header. Every
 * request must also come from an IP address whitelisted in the Namecheap
 * account (Profile -> Tools -> API Access -> Whitelisted IPs) — calls fail
 * regardless of how correct the credentials are until that IP is added.
 *
 * This client has no XML library dependency. It does a small attribute-only
 * parse (`parseSelfClosingTags`) sufficient for the endpoints below — it is
 * NOT a general XML parser. Don't reuse it for endpoints whose payload is
 * nested text content rather than self-closing tags with attributes without
 * upgrading the parsing approach.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const DEFAULT_BASE_URL = "https://api.namecheap.com/xml.response";

export class NamecheapError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "NamecheapError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class NamecheapClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiUser] - defaults to process.env.NAMECHEAP_API_USER
   * @param {string} [opts.apiKey] - defaults to process.env.NAMECHEAP_API_KEY
   * @param {string} [opts.userName] - defaults to process.env.NAMECHEAP_USERNAME, then apiUser
   * @param {string} [opts.clientIp] - defaults to process.env.NAMECHEAP_CLIENT_IP; must be whitelisted
   * @param {string} [opts.baseUrl] - defaults to process.env.NAMECHEAP_BASE_URL or the public API
   */
  constructor({ apiUser, apiKey, userName, clientIp, baseUrl } = {}) {
    this.apiUser = apiUser || process.env.NAMECHEAP_API_USER;
    this.apiKey = apiKey || process.env.NAMECHEAP_API_KEY;
    this.userName = userName || process.env.NAMECHEAP_USERNAME || this.apiUser;
    this.clientIp = clientIp || process.env.NAMECHEAP_CLIENT_IP;
    this.baseUrl = (baseUrl || process.env.NAMECHEAP_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");

    if (!this.apiUser || !this.apiKey || !this.clientIp) {
      throw new Error(
        "Missing Namecheap credentials. Set NAMECHEAP_API_USER, NAMECHEAP_API_KEY, and " +
          "NAMECHEAP_CLIENT_IP (a whitelisted IP — see Profile > Tools > API Access in your " +
          "Namecheap account) in your environment/.env, or pass them to `new NamecheapClient()`."
      );
    }
  }

  async _request(command, params = {}) {
    const query = new URLSearchParams({
      ApiUser: this.apiUser,
      ApiKey: this.apiKey,
      UserName: this.userName,
      ClientIp: this.clientIp,
      Command: command,
      ...params,
    });
    const url = `${this.baseUrl}?${query}`;
    const res = await fetch(url);
    const text = await res.text();
    const status = /<ApiResponse[^>]*\sStatus="([^"]+)"/.exec(text)?.[1];

    if (!res.ok || status !== "OK") {
      const errorMsg = /<Error[^>]*>([^<]*)<\/Error>/.exec(text)?.[1];
      throw new NamecheapError(`Namecheap ${command} failed: ${errorMsg || status || res.statusText}`, {
        status: res.status,
        body: text,
        url,
      });
    }
    return text;
  }

  /**
   * List domains in the account.
   * @param {object} [opts]
   * @param {number} [opts.pageSize=100] - Namecheap's default is 20; max is 100 per page.
   * @returns {Promise<Array<{Name: string, Expires: string, IsExpired: string, IsLocked: string,
   *   AutoRenew: string, WhoisGuard: string, [key: string]: string}>>}
   */
  async listDomains({ pageSize = 100 } = {}) {
    const xml = await this._request("namecheap.domains.getList", { PageSize: pageSize });
    return parseSelfClosingTags(xml, "Domain");
  }

  /**
   * DNS host records for a domain (only meaningful if Namecheap's own DNS is in use —
   * i.e. `IsOurDNS` was true in `listDomains()`; a domain pointed elsewhere returns an
   * empty list here even though DNS records exist at the other provider).
   */
  async getDnsHosts(domain) {
    const [sld, ...tldParts] = domain.split(".");
    const xml = await this._request("namecheap.domains.dns.getHosts", { SLD: sld, TLD: tldParts.join(".") });
    return parseSelfClosingTags(xml, "host");
  }
}

function parseSelfClosingTags(xml, tagName) {
  const tagRe = new RegExp(`<${tagName}\\s+([^>]*?)/>`, "g");
  const attrRe = /([\w:-]+)="([^"]*)"/g;
  const results = [];
  let tagMatch;
  while ((tagMatch = tagRe.exec(xml))) {
    const attrs = {};
    let attrMatch;
    attrRe.lastIndex = 0;
    while ((attrMatch = attrRe.exec(tagMatch[1]))) {
      attrs[attrMatch[1]] = attrMatch[2];
    }
    results.push(attrs);
  }
  return results;
}

export default NamecheapClient;
