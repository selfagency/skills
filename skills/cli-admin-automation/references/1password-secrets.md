# 1Password Secrets Management

## Critical Gotchas (Read First)

### Secret References Are Immutable

- Once created, 1Password secret reference (`op://vault/item/field`) **cannot be changed**
- **DANGER**: Changing reference syntax or renaming item breaks all scripts depending on it
- **FIX**: Plan naming scheme before creating secrets in production vault

### Caching Daemon Staleness

- 1Password CLI uses local daemon for caching. Daemon may cache stale credentials
- **SYMPTOM**: `op read` fails with permission error even after credential is updated
- **FIX**: Restart daemon: `killall op-daemon && sleep 2`

### Plaintext Secret Files Leave Traces

- Storing secrets in files (even `/tmp`) leaves traces in shell history, logs, process listings
- **DANGER**: `/tmp` is world-readable; any user can read secrets
- **FIX**: Use `op run --` to inject secrets as environment variables, never write to disk

  ```bash
  op run -- /script.sh  # Secrets injected as env vars, never written
  ```

### Missing Vault Access Permission

- Scripts fail silently if vault not accessible by authenticated user
- **FIX**: Always test access first: `op vault list`
- Ensure 1Password account has permission for target vault

### Secret Rotation Breaks Hardcoded References

- If storing `op://vault/item/field` in scripts, rotation requires updating all scripts
- **FIX**: Use vault structure that supports versioning: `op://vault/item-v2/field`

## 1Password CLI Essentials

### Authentication

**Sign In (First Time)**

```bash
# Interactive sign-in (asks for email, password, account URL)
eval $(op signin)

# Or programmatically (for CI/CD)
export OP_ACCOUNT=myaccount.1password.com
export OP_SIGNIN_ADDRESS=https://myaccount.1password.com
op signin --raw < <(echo "$OP_PASSWORD") > /tmp/op_token
export OP_SESSION_myaccount=$(cat /tmp/op_token)
rm /tmp/op_token  # Clean up immediately
```

**Verify Authentication**

```bash
# Check authenticated user and vault access
op whoami

# List accessible vaults
op vault list

# Test specific vault access
op vault get vault_name
```

### Reading Secrets

**Basic Secret Retrieval**

```bash
# Read field from item
op read op://vault_name/item_name/field_name

# Common usage: Read password field
op read op://personal/github/token

# Read username
op read op://personal/github/username

# Read entire item as JSON
op item get github --format=json
```

**Error Handling**

```bash
# Capture error if secret doesn't exist
secret=$(op read op://vault/item/field 2>/dev/null) || {
  echo "Secret not found" >&2
  exit 1
}
```

### Injecting Secrets into Commands

**Using `op run`** (Recommended - No Disk Traces)

```bash
# Method 1: Inject as environment variables
op run -- bash -c 'echo "API Key: $API_KEY"'

# Method 2: Use secrets in script
op run -- /path/to/script.sh

# Method 3: With explicit secret references
op run --env-file=<(echo "
API_KEY=op://prod/api/credentials/key
DB_PASSWORD=op://prod/database/password
") -- /deploy.sh
```

**Secrets Available in subprocess as env vars automatically**

```bash
# Create file with references
cat > env-secrets.txt << 'EOF'
API_KEY=op://prod/api/credentials/key
SLACK_WEBHOOK=op://work/slack/webhook
GITHUB_TOKEN=op://personal/github/token
EOF

# Pass to subprocess
op run --env-file=env-secrets.txt -- bash -c '
  echo "API Key: $API_KEY"
  curl -X POST "$SLACK_WEBHOOK" -d "Deployment started"
  git clone https://user:$GITHUB_TOKEN@github.com/repo.git
'
```

## Creating & Managing Secrets

### Creating New Items

```bash
# Create login item
op item create --template=login \
  --title="Production Database" \
  --vault=work \
  --username=dbadmin \
  --password='mypassword123'

# Create with additional fields
op item create --template=login \
  --title="API Credentials" \
  --vault=prod \
  --username=api_user \
  --password=$(openssl rand -base64 32) \
  --url=https://api.example.com

# Create password-only item (no username field)
op item create --template=password \
  --title="SSH Key Passphrase" \
  --vault=personal \
  --password=$(cat ~/.ssh/id_ed25519_passphrase)
```

### Editing Items

```bash
# Edit existing item (interactive prompt)
op item edit github

# Set field value directly
op item edit item_name username=newuser

# Update password
op item edit prod_db password=$(openssl rand -base64 32)
```

### Vault Organization

**Recommended Vault Structure**

```text
personal/
  ssh-key/
    private_key
    public_key

work/
  github/
    token
    username
  slack/
    webhook

prod/
  database/
    password
    username
    host
  api/
    key
    secret

audit/
  deployment-logs/
  system-inventory/
```

## SSH Key Management via 1Password

### Storing SSH Keys Securely

```bash
# Generate SSH key (if needed)
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519 -N ""

# Store public key in 1Password for reference
op item create --template=login \
  --title="SSH Key (Production)" \
  --vault=personal \
  --username="$(hostname)-user" \
  --password="$(cat ~/.ssh/id_ed25519)" \
  --url="ssh://prod.example.com"

# Store associated public key for audit
op item edit "SSH Key (Production)" \
  --custom-field="public_key[text]=$(cat ~/.ssh/id_ed25519.pub)"
```

### Using SSH Keys from 1Password

```bash
#!/bin/bash
# ssh-with-1password.sh - SSH using key stored in 1Password

set -euo pipefail

VAULT="personal"
ITEM="SSH Key (Production)"
HOST="prod.example.com"
COMMAND="${1:-}"

# Fetch private key from 1Password
private_key=$(op read "op://$VAULT/$ITEM/password")

# Write to temporary file with exact permissions
temp_key=$(mktemp)
chmod 0600 "$temp_key"
echo "$private_key" > "$temp_key"
trap "rm -f $temp_key" EXIT

# SSH with key
if [ -z "$COMMAND" ]; then
  ssh -i "$temp_key" user@"$HOST"
else
  ssh -i "$temp_key" user@"$HOST" "$COMMAND"
fi
```

### SSH Agent Integration

```bash
# Configure 1Password to provide SSH keys via agent
# (Only works with 1Password 7 Desktop app running)

export SSH_AUTH_SOCK=/run/user/$(id -u)/1password/agent.sock

# Now SSH automatically uses 1Password-managed keys (no passphrase needed)
ssh user@host

# Verify agent is working
ssh-add -l  # Should list 1Password-managed keys
```

## Advanced Patterns

### Secrets for CI/CD

**GitHub Actions**

```yaml
name: Deploy
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Authenticate to 1Password
        uses: 1Password/connect-action@v1
        with:
          connect-host: ${{ secrets.OP_CONNECT_HOST }}
          connect-token: ${{ secrets.OP_CONNECT_TOKEN }}

      - name: Deploy with secrets
        run: |
          op run -- bash -c '
            export API_KEY=$(op read op://prod/api/key)
            ./deploy.sh
          '
```

**GitLab CI**

```yaml
deploy:
  image: 1password/op:latest
  script:
    - export OP_SIGNIN_ADDRESS=$OP_ACCOUNT
    - echo "$OP_PASSWORD" | op signin --raw
    - op run -- bash -c '
      export DB_PASSWORD=$(op read op://prod/database/password)
      ./deploy.sh
      '
  secrets:
    OP_ACCOUNT:
      vault: gitlab
    OP_PASSWORD:
      vault: gitlab
```

### Batch Operations on Multiple Secrets

```bash
#!/bin/bash
# Rotate all API keys in vault

set -euo pipefail

VAULT="prod"

# Get all items in vault
op item list --vault="$VAULT" --format=json | jq -r '.[].id' | while read item_id; do
  item_name=$(op item get "$item_id" --format=json | jq -r '.title')

  # Check if this is an API key item
  if [[ "$item_name" == *"API"* ]]; then
    # Generate new key
    new_key=$(openssl rand -base64 32)

    # Update in 1Password
    op item edit "$item_name" password="$new_key"

    echo "Rotated: $item_name"
  fi
done
```

### Storing Deployment Artifacts

```bash
#!/bin/bash
# Store deployment results in 1Password audit vault

DEPLOY_DATE=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
BUILD_LOG="$1"
STATUS="${2:-SUCCESS}"

# Read deployment log
log_content=$(cat "$BUILD_LOG" || echo "No log file")

# Create 1Password item
op item create --template=login \
  --title="Deployment $DEPLOY_DATE" \
  --vault=audit \
  --username="$STATUS" \
  --password="$log_content" \
  --custom-field="build_date[date]=$(date -u +%s)"
```

## Troubleshooting

### "Invalid vault"

```text
Error: vault 'my-vault' not found
```

**Fix**: List available vaults and use exact name

```bash
op vault list
op vault get my-vault  # Verify vault accessible
```

### "Permission denied" on Secret Read

```text
Error: You don't have permission to read this secret
```

**Fix**: Check vault access

```bash
op whoami  # Verify authenticated
op vault list  # Check vault accessible

# If vault listed but still denied, restart daemon
killall op-daemon
sleep 2
op read op://vault/item/field
```

### Secrets Not Injected in CI/CD

```text
Error: API_KEY environment variable empty
```

**Fix**: Verify 1Password authentication in CI

```bash
# Test authentication
op whoami

# Test reading secret manually
op read op://vault/item/field

# If fails, check credentials in CI/CD environment
echo $OP_SIGNIN_ADDRESS
echo $OP_ACCOUNT
```

### SSH Key Permission Errors

```text
Error: Permissions 0644 for id_ed25519 are too open
```

**Fix**: Ensure key file has exactly 0600 permissions

```bash
chmod 0600 ~/.ssh/id_ed25519
ls -la ~/.ssh/id_ed25519  # Verify: -rw------- (0600)
```

## Integration Examples

### Deploy with Database Migration

```bash
#!/bin/bash
# deploy-with-migration.sh - Deploy app with secrets from 1Password

set -euo pipefail

# Authenticate to 1Password
eval $(op signin)

# Use op run to inject all secrets
op run -- bash -c '
  # Secrets injected as env vars: API_KEY, DB_PASSWORD, SLACK_WEBHOOK

  echo "Starting deployment..."

  # Run database migration
  export DB_PASSWORD=$(op read op://prod/database/password)
  ./scripts/migrate-db.sh

  # Deploy application
  docker push myapp:latest
  kubectl set image deployment/app app=myapp:latest

  # Notify team
  slack_webhook=$(op read op://work/slack/webhook)
  curl -X POST -d "Deployment completed" "$slack_webhook"

  echo "Deployment successful"
'
```

### Monitor and Alert

```bash
#!/bin/bash
# monitor.sh - Check server health and alert via Slack

set -euo pipefail

eval $(op signin)

op run -- bash -c '
  # Check server status
  if ! ping -c 1 -W 5 production.example.com &> /dev/null; then
    # Server down, fetch webhook and send alert
    slack_webhook=$(op read op://work/slack/webhook)
    curl -X POST -d "{\"text\": \"ALERT: Production server down!\"}" \
      -H "Content-Type: application/json" \
      "$slack_webhook"
  fi
'
```

## Summary

- **Never store secrets in files**—use `op run --` to inject as env vars
- **Secret references are immutable**—plan naming scheme in advance
- **SSH keys must be 0600**—test with `ls -la`
- **Restart daemon if stale**: `killall op-daemon`
- **Verify vault access**: `op vault list` before scripting
- **Use `op://vault/item/field` syntax** for all secret references
- **Rotate secrets regularly** by updating in 1Password vault
- **Store API credentials, SSH keys, database passwords** in separate vaults for audit
