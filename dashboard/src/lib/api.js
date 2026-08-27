// Single API surface used by the whole dashboard. Every function tries the real
// Express backend (dashboard/server/) first — which serves live Smartlead/HeyReach
// data plus Pipedrive when credentials are configured, mock data otherwise (see
// dashboard/README.md) — and transparently falls back to an in-browser mock layer
// if that server isn't running, so `npm run dev` alone still produces a working
// dashboard.
import * as fallback from "./localFallback.js";

async function call(path, options, fallbackFn, ...fallbackArgs) {
  try {
    const res = await fetch(`/api${path}`, {
      headers: { "Content-Type": "application/json" },
      ...options,
    });
    if (!res.ok) throw new Error(`API ${path} responded ${res.status}`);
    return await res.json();
  } catch (err) {
    if (import.meta.env.DEV) console.info(`[dashboard] /api${path} unavailable, using local fallback:`, err.message);
    return fallbackFn(...fallbackArgs);
  }
}

export const getSnapshot = () => call("/snapshot", undefined, fallback.getSnapshot);

export const reRunAutomations = (ids) =>
  call("/automations/rerun", { method: "POST", body: JSON.stringify({ ids }) }, fallback.reRunAutomations, ids);

export const setDomainCooldown = (domainId, cooldown) =>
  call(
    `/domains/${domainId}/cooldown`,
    { method: "POST", body: JSON.stringify({ cooldown }) },
    fallback.setDomainCooldown,
    domainId,
    cooldown
  );

export const sendQuickReply = (payload) =>
  call("/messages/reply", { method: "POST", body: JSON.stringify(payload) }, fallback.sendQuickReply, payload);

export const updateTask = (id, patch) =>
  call(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(patch) }, fallback.updateTask, id, patch);

export const createTask = (task) =>
  call("/tasks", { method: "POST", body: JSON.stringify(task) }, fallback.createTask, task);

export const muteAlert = (id) =>
  call(`/alerts/${id}/mute`, { method: "POST" }, fallback.muteAlert, id);

export const resetLayout = () => call("/layout/reset", { method: "POST" }, fallback.resetLayout);
