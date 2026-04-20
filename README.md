# Skills Repository

This repository contains Agent Skills used for specialized workflows.

## Currently Available Skills

| Skill                       | Path                                | Purpose                                                                                                                                                  |
| --------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `astro`                     | `skills/astro/`                     | Unified Astro 6 skill covering components, islands, routing, content collections, integrations, deployment, and Starwind component usage.                |
| `beans-mcp-workflow`        | `skills/beans-mcp-workflow/`        | Beans workspace task management via MCP (create, query, update, archive, relationships, `.beans` file workflows).                                        |
| `1password`                 | `skills/1password/`                 | 1Password CLI setup and operations: install/sign-in, secret reads/injection, shell plugins, and service account workflows.                               |
| `1password-environments`    | `skills/1password-environments/`    | Local FIFO `.env` mounts from 1Password Environments, plus agent-hook validation and troubleshooting guidance.                                           |
| `1password-ssh`             | `skills/1password-ssh/`             | 1Password SSH agent setup, key management, Git commit signing with SSH, and secure agent-forwarding practices.                                           |
| `1password-secrets-in-code` | `skills/1password-secrets-in-code/` | Secure secrets-in-code patterns for MCP wrapping, SDK resolution, CI/CD integrations, and plaintext-secret audits.                                       |
| `coolify`                   | `skills/coolify/`                   | MCP-first Coolify operations skill for diagnostics, deploy/restart, lifecycle management, and guarded admin actions across cloud and self-hosted setups. |
| `git-mcp-workflow`          | `skills/git-mcp-workflow/`          | MCP-first Git workflow and recovery (status, branches, commits, remotes, rebase/cherry-pick/stash/bisect/worktrees, safe undo).                          |

## Notes

- Skills are defined by each folder’s `SKILL.md` frontmatter (`name`, `description`) and body instructions.
- Optional supporting resources live in `references/`, `scripts/`, and `evals/` per skill.
