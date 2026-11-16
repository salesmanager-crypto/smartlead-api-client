// Creates the Natural Products Expo West campaign in Smartlead as a DRAFT with its three-email sequence.
// It never uploads leads, never attaches mailboxes and never starts the campaign: Yoni reviews first.
//
// Defaults to dry-run: prints the campaign and sequence it would create. Pass --create to create it.
//
// Usage:
//   node scripts/expowest-campaign-setup.mjs            # dry-run, prints the payloads
//   node scripts/expowest-campaign-setup.mjs --create   # creates the DRAFTED campaign and its sequence
//
// Copy (from pipeline/work/reviewed/expowest_smartlead_sequence.md): step 1 is the per-lead custom field
// {{email_body}} (each lead's reviewed email, already greeted by their own first name, signature included);
// steps 2 and 3 are replies in the same thread and use {{first_name}} and {{company_name}}.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { SmartleadClient } from "../src/client.js";

const projectRoot = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const envPath = path.join(projectRoot, ".env");
for (const line of (fs.existsSync(envPath) ? fs.readFileSync(envPath, "utf8") : "").split("\n")) {
  const t = line.trim();
  if (!t || t.startsWith("#")) continue;
  const eq = t.indexOf("=");
  if (eq === -1) continue;
  const k = t.slice(0, eq).trim();
  const v = t.slice(eq + 1).trim();
  if (!(k in process.env)) process.env[k] = v;
}

const NAME = "Natural Products Expo West: Amazon (Nov 2026) DRAFT";
const SIGN = "Best,<br>Yoni<br>Albert Scott<br>Full Service Amazon Agency";

const SEQUENCES = [
  {
    seq_number: 1,
    seq_delay_details: { delay_in_days: 0 },
    subject: "{{company_name}} on Amazon",
    email_body: "{{email_body}}",
  },
  {
    seq_number: 2,
    seq_delay_details: { delay_in_days: 3 },
    subject: "", // same thread
    email_body:
      "Hi {{first_name}},<br><br>" +
      "Following up on my note about {{company_name}} on Amazon. Two brands we work with show what a focused Amazon plan can do. " +
      "MouthWatchers grew from $40K to $1M a month on Amazon, driven by managing the whole channel and not advertising alone. " +
      "Atlas Olive Oils, a brand we met at Expo West, was selling a few hundred thousand dollars through resellers before launching its own seller account, " +
      "and it now sells over $30M a year on Amazon.<br><br>" +
      "We see a few opportunities for {{company_name}} that I'd like to walk you through, and brands are building their 2027 plans right now. " +
      "Would you be open to a short call to talk it through?<br><br>" +
      SIGN,
  },
  {
    seq_number: 3,
    seq_delay_details: { delay_in_days: 5 },
    subject: "", // same thread
    email_body:
      "Hi {{first_name}},<br><br>" +
      "Checking in one last time. This is the time of year brands set their strategy and goals for the next year, " +
      "and Amazon is part of that planning for many of them.<br><br>" +
      "I would welcome the chance to talk about where {{company_name}} wants to take its Amazon business in 2027 and how we could help. " +
      "Would a short call work for you?<br><br>" +
      SIGN,
  },
];

const create = process.argv.includes("--create");
console.log(`Campaign: ${NAME}`);
for (const s of SEQUENCES) {
  console.log(`\nStep ${s.seq_number} (wait ${s.seq_delay_details.delay_in_days} days) subject: ${s.subject || "(same thread)"}`);
  console.log(s.email_body.replace(/<br>/g, "\n"));
}

if (!create) {
  console.log("\nDry run: nothing created. Add --create to create the draft campaign.");
  process.exit(0);
}
if (!process.env.SMARTLEAD_API_KEY) {
  console.error("\nSMARTLEAD_API_KEY is not set (put it in .env or the environment). Nothing created.");
  process.exit(1);
}

const client = new SmartleadClient();
const existing = await client.listCampaigns();
const dup = (Array.isArray(existing) ? existing : existing?.campaigns || []).find((c) => c.name === NAME);
if (dup) {
  console.error(`\nA campaign named "${NAME}" already exists (id ${dup.id}, status ${dup.status}). Nothing created.`);
  process.exit(1);
}
const made = await client.createCampaign({ name: NAME });
const id = made.id ?? made.campaign_id;
console.log(`\nCreated campaign ${id} (status ${made.status || "DRAFTED"}).`);
await client.upsertCampaignSequences(id, { sequences: SEQUENCES });
console.log("Sequence saved. Leads not uploaded, no mailboxes attached, campaign not started.");
console.log("Next in Smartlead: attach sender mailboxes, set the schedule, preview three leads, send a test to Yoni.");
