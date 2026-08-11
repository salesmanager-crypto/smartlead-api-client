import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));

// minimal .env loader (mirrors src/cli.js)
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

const client = new SmartleadClient({});
const campaigns = await client.listCampaigns();
const active = campaigns.filter((c) => c.status === "ACTIVE");

const results = [];
for (const c of active) {
  try {
    const analytics = await client.getCampaignAnalytics(c.id);
    results.push({ id: c.id, name: c.name, analytics });
  } catch (err) {
    results.push({ id: c.id, name: c.name, error: err.message, body: err.body });
  }
}
console.log(JSON.stringify(results, null, 2));
