import express from "express";
import cors from "cors";
import { router as snapshotRouter } from "./routes/snapshot.js";
import { router as automationsRouter } from "./routes/automations.js";
import { router as domainsRouter } from "./routes/domains.js";
import { router as messagesRouter } from "./routes/messages.js";
import { router as tasksRouter } from "./routes/tasks.js";
import { router as alertsRouter } from "./routes/alerts.js";
import { smartlead, heyreach, pipedrive } from "./lib/liveClients.js";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api", snapshotRouter);
app.use("/api", automationsRouter);
app.use("/api", domainsRouter);
app.use("/api", messagesRouter);
app.use("/api", tasksRouter);
app.use("/api", alertsRouter);

app.get("/api/health", (_req, res) => {
  res.json({
    ok: true,
    live: { smartlead: !!smartlead, heyreach: !!heyreach, pipedrive: !!pipedrive },
  });
});

const port = Number(process.env.DASHBOARD_PORT) || 5175;
app.listen(port, () => {
  console.log(`Growth Ops dashboard API listening on http://localhost:${port}`);
  console.log(
    `Live sources — Smartlead: ${smartlead ? "yes" : "no (mock)"}, HeyReach: ${heyreach ? "yes" : "no (mock)"}, Pipedrive: ${
      pipedrive ? "yes" : "no (mock)"
    }`
  );
});
