#!/usr/bin/env node
/**
 * Pipedrive -> pipedrive.json (committed encrypted). Needs PIPEDRIVE_API_TOKEN and
 * PIPEDRIVE_COMPANY_DOMAIN.
 *
 *   node scripts/pull/pipedrive.mjs
 *
 * Open activities split into overdue / due today / next 7 days, all deals with
 * stage, person/org/lead counts, the user id -> name map. Also leaves an
 * email -> person id index on ctx for the SmartLead sync check.
 */
import { PipedriveClient } from "../../src/pipedrive.js";
import { today as todayFn, daysBetween, num } from "./lib.mjs";
import { runStandalone, isMain } from "./write.mjs";

/** email (lowercased) -> Pipedrive person id */
export function emailIndex(persons) {
  const byEmail = new Map();
  for (const p of persons) {
    for (const e of p.emails || []) {
      const v = String(e.value || "").toLowerCase().trim();
      if (v && !byEmail.has(v)) byEmail.set(v, p.id);
    }
  }
  return byEmail;
}

export async function pull(env, ctx = {}) {
  const pd = new PipedriveClient({ apiToken: env.PIPEDRIVE_API_TOKEN, companyDomain: env.PIPEDRIVE_COMPANY_DOMAIN });
  const TODAY = todayFn();

  const [users, stages, deals, persons, orgs, activities, leads] = await Promise.all([
    pd.users(), pd.stages(), pd.deals(), pd.persons(), pd.organizations(), pd.openActivities(), pd.leads(),
  ]);

  const stageName = new Map(stages.map((s) => [s.id, s.name]));
  const personName = new Map(persons.map((p) => [p.id, p.name]));
  const orgName = new Map(orgs.map((o) => [o.id, o.name]));
  ctx.personByEmail = emailIndex(persons);

  const row = (a) => ({
    id: a.id,
    subject: a.subject,
    type: a.type,
    due: a.due_date,
    person: a.person_id ?? null,
    personName: a.person_id ? personName.get(a.person_id) ?? null : null,
    org: a.org_id ?? null,
    orgName: a.org_id ? orgName.get(a.org_id) ?? null : null,
    owner: a.owner_id ?? null,
  });
  const byDue = (x, y) => (x.due < y.due ? -1 : x.due > y.due ? 1 : x.id - y.id);
  const open = activities.filter((a) => !a.done && a.due_date);

  const overdue = open.filter((a) => a.due_date < TODAY).map((a) => ({ ...row(a), days: daysBetween(a.due_date, TODAY) })).sort(byDue);
  const dueToday = open.filter((a) => a.due_date === TODAY).map((a) => ({ ...row(a), inDays: 0 })).sort(byDue);
  const upcoming = open
    .filter((a) => a.due_date > TODAY && daysBetween(TODAY, a.due_date) <= 7)
    .map((a) => ({ ...row(a), inDays: daysBetween(TODAY, a.due_date) }))
    .sort(byDue);

  const dealRows = deals
    .map((d) => ({
      id: d.id,
      title: d.title,
      stage: stageName.get(d.stage_id) ?? null,
      status: d.status,
      value: num(d.value),
      added: (d.add_time || "").slice(0, 10),
      closed: d.close_time ? d.close_time.slice(0, 10) : null,
      owner: d.owner_id ?? d.creator_user_id ?? null,
    }))
    .sort((x, y) => (x.added < y.added ? -1 : x.added > y.added ? 1 : x.id - y.id));

  const openTypeCounts = {};
  for (const a of open) openTypeCounts[a.type] = (openTypeCounts[a.type] || 0) + 1;
  const leadsByOwner = {};
  for (const l of leads) leadsByOwner[String(l.owner_id)] = (leadsByOwner[String(l.owner_id)] || 0) + 1;

  const repNames = {};
  for (const u of users) if (u.active_flag) repNames[String(u.id)] = u.name;

  ctx.records = open.length;
  return {
    pulledAt: new Date().toISOString(),
    today: TODAY,
    overdue,
    dueToday,
    upcoming,
    deals: dealRows,
    meta: {
      openTotal: open.length,
      openTypeCounts,
      leadsByOwner,
      leadsTotal: leads.length,
      leadsUnseen: leads.filter((l) => l.was_seen === false).length,
      personsTotal: persons.length,
      orgsTotal: orgs.length,
    },
    repNames,
  };
}

if (isMain(import.meta.url)) await runStandalone("pipedrive", pull);
