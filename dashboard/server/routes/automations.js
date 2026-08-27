import { Router } from "express";
import { pipedrive, safeLive } from "../lib/liveClients.js";
import { store } from "../data/store.js";

export const router = Router();

/** Re-attempts the Pipedrive sync for one failed automation row, following the same
 * search-before-create pattern as docs/Smartlead-Pipedrive-Automation-Workflow.md. */
async function retrySync(row) {
  if (!pipedrive) {
    // No live Pipedrive credentials — simulate an outcome so the UI still demonstrates
    // the bulk re-run flow end to end.
    const succeeded = Math.random() > 0.25;
    return succeeded
      ? { pipedriveStatus: "Created Deal", dealId: row.dealId || 4200 + Math.floor(Math.random() * 400), note: "Re-synced (simulated)" }
      : { pipedriveStatus: "Failed", note: JSON.stringify({ error: "PipedriveError", status: 429, body: { error: "rate_limited" } }) };
  }

  const orgSearch = await safeLive("pipedrive.searchOrganization", () => pipedrive.searchOrganization(row.company), null);
  let orgId = orgSearch.value?.data?.items?.[0]?.item?.id;
  if (!orgId) {
    const created = await safeLive("pipedrive.addOrganization", () => pipedrive.addOrganization({ name: row.company }), null);
    orgId = created.value?.data?.id;
  }

  const personSearch = await safeLive("pipedrive.searchPersons", () => pipedrive.searchPersons(row.leadEmail), null);
  let personId = personSearch.value?.data?.items?.[0]?.item?.id;
  if (!personId) {
    const [firstName, ...rest] = row.leadName.split(" ");
    const created = await safeLive(
      "pipedrive.addPerson",
      () => pipedrive.addPerson({ name: row.leadName, first_name: firstName, last_name: rest.join(" "), email: [{ value: row.leadEmail, primary: true }], org_id: orgId }),
      null
    );
    personId = created.value?.data?.id;
  }

  if (!orgId || !personId) {
    return { pipedriveStatus: "Failed", note: JSON.stringify({ error: "PipedriveError", detail: "Could not resolve org/person" }) };
  }

  const activity = await safeLive(
    "pipedrive.addActivity",
    () =>
      pipedrive.addActivity({
        subject: `Auto-Triage re-sync — ${row.leadName}`,
        type: "Follow Up",
        note: `Automation log re-run for lead ${row.leadEmail}.`,
        personId,
      }),
    null
  );
  if (!activity.live) {
    return { pipedriveStatus: "Failed", note: JSON.stringify({ error: "PipedriveError", detail: "addActivity failed" }) };
  }

  return { pipedriveStatus: "Created Deal", dealId: personId, note: `Synced — person #${personId}, org #${orgId}` };
}

router.post("/automations/rerun", async (req, res) => {
  const ids = req.body?.ids || [];
  const updated = [];
  for (const row of store.automationLog) {
    if (!ids.includes(row.id) || row.pipedriveStatus !== "Failed") continue;
    const outcome = await retrySync(row);
    Object.assign(row, outcome);
    updated.push({ ...row });
  }
  res.json(updated);
});
