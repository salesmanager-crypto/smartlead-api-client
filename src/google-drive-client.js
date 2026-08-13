/**
 * Minimal, dependency-free client for the Google Drive v3 API.
 *
 * Docs: https://developers.google.com/workspace/drive/api/reference/rest/v3
 *
 * Auth: OAuth2 refresh-token flow (see src/google-auth.js), scoped to `drive.file`
 * (files this app creates/opens). Run `node scripts/google-drive-auth.mjs` once to
 * obtain a refresh token. Requires Node.js 18+ (uses the built-in `fetch`).
 */

import { GoogleTokenProvider } from "./google-auth.js";

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
    this._auth = new GoogleTokenProvider({ clientId, clientSecret, refreshToken });
  }

  async _request(method, url, { query, body, headers = {}, rawBody } = {}) {
    const token = await this._auth.getAccessToken();
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
   * Copy an existing file. Passing `mimeType: "application/vnd.google-apps.spreadsheet"`
   * against a source .xlsx converts it to a native Google Sheet in the same request —
   * handy since the Sheets API can only operate on native Sheets files, not raw .xlsx blobs.
   */
  copyFile(fileId, { name, mimeType, parents } = {}) {
    return this._request("POST", `${DRIVE_BASE}/files/${fileId}/copy`, {
      body: { name, mimeType, parents },
      query: { fields: "id,name,mimeType" },
    });
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
