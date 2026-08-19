/**
 * Minimal, dependency-free client for the Fathom Public API.
 *
 * Docs: https://developers.fathom.ai
 *
 * Auth: `X-Api-Key` header on every request (a Bearer token is also accepted
 * per Fathom's docs, but this client standardizes on the API-key header).
 * Requires Node.js 18+ (uses the built-in `fetch`).
 *
 * ⚠️ SCOPE, BY EXPLICIT INSTRUCTION: this client only ever surfaces meetings
 * whose title contains "Albert Scott" in some spacing/hyphenation (Albertscott,
 * Albert-Scott, "Yoni -  Albertscott", etc.) — never any other meeting, even
 * though a single API key on this account can see recordings across unrelated
 * projects (confirmed empirically: the raw feed includes titles like "Penji -
 * Daily meeting" and "Yoni - Personal Task Work" alongside Albert Scott ones).
 *
 * This is enforced structurally, not just by convention:
 *   1. listAlbertScottMeetings() calls GET /meetings with NO include_summary /
 *      include_transcript / include_action_items flags — so the bulk listing
 *      call never pulls meeting content, only titles/ids, for anything.
 *   2. It filters by title client-side and returns ONLY matches (plus a count
 *      of how many non-matching meetings were skipped, for transparency).
 *   3. getMeetingContent() re-validates every title against the same regex
 *      before building its request, and throws rather than fetch content for
 *      a meeting whose cached title doesn't match — even if called directly
 *      with a recording id. It also uses Fathom's `recording_ids[]` filter so
 *      the content-fetching call itself is scoped server-side to only the
 *      confirmed Albert Scott recording ids, not the whole account's history.
 *
 * Known gap: a title has to actually contain some spacing/hyphenation of
 * "Albert Scott" to match. A misspelled title (seen in practice: "Yoni -
 * Alberscott", missing a letter) will NOT match and is silently excluded.
 * That's a deliberate trade-off — matching typos risks false positives on
 * completely unrelated meetings — but worth knowing about.
 */

const DEFAULT_BASE_URL = "https://api.fathom.ai/external/v1";

/** Matches "Albert Scott" / "AlbertScott" / "Albert-Scott" / "albertscott", case-insensitive. */
export const ALBERT_SCOTT_TITLE_RE = /albert\s*-?\s*scott/i;

export class FathomError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "FathomError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class FathomClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiKey] - defaults to process.env.FATHOM_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.FATHOM_BASE_URL or the public API
   */
  constructor({ apiKey, baseUrl } = {}) {
    this.apiKey = apiKey || process.env.FATHOM_API_KEY;
    this.baseUrl = (baseUrl || process.env.FATHOM_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");

    if (!this.apiKey) {
      throw new Error(
        "Missing Fathom API key. Set FATHOM_API_KEY in your environment/.env, or pass " +
          "{ apiKey } to `new FathomClient()`."
      );
    }
  }

  async _get(path, query = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [k, v] of Object.entries(query)) {
      if (v === undefined || v === null) continue;
      if (Array.isArray(v)) {
        for (const item of v) url.searchParams.append(`${k}[]`, item);
      } else {
        url.searchParams.set(k, v);
      }
    }
    const res = await fetch(url, { headers: { "X-Api-Key": this.apiKey, Accept: "application/json" } });
    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;
    if (!res.ok) {
      throw new FathomError(`Fathom GET ${path} failed: ${res.status} ${res.statusText}`, {
        status: res.status,
        body: data ?? text,
        url: url.toString(),
      });
    }
    return data;
  }

  /**
   * Lists meetings whose title matches "Albert Scott" (any spacing/hyphenation), newest first.
   * Never requests summary/transcript/action-item content — metadata only.
   * @param {object} [opts]
   * @param {string} [opts.createdAfter] - ISO 8601; only meetings created after this
   * @param {string} [opts.createdBefore] - ISO 8601; only meetings created before this
   * @param {number} [opts.maxPages=10] - safety cap on pagination
   * @returns {Promise<{matches: Array<object>, skippedCount: number, pagesRead: number}>}
   */
  async listAlbertScottMeetings({ createdAfter, createdBefore, maxPages = 10 } = {}) {
    const matches = [];
    let skippedCount = 0;
    let cursor;
    let pagesRead = 0;

    do {
      const page = await this._get("/meetings", {
        created_after: createdAfter,
        created_before: createdBefore,
        cursor,
        limit: 25,
      });
      pagesRead++;
      for (const m of page.items ?? []) {
        if (ALBERT_SCOTT_TITLE_RE.test(m.title || "")) {
          matches.push({
            recording_id: m.recording_id,
            title: m.title,
            url: m.url,
            created_at: m.created_at,
            recording_start_time: m.recording_start_time,
            recording_end_time: m.recording_end_time,
            recorded_by: m.recorded_by,
          });
        } else {
          skippedCount++;
        }
      }
      cursor = page.next_cursor;
    } while (cursor && pagesRead < maxPages);

    return { matches, skippedCount, pagesRead };
  }

  /**
   * Fetches summary + transcript + action items, but ONLY for meetings already
   * confirmed Albert-Scott-titled (re-validated here, not just trusted from the caller).
   *
   * ⚠️ VERIFIED BUG IN THE UPSTREAM API (2026-08-19): Fathom's `/meetings` endpoint
   * silently IGNORES the `recording_ids` filter whenever any `include_*` content flag
   * is set — it returns its normal unfiltered recent-meetings page instead, with
   * content attached for every item, `limit` included. Confirmed by direct test: a
   * single known `recording_ids: [X]` + `include_action_items: true` call returned 10
   * unrelated meetings, not the 1 requested. There is no server-side way to scope a
   * content-inclusive request to specific recordings on this API as it currently
   * behaves — do not trust `recording_ids` to do this again without re-testing.
   *
   * Because of that, this method has to do the filtering itself, in-process, on the
   * full (unfiltered) response — and it is written so that filtering happens before
   * the caller ever sees anything: only entries whose `recording_id` is in
   * `confirmedMeetings` are returned; everything else in the raw response is discarded
   * inside this function and never propagated, logged, or returned to the caller.
   * Callers must not `console.log`/print the raw response themselves for this reason —
   * always go through this method's return value, not `_get` directly, when the intent
   * is "content for specific meetings only."
   *
   * @param {Array<{recording_id: number, title: string}>} confirmedMeetings
   */
  async getMeetingContent(confirmedMeetings) {
    const ids = new Set(
      confirmedMeetings.filter((m) => ALBERT_SCOTT_TITLE_RE.test(m.title || "")).map((m) => m.recording_id)
    );
    if (ids.size === 0) return [];

    const page = await this._get("/meetings", {
      recording_ids: [...ids],
      include_summary: "true",
      include_transcript: "true",
      include_action_items: "true",
      limit: 50,
    });

    // Defense in depth: filter here even though the caller-facing contract already
    // promises this, in case the upstream bug above changes behavior in either direction.
    return (page.items ?? []).filter((item) => ids.has(item.recording_id));
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default FathomClient;
