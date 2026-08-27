# Growth Ops Command Center — Albert Scott CRM Live Dashboard

A single-pane dashboard over Albert Scott's outbound stack: Smartlead campaigns, the
Smartlead → Pipedrive automation (see [`../docs/Smartlead-Pipedrive-Automation-Workflow.md`](../docs/Smartlead-Pipedrive-Automation-Workflow.md)),
HeyReach LinkedIn outreach, sending-domain health, technical SEO, and a task board.

**Theme — Enterprise Growth Ops (dark-slate minimalist):** deep monochrome slate
surfaces (canvas `slate-950`, cards `slate-900`, hairline `slate-800/60` borders,
`slate-50`/`slate-400`/`slate-500` text hierarchy), Inter, cockpit-tight card padding,
and restrained font weights — hot magenta `#E51958` is kept strictly as the Albert
Scott brand's "one key signal" (primary CTAs, the drop-target/focus accent), never as
decoration. Status/severity reads through standard muted Tailwind semantic hues
(emerald/red/amber/sky/slate) as hollow, low-opacity badges instead of solid color
blocks — see "Enterprise theme" and "Layout density" below for the full breakdown.
Light mode stays available via the header toggle and keeps the original soft-gray
Albert Scott palette. The Pipeline card's win-rate ring is the one deliberate
"signature" element (see "Distinctive-design pass" below); everything else stays quiet
by design.

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

## Distinctive-design pass

Applied Anthropic's [`frontend-design`](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md)
skill as a self-critique pass — its core question is "does this read as templated, or
as a choice made for this specific brief?":

- **One signature element, spent deliberately.** `PipelineCard.jsx`'s win-rate ring
  (`WinRateRing`) is the one place this dashboard takes a real visual risk — a compact
  radial gauge (SVG `stroke-dasharray`, Closed Won vs. Closed Lost) instead of another
  stat tile. It's real information sales ops actually reads as a headline number, not
  decoration. Note: this is an original, generic progress-ring pattern, not a
  reproduction of Albert Scott's proprietary "ring motif" / Marketplace Control Loop
  mark — the brand skill explicitly bans hand-recreating that asset, so it wasn't used.
- **Responsive down to mobile (quality floor).** The draggable 12-column grid
  (`react-grid-layout`) turns unusably narrow on a phone; `useIsMobile.js` swaps it for
  a plain stacked column below 768px, and `TasksCard` forces List view on mobile
  (Kanban's 3 stacked columns don't fit a phone height) — no drag, no column math,
  everything stays legible.
- **Everything else stays quiet.** No new decorative elements were added elsewhere —
  restraint is the point once one thing has taken the risk.

## Layout density

Pulled the transferable parts of [`leonxlnx/taste-skill`](https://github.com/leonxlnx/taste-skill)'s
`VISUAL_DENSITY` dial reasoning and tactile-feedback guidance — its own header says
it's built for landing pages/portfolios/redesigns, explicitly *not* dashboards or data
tables, so the marketing-page rules (heroes, bento sections, testimonials, serif type,
image sourcing) don't apply here. What does transfer: a "cockpit" reading of
`VISUAL_DENSITY` (packed data, not art-gallery airiness) argues for less card chrome and
tighter spacing than a marketing site would use. Card padding, the grid's row height and
margins, and the automation table/drawer/modal padding were all pulled back down
(`CardShell.jsx`, `GridDashboard.jsx`, `DashboardContext.jsx`'s `DEFAULT_LAYOUT`) — same
information density, ~16% less vertical space for the same content at a 1440px viewport.

## Enterprise theme (dark-slate minimalist)

Applied as a "Style Specification Override" pass on top of the original Albert Scott
brand base — see `tailwind.config.js` for the token values:

- **Surfaces** — three nested monochrome layers in dark mode: global canvas
  (`slate-950`) < card/modal/drawer surface (`slate-900`) < inset tile (`slate-800/50`),
  each separated by a whisper-thin `slate-800/60` or `slate-700/60` border instead of a
  visible gray outline.
- **Text hierarchy** — `slate-50` for titles/active data, `slate-400` for secondary
  labels and metadata, `slate-500` for muted timestamps/subtext.
- **Badges** — `Badge` (`src/components/Badge.jsx`) renders hollow, low-opacity pills
  (`bg-{color}-500/10 text-{color}-400 border-{color}-500/20`) instead of solid color
  blocks; `MicroTag` renders the even-lighter microscopic lowercase dot+text tags used
  for Kanban/List priority and category.
- **Alerts** — consolidated into a single-row container (`AlertBanner.jsx`) with tiny
  muted colored chips instead of stacked full-width bars, `rounded-md` corners only.
- **Pipeline funnel** — `PipelineCard.jsx`'s stage bar uses a monochrome slate ramp
  (lighter → darker as a deal progresses) with the accent budget spent on exactly one
  color: emerald for Closed Won.
- **Status lights** — the active/dead inbox counters use a tiny pulsating 8px
  `animate-pulse` dot rather than bold colored text.
- **Kanban** — columns are transparent/bordered rather than filled; cards get a
  `hover:border-slate-700` transition instead of relying on a heavy border by default.

## Motion & interaction polish

Interaction details (durations, easing, press/hover feedback, reduced-motion handling)
follow the `ui-ux-pro-max` design-intelligence skill's Animation and Touch & Interaction
guidance rather than one-off values:

- **Framer Motion** drives every enter/exit transition that needs to feel physical: the
  sidebar drawer and profile modal spring in and fade/slide out ~35% faster than they
  entered (`SidebarDrawer.jsx`, `ProfileModal.jsx`), the alert banner and bulk-action bar
  animate in/out instead of popping, and the Kanban board uses shared `layoutId`s so a
  card moving between columns animates its position instead of jump-cutting.
- **`prefers-reduced-motion`** is honored globally — `<MotionConfig reducedMotion="user">`
  in `App.jsx` collapses every Framer Motion animation automatically, and `index.css` has
  a matching fallback for plain Tailwind transitions.
- **Press/focus feedback**: the shared `.press` (active:scale-96) and `.focus-ring`
  utility classes in `index.css` give every button consistent tap feedback and a visible
  keyboard focus ring instead of the browser default outline being silently removed.
- **Single-pointer alternative to drag**: Kanban cards get ▲/▼ move buttons (visible on
  hover/focus) so reordering a task never depends on drag-and-drop alone — dragging is
  still the primary interaction, but it's not the *only* one (WCAG 2.2 SC 2.5.7).
- **Loading state**: the initial fetch shows a skeleton shaped like the real grid
  (`DashboardSkeleton.jsx`) instead of a blank screen or a bare "Loading…" string.
