# Coolify Cloud vs self-hosted

Use this to adapt guidance to the user’s deployment model.

## Shared model

Both use the same core Coolify concepts (servers, projects, environments, resources).
Most operational workflows are identical once authenticated.

## Self-hosted specifics

- User controls Coolify instance lifecycle and updates.
- Network/firewall/proxy and host-level concerns are often in scope.
- Instance-level troubleshooting may include host/container concerns.

## Coolify Cloud specifics

- Coolify control plane is managed; user still brings/manages their own servers.
- Focus more on connected server/resource operations than instance maintenance.
- IP allowlists and connectivity to managed control plane may matter.

## Decision cues

If the request mentions:

- install/upgrade/downgrade/uninstall Coolify instance → likely self-hosted
- app.coolify.io subscription/managed dashboard behavior → likely cloud
- generic resource operation only → same workflow works for both

## Reporting advice

When uncertain, ask one clarifying question only if it changes action safety.
Otherwise proceed with resource-level diagnostics/actions that are valid in both models.
