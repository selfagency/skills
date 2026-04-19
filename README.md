# Skills Repository

This repository contains Agent Skills used for specialized workflows.

## Currently Available Skills

| Skill                | Path                         | Purpose                                                                                                                                                  |
| -------------------- | ---------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `astro`              | `skills/astro/`              | Unified Astro 6 skill covering components, islands, routing, content collections, integrations, deployment, and Starwind component usage.                |
| `beans-mcp-workflow` | `skills/beans-mcp-workflow/` | Beans workspace task management via MCP (create, query, update, archive, relationships, `.beans` file workflows).                                        |
| `coolify`            | `skills/coolify/`            | MCP-first Coolify operations skill for diagnostics, deploy/restart, lifecycle management, and guarded admin actions across cloud and self-hosted setups. |
| `git-mcp-workflow`   | `skills/git-mcp-workflow/`   | MCP-first Git workflow and recovery (status, branches, commits, remotes, rebase/cherry-pick/stash/bisect/worktrees, safe undo).                          |

## Astro Skill Modules

The `astro` skill is intentionally consolidated under one skill directory and routes to internal module references:

- `references/module-components.md`
- `references/module-islands.md`
- `references/module-routing.md`
- `references/module-content.md`
- `references/module-integrations.md`
- `references/module-deployment.md`
- `references/module-starwind.md`

Detailed topic references are also available under `skills/astro/references/`.

## Repository Structure

```text
skills/
  astro/
  beans-mcp-workflow/
  coolify/
  git-mcp-workflow/
```

## Notes

- Skills are defined by each folder’s `SKILL.md` frontmatter (`name`, `description`) and body instructions.
- Optional supporting resources live in `references/`, `scripts/`, and `evals/` per skill.
