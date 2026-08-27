# Growth Ops Command Center — Albert Scott CRM Live Dashboard

A single-pane dashboard over Albert Scott's outbound stack: Smartlead campaigns, the
Smartlead → Pipedrive automation (see [`../docs/Smartlead-Pipedrive-Automation-Workflow.md`](../docs/Smartlead-Pipedrive-Automation-Workflow.md)),
HeyReach LinkedIn outreach, sending-domain health, technical SEO, and a task board —
themed to Albert Scott's brand (charcoal/grey structure, hot magenta `#E51958` as the
one signal color, Montserrat).

## What's live vs. simulated

| Card / feature | Data source | Live when… |
| --- | --- | --- |
| Outbound Performance — Smartlead | `src/client.js` (`getAnalyticsOverview`) | `SMARTLEAD_API_KEY` is set |
| Outbound Performance — Heyreach | `src/heyreach.js` (`listCampaigns`) | `HEYREACH_API_KEY` is set |
| Domain Asset Ledger / infra counts | `src/client.js` (`getAllInboxHealth`) | `SMARTLEAD_API_KEY` is set |
| Domain "Cool Down" toggle | `src/client.js` (`setEmailAccountWarmup`) | domain came from a live inbox above |
| Pipedrive CRM Pipeline | `src/pipedrive.js` (`getDeals`, `getStages`) | `PIPEDRIVE_API_TOKEN` + `PIPEDRIVE_COMPANY_DOMAIN` are set |
| Automation Log — "Re-Run Failed" | `src/pipedrive.js` (search → create org/person/activity, per the workflow doc) | `PIPEDRIVE_API_TOKEN` is set (else simulated) |
| Automation Log rows, Tasks board | In-memory store seeded to look like the real workflow's category taxonomy and owner | Always — this is the dashboard's own data, not mirrored from an external log store |
| Technical SEO diagnostics (Core Web Vitals, broken links, crawl errors) | Mock | Not wired — natural next step is the Semrush Site Audit API |
| Quick-Reply send | `src/client.js` (`replyToLeadThread`) | Only if a real `leadId` is passed in; simulated otherwise (mock rows don't carry one) |

Every live call is wrapped so a missing key, a shape mismatch, or a failed request
falls back to realistic mock data instead of breaking the page — check the server
console for `[dashboard] …` log lines to see what's live vs. mock on each request.

## Setup

```bash
cd dashboard
npm install
```

Real data (optional) — from the repo root, copy `.env.example` to `.env` and fill in
whichever keys you have: `SMARTLEAD_API_KEY`, `HEYREACH_API_KEY`,
`PIPEDRIVE_API_TOKEN` + `PIPEDRIVE_COMPANY_DOMAIN`. Anything left unset just serves
mock data for that card.

## Run

```bash
npm run dev:all   # Vite dev server (5174) + Express API (5175), proxied together
```

Or run the pieces separately:

```bash
npm run server    # Express API on :5175 (or $DASHBOARD_PORT)
npm run dev        # Vite dev server on :5174, proxies /api -> :5175
```

The frontend also works with **no backend running at all** (`npm run dev` alone) — every
API call falls back to an in-browser mock layer (`src/lib/localFallback.js`) so the
dashboard is fully interactive as a static preview; it just won't persist across a
reload and can't reach real Pipedrive/Smartlead/HeyReach.

Open http://localhost:5174.

## Notable behavior

- **Layout**: cards are dragged by their header, resized from the bottom-right corner
  (`react-grid-layout`), and the arrangement is saved to `localStorage` automatically.
  Reset it from the profile menu ("Reset Default Dashboard Layout") or the sidebar's ↺ icon.
- **Theme**: light/dark toggle in the header, also persisted, defaults to the OS preference.
- **Tasks**: the 1-week auto-archive engine runs on every snapshot fetch (client
  fallback and server both run the same sweep) — `Done` tasks older than 7 days flip
  `is_archived: true` and drop out of the active Kanban/List views, but stay searchable
  under the "Archived" tab.
- **Automation log**: "Show failures only", multi-select + bulk "Re-Run N Failed
  Automations", and row click opens the contextual sidebar drawer (resize it from its
  left edge, 30–60vw).
