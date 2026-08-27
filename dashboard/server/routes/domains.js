import { Router } from "express";
import { smartlead, safeLive } from "../lib/liveClients.js";
import { store } from "../data/store.js";

export const router = Router();

// "Cool Down" (spec section 6B) — pause a failing domain from active sends and route
// its inbox into warm-up mode. If the domain came from a live Smartlead inbox (it
// carries `emailAccountId`), this really calls setEmailAccountWarmup(); otherwise it
// mutates the local mock store so the toggle is still fully interactive.
router.post("/domains/:id/cooldown", async (req, res) => {
  const { id } = req.params;
  const { cooldown } = req.body || {};

  const mockDomain = store.domains.find((d) => d.id === id);
  const emailAccountId = mockDomain?.emailAccountId || (id.startsWith("live_") ? id.replace("live_", "") : null);

  if (smartlead && emailAccountId) {
    const { live } = await safeLive(
      "smartlead.setEmailAccountWarmup",
      () =>
        smartlead.setEmailAccountWarmup(emailAccountId, {
          warmup_enabled: cooldown,
          total_warmup_per_day: 35,
          daily_rampup: 2,
          reply_rate_percentage: 30,
        }),
      null
    );
    if (live) {
      return res.json({ id, status: cooldown ? "warming" : "active", coolingDown: cooldown, live: true });
    }
  }

  if (mockDomain) {
    mockDomain.status = cooldown ? "warming" : "active";
    mockDomain.coolingDown = cooldown;
    return res.json({ ...mockDomain });
  }

  res.status(404).json({ error: "Domain not found" });
});
