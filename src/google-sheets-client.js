/**
 * Minimal, dependency-free client for the Google Sheets v4 API.
 *
 * Docs: https://developers.google.com/workspace/sheets/api/reference/rest
 *
 * Auth: OAuth2 refresh-token flow (see src/google-auth.js), scoped to `spreadsheets`.
 * Run `node scripts/google-drive-auth.mjs` once to obtain a refresh token.
 * Requires Node.js 18+ (uses the built-in `fetch`).
 */

import { GoogleTokenProvider } from "./google-auth.js";

const SHEETS_BASE = "https://sheets.googleapis.com/v4/spreadsheets";

export class GoogleSheetsError extends Error {
  constructor(message, { status, body } = {}) {
    super(message);
    this.name = "GoogleSheetsError";
    this.status = status;
    this.body = body;
  }
}

export class GoogleSheetsClient {
  /**
   * @param {object} opts
   * @param {string} [opts.clientId] - defaults to process.env.GOOGLE_CLIENT_ID
   * @param {string} [opts.clientSecret] - defaults to process.env.GOOGLE_CLIENT_SECRET
   * @param {string} [opts.refreshToken] - defaults to process.env.GOOGLE_REFRESH_TOKEN
   */
  constructor({ clientId, clientSecret, refreshToken } = {}) {
    this._auth = new GoogleTokenProvider({ clientId, clientSecret, refreshToken });
  }

  async _request(method, url, { query, body } = {}) {
    const token = await this._auth.getAccessToken();
    const fullUrl = new URL(url);
    for (const [k, v] of Object.entries(query || {})) {
      if (v !== undefined && v !== null) fullUrl.searchParams.set(k, v);
    }

    const res = await fetch(fullUrl, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;

    if (!res.ok) {
      throw new GoogleSheetsError(`Google Sheets API ${method} ${fullUrl.pathname} failed: ${res.status}`, {
        status: res.status,
        body: data ?? text,
      });
    }
    return data;
  }

  /** Spreadsheet metadata, including all sheets/tabs (id, title, index). */
  getSpreadsheet(spreadsheetId, { fields } = {}) {
    return this._request("GET", `${SHEETS_BASE}/${spreadsheetId}`, { query: { fields } });
  }

  /** Create a brand-new spreadsheet. Returns the full spreadsheet resource (incl. spreadsheetId). */
  createSpreadsheet(title) {
    return this._request("POST", SHEETS_BASE, { body: { properties: { title } } });
  }

  /** Any batchUpdate request(s) not covered by a dedicated helper below. */
  batchUpdate(spreadsheetId, requests) {
    return this._request("POST", `${SHEETS_BASE}/${spreadsheetId}:batchUpdate`, { body: { requests } });
  }

  /** Create a new tab. Returns the created sheet's properties (incl. sheetId). */
  async addSheet(spreadsheetId, { title, index } = {}) {
    const res = await this.batchUpdate(spreadsheetId, [
      { addSheet: { properties: { title, index } } },
    ]);
    return res.replies[0].addSheet.properties;
  }

  /** Rename and/or reposition an existing tab. */
  updateSheetProperties(spreadsheetId, sheetId, properties) {
    return this.batchUpdate(spreadsheetId, [
      {
        updateSheetProperties: {
          properties: { sheetId, ...properties },
          fields: Object.keys(properties).join(","),
        },
      },
    ]);
  }

  /** Rename the spreadsheet itself (its file title, not a tab). */
  updateSpreadsheetProperties(spreadsheetId, properties) {
    return this.batchUpdate(spreadsheetId, [
      { updateSpreadsheetProperties: { properties, fields: Object.keys(properties).join(",") } },
    ]);
  }

  deleteSheet(spreadsheetId, sheetId) {
    return this.batchUpdate(spreadsheetId, [{ deleteSheet: { sheetId } }]);
  }

  /**
   * Copy a tab from one spreadsheet into another, as a new tab there.
   * Returns the new sheet's properties (in the destination spreadsheet).
   */
  copySheetTo(sourceSpreadsheetId, sheetId, destinationSpreadsheetId) {
    return this._request("POST", `${SHEETS_BASE}/${sourceSpreadsheetId}/sheets/${sheetId}:copyTo`, {
      body: { destinationSpreadsheetId },
    });
  }

  /** Read cell values for a range, e.g. `"Tab 2"` or `"Tab 2!A1:Z"`. */
  async getValues(spreadsheetId, range, { valueRenderOption } = {}) {
    const res = await this._request("GET", `${SHEETS_BASE}/${spreadsheetId}/values/${encodeURIComponent(range)}`, {
      query: { valueRenderOption },
    });
    return res.values || [];
  }

  /** Overwrite cell values for a range (auto-expands as needed). */
  updateValues(spreadsheetId, range, values, { valueInputOption = "RAW" } = {}) {
    return this._request("PUT", `${SHEETS_BASE}/${spreadsheetId}/values/${encodeURIComponent(range)}`, {
      query: { valueInputOption },
      body: { range, values },
    });
  }

  clearValues(spreadsheetId, range) {
    return this._request("POST", `${SHEETS_BASE}/${spreadsheetId}/values/${encodeURIComponent(range)}:clear`);
  }
}

/** Extract the spreadsheet ID out of a full Google Sheets URL, or pass an ID straight through. */
export function extractSpreadsheetId(urlOrId) {
  const match = urlOrId.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/);
  return match ? match[1] : urlOrId;
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default GoogleSheetsClient;
