/**
 * Open-tracking domain auditing, shared by the standalone report
 * (`scripts/check-tracking-domains.mjs`) and the daily deliverability check.
 *
 * Smartlead flags a mailbox when its custom tracking domain "isn't verified yet, or
 * none set up at all", without distinguishing them, and the API exposes
 * `custom_tracking_domain` as a plain string with no verification state. So the only
 * way to tell a real fault from a stale flag is to check DNS and TLS directly.
 *
 * Two traps this exists to avoid:
 *
 *   - A parked domain carries a wildcard CNAME (Porkbun points `*` at
 *     uixie.porkbun.com), so every subdomain resolves and a naive lookup reports a
 *     tracking record that was never created. Resolution is compared against the
 *     tracking edge rather than merely succeeding.
 *   - A hostname can resolve correctly while its certificate doesn't cover it, which
 *     breaks open pixels over HTTPS without touching DNS. Both are checked.
 */

import tls from "node:tls";
import dns from "node:dns/promises";

export const TRACKING_EDGE = "open.sleadtrack.com";

/** Every sending inbox, paginated. The API caps a page at 100 and silently truncates. */
export async function listAllEmailAccounts(client) {
  const all = [];
  for (let offset = 0; ; offset += 100) {
    const batch = await client.listEmailAccounts({ offset, limit: 100 });
    if (!Array.isArray(batch) || batch.length === 0) break;
    all.push(...batch);
    if (batch.length < 100) break;
  }
  return all;
}

/** CNAME targets for a host, or null when it has no CNAME record. */
export async function cnameTarget(host) {
  try {
    return await dns.resolveCname(host);
  } catch {
    return null;
  }
}

export async function pointsAtEdge(host) {
  const targets = await cnameTarget(host);
  return Boolean(targets?.some((t) => t.toLowerCase() === TRACKING_EDGE));
}

/**
 * TLS handshake against a host. `ok` mirrors what a mail client sees, `covers` says
 * whether the certificate actually names this host rather than only its parent.
 */
export function checkCert(host, { timeout = 10000 } = {}) {
  return new Promise((resolve) => {
    const socket = tls.connect({ host, port: 443, servername: host, timeout }, () => {
      const cert = socket.getPeerCertificate();
      const names = String(cert.subjectaltname || "")
        .split(",")
        .map((n) => n.trim().replace(/^DNS:/, ""));
      resolve({ ok: socket.authorized, covers: names.includes(host), names });
      socket.destroy();
    });
    const fail = (reason) => {
      resolve({ ok: false, covers: false, error: reason });
      socket.destroy();
    };
    socket.on("error", (err) => fail(err.code || err.message));
    socket.on("timeout", () => fail("timeout"));
  });
}

/**
 * Classify every mailbox by the health of its tracking domain.
 *
 * Each distinct hostname is resolved once rather than once per mailbox, since three
 * inboxes on one sending domain share a single record.
 *
 * @returns {Promise<{missing: object[], broken: object[], healthy: object[], mixedCase: object[]}>}
 *   `broken` and `healthy` group accounts under `{host, accounts, problems}`.
 */
export async function auditTrackingDomains(accounts) {
  const missing = [];
  const configured = new Map();
  for (const account of accounts) {
    const host = (account.custom_tracking_domain || "").trim();
    if (!host) missing.push(account);
    else {
      const key = host.toLowerCase();
      if (!configured.has(key)) configured.set(key, []);
      configured.get(key).push(account);
    }
  }

  const broken = [];
  const healthy = [];
  for (const [host, users] of configured) {
    const targets = await cnameTarget(host);
    const problems = [];
    if (!targets) problems.push("no CNAME record");
    else if (!targets.some((t) => t.toLowerCase() === TRACKING_EDGE))
      problems.push(`CNAME points at ${targets.join(",")}, not ${TRACKING_EDGE}`);

    if (problems.length === 0) {
      const cert = await checkCert(host);
      if (cert.error) problems.push(`TLS handshake failed (${cert.error})`);
      else if (!cert.ok) problems.push("TLS certificate is not trusted");
      else if (!cert.covers) problems.push("TLS certificate does not cover this hostname");
    }
    (problems.length ? broken : healthy).push({ host, accounts: users, problems });
  }

  const mixedCase = accounts.filter(
    (a) =>
      (a.custom_tracking_domain || "").trim() &&
      a.custom_tracking_domain !== a.custom_tracking_domain.toLowerCase(),
  );

  return { missing, broken, healthy, mixedCase };
}

/** One-line alert strings for a scheduled check. Empty array means nothing is wrong. */
export function trackingDomainFlags({ missing, broken }) {
  const flags = [];
  for (const { host, accounts, problems } of broken)
    flags.push(`${host} (${accounts.length} mailboxes): ${problems.join("; ")}`);
  if (missing.length) {
    const domains = [...new Set(missing.map((a) => a.from_email.split("@")[1].toLowerCase()))];
    flags.push(
      `${missing.length} mailboxes have no tracking domain (${domains.join(", ")})`,
    );
  }
  return flags;
}
