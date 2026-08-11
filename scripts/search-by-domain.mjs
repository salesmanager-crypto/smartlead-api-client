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

// Domains to search for, passed as CLI args, e.g.:
//   node scripts/search-by-domain.mjs artofbeauty.com urb.shop mexicosfinestllc.com
const domains = process.argv.slice(2).map((d) => d.toLowerCase());
if (domains.length === 0) {
  console.error("Usage: node scripts/search-by-domain.mjs <domain1> [domain2] ...");
  process.exit(1);
}

const client = new SmartleadClient({});
const campaigns = await client.listCampaigns();
console.error(`Scanning ${campaigns.length} campaigns for domains: ${domains.join(", ")}`);

const CONCURRENCY = 8;
let idx = 0;
let done = 0;
const matches = [];
const errors = [];

async function worker() {
  while (idx < campaigns.length) {
    const c = campaigns[idx++];
    try {
      const csv = await client.exportCampaignLeads(c.id);
      const text = typeof csv === "string" ? csv : JSON.stringify(csv);
      const lines = text.split("\n");
      const header = lines[0] || "";
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i];
        if (!line.trim()) continue;
        const lower = line.toLowerCase();
        for (const d of domains) {
          if (lower.includes(d)) {
            matches.push({ campaignId: c.id, campaignName: c.name, campaignStatus: c.status, domain: d, row: line });
          }
        }
      }
    } catch (err) {
      errors.push({ campaignId: c.id, campaignName: c.name, error: err.message, status: err.status });
    } finally {
      done++;
      if (done % 25 === 0 || done === campaigns.length) {
        console.error(`  ${done}/${campaigns.length} campaigns scanned, ${matches.length} matches so far`);
      }
    }
  }
}

await Promise.all(Array.from({ length: CONCURRENCY }, worker));

console.log(JSON.stringify({ matches, errors, scanned: campaigns.length }, null, 2));
