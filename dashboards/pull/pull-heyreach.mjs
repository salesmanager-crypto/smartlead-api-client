import fs from "node:fs";
import { HeyReachClient } from "../../src/heyreach.js";
for (const line of fs.readFileSync("../../.env","utf8").split("\n")) { const t=line.trim(); if(!t||t.startsWith("#")) continue; const eq=t.indexOf("="); if(eq===-1) continue; const k=t.slice(0,eq).trim(), v=t.slice(eq+1).trim(); if(!(k in process.env)) process.env[k]=v; }
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
    if (items.length < 100 || offset > 5000) break;
  }
  const count = (k) => leads.reduce((m, l) => { m[l[k] || "null"] = (m[l[k] || "null"] || 0) + 1; return m; }, {});
  out.leadsByCampaign[c.id] = { total: leads.length, byCampaignStatus: count("campaignStatus"), byConnection: count("connection"), byMessage: count("message"), bySender: count("sender"), leads };
}
fs.writeFileSync("./heyreach-pull.json", JSON.stringify(out));
const c = out.leadsByCampaign[out.campaigns[0].id];
console.log(JSON.stringify({ total: c.total, byCampaignStatus: c.byCampaignStatus, byConnection: c.byConnection, byMessage: c.byMessage, bySender: c.bySender, progress: out.campaigns[0].progressStats, status: out.campaigns[0].status }, null, 1));
