// The only supported way to put a custom-email lead file into a Smartlead campaign and launch it.
// Every step must pass before the next one runs; any failure stops the script with nothing launched.
//
//   1. File check: every row is a real, send-ready email. No merge tags or brackets anywhere, the
//      greeting is "Hi <this lead's first_name>," (or "Hi there," when the name is blank), it ends
//      "Best,<br>Yoni", paragraphs use <br>, no raw newlines, no typos (double possessive "Lola's'",
//      double punctuation, repeated words), the brand in company_name appears in the email, no
//      duplicate or invalid emails.
//   2. Campaign check: the campaign exists and is not ACTIVE; every step that sends the custom copy
//      contains only that custom field (a "Hi {{first_name}}," in front of it would greet twice);
//      every merge field the subjects or steps use is filled for every lead.
//   3. Source check (--source-campaign, for a relaunch): every lead is still uncontacted (STARTED)
//      in the original campaign, so nobody gets the same step twice.
//   4. Upload (--apply): batches of 100. ignore_duplicate_leads_in_other_campaign is false on purpose:
//      true means "skip leads that already exist in another campaign", which silently drops every
//      lead of a relaunch. The script stops if Smartlead skips, blocks or rejects any lead.
//   5. Read-back: every lead in the campaign is compared with the file (email, names, company_name and
//      the custom email text, character for character), with no extra or missing leads.
//   6. Launch (--launch, only after 1-5 pass): POST /campaigns/{id}/status START, then the status
//      must read ACTIVE.
//
// Usage:
//   node scripts/upload-verified-leads.mjs --campaign 4294007 --file LV_V2_upload.csv                  # checks 1-3 only
//   node scripts/upload-verified-leads.mjs --campaign 4294007 --file LV_V2_upload.csv --source-campaign 4254132 --apply
//   node scripts/upload-verified-leads.mjs --campaign 4294007 --file LV_V2_upload.csv --apply --launch
// Options: --body-field <name> (default Email_Body_HTML), --sign-off <html> (default "Best,<br>Yoni").

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

const args = process.argv.slice(2);
const opt = (name, dflt) => (args.includes(name) ? args[args.indexOf(name) + 1] : dflt);
const campaignId = Number(opt("--campaign"));
const file = opt("--file");
const sourceId = opt("--source-campaign") ? Number(opt("--source-campaign")) : null;
const bodyField = opt("--body-field", "Email_Body_HTML");
const signOff = opt("--sign-off", "Best,<br>Yoni");
const apply = args.includes("--apply");
const launch = args.includes("--launch");
if (!campaignId || !file) {
  console.error("Usage: node scripts/upload-verified-leads.mjs --campaign <id> --file <leads.csv> [--source-campaign <id>] [--apply] [--launch]");
  process.exit(2);
}
if (launch && !apply) {
  console.error("--launch needs --apply: a campaign is only launched in the same run that uploaded and read back its leads.");
  process.exit(2);
}

const STANDARD = new Set(["email", "first_name", "last_name", "company_name", "phone_number", "website", "location", "linkedin_profile", "company_url"]);
const TYPO = /'s'|(?<!\.)\.\.(?!\.)|,,| {2}|\s[,.]|\b(\w+) \1\b/i;
const EMAIL = /^[^@\s]+@[^@\s]+\.[a-z]{2,}$/i;

function parseCSV(text) {
  const rows = [];
  let row = [], f = "", q = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    if (q) {
      if (ch === '"') {
        if (text[i + 1] === '"') { f += '"'; i++; } else q = false;
      } else f += ch;
    } else if (ch === '"') q = true;
    else if (ch === ",") { row.push(f); f = ""; }
    else if (ch === "\n") { row.push(f); rows.push(row); row = []; f = ""; }
    else if (ch !== "\r") f += ch;
  }
  if (f || row.length) { row.push(f); rows.push(row); }
  const [header, ...data] = rows.filter((r) => r.length > 1 || r[0]);
  return data.map((r) => Object.fromEntries(header.map((h, i) => [h.trim(), r[i] ?? ""])));
}

const fails = [];
let uploaded = false;
const fail = (msg) => fails.push(msg);
function stopIfFailed(stage) {
  if (!fails.length) return console.log(`PASS ${stage}`);
  const done = uploaded ? "leads were uploaded but the campaign was NOT launched; fix or remove them" : "nothing was uploaded or launched";
  console.log(`FAIL ${stage}: ${fails.length} problem(s), ${done}.`);
  for (const f of fails.slice(0, 60)) console.log(`  - ${f}`);
  process.exit(1);
}

// 1. File check -----------------------------------------------------------------------------------
const leads = parseCSV(fs.readFileSync(file, "utf8"));
const cols = Object.keys(leads[0] ?? {});
for (const c of ["email", "first_name", "company_name", bodyField]) if (!cols.includes(c)) fail(`file has no "${c}" column`);
const seen = new Map();
leads.forEach((l, i) => {
  const at = `row ${i + 2} (${l.email})`;
  const body = l[bodyField] ?? "";
  const email = (l.email ?? "").trim().toLowerCase();
  if (!EMAIL.test(email)) fail(`${at}: invalid email`);
  if (seen.has(email)) fail(`${at}: duplicate of row ${seen.get(email)}`);
  seen.set(email, i + 2);
  for (const [k, v] of Object.entries(l)) if (/\{\{|\}\}|\{[a-z_]+\}|\[(first ?name|name|company)\]/i.test(v)) fail(`${at}: unfilled merge tag in ${k}`);
  const name = l.first_name.trim() || "there";
  if (!body.startsWith(`Hi ${name},<br><br>`)) fail(`${at}: greeting is not "Hi ${name},"`);
  if (!body.endsWith(`<br><br>${signOff}`)) fail(`${at}: does not end with "${signOff}"`);
  if (/[\r\n]/.test(body)) fail(`${at}: raw line break, use <br>`);
  const typo = body.replace(/<br>/g, "\n").match(TYPO);
  if (typo) fail(`${at}: typo "${typo[0]}"`);
  if (l.company_name && !body.toLowerCase().includes(l.company_name.toLowerCase())) fail(`${at}: company_name "${l.company_name}" is not in the email`);
  const words = body.replace(/<br>/g, " ").split(/\s+/).filter(Boolean).length;
  if (words < 40 || words > 140) fail(`${at}: ${words} words`);
});
console.log(`${file}: ${leads.length} leads`);
stopIfFailed("1 file check");

// 2. Campaign check -------------------------------------------------------------------------------
const client = new SmartleadClient();
const asList = (v) => (Array.isArray(v) ? v : v?.data ?? []);
const campaign = await client.getCampaign(campaignId);
console.log(`campaign ${campaignId} "${campaign.name}" is ${campaign.status}`);
if (campaign.status === "ACTIVE") fail("campaign is already ACTIVE; pause it before adding leads");
const steps = asList(await client.getCampaignSequences(campaignId));
if (!steps.length) fail("campaign has no sequence steps");
const texts = [];
for (const s of steps) {
  const variants = asList(s.sequence_variants);
  for (const v of variants.length ? variants : [s]) {
    texts.push(v.subject ?? "", v.email_body ?? "");
    const b = v.email_body ?? "";
    const usesBody = new RegExp(`\\{\\{\\s*${bodyField}\\s*\\}\\}`).test(b);
    if (usesBody && b.replace(/<[^>]+>/g, "").replace(new RegExp(`\\{\\{\\s*${bodyField}\\s*\\}\\}`), "").trim())
      fail(`step ${s.seq_number}: has text around {{${bodyField}}} (a second greeting or sign-off): "${b.slice(0, 80)}"`);
  }
}
if (!texts.some((t) => t.includes(`{{${bodyField}}}`))) fail(`no step sends {{${bodyField}}}`);
for (const tag of new Set(texts.join(" ").match(/\{\{\s*[\w.]+\s*\}\}/g) ?? [])) {
  const key = tag.replace(/[{}\s]/g, "");
  const missing = leads.filter((l) => !(l[key] ?? "").trim()).length;
  if (!cols.includes(key)) fail(`the campaign uses ${tag} but the file has no "${key}" column`);
  else if (missing) fail(`the campaign uses ${tag} but ${missing} lead(s) have it blank`);
}
stopIfFailed("2 campaign check");

// 3. Source check ---------------------------------------------------------------------------------
async function allLeads(id) {
  let out = [], offset = 0;
  for (;;) {
    const r = await client.listCampaignLeads(id, { offset, limit: 100 });
    const d = r.data ?? [];
    out = out.concat(d);
    offset += d.length;
    if (!d.length || offset >= Number(r.total_leads ?? 0)) return out;
  }
}
if (sourceId) {
  const src = new Map((await allLeads(sourceId)).map((x) => [x.lead.email.toLowerCase(), x.status]));
  for (const l of leads) {
    const st = src.get(l.email.trim().toLowerCase());
    if (st && st !== "STARTED") fail(`${l.email}: already ${st} in campaign ${sourceId}`);
  }
  stopIfFailed(`3 source check against campaign ${sourceId}`);
} else console.log("SKIP 3 source check (no --source-campaign)");

if (!apply) {
  console.log("Checks passed. Re-run with --apply to upload (and --launch to start after the read-back).");
  process.exit(0);
}

// 4. Upload ---------------------------------------------------------------------------------------
const toLead = (l) => {
  const lead = { custom_fields: {} };
  for (const [k, v] of Object.entries(l)) if (v !== "") (STANDARD.has(k) ? lead : lead.custom_fields)[k] = v;
  lead.email = l.email.trim();
  return lead;
};
for (let i = 0; i < leads.length; i += 100) {
  const batch = leads.slice(i, i + 100);
  const r = await client.addLeadsToCampaign(campaignId, batch.map(toLead), {
    settings: {
      ignore_global_block_list: false,
      ignore_unsubscribe_list: false,
      // false = add the lead even if it is in another campaign. true SKIPS those leads.
      ignore_duplicate_leads_in_other_campaign: false,
    },
  });
  console.log(`batch ${i / 100 + 1}: ${JSON.stringify(r)}`);
  if (Number(r.total_leads ?? 0) > 0) uploaded = true;
  if (r.upload_count !== batch.length) fail(`batch ${i / 100 + 1}: Smartlead took ${r.upload_count} of ${batch.length}`);
  for (const k of ["skipped_in_other_campaign_count", "block_count", "duplicate_count", "invalid_email_count", "bounce_count", "lead_import_stopped_count"])
    if (Number(r[k] ?? 0) > 0) fail(`batch ${i / 100 + 1}: ${k} = ${r[k]}`);
  if ((r.unsubscribed_leads ?? []).length) fail(`batch ${i / 100 + 1}: unsubscribed ${r.unsubscribed_leads.join(", ")}`);
}
stopIfFailed("4 upload");

// 5. Read-back ------------------------------------------------------------------------------------
const live = await allLeads(campaignId);
const byEmail = new Map(live.map((x) => [x.lead.email.toLowerCase(), x]));
if (live.length !== leads.length) fail(`campaign holds ${live.length} leads, file has ${leads.length}`);
for (const l of leads) {
  const x = byEmail.get(l.email.trim().toLowerCase());
  if (!x) { fail(`${l.email}: not in the campaign`); continue; }
  let cf = x.lead.custom_fields ?? {};
  if (typeof cf === "string") cf = JSON.parse(cf);
  for (const k of ["first_name", "last_name", "company_name"]) if ((x.lead[k] ?? "") !== (l[k] ?? "")) fail(`${l.email}: ${k} is "${x.lead[k]}", file has "${l[k]}"`);
  if (cf[bodyField] !== l[bodyField]) fail(`${l.email}: ${bodyField} in Smartlead differs from the file`);
  if (x.lead.is_unsubscribed) fail(`${l.email}: unsubscribed`);
}
stopIfFailed(`5 read-back of ${live.length} leads`);

// 6. Launch ---------------------------------------------------------------------------------------
if (!launch) {
  console.log("Leads uploaded and verified. Preview a few, then re-run the start with: node src/cli.js campaigns:start " + campaignId);
  process.exit(0);
}
await client.startCampaign(campaignId);
const after = await client.getCampaign(campaignId);
if (after.status !== "ACTIVE") fail(`status after start is ${after.status}`);
stopIfFailed(`6 launch (status ${after.status})`);
