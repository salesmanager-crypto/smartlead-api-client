import fs from "node:fs";
import path from "node:path";
import { execFile } from "node:child_process";
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

const WATCHED_ACCOUNTS = [
  { id: 630339, email: "ylebovits@AlbertScottCo.com" },
  { id: 630338, email: "yoni.lebovits@AlbertScottCo.com" },
  { id: 630337, email: "yoni@AlbertScottCo.com" },
  { id: 481772, email: "yoni@AlbertScottLLC.com" },
  { id: 481763, email: "yoni.lebovits@albertscottny.com" },
  { id: 481762, email: "yoni@albertscottny.com" },
  { id: 481758, email: "ylebovits@albertscottny.com" },
  { id: 481756, email: "ylebovits@AlbertScottLLC.com" },
  { id: 481754, email: "Yoni.Lebovits@AlbertScottLLC.com" },
];

const WEEKLY_SPAM_SAVE_THRESHOLD = 4; // worst historical week was 4
const DAY_OVER_DAY_DRIFT_THRESHOLD = 2; // lifetime spam count jump since last check

const STATE_PATH = path.join(projectRoot, "scripts", ".deliverability-state.json");
const LOG_PATH = path.join(projectRoot, "scripts", "deliverability-log.txt");

function loadState() {
  try {
    return JSON.parse(fs.readFileSync(STATE_PATH, "utf8"));
  } catch {
    return {};
  }
}
function saveState(state) {
  fs.writeFileSync(STATE_PATH, JSON.stringify(state, null, 2));
}
function log(line) {
  fs.appendFileSync(LOG_PATH, `[${new Date().toISOString()}] ${line}\n`);
}
function notify(title, message) {
  execFile("osascript", ["-e", `display notification ${JSON.stringify(message)} with title ${JSON.stringify(title)} sound name "Basso"`]);
}

async function main() {
  const client = new SmartleadClient({});
  const prevState = loadState();
  const nextState = {};
  const flags = [];

  const allAccounts = await client.listEmailAccounts();
  const byId = new Map(allAccounts.map((a) => [a.id, a]));

  for (const target of WATCHED_ACCOUNTS) {
    const acct = byId.get(target.id);
    if (!acct) {
      flags.push(`${target.email}: MISSING from account list entirely`);
      continue;
    }
    if (!acct.is_smtp_success || !acct.is_imap_success) {
      flags.push(`${target.email}: connection failure (smtp_ok=${acct.is_smtp_success}, imap_ok=${acct.is_imap_success})`);
    }
    if (acct.warmup_details?.status !== "ACTIVE") {
      flags.push(`${target.email}: warmup status is ${acct.warmup_details?.status ?? "NONE"}, not ACTIVE`);
    }

    const lifetimeSpam = acct.warmup_details?.total_spam_count ?? 0;
    const prevLifetimeSpam = prevState[target.id]?.lifetimeSpam;
    const drift = prevLifetimeSpam !== undefined ? lifetimeSpam - prevLifetimeSpam : 0;
    if (drift > DAY_OVER_DAY_DRIFT_THRESHOLD) {
      flags.push(`${target.email}: lifetime spam count jumped +${drift} since last check (${prevLifetimeSpam} -> ${lifetimeSpam})`);
    }

    let weeklySpamSaves = 0;
    try {
      const stats = await client.getEmailAccountWarmupStats(target.id);
      weeklySpamSaves = (stats.stats_by_date || []).reduce((s, d) => s + (d.save_from_spam_count || 0), 0);
      if (weeklySpamSaves > WEEKLY_SPAM_SAVE_THRESHOLD) {
        flags.push(`${target.email}: ${weeklySpamSaves} spam-saves in the trailing week (threshold: ${WEEKLY_SPAM_SAVE_THRESHOLD})`);
      }
    } catch (err) {
      flags.push(`${target.email}: failed to fetch warmup-stats (${err.message})`);
    }

    nextState[target.id] = { email: target.email, lifetimeSpam, weeklySpamSaves, checkedAt: new Date().toISOString() };
  }

  saveState(nextState);

  if (flags.length === 0) {
    log(`All clear — 9/9 inboxes healthy.`);
    // Silent on success, per preference — no desktop notification when nothing's wrong.
  } else {
    const summary = flags.join(" | ");
    log(`FLAGGED: ${summary}`);
    notify("Smartlead deliverability alert", flags.length === 1 ? flags[0] : `${flags.length} inboxes flagged — check deliverability-log.txt`);
  }

  console.log(flags.length === 0 ? "All clear." : flags.join("\n"));
}

main().catch((err) => {
  log(`ERROR running check: ${err.message}`);
  notify("Smartlead check failed", err.message);
  process.exit(1);
});
