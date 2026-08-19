/**
 * Minimal, dependency-free client for the Premium Inboxes Client API.
 *
 * Docs: https://api.premiuminboxes.com/client/swagger
 *
 * Auth: `x-api-token` header on every request (opaque token, no Bearer/Basic prefix).
 * One token represents the whole agency; pass `workspaceId` per-call (or set a default
 * in the constructor) to scope an endpoint to one workspace via `x-workspace-id`.
 * Rate limit: 100 requests/minute per token (see `RateLimit-*` response headers).
 * Requires Node.js 18+ (uses the built-in `fetch`).
 *
 * ⚠️ SECURITY: the raw `/client/order` and `/client/subscription` payloads include each
 * mailbox's password in PLAINTEXT under `emails[].password`. `getOrders()` and
 * `getSubscriptions()` return that raw shape because some callers legitimately need it
 * (e.g. provisioning tooling) — but never log, print, persist, or forward those fields.
 * For any health/monitoring/reporting use case, use `listEmailAccounts()` instead, which
 * the API itself returns without a password field, or `getOrderSummaries()` /
 * `getSubscriptionSummaries()` below, which strip `password` (and the rest of the `emails`
 * array) before returning.
 */

const DEFAULT_BASE_URL = "https://api.premiuminboxes.com/api";

export class PremiumInboxesError extends Error {
  constructor(message, { status, body, url } = {}) {
    super(message);
    this.name = "PremiumInboxesError";
    this.status = status;
    this.body = body;
    this.url = url;
  }
}

export class PremiumInboxesClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.apiToken] - defaults to process.env.PREMIUM_INBOXES_API_KEY
   * @param {string} [opts.baseUrl] - defaults to process.env.PREMIUM_INBOXES_BASE_URL or the public API
   * @param {string} [opts.workspaceId] - default `x-workspace-id` for calls that accept one
   */
  constructor({ apiToken, baseUrl, workspaceId } = {}) {
    this.apiToken = apiToken || process.env.PREMIUM_INBOXES_API_KEY;
    this.baseUrl = (baseUrl || process.env.PREMIUM_INBOXES_BASE_URL || DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.workspaceId = workspaceId;

    if (!this.apiToken) {
      throw new Error(
        "Missing Premium Inboxes API token. Set PREMIUM_INBOXES_API_KEY in your " +
          "environment/.env, or pass { apiToken } to `new PremiumInboxesClient()`."
      );
    }
  }

  async _request(method, path, { workspaceId, query = {}, body } = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    for (const [k, v] of Object.entries(query)) {
      if (v !== undefined && v !== null) url.searchParams.set(k, v);
    }

    const headers = { "x-api-token": this.apiToken, "Content-Type": "application/json" };
    const ws = workspaceId ?? this.workspaceId;
    if (ws) headers["x-workspace-id"] = ws;

    const res = await fetch(url, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    const text = await res.text();
    const data = text ? safeJsonParse(text) : null;

    if (!res.ok) {
      throw new PremiumInboxesError(`Premium Inboxes ${method} ${path} failed: ${res.status} ${res.statusText}`, {
        status: res.status,
        body: data ?? text,
        url: url.toString(),
      });
    }
    return data;
  }

  get(path, opts) {
    return this._request("GET", path, opts);
  }
  post(path, body, opts) {
    return this._request("POST", path, { ...opts, body });
  }
  put(path, body, opts) {
    return this._request("PUT", path, { ...opts, body });
  }

  // ---- Workspaces -----------------------------------------------------------

  listWorkspaces() {
    return this.get("/client/workspaces");
  }
  createWorkspace(body) {
    return this.post("/client/workspaces", body);
  }
  getWorkspace(workspaceId) {
    return this.get(`/client/workspaces/${workspaceId}`);
  }

  // ---- Subscriptions ----------------------------------------------------------
  // ⚠️ raw shape includes plaintext mailbox passwords nested under orders[].emails[].password.

  getSubscriptions({ workspaceId } = {}) {
    return this.get("/client/subscription", { workspaceId });
  }
  getSubscription(subscriptionId) {
    return this.get(`/client/subscription/${subscriptionId}`);
  }
  cancelSubscription(subscriptionId, { reason, removeImmediately } = {}) {
    return this.put(`/client/subscription/cancel/${subscriptionId}`, { reason, removeImmediately });
  }
  reactivateSubscription(subscriptionId) {
    return this.put(`/client/subscription/reactivate/${subscriptionId}`, {});
  }

  /** Subscription billing/status info only — no order or mailbox detail, nothing sensitive. */
  async getSubscriptionSummaries({ workspaceId } = {}) {
    const { data } = await this.getSubscriptions({ workspaceId });
    return data.map((s) => ({
      id: s._id,
      status: s.status,
      lastBillingDate: s.lastBillingDate,
      nextBillingDate: s.nextBillingDate,
      price: s.price,
      discount: s.discount,
      cancelled: s.cancelled ?? null,
      orderIds: (s.orders || []).map((o) => o._id ?? o),
    }));
  }

  // ---- Orders -----------------------------------------------------------------
  // ⚠️ raw shape includes plaintext mailbox passwords under emails[].password.

  getOrders({ workspaceId } = {}) {
    return this.get("/client/order", { workspaceId });
  }
  getOrder(orderId) {
    return this.get(`/client/order/${orderId}`);
  }
  createPurchase(body, { workspaceId } = {}) {
    return this.post("/client/purchase", body, { workspaceId });
  }

  /** Order/provisioning metadata only — domains, inbox counts, status — no `emails[].password`. */
  async getOrderSummaries({ workspaceId } = {}) {
    const { data } = await this.getOrders({ workspaceId });
    return data.map((o) => ({
      id: o._id,
      createdAt: o.createdAt,
      updatedAt: o.updatedAt,
      status: o.status,
      domains: o.domains,
      emailProvider: o.emailProvider,
      inboxes: o.inboxes,
      forwardedDomain: o.forwardedDomain,
      emailCount: (o.emails || []).length,
      subscriptionStatus: o.subscriptionStatus,
    }));
  }

  // ---- Email accounts -----------------------------------------------------------
  // Safe by construction: the API itself does not return a password field here.

  listEmailAccounts({ workspaceId } = {}) {
    return this.get("/client/email-account", { workspaceId });
  }
  cancelEmails(emails, { workspaceId } = {}) {
    return this.post("/client/email-account/cancel", { emails }, { workspaceId });
  }
}

function safeJsonParse(text) {
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

export default PremiumInboxesClient;
