# Tool cookbook

Use this as a quick routing map from user intent to exact Coolify MCP tools.

## Orientation and diagnostics

- Infra unknown or broad “what is broken?”:
- `get_infrastructure_overview`
- `find_issues`
- Known app issue:
- `diagnose_app`
- `application_logs`
- `deployment` (`action: list_for_app|get`)
- Known server issue:
- `diagnose_server`
- `server_resources`
- `server_domains`

## Inventory and targeting

- Use summarized list calls first:
- `list_servers`, `list_applications`, `list_databases`, `list_services`, `projects`, `environments`
- Use deep detail only on selected targets:
- `get_server`, `get_application`, `get_database`, `get_service`
- Prefer smart lookup where available:
- `diagnose_app` accepts UUID/name/domain
- `diagnose_server` accepts UUID/name/IP

## Acting on resources

- Start/stop/restart:
- `control` (`resource: application|database|service`, `action: start|stop|restart`)
- Deploy/redeploy:
- `deploy`
- `deployment` (`action: get|list_for_app|cancel`)
- Env vars:
- `env_vars` with `resource: application|service`
- App supports `list|create|update|delete`
- Service supports `list|create|delete`
- CRUD dispatchers:
- `application`, `database`, `service`, `projects`, `environments`

## Verification

After every mutation:

1. Retrieve status again using diagnose/get/list calls.
2. Inspect logs or deployment execution where relevant.
3. Confirm user-visible impact where possible

## Reporting format

- action performed
- target resource
- current resulting state
- unresolved risks/issues
- suggested next operations

When available, surface likely next operations similarly to MCP `_actions` hints.
