# Coolify concepts reference

Full docs: <https://coolify.io/docs/llms-full.txt>

## Resource hierarchy

```text
Server → Project → Environment → Resource
                                  ├── Application
                                  ├── Database
                                  └── Service (one-click template)
```

- **Server**: any Linux machine reachable via SSH (localhost or remote). Type `localhost` is where Coolify itself runs.
- **Project**: logical grouping of related environments.
- **Environment**: scoped context (e.g. production, staging) within a project. Resources inherit environment settings.
- **Application**: any web app, API, or static site deployed by Coolify.
- **Database**: managed database container (see types below).
- **Service**: one-click Docker Compose template (200+ available).

MCP identifiers: resources are addressed by UUID. `diagnose_app` and `diagnose_server` also accept name or domain.

---

## Build packs

| Build pack | When to use |
|---|---|
| **Nixpacks** (default) | Auto-detects language/framework; works for most Node, Python, Ruby, Go, PHP apps |
| **Static** | Pre-built files; serves via Nginx. Set `Publish Directory` (e.g. `dist`). |
| **Dockerfile** | Full image control; use your own Dockerfile |
| **Docker Compose** | Multi-service apps; Coolify wraps and proxies the compose network |
| **Docker Image** | Deploy a pre-built image from a registry |

Key build pack config fields:

- `Base Directory`: root for all build commands (useful for monorepos)
- `Publish Directory`: for static builds — directory Nginx serves
- `Port Exposes`: first port becomes health check port
- Build/Install/Start commands can be overridden; leave blank for Nixpacks auto-detect

---

## Magic environment variables (Docker Compose / Services)

Coolify auto-generates dynamic values using `SERVICE_<TYPE>_<IDENTIFIER>` syntax.

| Syntax | Generates |
|---|---|
| `SERVICE_URL_<ID>` | URL from wildcard domain: `http://app-abc.example.com` |
| `SERVICE_URL_<ID>_3000` | URL proxied to port 3000 |
| `SERVICE_URL_<ID>=/api` | URL with path appended |
| `SERVICE_FQDN_<ID>` | FQDN only (no scheme) |
| `SERVICE_USER_<ID>` | Random 16-char string (use as username) |
| `SERVICE_PASSWORD_<ID>` | Strong random password |
| `SERVICE_PASSWORD_64_<ID>` | 64-bit random password |
| `SERVICE_BASE64_<ID>` | Base64-encoded random string |

Use these in compose `environment:` stanzas. Values stay consistent across all services in a stack.

---

## Predefined application variables

Coolify injects these automatically (opt-in by referencing them):

| Variable | Value |
|---|---|
| `COOLIFY_FQDN` | App FQDN(s) |
| `COOLIFY_URL` | App URL(s) |
| `COOLIFY_BRANCH` | Git branch |
| `COOLIFY_RESOURCE_UUID` | Resource UUID |
| `COOLIFY_CONTAINER_NAME` | Container name |
| `SOURCE_COMMIT` | Git commit hash (must enable "Include Source Commit in Build") |
| `PORT` | Defaults to first port in Port Exposes |
| `HOST` | Defaults to `0.0.0.0` |

---

## Database types

Supported via `database` tool with `type` param:

| Type | Notes |
|---|---|
| `postgresql` | Most common; full backup support |
| `mysql` | |
| `mariadb` | |
| `mongodb` | |
| `redis` | |
| `keydb` | Redis-compatible, multi-threaded |
| `clickhouse` | Columnar analytics |
| `dragonfly` | Redis-compatible, high-throughput |

Database SSL: auto-cert generation available per-database. Databases do not support domain configuration.

---

## Proxy options

- **Traefik** (default): automatic SSL via Let's Encrypt, dynamic config via labels, dashboard available, supports wildcard certs via DNS challenge
- **Caddy**: simpler config, HTTP/2 auto, alternative to Traefik

SSL/TLS:

- Let's Encrypt auto-provisioned on first HTTPS domain request
- Custom certs: place `.cert` and `.key` in `/data/coolify/proxy/certs/`
- Wildcard certs: require DNS challenge provider (Cloudflare, Hetzner, etc.)
- Cert files for custom: `.cert` extension (not `.pem`), `.key` for key

Domain format: FQDN with scheme (`https://coolify.io`). Multiple domains comma-separated. Port suffix for proxy routing (`https://app.example.com:3000`).

---

## Git integration options

| Method | Best for |
|---|---|
| **GitHub App** | GitHub repos; automatic webhooks, PR deployments, commit status |
| **Deploy Keys** | Any Git provider; SSH-based, universal, works air-gapped |
| **Public URL** | Public repos only; no auth needed |

Auto-deploy triggers:

- GitHub App: automatic on push
- Deploy Keys / other providers: use Coolify API token + Deploy Webhook URL in CI (GitHub Actions, GitLab CI, Bitbucket Pipelines)

---

## S3 backup storage

Supported providers:

- AWS S3
- DigitalOcean Spaces
- MinIO
- Cloudflare R2
- Supabase Storage
- Backblaze B2
- Scaleway Object Storage
- Hetzner S3 Storage
- Wasabi

Verification: Coolify calls `ListObjectsV2` against the bucket before activating. Bucket must exist first.

Database backup schedule: configured per-database via `database_backups` tool. Uses cron syntax.

Coolify self-backup: configured in Settings → Backup. Backs up Coolify's own database to S3.

---

## Log draining

Supported destinations:

- **Axiom**: requires API token + dataset name
- **New Relic**: requires License Key. Set `COOLIFY_APP_NAME` env var on the resource to split logs by service in New Relic.
- **Custom FluentBit**: bring your own config

Enable per-resource in Configuration → Environment Variables + log drain settings.

---

## Rolling updates (zero-downtime)

Coolify supports zero-downtime deployments using health checks. When a new container starts, Coolify waits for health checks to pass before routing traffic and removing old container.

Requires: health check endpoint configured in app settings.

---

## Scaling options

| Method | Notes |
|---|---|
| **Traditional horizontal** | Deploy same app to multiple servers, use external load balancer |
| **Docker Swarm** | Multi-node cluster managed by Coolify |
| **Kubernetes** | Planned, not yet available |

---

## Firewall considerations (self-hosted)

Docker uses NAT-based iptables rules that **bypass UFW**. UFW alone is not effective for blocking Docker-exposed ports.

Required open ports for self-hosted:

- **22** (SSH, or custom SSH port)
- **80** (SSL cert generation via reverse proxy)
- **443** (HTTPS traffic)
- **8000** (Coolify dashboard, can restrict to trusted IPs)

Internal ports (usually not exposed):

- `5432` (PostgreSQL)
- `6379` (Redis)
- `6001` (Soketi/Realtime)

Coolify Cloud IP ranges (for firewall whitelisting):

- <https://coolify.io/ipv4.txt>
- <https://coolify.io/ipv6.txt>

---

## Cloudflare Tunnel integration

Options:

1. **All resources via tunnel**: easiest, recommended for beginners; one tunnel routes all Coolify resources
2. **Single resource**: per-app tunnel with port mapping
3. **Server SSH access**: tunnel your SSH connection through Cloudflare
4. **Full HTTPS/TLS**: end-to-end encryption with Cloudflare Origin Certificates

Use when: no public IP, want to avoid exposing server IP, need DDoS protection.

---

## Installation paths

Self-hosted quick install:

```sh
curl -fsSL https://cdn.coollabs.io/coolify/install.sh | sudo bash
```

Supported: Ubuntu LTS (20.04, 22.04, 24.04), Debian, other Linux. Non-LTS Ubuntu requires manual install.

Key directories:

- `/data/coolify/` — all Coolify data
- `/data/coolify/source/.env` — environment config (APP_KEY, DB_PASSWORD, etc.)
- `/data/coolify/proxy/` — Traefik config and certs
- `/data/coolify/proxy/certs/` — custom SSL certs

Coolify ports on host:

- `8000`: dashboard
- `6001`: Soketi realtime
- `5432`: PostgreSQL (internal)
- `6379`: Redis (internal)

---

## One-click services

200+ pre-configured Docker Compose templates. Categories include:
Administration, AI, Analytics, Automation, Business, CMS, Communication, Database, Development, Documentation, Email, Finance, Monitoring, Networking, Productivity, Security, Storage, and more.

Notable services for ops context:

- **Authentik / Keycloak / Logto**: SSO/identity
- **Uptime Kuma / Checkmate / Statusnook**: monitoring
- **Plausible / Umami / PostHog**: analytics
- **Infisical**: secrets management
- **Minio**: S3-compatible storage
- **Gitea / Forgejo**: self-hosted Git

To find a specific service: use `search_docs` with service name, or browse the MCP service list.

---

## OAuth login to Coolify dashboard

Supported providers: GitHub, GitLab, Google, Azure, Bitbucket.

Delegates email verification to external IDP; does not replace password, just provides alternative login.

---

## Teams

Multi-user access via teams. `teams` tool supports `list|get|get_members|get_current|get_current_members`. Team roles control which resources members can access.
