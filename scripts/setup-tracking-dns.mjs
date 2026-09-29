// Creates the missing open-tracking CNAMEs at Porkbun. Dry run unless --apply.
//
//   node scripts/setup-tracking-dns.mjs                 # what's missing, and is the API able to fix it
//   node scripts/setup-tracking-dns.mjs --apply         # create the records
//   node scripts/setup-tracking-dns.mjs --prefix open   # default is trk
//
// Works out the domains that need a record by asking Smartlead which mailboxes have no
// tracking domain, so it never invents work: a sending domain only appears here if real
// inboxes are sending without tracking.
//
// Two Porkbun specifics decide whether this can run at all:
//
//   1. Per-domain API access is an account setting, off by default, and separate from
//      having an API key. Every DNS call on a domain without it fails. listDomains() is
//      account-level and reports the flag, so the preflight below names the domains to
//      switch on rather than failing one at a time mid-run.
//   2. Parked domains carry a wildcard CNAME (`*` -> uixie.porkbun.com), which makes
//      every subdomain resolve and hides that no real record exists. An explicit record
//      at `trk` takes precedence over the wildcard, so this adds one and leaves the
//      wildcard serving everything else. That is why existence is checked through
//      retrieveRecordsByNameType and not through a DNS lookup.
//
// Setting the Smartlead field is the other half: run fix-tracking-domains.mjs once these
// records have propagated.

import fs from "node:fs";
import path from "node:path";
import dnsPromises from "node:dns/promises";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";
import { PorkbunClient } from "../src/porkbun.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

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
const APPLY = process.argv.includes("--apply");
const prefixArg = process.argv.indexOf("--prefix");
const PREFIX = prefixArg === -1 ? "trk" : process.argv[prefixArg + 1];

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

async function main() {
  const smartlead = new SmartleadClient();
  const accounts = await listAllAccounts(smartlead);

  // Sending domains where every mailbox is missing a tracking domain.
  const bySendingDomain = new Map();
  for (const account of accounts) {
    const domain = account.from_email.split("@")[1].toLowerCase();
    if (!bySendingDomain.has(domain)) bySendingDomain.set(domain, []);
    bySendingDomain.get(domain).push(account);
  }
  const needsRecord = [...bySendingDomain.entries()]
    .filter(([, mailboxes]) => mailboxes.every((a) => !(a.custom_tracking_domain || "").trim()))
    .map(([domain, mailboxes]) => ({ domain, mailboxes: mailboxes.length }));

  if (needsRecord.length === 0) {
    console.log("Every sending domain already has a tracking domain on at least one mailbox.");
    return;
  }

  const porkbun = new PorkbunClient();
  const owned = await porkbun.listDomains();
  const byName = new Map(owned.map((d) => [d.domain.toLowerCase(), d]));

  const actionable = [];
  const notAtPorkbun = [];
  const needsApiAccess = [];
  for (const entry of needsRecord) {
    const record = byName.get(entry.domain);
    if (!record) notAtPorkbun.push(entry);
    // Porkbun reports this flag as the string "1"/"0" in places and a boolean in others.
    else if (record.apiAccess === "0" || record.apiAccess === 0 || record.apiAccess === false)
      needsApiAccess.push(entry);
    else actionable.push(entry);
  }

  if (notAtPorkbun.length) {
    console.log(`NOT AT PORKBUN - ${notAtPorkbun.length} domains, add the record at their own registrar:`);
    for (const e of notAtPorkbun) console.log(`  ${e.domain} (${e.mailboxes} mailboxes)`);
    console.log();
  }
  if (needsApiAccess.length) {
    console.log(`API ACCESS OFF - ${needsApiAccess.length} domains; switch it on in Porkbun (Domain Management > the domain > API Access), then re-run:`);
    for (const e of needsApiAccess) console.log(`  ${e.domain} (${e.mailboxes} mailboxes)`);
    console.log();
  }
  if (actionable.length === 0) {
    console.log("Nothing this script can act on yet.");
    process.exitCode = 1;
    return;
  }

  console.log(`${APPLY ? "APPLYING" : "DRY RUN"} - CNAME ${PREFIX}.<domain> -> ${TRACKING_EDGE} on ${actionable.length} domains:`);
  for (const { domain, mailboxes } of actionable) {
    const existing = await porkbun
      .retrieveRecordsByNameType(domain, "CNAME", PREFIX)
      .catch((err) => ({ error: err.message }));

    if (existing.error) {
      console.log(`  FAIL ${domain}: ${existing.error}`);
      continue;
    }
    if (existing.length) {
      const content = existing[0].content;
      const verdict = content.toLowerCase().replace(/\.$/, "") === TRACKING_EDGE ? "already correct" : `points at ${content}, edit needed`;
      console.log(`  SKIP ${domain}: ${PREFIX}.${domain} exists, ${verdict}`);
      continue;
    }
    if (!APPLY) {
      console.log(`  WOULD CREATE ${PREFIX}.${domain} (unblocks ${mailboxes} mailboxes)`);
      continue;
    }
    try {
      const id = await porkbun.createDnsRecord(domain, {
        name: PREFIX,
        type: "CNAME",
        content: TRACKING_EDGE,
        ttl: 600,
      });
      console.log(`  OK   ${PREFIX}.${domain} created (record ${id})`);
    } catch (err) {
      console.log(`  FAIL ${domain}: ${err.message}`);
    }
  }

  if (!APPLY) {
    console.log("\nRe-run with --apply to create these.");
    return;
  }

  // Porkbun's floor is a 600s TTL, but these names are new rather than cached, so they
  // usually answer within a minute. Report rather than wait: the Smartlead half can run
  // whenever, and check-tracking-domains.mjs re-checks propagation on demand.
  console.log("\nPropagation check:");
  for (const { domain } of actionable) {
    const host = `${PREFIX}.${domain}`;
    const targets = await dnsPromises.resolveCname(host).catch(() => null);
    const live = targets?.some((t) => t.toLowerCase() === TRACKING_EDGE);
    console.log(`  ${live ? "live   " : "pending"} ${host}${targets && !live ? ` (still ${targets.join(",")})` : ""}`);
  }
  console.log("\nOnce these read live, run: node scripts/fix-tracking-domains.mjs --apply");
}

main().catch((err) => {
  console.error(`Tracking DNS setup failed: ${err.message}`);
  process.exit(1);
});
