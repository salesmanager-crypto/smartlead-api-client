import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

const envPath = path.join(projectRoot, ".env");
for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#")) continue;
  const eq = t.indexOf("=");
  if (eq === -1) continue;
  const k = t.slice(0, eq).trim();
  const v = t.slice(eq + 1).trim();
  if (!(k in process.env)) process.env[k] = v;
}

const FLAGGED_DOMAINS = new Set([
  "albertscottllc.com",
  "albertscottny.com",
  "albertscottco.com",
]);

const client = new SmartleadClient({});

const [accounts, campaigns] = await Promise.all([
  client.listEmailAccounts(),
  client.listCampaigns(),
]);

const flaggedAccounts = accounts.filter((a) => {
  const domain = (a.from_email || "").split("@")[1]?.toLowerCase();
  return FLAGGED_DOMAINS.has(domain);
});
const flaggedIds = new Set(flaggedAccounts.map((a) => a.id));

console.error(`Flagged inboxes (${flaggedAccounts.length}):`);
for (const a of flaggedAccounts) console.error(`  #${a.id}  ${a.from_email}`);

const active = campaigns.filter((c) => c.status === "ACTIVE");

const results = [];
for (const c of active) {
  try {
    const assigned = await client.listCampaignEmailAccounts(c.id);
    const list = Array.isArray(assigned) ? assigned : assigned?.data ?? [];
    const matches = list.filter((a) => flaggedIds.has(a.id ?? a.email_account_id));
    results.push({
      id: c.id,
      name: c.name,
      assignedCount: list.length,
      flaggedMatches: matches.map((m) => m.from_email ?? m.email ?? m.id),
    });
  } catch (err) {
    results.push({ id: c.id, name: c.name, error: err.message, body: err.body });
  }
}

console.log(JSON.stringify(results, null, 2));
