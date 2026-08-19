/**
 * Minimal, dependency-free client for the QuickEmailVerification.com REST API.
 *
 * Docs: https://docs.quickemailverification.com/email-verification-api/verify-an-email-address
 *
 * Auth: `apikey` query parameter on every request.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const DEFAULT_BASE_URL = "https://api.quickemailverification.com/v1";

export class QuickEmailVerificationError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "QuickEmailVerificationError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class QuickEmailVerificationClient {
  /**
   * @param {object} opts
   * @param {string} [opts.apiKey] - defaults to process.env.QUICKEMAILVERIFICATION_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.QEV_BASE_URL or the public API
   */
  constructor({ apiKey, baseUrl } = {}) {
    this.apiKey = apiKey || process.env.QUICKEMAILVERIFICATION_API_KEY;
    this.baseUrl = (baseUrl || process.env.QEV_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");

    if (!this.apiKey) {
      throw new Error(
        "Missing QuickEmailVerification API key. Set QUICKEMAILVERIFICATION_API_KEY in your " +
          "environment/.env, or pass { apiKey } to `new QuickEmailVerificationClient()`."
      );
    }
  }

  /**
   * Verify a single email address in real time.
   * @param {string} email
   * @returns {Promise<{result: string, reason: string, disposable: string, accept_all: string,
   *   role: string, free: string, email: string, user: string, domain: string, mx_record: string,
   *   mx_domain: string, safe_to_send: string, did_you_mean: string, success: string, message: string,
   *   remainingCredits: number|null}>}
   */
  async verifyEmail(email) {
    const url = new URL(`${this.baseUrl}/verify`);
    url.searchParams.set("email", email);
    url.searchParams.set("apikey", this.apiKey);

    const res = await fetch(url);
    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;
    const remainingCreditsHeader = res.headers.get("x-qev-remaining-credits");

    if (!res.ok || data?.success === "false") {
      throw new QuickEmailVerificationError(
        `QuickEmailVerification GET /verify failed: ${res.status} ${res.statusText}`,
        { status: res.status, body: data ?? text, url: url.toString() }
      );
    }

    return {
      ...data,
      remainingCredits: remainingCreditsHeader !== null ? Number(remainingCreditsHeader) : null,
    };
  }

  /**
   * Verify a batch of email addresses sequentially (the API has no native bulk-sync endpoint
   * for real-time verification; this simply loops `verifyEmail` with a small delay to be polite
   * to rate limits).
   * @param {string[]} emails
   * @param {object} [opts]
   * @param {number} [opts.delayMs=150] - delay between requests
   * @returns {Promise<Array<{email: string, ok: boolean, data?: object, error?: string}>>}
   */
  async verifyEmails(emails, { delayMs = 150 } = {}) {
    const results = [];
    for (const email of emails) {
      try {
        const data = await this.verifyEmail(email);
        results.push({ email, ok: true, data });
      } catch (err) {
        results.push({ email, ok: false, error: err.message });
      }
      if (delayMs) await new Promise((r) => setTimeout(r, delayMs));
    }
    return results;
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default QuickEmailVerificationClient;
