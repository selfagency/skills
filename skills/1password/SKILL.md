---
name: 1password
description: Set up and use 1Password CLI (op). Use when installing the CLI, enabling desktop app integration, signing in (single or multi-account), reading/injecting/running secrets via op run or op inject, configuring shell plugins for biometric auth of CLIs (AWS, GitHub, etc.), or creating and using service accounts for programmatic vault access.
---

# 1Password CLI

Use this skill for practical, security-first `op` workflows.

## Core rules

- Prefer `op run` and `op inject` over writing plaintext secrets to disk.
- Never print raw secret values in output, logs, or code.
- Use the least privilege model: minimum vault scope and minimum permissions.
- If both Connect and service account env vars are set, Connect takes precedence.

## tmux guardrail for interactive auth

When interactive sign-in is required, run `op` commands in a dedicated tmux session so auth state is stable across commands.

1. Create a fresh tmux session.
2. Run `op signin` and complete desktop auth.
3. Verify with `op whoami`.
4. Continue secret operations in that same session.

If tmux is unavailable, stop and ask before continuing with interactive auth.

## Workflow

1. Verify install: `op --version`.
2. Ensure desktop app integration is enabled and app is unlocked.
3. Sign in (`op signin`) and verify (`op whoami`).
4. Read or inject secrets:
   - `op read op://vault/item/field`
   - `op run --env-file=.env.op -- <command>`
   - `op inject -i config.tpl -o config.resolved`
5. For long-lived automation, use service accounts with `OP_SERVICE_ACCOUNT_TOKEN`.

## Shell plugins

Use shell plugins for biometric auth with supported CLIs (for example AWS and GitHub).

1. Initialize plugin: `op plugin init <plugin>`.
2. Add generated `eval $(...)` snippet to shell rc file.
3. Restart shell and verify tool auth flow.

See [shell plugin reference](references/shell-plugins.md).

## Service accounts

Use service accounts for non-user automation and CI workflows.

1. Create service account with narrow vault access.
2. Export token to `OP_SERVICE_ACCOUNT_TOKEN`.
3. Verify identity with `op user get --me`.
4. Use `op read`, `op run`, `op inject`, and scoped `op item` commands.

See [service account reference](references/service-accounts.md).

## Gotchas

- Service account vault/environment access and permissions are immutable after creation. Create a new service account to change scope.
- Service accounts require 1Password CLI 2.18.0+.
- Avoid `op item` without `--vault` when service account can access multiple vaults.

## Companion skills

- `1password-environments` for local FIFO `.env` Environments + agent hooks.
- `1password-ssh` for SSH agent, keys, and Git signing.
- `1password-secrets-in-code` for MCP wrapping, SDK patterns, and CI/CD integrations.

## References

- [Get started](references/get-started.md)
- [CLI examples](references/cli-examples.md)
- [Shell plugins](references/shell-plugins.md)
- [Service accounts](references/service-accounts.md)
