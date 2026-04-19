# Setup and authentication

Use this reference when Coolify MCP is not configured or credentials are missing.

## Prerequisites

- Node.js >= 18
- Reachable Coolify instance URL
- Coolify API token (generated from Coolify settings)

Required environment variables:

- `COOLIFY_ACCESS_TOKEN` (required)
- `COOLIFY_BASE_URL` (optional, defaults to `http://localhost:3000`)

## Claude Desktop

Add MCP config in:

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS)

```json
{
  "mcpServers": {
    "coolify": {
      "command": "npx",
      "args": ["-y", "@masonator/coolify-mcp"],
      "env": {
        "COOLIFY_ACCESS_TOKEN": "your-api-token",
        "COOLIFY_BASE_URL": "https://your-coolify-instance.com"
      }
    }
  }
}
```

## Claude Code

```bash
claude mcp add coolify \
  -e COOLIFY_BASE_URL="https://your-coolify-instance.com" \
  -e COOLIFY_ACCESS_TOKEN="your-api-token" \
  -- npx @masonator/coolify-mcp@latest
```

Note: use `@latest` in Claude Code for reliable startup.

## VS Code-compatible MCP setup

Use your client’s MCP server registration flow with:

- command: `npx`
- args: `-y @masonator/coolify-mcp`
- env: `COOLIFY_ACCESS_TOKEN`, `COOLIFY_BASE_URL`

## Authentication checklist

- Token has required permissions for requested actions
- Base URL points to the expected Coolify instance
- Connectivity works from the MCP client runtime

## If setup fails

1. Re-check token value and scope.
2. Re-check base URL and protocol (`http` vs `https`).
3. Confirm node/npx are available in PATH.
4. Re-register MCP server and retry a read-only call.
