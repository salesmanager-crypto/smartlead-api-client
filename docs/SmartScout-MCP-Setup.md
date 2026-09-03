# SmartScout MCP connector

SmartScout exposes its Amazon marketplace data (products, keywords, brands, sellers,
subcategories, Ad Spy / share of voice, category trends) as a remote MCP server at
`https://mcp.smartscout.com/`. This repo registers it in `.mcp.json` so Claude Code
picks it up automatically when working here. It is read-only: nothing it does can change
the SmartScout account.

**Requirements:** an active SmartScout **Business or Enterprise** subscription. There is no
API key to paste anywhere. Auth is OAuth in the browser; the server registers the client
automatically, so Client ID / Client Secret stay blank.

## Claude Code (this repo)

`.mcp.json` at the repo root already contains:

```json
{
  "mcpServers": {
    "smartscout": { "type": "http", "url": "https://mcp.smartscout.com/" }
  }
}
```

1. Open the repo in Claude Code and approve the project MCP server when prompted.
2. Run `/mcp`, pick **smartscout**, and choose **Authenticate**. A browser window opens
   for the SmartScout login; approve it and the tools appear in the same session.
3. Verify with `/mcp` (status should read connected) or ask Claude to run a SmartScout
   keyword or brand lookup.

To add it globally instead of per-project:

```bash
claude mcp add --transport http --scope user smartscout https://mcp.smartscout.com/
```

## claude.ai / Claude Desktop (custom connector)

SmartScout is not in the connector directory, so add it by URL:

1. **Settings → Connectors → Add custom connector**
2. URL: `https://mcp.smartscout.com/`
3. Leave **Client ID** and **Client Secret** blank
4. Name it **SmartScout** and save; complete the SmartScout authorization in the browser
5. Enable it in the connector menu of any new chat (and in scheduled-task sessions that
   should use it)

## Troubleshooting

- `Missing or invalid bearer token` (HTTP 401) means the OAuth step was skipped or the
  token expired. Re-run **Authenticate** from `/mcp`, or reconnect the custom connector.
- Authorization page rejects the login: confirm the SmartScout account is on a Business or
  Enterprise plan, since lower tiers do not include MCP / API access.
- Tools not showing in a claude.ai chat even though the connector is connected: it is
  toggled off for that chat. Enable it from the chat's connector settings.
- Still stuck: `support@smartscout.com`.

## Where it fits

Use it for prospect research before writing outreach, for example pulling a brand's
revenue trend, top ASINs, subcategory share, or sponsored-ad footprint so a first email
can reference something specific to that seller rather than a generic pitch.
