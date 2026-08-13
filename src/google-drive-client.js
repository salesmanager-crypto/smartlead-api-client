/**
 * Minimal, dependency-free client for the Google Drive v3 API.
 *
 * Docs: https://developers.google.com/workspace/drive/api/reference/rest/v3
 *
 * Auth: OAuth2 refresh-token flow, scoped to `drive.file` (files this app creates/opens).
 * Run `node scripts/google-drive-auth.mjs` once to obtain a refresh token.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

const TOKEN_URL = "https://oauth2.googleapis.com/token";
const DRIVE_BASE = "https://www.googleapis.com/drive/v3";
const UPLOAD_BASE = "https://www.googleapis.com/upload/drive/v3/files";

export class GoogleDriveError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.name = "GoogleDriveError";
    this.status = status;
    this.body = body;
  }
}

export class GoogleDriveClient {
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

  async _getAccessToken() {
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
      throw new GoogleDriveError(`Failed to refresh Google access token: ${res.status}`, { status: res.status, body: data });
    }
    this._accessToken = data.access_token;
    this._accessTokenExpiry = Date.now() + data.expires_in * 1000;
    return this._accessToken;
  }

  async _request(method, url, { query, body, headers = {}, rawBody } = {}) {
    const token = await this._getAccessToken();
    const fullUrl = new URL(url);
    for (const [k, v] of Object.entries(query || {})) {
      if (v !== undefined && v !== null) fullUrl.searchParams.set(k, v);
    }

    const res = await fetch(fullUrl, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(rawBody === undefined && body !== undefined ? { "Content-Type": "application/json" } : {}),
        ...headers,
      },
      body: rawBody !== undefined ? rawBody : body !== undefined ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;

    if (!res.ok) {
      throw new GoogleDriveError(`Google Drive API ${method} ${fullUrl.pathname} failed: ${res.status}`, {
        status: res.status,
        body: data ?? text,
      });
    }
    return data;
  }

  /** List/search files. @param {string} [opts.query] - Drive query syntax, e.g. `name contains 'fancy-food'`. */
  listFiles({ query, pageSize = 50, pageToken, fields } = {}) {
    return this._request("GET", `${DRIVE_BASE}/files`, {
      query: {
        q: query,
        pageSize,
        pageToken,
        fields: fields || "files(id,name,mimeType,parents,webViewLink),nextPageToken",
      },
    });
  }

  getFile(fileId, { fields } = {}) {
    return this._request("GET", `${DRIVE_BASE}/files/${fileId}`, { query: { fields } });
  }

  /** Create a folder under an optional parent. */
  createFolder(name, parentId) {
    return this._request("POST", `${DRIVE_BASE}/files`, {
      body: { name, mimeType: "application/vnd.google-apps.folder", parents: parentId ? [parentId] : undefined },
      query: { fields: "id,name,parents,webViewLink" },
    });
  }

  /** Move a file by swapping its parent folder(s). */
  moveFile(fileId, { addParents, removeParents } = {}) {
    return this._request("PATCH", `${DRIVE_BASE}/files/${fileId}`, {
      query: { addParents, removeParents, fields: "id,name,parents" },
      body: {},
    });
  }

  /** Rename or update metadata on an existing file. */
  updateFile(fileId, metadata) {
    return this._request("PATCH", `${DRIVE_BASE}/files/${fileId}`, { body: metadata });
  }

  deleteFile(fileId) {
    return this._request("DELETE", `${DRIVE_BASE}/files/${fileId}`);
  }

  /**
   * Upload file content to Drive (multipart: metadata + media in one request).
   * @param {object} opts
   * @param {Buffer|string} opts.content - file bytes or text
   * @param {string} opts.name
   * @param {string} [opts.mimeType]
   * @param {string} [opts.folderId] - parent folder to create the file in
   */
  uploadFile({ content, name, mimeType = "text/csv", folderId }) {
    const boundary = `smartlead-drive-${Math.random().toString(16).slice(2)}`;
    const metadata = { name, parents: folderId ? [folderId] : undefined };
    const contentBuf = Buffer.isBuffer(content) ? content : Buffer.from(content, "utf8");

    const rawBody = Buffer.concat([
      Buffer.from(`--${boundary}\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n${JSON.stringify(metadata)}\r\n`, "utf8"),
      Buffer.from(`--${boundary}\r\nContent-Type: ${mimeType}\r\n\r\n`, "utf8"),
      contentBuf,
      Buffer.from(`\r\n--${boundary}--`, "utf8"),
    ]);

    return this._request("POST", UPLOAD_BASE, {
      query: { uploadType: "multipart", fields: "id,name,webViewLink,parents" },
      headers: { "Content-Type": `multipart/related; boundary=${boundary}` },
      rawBody,
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

export default GoogleDriveClient;
