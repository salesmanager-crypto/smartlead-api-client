import { Router } from "express";
import { store } from "../data/store.js";

export const router = Router();

router.post("/alerts/:id/mute", (req, res) => {
  store.mutedAlerts.add(req.params.id);
  res.json({ ok: true });
});

router.post("/layout/reset", (_req, res) => {
  // Layout is persisted client-side (localStorage / user preference state per spec
  // section 1A) — the server has nothing to reset, this just acks the action.
  res.json({ ok: true });
});
