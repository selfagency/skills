# Service Accounts

Service accounts provide non-user auth for automation.

## Best practices

- Grant only required vault access and permissions.
- Prefer read-only unless writes are required.
- Store token in 1Password immediately after creation.
- Export token only where needed.

## Setup

1. Create service account in 1Password Developer tools.
2. Scope vault access and permissions.
3. Export token to `OP_SERVICE_ACCOUNT_TOKEN`.
4. Verify with `op user get --me`.

## Command support highlights

- Supported: `op read`, `op inject`, `op run`, scoped `op item`/`op document` operations.
- Not supported: several user/group/connect workflows.

## Important gotchas

- Access/permissions are immutable after creation.
- Service account commands can hit hourly/daily limits; use IDs and scoped commands to reduce request count.
- If `OP_CONNECT_HOST` and `OP_CONNECT_TOKEN` are set, they override `OP_SERVICE_ACCOUNT_TOKEN`.
