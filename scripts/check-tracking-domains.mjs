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
//
// Smartlead's own banner lumps a fourth case in with these: a domain that is set and
// resolves fine, but that Smartlead hasn't verified yet. That state lives only in their
// UI, so pass --flagged <file> (one email per line, pasted from the banner) to split
// their list against live DNS. Verification is tracked per mailbox, not per domain, so
// siblings sharing one healthy tracking domain can disagree; when a flagged mailbox sits
// on a domain this script calls healthy, the record is fine and only the Verify click
// in Smartlead is outstanding.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import {
  TRACKING_EDGE,
  auditTrackingDomains,
  cnameTarget,
  listAllEmailAccounts,
} from "../src/trackingdomains.js";

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

const COMMON_PREFIXES = ["trk", "open", "hello", "track", "go", "link"];

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

/** Emails pasted out of Smartlead's "Needs Attention" banner, one per line. */
function loadFlagged() {
  const i = process.argv.indexOf("--flagged");
  if (i === -1) return null;
  const file = process.argv[i + 1];
  if (!file) throw new Error("--flagged needs a file path");
  return new Set(
    fs
      .readFileSync(file, "utf8")
      .split("\n")
      .map((l) => l.trim().toLowerCase())
      .filter((l) => l && l.includes("@")),
  );
}

async function main() {
  const flaggedInUi = loadFlagged();
  const client = new SmartleadClient();
  const accounts = await listAllEmailAccounts(client);

  const plural = (n, word) => `${n} ${word}${n === 1 ? "" : "es"}`;

  const { missing, broken, healthy, mixedCase } = await auditTrackingDomains(accounts);

  console.log(`${accounts.length} mailboxes: ${accounts.length - missing.length} with a tracking domain, ${missing.length} without.\n`);

  if (broken.length) {
    console.log(`BROKEN - ${broken.reduce((n, b) => n + b.accounts.length, 0)} mailboxes on ${broken.length} tracking domains:`);
    for (const { host, accounts: users, problems } of broken) {
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

  if (flaggedInUi) {
    const byEmail = new Map(accounts.map((a) => [a.from_email.toLowerCase(), a]));
    const healthyHosts = new Set(healthy.map((h) => h.host));
    const unverified = [];
    const unset = [];
    const realFault = [];
    const unknown = [];
    for (const email of flaggedInUi) {
      const account = byEmail.get(email);
      if (!account) {
        unknown.push(email);
        continue;
      }
      const host = (account.custom_tracking_domain || "").trim().toLowerCase();
      if (!host) unset.push(account);
      else if (healthyHosts.has(host)) unverified.push(account);
      else realFault.push(account);
    }

    console.log(`SMARTLEAD'S LIST - ${plural(flaggedInUi.size, "mailbox")} flagged in the UI, split against live DNS:`);
    console.log(`  ${unset.length} with no tracking domain set (see above for the per-domain fix)`);
    console.log(`  ${realFault.length} with a tracking domain that genuinely fails DNS or TLS`);
    console.log(`  ${unverified.length} set and resolving correctly: nothing to fix in DNS, just hit Verify in Smartlead`);
    if (unknown.length) console.log(`  ${unknown.length} not found in the API (renamed or disconnected?): ${unknown.join(", ")}`);
    for (const a of unverified) console.log(`      ${a.from_email} -> ${a.custom_tracking_domain}`);
    console.log();
  }

  if (healthy.length) console.log(`HEALTHY - ${healthy.reduce((n, h) => n + h.accounts.length, 0)} mailboxes on ${healthy.length} tracking domains resolve to ${TRACKING_EDGE} with a valid certificate.`);

  const flagged = broken.reduce((n, b) => n + b.accounts.length, 0) + missing.length;
  console.log(`\n${plural(flagged, "mailbox")} need attention from this side.`);
  process.exitCode = flagged === 0 ? 0 : 1;
}

main().catch((err) => {
  console.error(`Tracking-domain check failed: ${err.message}`);
  process.exit(1);
});
