// Duplicates a campaign's setup (sequences and variants, schedule, settings, sending inboxes) into a new
// DRAFTED campaign with no leads, so a cleaned lead list can be uploaded and launched as a fresh version.
// It never adds leads and never starts the new campaign.
//
// Defaults to dry-run: it prints what it would copy (including each step's body, so a duplicate
// greeting such as "Hi {{first_name}}," in front of a custom-field body is easy to spot). Pass --apply
// to create the copies.
//
// Usage:
//   node scripts/duplicate-campaign.mjs                          # dry-run, the LV and NACS 2026 campaigns
//   node scripts/duplicate-campaign.mjs --apply                  # create "LV 2026 - Eikko V2" and "NACS 2026 - Eikko V2"
//   node scripts/duplicate-campaign.mjs 4254132 --suffix " V3" --apply

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

// The two Oct 2026 trade-show campaigns paused after step 1 went out with an unfilled {{first_name}}.
const DEFAULT_CAMPAIGN_IDS = [
  4254132, // LV 2026 - Eikko
  4255122, // NACS 2026 - Eikko
];

const args = process.argv.slice(2);
const apply = args.includes("--apply");
const suffixAt = args.indexOf("--suffix");
const suffix = suffixAt >= 0 ? args[suffixAt + 1] : " V2";
const ids = args.filter((a, i) => /^\d+$/.test(a) && args[i - 1] !== "--suffix").map(Number);
const campaignIds = ids.length ? ids : DEFAULT_CAMPAIGN_IDS;

const client = new SmartleadClient();
const asList = (v) => (Array.isArray(v) ? v : v?.data ?? v?.sequences ?? v?.email_accounts ?? []);
const delayDays = (s) => s.seq_delay_details?.delay_in_days ?? s.seq_delay_details?.delayInDays ?? 0;
const preview = (html) => String(html ?? "").replace(/<br\s*\/?>/gi, " / ").replace(/<[^>]+>/g, "").slice(0, 160);

function schedulePayload(c) {
  const cron = c.scheduler_cron_value ?? {};
  return {
    timezone: cron.tz,
    days_of_the_week: cron.days,
    start_hour: cron.startHour,
    end_hour: cron.endHour,
    min_time_btw_emails: c.min_time_btwn_emails,
    max_new_leads_per_day: c.max_leads_per_day,
  };
}

function settingsPayload(c) {
  return {
    track_settings: c.track_settings,
    stop_lead_settings: c.stop_lead_settings,
    unsubscribe_text: c.unsubscribe_text,
    send_as_plain_text: c.send_as_plain_text,
    follow_up_percentage: c.follow_up_percentage,
    client_id: c.client_id,
    enable_ai_esp_matching: c.enable_ai_esp_matching,
  };
}

function sequencesPayload(steps) {
  return {
    sequences: steps
      .sort((a, b) => a.seq_number - b.seq_number)
      .map((s) => {
        const variants = asList(s.sequence_variants ?? s.seq_variants);
        const step = { seq_number: s.seq_number, seq_delay_details: { delay_in_days: delayDays(s) } };
        if (variants.length) {
          step.seq_variants = variants.map((v) => ({
            subject: v.subject ?? "",
            email_body: v.email_body ?? "",
            variant_label: v.variant_label,
            ...(v.variant_distribution_percentage != null && { variant_distribution_percentage: v.variant_distribution_percentage }),
          }));
        } else {
          step.subject = s.subject ?? "";
          step.email_body = s.email_body ?? "";
        }
        return step;
      }),
  };
}

for (const id of campaignIds) {
  const src = await client.getCampaign(id);
  const steps = asList(await client.getCampaignSequences(id));
  const accounts = asList(await client.listCampaignEmailAccounts(id));
  const name = `${src.name}${suffix}`;

  console.log(`\n${src.name} (${id}, ${src.status}) -> "${name}"`);
  console.log(`  schedule: ${JSON.stringify(schedulePayload(src))}`);
  console.log(`  settings: ${JSON.stringify(settingsPayload(src))}`);
  console.log(`  sending inboxes: ${accounts.length} (${accounts.map((a) => a.from_email ?? a.email ?? a.id).join(", ")})`);
  for (const s of sequencesPayload(steps).sequences) {
    const bodies = s.seq_variants ?? [{ subject: s.subject, email_body: s.email_body }];
    bodies.forEach((v, n) => {
      console.log(`  step ${s.seq_number}${bodies.length > 1 ? ` variant ${n + 1}` : ""} (day ${s.seq_delay_details.delay_in_days}): subject "${v.subject}"`);
      console.log(`    body: ${preview(v.email_body)}`);
      if (/\{\{\s*first_name\s*\}\}/i.test(v.email_body) && /\{\{\s*(email_body|Email_Body(_HTML)?)\s*\}\}/i.test(v.email_body)) {
        console.log("    WARNING: this step has a {{first_name}} greeting AND a custom-field body; the cleaned body already has the greeting.");
      }
    });
  }

  if (!apply) continue;
  const created = await client.createCampaign({ name, client_id: src.client_id });
  const newId = created.id ?? created.campaign_id ?? created.data?.id;
  if (!newId) throw new Error(`Could not read the new campaign id from ${JSON.stringify(created)}`);
  await client.upsertCampaignSequences(newId, sequencesPayload(steps));
  await client.setCampaignSchedule(newId, schedulePayload(src));
  await client.updateCampaignSettings(newId, settingsPayload(src));
  if (accounts.length) await client.addEmailAccountsToCampaign(newId, accounts.map((a) => a.id));
  console.log(`  created ${newId} (DRAFTED, no leads). Upload the leads, preview a few, then start it.`);
}

if (!apply) console.log("\nDry-run only. Re-run with --apply to create the copies.");
