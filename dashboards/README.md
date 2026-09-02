# Dashboards

Source for the Claude artifact dashboards. Republish the file to the artifact URL listed
here (pass it as `url`) so the link stays the same; never resolve the URL by title.

| File | Artifact | Notes |
| --- | --- | --- |
| `yoni-command-center.html` | https://claude.ai/code/artifact/e803bcae-9873-490a-8b87-f1e352bc7597 | Yoni Sales & Marketing Command Center. Data snapshot is from the Aug 27, 2026 pull; the `YESTERDAY`, `LINKEDIN`, `OVERDUE`, `DUE_TODAY`, `UPCOMING`, `CAMPAIGNS`, and `DEALS` constants are the only things a data refresh should touch. |

The file is the page body only. The publisher wraps it in `<!doctype html>`, `<head>`, and `<body>`.
