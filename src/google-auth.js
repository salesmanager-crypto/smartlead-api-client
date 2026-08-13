/**
 * Shared OAuth2 refresh-token flow for Google APIs (Drive, Sheets, ...).
 *
 * Run `node scripts/google-drive-auth.mjs` once to obtain a refresh token that
 * covers whatever scopes that script requests.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const TOKEN_URL = "https://oauth2.googleapis.com/token";

export class GoogleAuthError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.name = "GoogleAuthError";
    this.status = status;
    this.body = body;
  }
}

export class GoogleTokenProvider {
  /**
   * @param {object} opts
   * @param {string} [opts.clientId] - defaults to process.env.GOOGLE_CLIENT_ID
   * @param {string} [opts.clientSecret] - defaults to process.env.GOOGLE_CLIENT_SECRET
   * @param {string} [opts.refreshToken] - defaults to process.env.GOOGLE_REFRESH_TOKEN
   */
  constructor({ clientId, clientSecret, refreshToken } = {}) {
    this.clientId = clientId || process.env.GOOGLE_CLIENT_ID;
    this.clientSecret = clientSecret || process.env.GOOGLE_CLIENT_SECRET;
    this.refreshToken = refreshToken || process.env.GOOGLE_REFRESH_TOKEN;

    if (!this.clientId || !this.clientSecret || !this.refreshToken) {
      throw new Error(
        "Missing Google OAuth config. Set GOOGLE_CLIENT_ID / GOOGLE_CLIENT_SECRET / GOOGLE_REFRESH_TOKEN " +
          "in your environment/.env (run `node scripts/google-drive-auth.mjs` once to obtain a refresh token)."
      );
    }

    this._accessToken = null;
    this._accessTokenExpiry = 0;
  }

  async getAccessToken() {
    if (this._accessToken && Date.now() < this._accessTokenExpiry - 30_000) {
      return this._accessToken;
    }
    const res = await fetch(TOKEN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        grant_type: "refresh_token",
        refresh_token: this.refreshToken,
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      throw new GoogleAuthError(`Failed to refresh Google access token: ${res.status}`, { status: res.status, body: data });
    }
    this._accessToken = data.access_token;
    this._accessTokenExpiry = Date.now() + data.expires_in * 1000;
    return this._accessToken;
  }
}

export default GoogleTokenProvider;
