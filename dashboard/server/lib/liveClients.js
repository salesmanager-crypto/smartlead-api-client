// Wires up the dashboard's live data sources from the real API clients that already
// live in ../../src/. Every client is optional — if its env vars aren't set, the
// corresponding export is `null` and routes fall back to the mock data layer.
// See dashboard/README.md for exactly which cards go live with which env var.
import dotenv from "dotenv";
import { fileURLToPath } from "node:url";
import path from "node:path";
import { SmartleadClient } from "../../../src/client.js";
import { HeyReachClient } from "../../../src/heyreach.js";
import { PipedriveClient } from "../../../src/pipedrive.js";

// The repo's .env lives at the repo root (one level above dashboard/), not inside
// dashboard/ itself — load it explicitly rather than relying on dotenv's cwd guess.
const __dirname = path.dirname(fileURLToPath(import.meta.url));
dotenv.config({ path: path.join(__dirname, "../../../.env") });

function tryInit(label, factory) {
  try {
    return factory();
  } catch (err) {
    console.info(`[dashboard] ${label} not configured (${err.message.split("\n")[0]}) — using mock data for it.`);
    return null;
  }
}

export const smartlead = tryInit("Smartlead", () => new SmartleadClient());
export const heyreach = tryInit("HeyReach", () => new HeyReachClient());
export const pipedrive = tryInit("Pipedrive", () => new PipedriveClient());

/** Runs `fn(...)`, returns its resolved value, or `fallback` (and logs once) on any failure. */
export async function safeLive(label, fn, fallback) {
  try {
    const result = await fn();
    return { value: result, live: true };
  } catch (err) {
    console.warn(`[dashboard] live call failed (${label}): ${err.message} — falling back to mock data.`);
    return { value: fallback, live: false };
  }
}
