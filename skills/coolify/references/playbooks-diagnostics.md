# Diagnostics playbooks

Use these for troubleshooting-first requests.

Full docs: <https://coolify.io/docs/llms-full.txt>

## Playbook: “my app is failing / returns 5xx”

1. Run `diagnose_app` for status, env context, and deployment signals.
2. Inspect deploy history/status with `deployment`.
3. Pull runtime evidence via `application_logs`.
4. Check/update env vars with `env_vars` if config issue is confirmed.
5. If needed, trigger `deploy` (or targeted `control` restart).
6. Verify using `diagnose_app` and deployment status.

## Playbook: “what’s broken in my infra?”

1. Start with `get_infrastructure_overview`.
2. Run `find_issues`.
3. Deep-diagnose highest impact resources (`diagnose_app` / `diagnose_server`).
4. Group by severity and blast radius.
5. Present prioritized remediation options before broad-impact actions.

## Playbook: “server unhealthy / not validating”

1. Run `diagnose_server`.
2. Inspect attached workloads via `server_resources`.
3. Check domain/proxy surface with `server_domains`.
4. Identify likely connectivity/domain mismatch patterns.
5. Re-run `validate_server` after corrective actions.

**Common server connection issues (from docs):**

- UFW `LIMIT` rules can cause unstable SSH connections — check iptables rules
- Docker bypasses UFW via NAT/iptables; port blocking requires iptables rules, not just UFW
- Required open: 22 (SSH), 80 (SSL cert), 443 (HTTPS), 8000 (dashboard)

## Playbook: “deployment stuck/failed”

1. List relevant executions via `deployment` (`action: list_for_app`).
2. Inspect the failing deployment via `deployment` (`action: get`).
3. Pull deployment logs (paged if needed).
4. Classify failure: config/env, build/runtime, external dependency.
5. Apply minimal fix (for example env/config update).
6. Trigger `deploy` and verify completion.

**Common build failures by build pack:**

- Nixpacks: app type not detected → check that lock file exists (package-lock.json, Pipfile.lock, etc.)
- Static: wrong Publish Directory (should be `dist` for Vite/Vue/React, `_site` for Jekyll)
- Docker Compose: wrong Base Directory or compose file path/extension mismatch
- Docker image not pushed to registry yet before deploy

## Playbook: "env var issue suspected"

1. List current vars via `env_vars`.
2. Compare against expected required keys.
3. Apply only scoped/justified updates.
4. Redeploy/restart if config reload is required.
5. Verify behavior using status + logs.

**Notes from docs:**

- Build-time vs runtime distinction matters: some vars must be set before build (build args), not just runtime
- Magic env vars (`SERVICE_*`) are for Docker Compose stacks only — not for regular apps
- `SOURCE_COMMIT` not injected by default; enable "Include Source Commit in Build" if needed

## Playbook: "dashboard inaccessible"

1. Check if Coolify container is running: `docker ps -a --filter "name=coolify"`
2. Check port 8000 is open and not conflicted: `ss -tulpn | grep :8000`
3. Check proxy status — most inaccessibility is due to proxy not running
4. Check for proxy misconfiguration in dynamic config
5. Verify container health (unhealthy Coolify container blocks dashboard)
6. If needed, run install script again: `curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash`

## Playbook: "installation script failed"

Key diagnostic sequence (from docs):

1. Check installation logs: `tail -100 /data/coolify/source/installation-*.log`
2. Check Docker: `docker --version && docker compose version`
3. Check Docker service: `systemctl status docker`
4. Check containers: `docker ps -a --filter "name=coolify"`
5. Check port 8000: `ss -tulpn | grep :8000`
6. Check Docker network: `docker network ls | grep coolify`

If network missing: `docker network create --attachable --ipv6 coolify`

Expected Docker images post-install:

- `ghcr.io/coollabsio/coolify`
- `ghcr.io/coollabsio/coolify-helper`
- `ghcr.io/coollabsio/coolify-realtime`

## Playbook: "SSL/wildcard cert not working"

1. Verify cert is valid and not expired; CN must match domain
2. File extensions: must be `.cert` and `.key` (not `.pem` — rename if needed)
3. File location: `/data/coolify/proxy/certs/`
4. Verify cert is added in Coolify dashboard under Proxy → Dynamic Configuration
5. Delete stale `acme.json` from `/data/coolify/proxy/` if proxy cached old cert, then restart proxy
6. Check DNS challenge config if using wildcard certs (provider API key, correct DNS provider selected)
7. Test with different browser/network to rule out browser cache

## Playbook: "health check failing"

From docs: first port in `Port Exposes` becomes default health check port.

1. Confirm app actually listens on that port (check start command)
2. Check `application_logs` for startup errors
3. Test health endpoint from inside container if accessible via terminal
4. Update Port Exposes if app uses non-default port
5. Consider adding explicit health check path in app settings
