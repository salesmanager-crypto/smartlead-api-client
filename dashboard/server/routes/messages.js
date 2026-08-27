import { Router } from "express";
import { smartlead, safeLive } from "../lib/liveClients.js";

export const router = Router();

// Inline Quick-Reply (spec section 6A). A real send needs a resolved Smartlead
// leadId for `replyToLeadThread(campaignId, payload)` — the automation log's mock
// rows don't carry one, so this simulates unless the caller supplies leadId
// explicitly (wire that up once the log is backed by real getMasterInboxReplies()
// data, which does carry it).
router.post("/messages/reply", async (req, res) => {
  const { channel, campaignId, leadId, message } = req.body || {};

  if (channel === "smartlead" && smartlead && leadId) {
    const { value, live } = await safeLive(
      "smartlead.replyToLeadThread",
      () => smartlead.replyToLeadThread(campaignId, { lead_id: leadId, email_body: message }),
      null
    );
    if (live) return res.json({ ok: true, sentAt: new Date().toISOString(), live: true, result: value });
  }

  res.json({ ok: true, sentAt: new Date().toISOString(), live: false, simulated: true });
});
