// Repairs the custom tracking domain on Smartlead inboxes. Dry run unless --apply.
//
//   node scripts/fix-tracking-domains.mjs                  # show what would change
//   node scripts/fix-tracking-domains.mjs --apply          # set missing / normalise case
//   node scripts/fix-tracking-domains.mjs --reverify --apply  # re-submit existing values
//
// Three repairs, all of which leave DNS alone:
//
//   missing   a mailbox with no tracking domain, where a sibling on the same sending
//             domain already has a working one (or DNS has a matching record). The
//             correct value is knowable, so fill it in.
//   case      a hostname stored with capitals. DNS doesn't care, but it makes one
//             domain look like two in every report.
//   reverify  re-submit a value that is already correct, to make Smartlead re-run a
//             verification that went stale. Confirmed working on 2026-09-17: a
//             re-submit on 10 stale mailboxes dropped the UI banner from 34 to 24,
//             so writing custom_tracking_url re-runs the check rather than only
//             storing the value. Nothing else has to happen for a mailbox to verify,
//             which is also why setting the field on a fresh mailbox needs no
//             follow-up click.
//
//             Requires --flagged, and the reason survives that result: Smartlead
//             exposes no verification state through the API, so the UI banner is the
//             only way to know which mailboxes are stale. Re-submitting blind would
//             write to every healthy mailbox, and a write that re-runs verification
//             can also fail it, so the blast radius must not default to everything.
//
// Mailboxes whose tracking domain does NOT resolve to the tracking edge are left
// alone: that is a DNS problem, and writing a Smartlead field would only hide it.
// Run check-tracking-domains.mjs first to see those.
//
// The update endpoint replaces the fields it receives, and the per-account GET omits
// minTimeToWaitInMins, so current values are read from the list endpoint and passed
// back unchanged. Reading them from the GET silently resets a mailbox's send delay.

import fs from "node:fs";
import path from "node:path";
import dns from "node:dns/promises";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

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
const COMMON_PREFIXES = ["trk", "open", "hello", "track", "go", "link"];
const APPLY = process.argv.includes("--apply");
const REVERIFY = process.argv.includes("--reverify");

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

async function pointsAtEdge(host) {
  try {
    const targets = await dns.resolveCname(host);
    return targets.some((t) => t.toLowerCase() === TRACKING_EDGE);
  } catch {
    return false;
  }
}

/** The tracking hostname a sending domain should use, or null if DNS isn't ready. */
async function resolveCorrectHost(sendingDomain, siblingHosts) {
  // Prefer what working siblings already use, so one domain never ends up split
  // across two tracking hostnames.
  for (const host of siblingHosts) if (await pointsAtEdge(host)) return host;
  for (const prefix of COMMON_PREFIXES) {
    const host = `${prefix}.${sendingDomain}`;
    if (await pointsAtEdge(host)) return host;
  }
  return null;
}

/** Writes custom_tracking_url while preserving every other field the endpoint replaces. */
async function setTrackingDomain(client, account, host) {
  return client.updateEmailAccount(account.id, {
    max_email_per_day: account.message_per_day,
    custom_tracking_url: host,
    bcc: account.bcc_email || "",
    signature: account.signature || "",
    client_id: account.client_id,
    time_to_wait_in_mins: account.minTimeToWaitInMins,
  });
}

async function main() {
  const flaggedInUi = loadFlagged();
  if (REVERIFY && !flaggedInUi)
    throw new Error(
      "--reverify needs --flagged <file> so it only touches mailboxes Smartlead actually " +
        "reports as unverified. Without it this would re-submit every healthy mailbox.",
    );
  const client = new SmartleadClient();
  const accounts = await listAllAccounts(client);

  const bySendingDomain = new Map();
  for (const account of accounts) {
    const domain = account.from_email.split("@")[1].toLowerCase();
    if (!bySendingDomain.has(domain)) bySendingDomain.set(domain, []);
    bySendingDomain.get(domain).push(account);
  }

  const planned = [];
  const blocked = [];
  for (const [domain, siblings] of bySendingDomain) {
    const hosts = [
      ...new Set(
        siblings.map((a) => (a.custom_tracking_domain || "").trim().toLowerCase()).filter(Boolean),
      ),
    ];
    const correct = hosts.length ? await resolveCorrectHost(domain, hosts) : null;

    for (const account of siblings) {
      const current = (account.custom_tracking_domain || "").trim();
      if (!current) {
        const host = correct || (await resolveCorrectHost(domain, []));
        if (host) planned.push({ account, host, reason: "missing" });
        else blocked.push({ account, reason: "no tracking CNAME exists for this domain yet" });
      } else if (current !== current.toLowerCase()) {
        if (await pointsAtEdge(current.toLowerCase()))
          planned.push({ account, host: current.toLowerCase(), reason: "case" });
        else blocked.push({ account, reason: `${current} does not resolve to ${TRACKING_EDGE}` });
      } else if (
        REVERIFY &&
        flaggedInUi.has(account.from_email.toLowerCase()) &&
        (await pointsAtEdge(current))
      ) {
        planned.push({ account, host: current, reason: "reverify" });
      }
    }
  }

  if (blocked.length) {
    console.log(`SKIPPED - ${blocked.length} mailboxes need DNS work first, not a Smartlead field:`);
    for (const { account, reason } of blocked) console.log(`  ${account.from_email}: ${reason}`);
    console.log();
  }

  if (planned.length === 0) {
    console.log("Nothing to change.");
    return;
  }

  console.log(`${APPLY ? "APPLYING" : "DRY RUN"} - ${planned.length} updates:`);
  for (const { account, host, reason } of planned) {
    const from = (account.custom_tracking_domain || "").trim() || "(none)";
    console.log(`  [${reason}] ${account.from_email}: ${from} -> ${host}`);
  }

  if (!APPLY) {
    console.log("\nRe-run with --apply to write these.");
    return;
  }

  console.log();
  let ok = 0;
  for (const { account, host } of planned) {
    try {
      await setTrackingDomain(client, account, host);
      // Read back rather than trusting the response: the endpoint returns ok:true
      // even when it silently ignores a field.
      const fresh = await client.getEmailAccount(account.id);
      const got = (fresh.custom_tracking_domain || "").trim();
      if (got.toLowerCase() === host.toLowerCase()) {
        ok += 1;
        console.log(`  OK   ${account.from_email} -> ${got}`);
      } else {
        console.log(`  WARN ${account.from_email}: wrote ${host}, reads back as "${got}"`);
      }
    } catch (err) {
      console.log(`  FAIL ${account.from_email}: ${err.message}`);
    }
  }
  console.log(`\n${ok}/${planned.length} applied.`);
  if (REVERIFY)
    console.log("Smartlead exposes no verification state through the API, so confirm in the UI banner.");
}

main().catch((err) => {
  console.error(`Tracking-domain fix failed: ${err.message}`);
  process.exit(1);
});
