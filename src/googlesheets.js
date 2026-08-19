/**
 * Minimal, dependency-free client for the Google Sheets API v4, authenticated as a
 * service account (JWT bearer flow — no OAuth consent screen, no refresh-token expiry).
 *
 * Docs: https://developers.google.com/workspace/sheets/api/guides/values
 *
 * Auth: signs a short-lived JWT with the service account's RSA private key (Node's
 * built-in `crypto`, RS256 — no external JWT library), exchanges it at Google's token
 * endpoint for an access token, then calls the Sheets API with that as a Bearer token.
 * Tokens are cached in-memory and refreshed automatically ~1 minute before expiry.
 *
 * Requires the target spreadsheet to be shared with the service account's `client_email`
 * as an Editor — the API key alone isn't enough, this is a normal Sheets permission.
 * Requires Node.js 18+ (uses the built-in `fetch` and `crypto`).
 */

import crypto from "node:crypto";

const TOKEN_URI = "https://oauth2.googleapis.com/token";
const SHEETS_BASE = "https://sheets.googleapis.com/v4/spreadsheets";
const SHEETS_SCOPE = "https://www.googleapis.com/auth/spreadsheets";

export class GoogleSheetsError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "GoogleSheetsError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class GoogleSheetsClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.clientEmail] - defaults to process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL
   * @param {string} [opts.privateKey] - defaults to process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY
   *   (stored in .env with literal `\n` sequences; unescaped to real newlines here)
   * @param {string} [opts.spreadsheetId] - defaults to process.env.GOOGLE_SHEETS_SPREADSHEET_ID
   */
  constructor({ clientEmail, privateKey, spreadsheetId } = {}) {
    this.clientEmail = clientEmail || process.env.GOOGLE_SERVICE_ACCOUNT_EMAIL;
    this.privateKey = (privateKey || process.env.GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY || "").replace(/\\n/g, "\n");
    this.spreadsheetId = spreadsheetId || process.env.GOOGLE_SHEETS_SPREADSHEET_ID;

    if (!this.clientEmail || !this.privateKey || !this.spreadsheetId) {
      throw new Error(
        "Missing Google Sheets credentials. Set GOOGLE_SERVICE_ACCOUNT_EMAIL, " +
          "GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY, and GOOGLE_SHEETS_SPREADSHEET_ID in your " +
          "environment/.env, or pass them to `new GoogleSheetsClient()`."
      );
    }
    this._accessToken = null;
    this._tokenExpiresAtMs = 0;
  }

  async _getAccessToken() {
    if (this._accessToken && Date.now() < this._tokenExpiresAtMs - 60_000) {
      return this._accessToken;
    }
    const nowSec = Math.floor(Date.now() / 1000);
    const header = { alg: "RS256", typ: "JWT" };
    const claims = {
      iss: this.clientEmail,
      scope: SHEETS_SCOPE,
      aud: TOKEN_URI,
      exp: nowSec + 3600,
      iat: nowSec,
    };
    const encode = (obj) => Buffer.from(JSON.stringify(obj)).toString("base64url");
    const unsigned = `${encode(header)}.${encode(claims)}`;
    const signature = crypto.createSign("RSA-SHA256").update(unsigned).sign(this.privateKey, "base64url");
    const jwt = `${unsigned}.${signature}`;

    const res = await fetch(TOKEN_URI, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer",
        assertion: jwt,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new GoogleSheetsError(`Google token exchange failed: ${data.error_description || data.error}`, {
        status: res.status,
        body: data,
        url: TOKEN_URI,
      });
    }
    this._accessToken = data.access_token;
    this._tokenExpiresAtMs = Date.now() + data.expires_in * 1000;
    return this._accessToken;
  }

  async _request(method, path, { query = {}, body } = {}) {
    const token = await this._getAccessToken();
    const url = new URL(`${SHEETS_BASE}/${this.spreadsheetId}${path}`);
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, v);
    }
    const res = await fetch(url, {
      method,
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;
    if (!res.ok) {
      throw new GoogleSheetsError(`Sheets ${method} ${path} failed: ${data?.error?.message ?? res.statusText}`, {
        status: res.status,
        body: data,
        url: url.toString(),
      });
    }
    return data;
  }

  /** Read a range, e.g. "Sheet1!A1:D5" or "Sheet1" for the whole sheet. */
  getValues(range) {
    return this._request("GET", `/values/${encodeURIComponent(range)}`);
  }

  /** Append one row after the last row of data in `range`'s sheet (e.g. "Sheet1!A:D"). */
  appendRow(range, rowValues) {
    return this._request("POST", `/values/${encodeURIComponent(range)}:append`, {
      query: { valueInputOption: "USER_ENTERED", insertDataOption: "INSERT_ROWS" },
      body: { values: [rowValues] },
    });
  }

  /** Overwrite an exact range, e.g. "Sheet1!C14" for one cell or "Sheet1!A14:D14" for a row. */
  updateRange(range, values) {
    return this._request("PUT", `/values/${encodeURIComponent(range)}`, {
      query: { valueInputOption: "USER_ENTERED" },
      body: { values },
    });
  }

  /** Clear all values in a range back to empty cells (not just empty strings). */
  clearRange(range) {
    return this._request("POST", `/values/${encodeURIComponent(range)}:clear`);
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default GoogleSheetsClient;
