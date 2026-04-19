---
name: coolify
description: Use this skill when a user needs to inspect, troubleshoot, deploy, restart, or manage resources in a Coolify environment (self-hosted or Coolify Cloud) via the @masonator/coolify-mcp server. Trigger for requests about Coolify applications, databases, services, servers, projects, environments, deployments, environment variables, backups, private keys, GitHub app integrations, teams, or cloud tokens—even if the user does not explicitly say “Coolify” (for example: “redeploy my API”, “why is staging unhealthy?”, “restart postgres”, “what’s broken in my infra?”). Prefer Coolify MCP tools over direct API calls, curl, or ad-hoc shell commands when available.
---

# Coolify MCP Operations

This skill is the MCP-first runbook for operating Coolify infrastructure.

## When to use this skill

Use this skill for any request that targets Coolify-managed resources, including when the user uses product language instead of saying "Coolify" directly.

Examples that should trigger this skill:

- "redeploy my API"
- "why is staging unhealthy?"
- "restart postgres"
- "what is broken in my infra?"
- "set DATABASE_URL and roll out"

If a Coolify MCP tool can do the job, prefer it over direct API calls, curl, or ad-hoc shell commands.

## Core operating model

Use this loop for nearly every task:

1. **Orient**: understand infra scope and target resource.
2. **Diagnose**: gather evidence before changing state.
3. **Act**: apply the smallest safe change.
4. **Verify**: confirm the outcome from status/logs/deployments.
5. **Report**: summarize what changed and next suggested actions.

Resource hierarchy to keep in mind:

`Server → Project → Environment → (Application | Database | Service)`

## Fast path

- If target is unknown: use `get_infrastructure_overview`, then `find_issues`.
- If target is known: jump to `diagnose_app` or `diagnose_server`.
- Prefer summarized list calls first, then deep `get_*` calls only for selected targets.

## Tool reference (use exact tool names)

### Infrastructure and diagnostics

- `get_version`
- `get_mcp_version`
- `get_infrastructure_overview`
- `find_issues`
- `diagnose_app`
- `diagnose_server`

### Servers

- `list_servers`
- `get_server`
- `server_resources`
- `server_domains`
- `validate_server`

### Projects and environments

- `projects` (`action: list|get|create|update|delete`)
- `environments` (`action: list|get|create|delete`)

### Applications

- `list_applications`
- `get_application`
- `application_logs`
- `application` (`action: create_public|create_github|create_key|create_dockerimage|update|delete`)
- `env_vars` (`resource: application`, `action: list|create|update|delete`)
- `control` (`resource: application`, `action: start|stop|restart`)

### Databases

- `list_databases`
- `get_database`
- `database` (`action: create|delete`, `type: postgresql|mysql|mariadb|mongodb|redis|keydb|clickhouse|dragonfly`)
- `database_backups` (`action: list_schedules|get_schedule|create|update|delete|list_executions|get_execution`)
- `control` (`resource: database`, `action: start|stop|restart`)

### Services

- `list_services`
- `get_service`
- `service` (`action: create|update|delete`)
- `env_vars` (`resource: service`, `action: list|create|delete`)
- `control` (`resource: service`, `action: start|stop|restart`)

### Deployments

- `list_deployments`
- `deploy`
- `deployment` (`action: get|cancel|list_for_app`)

### Integrations and access

- `private_keys` (`action: list|get|create|update|delete`)
- `github_apps` (`action: list|get|create|update|delete`)
- `teams` (`action: list|get|get_members|get_current|get_current_members`)
- `cloud_tokens` (`action: list|get|create|update|delete|validate`)

### Documentation

- `search_docs`

## Safety policy

### Confirm before destructive actions

Ask for explicit confirmation before:

- delete operations (apps, databases, services, projects, environments)
- emergency-stop style operations affecting many resources
- credential/key/token deletion
- backup schedule deletion where retention impact is unclear
- `stop_all_apps` or comparable broad-impact operations

For each destructive operation, state:

- target resource(s)
- exact action
- expected impact
- rollback/recovery posture (if available)

### Non-destructive operations usually proceed directly

You can proceed without extra confirmation for:

- diagnostics/reads
- log retrieval
- validate/check operations
- restarts/redeploys requested by the user
- narrow env var updates explicitly requested by the user

For routine break-fix requests, restart/redeploy actions can proceed when explicitly requested by the user.

## Execution standards

- Diagnose before mutate whenever possible.
- Use the smallest safe change first.
- Verify after every mutation using status/log/deployment evidence.
- Mention practical next operations when obvious (mirroring MCP `_actions` style).

## Practical examples

### Example: app throws 500s after deploy

1. `diagnose_app` using app name/domain/uuid.
2. Inspect deployment status via `deployment` and logs via `application_logs`.
3. If config issue found, update with `env_vars`.
4. Trigger `deploy`.
5. Re-check using `diagnose_app` and deployment status.

### Example: broad "what is broken?"

1. `get_infrastructure_overview`
2. `find_issues`
3. Deep-diagnose top failures (`diagnose_app` / `diagnose_server`)
4. Present prioritized remediation before high-impact mutations.

### Example: create postgres in staging

1. `projects` with `action: list` to locate project.
2. `environments` with `action: list` to confirm environment name.
3. `database` with `action: create`, `type: postgresql`, plus target IDs.
4. `get_database` to confirm running state and connection details.

## Output conventions

- Keep operator output concise and decision-oriented.
- Prefer human-readable names and short ID prefixes for traceability.
- Do not dump raw JSON unless the user asks.
- Include practical next steps when they are obvious.

## Setup behavior (when MCP is missing)

If Coolify MCP is not configured, do not guess API behavior.
Give setup guidance and resume once configured.

Load setup details from:

- `references/setup-and-auth.md`

## Playbook routing

Load detailed playbooks based on task type:

- Diagnostics and triage: `references/playbooks-diagnostics.md`
- Full admin operations: `references/playbooks-admin.md`
- Safety/confirmation policy: `references/safety-and-guardrails.md`
- Self-hosted vs cloud differences: `references/cloud-vs-selfhosted.md`
- Tool/action lookup: `references/tool-cookbook.md`
- Coolify concepts (build packs, magic env vars, resource types, proxy, S3, etc.): `references/concepts.md`

## Scope boundaries

Do not trigger this skill for generic tasks unrelated to Coolify resource operations, such as:

- generic GitHub PR authoring/review
- Kubernetes-only workflows
- Jira-only ticket workflows
- generic Dockerfile authoring without Coolify management context

## Minimal execution checklist

- [ ] Target resource identified
- [ ] Current state verified from Coolify MCP
- [ ] Action is least-destructive option
- [ ] Post-action verification completed
- [ ] User-facing summary includes state + next action options
