# MCP Wrapping with 1Password

## Goal

Run MCP servers with runtime-injected secrets and no plaintext credentials in config files.

## 4-step pattern

1. Store secrets in 1Password vault items.
2. Create `.env.op` with secret references.
3. Add `.env` and `.env.op` to `.gitignore`.
4. Start server with:

```text
op run --env-file=.env.op -- <mcp-server-command>
```

## Example `.env.op`

```text
GITHUB_TOKEN=op://AI/GitHub/token
SUPABASE_ACCESS_TOKEN=op://AI/Supabase/token
```

## Example server launch

```text
op run --env-file=.env.op -- npx -y @modelcontextprotocol/server-github
```

## Notes

- Secrets are resolved in process memory for the wrapped process.
- Keep `mcp.json` free of hardcoded secrets; use environment interpolation where supported.
