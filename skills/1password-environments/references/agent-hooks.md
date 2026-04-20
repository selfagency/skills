# Agent Hook Validation

Use the 1Password local `.env` validation hook to block commands when required mounts are missing or invalid.

## Supported hosts

- Claude Code
- Cursor
- GitHub Copilot
- Windsurf

## Configured mode

Create `.1password/environments.toml` with explicit paths:

```toml
mount_paths = [".env", "billing.env"]
```

Only listed files are validated.

## Default mode

If TOML is missing or malformed, hook checks known mounts in the project path (fail-open if app DB unavailable).

## Validation checks

- Mount is enabled
- File exists
- File is valid FIFO

## Troubleshooting

- Hook logs: `/tmp/1password-hooks.log`
- If no files are specified (`mount_paths = []`), commands are allowed
- If TOML exists without `mount_paths`, hook warns and falls back to default mode
