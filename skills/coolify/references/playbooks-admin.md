# Admin playbooks (full coverage)

Use these for lifecycle and configuration management tasks.

## Projects and environments

### Create project and environment

1. Use `projects` (`action: list`) to avoid duplicates.
2. Create project with `projects` (`action: create`) if needed.
3. Create environment with `environments` (`action: create`).
4. Verify identifiers with list/get calls.

### Update project metadata

1. Load current state with `projects` (`action: get`).
2. Apply minimal patch with `projects` (`action: update`).
3. Verify persisted state.

## Applications

### Create application

1. Identify deployment source type (public repo, private GitHub, key-based, docker image).
2. Confirm server/project/environment targets.
3. Create app via `application`:

- `action: create_public`
- `action: create_github`
- `action: create_key`
- `action: create_dockerimage`

4. Trigger/monitor via `deploy` and `deployment` as needed.
5. Verify via `diagnose_app` / `get_application` and `application_logs`.

### Update application config

1. Retrieve with `get_application`.
2. Apply scoped changes with `application` (`action: update`).
3. Redeploy if required (`deploy`).
4. Verify using `diagnose_app` and deployment status.

## Databases

### Create database

1. Confirm required DB type.
2. Create with `database` (`action: create`) and explicit `type`.
3. Confirm state/details with `get_database`.
4. Use `control` for database start/restart only if needed.

### Manage backup schedules

1. List schedules/executions via `database_backups`.
2. Create/update/enable/disable using `database_backups` actions.
3. Confirm retention/frequency values.
4. Report next run expectations when available.

## Services

### Create/update service

1. Confirm intended service and environment.
2. Create/update via `service` (`action: create|update`).
3. Apply env vars via `env_vars` (`resource: service`).
4. Start/restart via `control` and verify with `get_service` + logs/health signals.

## Integrations and access

### Private keys / GitHub apps / cloud tokens

1. List existing entries (`private_keys`, `github_apps`, `cloud_tokens`).
2. Create/update/delete only as requested.
3. Run `cloud_tokens` validation where supported.
4. Treat deletes as destructive and require confirmation.

## Bulk/impactful operations

For restart-all/redeploy-project/stop-all style tasks:

1. Confirm target scope explicitly.
2. Explain impact and expected downtime/risk.
3. Require explicit confirmation.
4. Execute and verify in batches.

Use these tools where available:

- `restart_project_apps`
- `redeploy_project`
- `bulk_env_update`
- `stop_all_apps` (always confirmation-gated)
