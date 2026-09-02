#!/usr/bin/env node
// Pulls the HeyReach campaign list and every lead's status per campaign, writes
// dashboards/pull/out/heyreach-pull.json. Needs HEYREACH_API_KEY in the environment or .env.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { HeyReachClient } from "../../src/heyreach.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..", "..");
const outDir = path.join(here, "out");
fs.mkdirSync(outDir, { recursive: true });

const envPath = path.join(root, ".env");
if (fs.existsSync(envPath)) {
  for (const line of fs.readFileSync(envPath, "utf8").split("\n")) {
    const t = line.trim(); if (!t || t.startsWith("#")) continue;
    const eq = t.indexOf("="); if (eq === -1) continue;
    const k = t.slice(0, eq).trim(), v = t.slice(eq + 1).trim();
    if (!(k in process.env)) process.env[k] = v;
  }
}
if (!process.env.HEYREACH_API_KEY) { console.error("HEYREACH_API_KEY is not set"); process.exit(2); }

const hr = new HeyReachClient({});
const out = { pulledAt: new Date().toISOString(), errors: [] };
const list = await hr.listCampaigns({ offset: 0, limit: 100 });
out.campaigns = list.items || list;
out.leadsByCampaign = {};
for (const c of out.campaigns) {
  const leads = [];
  for (let offset = 0; ; offset += 100) {
    const r = await hr.getLeadsFromCampaign({ campaignId: c.id, offset, limit: 100 });
    const items = r.items || [];
    leads.push(...items.map((l) => ({ campaignStatus: l.leadCampaignStatus, connection: l.leadConnectionStatus, message: l.leadMessageStatus, lastAction: l.lastActionTime, created: l.creationTime, sender: l.linkedInSenderFullName })));
    if (items.length < 100 || offset > 20000) break;
  }
  const count = (k) => leads.reduce((m, l) => { m[l[k] || "null"] = (m[l[k] || "null"] || 0) + 1; return m; }, {});
  out.leadsByCampaign[c.id] = { total: leads.length, byCampaignStatus: count("campaignStatus"), byConnection: count("connection"), byMessage: count("message"), bySender: count("sender") };
}
const file = path.join(outDir, "heyreach-pull.json");
fs.writeFileSync(file, JSON.stringify(out));
console.error("heyreach: campaigns", out.campaigns.length, "written", file);
