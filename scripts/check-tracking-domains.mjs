// Audits the custom tracking domain (open-tracking CNAME) behind every Smartlead inbox.
//
// Smartlead's UI flags a mailbox with a "CNAME issue" but doesn't say which half is
// broken, and the API exposes `custom_tracking_domain` as a plain string with no
// verification state. So this checks the three things that can actually be wrong:
//
//   1. no tracking domain set on the mailbox at all
//   2. the hostname doesn't CNAME to Smartlead's tracking edge
//   3. it does, but the TLS cert doesn't cover it (open pixels fail on HTTPS)
//
// For mailboxes with nothing set, it also probes the usual prefixes on the sending
// domain so you can tell "DNS is ready, just fill in the field" from "DNS first".
// Watch for registrar wildcards (Porkbun parks *.domain at uixie.porkbun.com): every
// prefix appears to resolve, but to the parking host, not the tracking edge.

import fs from "node:fs";
import path from "node:path";
import tls from "node:tls";
import dns from "node:dns/promises";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

// minimal .env loader (mirrors src/cli.js); no-op when the vars are already in the env
const envPath = path.join(projectRoot, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim();
    if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("=");
    if (eq === -1) continue;
    const k = t.slice(0, eq).trim();
    if (!(k in process.env)) process.env[k] = t.slice(eq + 1).trim();
  }
}

const TRACKING_EDGE = "open.sleadtrack.com";
const COMMON_PREFIXES = ["trk", "open", "hello", "track", "go", "link"];

async function listAllAccounts(client) {
  const all = [];
  for (let offset = 0; ; offset += 100) {
    const batch = await client.listEmailAccounts({ offset, limit: 100 });
    if (!Array.isArray(batch) || batch.length === 0) break;
    all.push(...batch);
    if (batch.length < 100) break;
  }
  return all;
}

async function cnameTarget(host) {
  try {
    return await dns.resolveCname(host);
  } catch {
    return null;
  }
}

/** Resolves once the handshake completes; `authorized` is what a mail client sees. */
function checkCert(host) {
  return new Promise((resolve) => {
    const socket = tls.connect({ host, port: 443, servername: host, timeout: 10000 }, () => {
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

/** Which of the usual prefixes on `domain` already point at the tracking edge. */
async function probeSendingDomain(domain) {
  const ready = [];
  const parked = [];
  for (const prefix of COMMON_PREFIXES) {
    const targets = await cnameTarget(`${prefix}.${domain}`);
    if (!targets) continue;
    if (targets.some((t) => t.toLowerCase() === TRACKING_EDGE)) ready.push(`${prefix}.${domain}`);
    else parked.push(`${prefix}.${domain} -> ${targets.join(",")}`);
  }
  return { ready, parked };
}

async function main() {
  const client = new SmartleadClient();
  const accounts = await listAllAccounts(client);

  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "es"}`;

  const missing = [];
  const configured = new Map(); // tracking host -> accounts using it
  for (const account of accounts) {
    const host = (account.custom_tracking_domain || "").trim();
    if (!host) missing.push(account);
    else {
      const key = host.toLowerCase();
      if (!configured.has(key)) configured.set(key, []);
      configured.get(key).push(account);
    }
  }

  // 2 + 3: every distinct tracking host is checked once, not once per mailbox.
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
    (problems.length ? broken : healthy).push({ host, users, problems });
  }

  const mixedCase = [...configured.entries()].flatMap(([, users]) =>
    users.filter((a) => a.custom_tracking_domain !== a.custom_tracking_domain.toLowerCase()),
  );

  console.log(`${accounts.length} mailboxes: ${accounts.length - missing.length} with a tracking domain, ${missing.length} without.\n`);

  if (broken.length) {
    console.log(`BROKEN - ${broken.reduce((n, b) => n + b.users.length, 0)} mailboxes on ${broken.length} tracking domains:`);
    for (const { host, users, problems } of broken) {
      console.log(`  ${host} (${plural(users.length, "mailbox")}): ${problems.join("; ")}`);
      for (const a of users) console.log(`      ${a.from_email}`);
    }
    console.log();
  }

  if (missing.length) {
    // Group by sending domain: the DNS fix is per domain, not per mailbox.
    const bySendingDomain = new Map();
    for (const a of missing) {
      const domain = a.from_email.split("@")[1].toLowerCase();
      if (!bySendingDomain.has(domain)) bySendingDomain.set(domain, []);
      bySendingDomain.get(domain).push(a);
    }
    console.log(`NO TRACKING DOMAIN - ${missing.length} mailboxes across ${bySendingDomain.size} sending domains:`);
    for (const [domain, users] of bySendingDomain) {
      const { ready, parked } = await probeSendingDomain(domain);
      const verdict = ready.length
        ? `DNS ready - set ${ready[0]} in Smartlead`
        : parked.length
          ? `DNS needed - prefixes resolve to a parking/wildcard host (${parked[0]}), so a real CNAME must override it`
          : "DNS needed - no tracking CNAME exists yet";
      console.log(`  ${domain} (${plural(users.length, "mailbox")}): ${verdict}`);
      for (const a of users) console.log(`      ${a.from_email}`);
    }
    console.log();
  }

  if (mixedCase.length) {
    console.log(`MIXED CASE - hostname stored with capitals on ${plural(mixedCase.length, "mailbox")}; harmless for DNS, but normalise to avoid duplicate-looking entries:`);
    for (const a of mixedCase) console.log(`  ${a.from_email} -> ${a.custom_tracking_domain}`);
    console.log();
  }

  if (healthy.length) console.log(`HEALTHY - ${healthy.reduce((n, h) => n + h.users.length, 0)} mailboxes on ${healthy.length} tracking domains resolve to ${TRACKING_EDGE} with a valid certificate.`);

  const flagged = broken.reduce((n, b) => n + b.users.length, 0) + missing.length;
  console.log(`\n${flagged} mailboxes need attention.`);
  process.exitCode = flagged === 0 ? 0 : 1;
}

main().catch((err) => {
  console.error(`Tracking-domain check failed: ${err.message}`);
  process.exit(1);
});
