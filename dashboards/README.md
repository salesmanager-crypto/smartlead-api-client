# Dashboards

Source for the Claude artifact dashboards. Republish the file to the artifact URL listed
here (pass it as `url`) so the link stays the same; never resolve the URL by title.

| File | Artifact | Notes |
| --- | --- | --- |
| `yoni-command-center.html` | https://claude.ai/code/artifact/e803bcae-9873-490a-8b87-f1e352bc7597 | Yoni Sales & Marketing Command Center. Data snapshot from the Sep 2, 2026 pull. |

The file is the page body only. The publisher wraps it in `<!doctype html>`, `<head>`, and `<body>`.

## Refreshing the data

Only the constants block at the top of the `<script>` changes on a refresh: `DATA_DATE`, `TODAY`,
`OVERDUE`, `DUE_TODAY`, `UPCOMING`, `CAMPAIGNS`, `DEALS`, `INBOX_LOG`, `YESTERDAY`, `LINKEDIN`,
`PD_META`, `INBOXES`. Everything below it is render code and computes its captions from those.

- `pull/pull-smartlead.mjs` pulls campaigns, per-campaign analytics, yesterday's sends, all inboxes,
  and the last 7 days of Master Inbox replies with categories. Needs `SMARTLEAD_API_KEY` in `.env`.
- `pull/pull-heyreach.mjs` pulls the HeyReach campaign and its lead statuses. Needs `HEYREACH_API_KEY`.
- Pipedrive comes from the connector: open activities sorted by due date, deals by status, leads,
  and every person and organization (for name resolution and the sync check).

`INBOX_LOG` rows carry a `status`: `synced` when the category is one the Smartlead-to-Pipedrive
automation syncs (Interested, Meeting Request, Follow Up) and a Pipedrive person exists with the
lead's email; `gap` when it should have synced but no person exists; `uncategorized` when SmartLead
has not tagged the reply yet; `none` for categories the automation does not sync.
