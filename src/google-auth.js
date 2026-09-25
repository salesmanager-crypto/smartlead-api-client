/**
 * Minimal Google service-account auth. No npm dependencies: signs its own JWT
 * with node:crypto and exchanges it at the token endpoint, the same way the
 * googleapis library does.
 *
 * Credentials come from GOOGLE_SERVICE_ACCOUNT_JSON, which holds the whole key
 * file as a single-line JSON string (that is how it is stored as a repo secret).
 *
 *   const auth = new GoogleAuth(["https://www.googleapis.com/auth/drive.readonly"]);
 *   const token = await auth.token();
 *
 * `subject` impersonates a Workspace user and only works if a super-admin has
 * granted this service account domain-wide delegation for the scopes asked for.
 * Drive and Sheets do not need it when the file is shared with the service
 * account directly; Gmail always does, because a service account has no mailbox.
 */
import crypto from "node:crypto";

const TOKEN_URI = "https://oauth2.googleapis.com/token";

function loadKey() {
  const raw = process.env.GOOGLE_SERVICE_ACCOUNT_JSON;
  if (!raw) {
    throw new Error(
      "GOOGLE_SERVICE_ACCOUNT_JSON is not set. Put the service account key JSON in that variable " +
      "(locally in a .env file, in CI as a repository secret). Never commit the key file itself."
    );
  }
  let key;
  try {
    key = JSON.parse(raw);
  } catch {
    throw new Error("GOOGLE_SERVICE_ACCOUNT_JSON is not valid JSON. Paste the whole key file, including the outer braces.");
  }
  if (key.type !== "service_account") {
    throw new Error(
      `Expected a service account key but got type "${key.type || "unknown"}". ` +
      "An OAuth client_secret file (the \"installed\"/desktop kind) will not work here: it needs a human to click through a browser consent screen, which a scheduled job cannot do."
    );
  }
  for (const f of ["client_email", "private_key"]) {
    if (!key[f]) throw new Error(`Service account key is missing "${f}".`);
  }
  return key;
}

const b64url = (buf) => Buffer.from(buf).toString("base64url");

export class GoogleAuth {
  /** @param {string[]} scopes @param {string} [subject] Workspace user to impersonate (needs domain-wide delegation) */
  constructor(scopes, subject) {
    this.scopes = scopes;
    this.subject = subject;
    this.key = loadKey();
    this.cached = null;
  }

  get clientEmail() { return this.key.client_email; }

  async token() {
    if (this.cached && this.cached.expires > Date.now() + 60_000) return this.cached.token;

    const now = Math.floor(Date.now() / 1000);
    const claim = {
      iss: this.key.client_email,
      scope: this.scopes.join(" "),
      aud: TOKEN_URI,
      iat: now,
      exp: now + 3600,
    };
    if (this.subject) claim.sub = this.subject;

    const unsigned = b64url(JSON.stringify({ alg: "RS256", typ: "JWT" })) + "." + b64url(JSON.stringify(claim));
    const signature = crypto.createSign("RSA-SHA256").update(unsigned).sign(this.key.private_key);
    const assertion = unsigned + "." + b64url(signature);

    const res = await fetch(TOKEN_URI, {
      method: "POST",
      headers: { "content-type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({ grant_type: "urn:ietf:params:oauth:grant-type:jwt-bearer", assertion }),
    });
    const body = await res.json().catch(() => ({}));

    if (!res.ok) {
      const detail = body.error_description || body.error || `HTTP ${res.status}`;
      if (this.subject && /unauthorized_client|invalid_grant/i.test(String(detail))) {
        throw new Error(
          `Google refused to let ${this.key.client_email} act as ${this.subject}: ${detail}\n` +
          "This almost always means domain-wide delegation is not set up yet. A Workspace super-admin has to go to\n" +
          "  admin.google.com > Security > Access and data control > API controls > Domain-wide delegation\n" +
          `and authorise client ID ${this.key.client_id || "(client_id from the key file)"} for exactly these scopes:\n  ${this.scopes.join("\n  ")}`
        );
      }
      throw new Error(`Google token request failed: ${detail}`);
    }

    this.cached = { token: body.access_token, expires: Date.now() + (body.expires_in || 3600) * 1000 };
    return this.cached.token;
  }

  /** Authenticated GET returning parsed JSON, with Google's error text surfaced intact. */
  async get(url, params) {
    const u = new URL(url);
    for (const [k, v] of Object.entries(params || {})) if (v != null) u.searchParams.set(k, v);
    const res = await fetch(u, { headers: { authorization: `Bearer ${await this.token()}` } });
    const body = await res.json().catch(() => ({}));
    if (!res.ok) {
      const msg = (body.error && (body.error.message || body.error)) || `HTTP ${res.status}`;
      const err = new Error(`${u.pathname}: ${msg}`);
      err.status = res.status;
      throw err;
    }
    return body;
  }
}
