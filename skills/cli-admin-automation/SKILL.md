---
name: cli-admin-automation
description: Automate system administration workflows on macOS and Linux. Use this skill when: setting up reproducible dev environments (Brewfile), parsing CLI command output programmatically (jc + jq), monitoring remote servers via SSH with alerts, integrating API keys and secrets securely (1Password CLI), building automation workflows (Cherri Siri Shortcuts programming), or batch-managing system configurations. Covers package management (Homebrew), structured JSON parsing (jc), SSH-based remote administration, secure credential injection, cross-platform multi-step automation, and fleet monitoring.
compatibility: "Requires: macOS 10.15+ or Linux with SSH; optional: jc, Homebrew, 1Password CLI, Cherri"
metadata:
  version: "1.0"
  primary_platforms: "macOS,Linux"
  integrations: "jc,Homebrew,1Password CLI,Cherri,m-cli"
---

# CLI Administration & Automation

## Overview

This skill provides integrated patterns for **secrets-first CLI administration** across macOS and Linux systems. It combines five core tools:

- **jc**: Transform CLI command output to structured JSON for programmatic parsing
- **Homebrew**: Reproducible package management with Brewfile for team environments
- **1Password CLI**: Secrets as first-class citizens in scripts (not hardcoded)
- **Cherri**: Siri Shortcuts programming language for sophisticated automation
- **m-cli**: macOS system administration toolkit (30+ commands)

### Core Integration Pattern

```text
command | jc → JSON | jq filter → conditional logic → 1Password inject → Cherri automate
```

Use this skill when you need to:

- Parse CLI command output programmatically
- Manage dependencies reproducibly across teams
- Integrate credentials securely into automation
- Monitor remote systems and trigger alerts
- Build deterministic infrastructure-as-code workflows

## Module Index

**Read `references/` modules when the user asks about:**

- **cli-foundations.md**: Shell basics, pipes, quoting, keybindings (prerequisite for others)
- **jc-parser-reference.md**: Parsing command output (ps, netstat, df, etc.) with jq filtering
- **homebrew-workflows.md**: Package management, Brewfile setup, team environments
- **macos-system-admin.md**: macOS-specific CLI (m-cli, defaults write, launchd)
- **linux-remote-admin.md**: SSH-based Linux admin, package managers, systemctl
- **cherri-automation.md**: Siri Shortcuts programming, multi-step workflows
- **1password-secrets.md**: Secret references, credential rotation, vault management

## Critical Gotchas

These non-obvious issues cause most failures. Read them first.

### jc

- Locale affects output sorting. Use `LC_ALL=C` for reproducibility across systems.
- Timezone-aware parsing varies by jc version. Test with specific jc version pinned.

### Homebrew

- Tap authentication requires GitHub token (not plaintext). Store token in 1Password vault, not `~/.gitconfig`.
- `HOMEBREW_NO_ANALYTICS=1` is a hidden environment variable; not set by default.

### 1Password CLI

- Caching daemon may stale on permission changes. Restart daemon if secret reads fail unexpectedly.
- Secret references (`op://vault/item/field`) are immutable after creation. Changing reference syntax requires creating new item.

### Cherri

- macOS-only. No Linux equivalent. Reference AppleScript for legacy macOS automation.
- Compiles to binary `.shortcut` format (human-unreadable). Development cycle slower than Shortcuts.app GUI.

### SSH

- Key-based authentication preferred. Use 1Password CLI agent for key storage (not `~/.ssh/config` plaintext).
- SSH key permissions must be exactly `0600`. Mismatched permissions cause silent auth failures.

## Quick Command Reference

### jc (Top 5 Parsers)

```bash
ps aux | jc --ps | jq '.[] | select(.comm == "node")'    # Find specific process
df -h | jc --df | jq '.[] | select(.use_percent > 80)'   # Find full disks
netstat -an | jc --netstat | jq '.[] | select(.state == "ESTABLISHED")'  # Active connections
ls -la | jc --ls | jq '.[] | select(.size > 1000000)'    # Find large files
git log --oneline | jc --git-log | jq '.[] | .commit'    # Parse git history
```

### Homebrew

```bash
brew install <formula>          # Install package
brew bundle install             # Install from Brewfile
brew tap <owner>/<repo>         # Add third-party tap
brew list                        # List installed packages
brew cleanup                     # Remove old versions
```

### 1Password CLI

```bash
op read op://vault/item/field    # Read secret field
op run -- command               # Pass secrets as env vars to subprocess
op item get ItemName            # Retrieve item details (JSON)
op vault list                   # List available vaults
```

### m-cli (macOS System)

```bash
m battery                        # Show battery status
m wifi                           # Show WiFi status
m disk                           # Show disk usage
m dock add <app>                # Add app to dock
m system info                   # Show system information
```

## Workflows

### Scenario 1: Reproducible Team Environment (Brewfile + Validation)

```bash
# 1. Create Brewfile in project root (macOS)
brew bundle dump --file Brewfile

# 2. Team members install identical packages
brew bundle install --file Brewfile

# 3. Validate installation (see references/homebrew-workflows.md)
bash scripts/parse-homebrew-bundle.sh Brewfile --check

# 4. Troubleshoot: Run Brewfile against specific GitHub token (if private taps)
export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)
brew bundle install --file Brewfile --verbose
```

**Use when**: Setting up dev environments, CI/CD containers, standardizing across team, or managing private taps with authentication.

**Common issues:**

- GitHub token not exported → taps fail silently
- `brew bundle` picks wrong Brewfile if multiple exist → use explicit `--file`
- Cask apps installed via tap require native GUI → fails in headless CI

### Scenario 2: Remote Server Health Monitoring (SSH + jc + Alerts)

```bash
# 1. SSH to remote, parse output with jc
ssh user@remote 'ps aux' | jc --ps | jq '.[] | select(.cpu_percent > 50)'

# 2. Store result in variable
high_cpu=$(ssh user@remote 'ps aux' | jc --ps | jq '.[] | select(.cpu_percent > 50)' | wc -l)

# 3. Conditionally fetch alert credentials from 1Password (see references/1password-secrets.md)
if [ "$high_cpu" -gt 5 ]; then
  slack_webhook=$(op read op://work/slack/webhook)
  curl -X POST -d "High CPU detected: $high_cpu processes" "$slack_webhook"
fi

# 4. For fleet monitoring, loop over servers with error handling
for host in server1 server2 server3; do
  status=$(ssh -o ConnectTimeout=5 user@"$host" 'df -h' | jc --df | jq '.[] | select(.use_percent > 80) | .filesystem' || echo "OFFLINE")
  echo "$host: $status"
done
```

**Use when**: Monitoring fleets, automating health checks, triggering alerts on conditions, batch diagnostics.

**Common issues:**

- SSH key perms wrong (not exactly 0600) → silent auth failures
- jc output differs by locale → use `LC_ALL=C` for consistency
- `op read` fails if caching daemon stale → restart: `killall op-daemon`

### Scenario 3: Automated Deployment with Secrets (1Password + Validation)

```bash
# 1. Create deployment plan with placeholders
cp deployment-template.yaml deployment-plan.yaml

# 2. Fetch secrets from 1Password and inject (never hardcode!)
op read op://prod/db/password > /tmp/db_pass
sed -i "s|DB_PASSWORD|$(cat /tmp/db_pass)|" deployment-plan.yaml

# 3. Validate plan before executing
cat deployment-plan.yaml | jq .   # Ensure valid JSON

# 4. Clean up secret from disk (critical!)
shred -vfz /tmp/db_pass 2>/dev/null || rm /tmp/db_pass

# 5. Execute deployment
kubectl apply -f deployment-plan.yaml
```

**Use when**: Infrastructure deployments, credential-protected workflows, multi-step automation, secret rotation.

**Common issues:**

- Secret files left in `/tmp` after script exit → secrets visible in process history
- `op://` reference syntax changed → immutable after creation, must create new item
- Mixing `op read` with shell expansion → loses indentation in YAML

### Scenario 4: Multi-Step Cherri Automation (Siri Shortcuts Integration)

```bash
# 1. Write Cherri script for complex conditionals
cat > backup-automation.cherri << 'EOF'
func backupWithRetry(source: String, destination: String) -> Bool {
  var attempts = 0
  while attempts < 3 {
    if executeCommand("rsync -av \(source) \(destination)") {
      return true
    }
    attempts += 1
  }
  return false
}
EOF

# 2. Compile to .shortcut binary (macOS only)
cherri compile backup-automation.cherri -o backup-automation.shortcut

# 3. Execute from shell with secret injection
op run -- open -a Shortcuts backup-automation.shortcut
```

**Use when**: macOS-specific automation, conditional retry logic, GUI automation within scripts.

**Critical:** Cherri is macOS-only. For Linux, use Bash functions or Python instead.

### Scenario 5: Batch System Configuration (m-cli + Defaults Write)

```bash
# 1. List current macOS settings via m-cli
m wifi                              # Show WiFi name
m battery status                    # Show battery level
m dock autohide                     # Check dock autohide

# 2. Batch-set defaults (requires user approval for some)
defaults write com.apple.dock autohide -bool true
defaults write com.apple.finder ShowHiddenFiles -bool true
defaults write com.apple.Safari HistoryDeletionBehavior 2

# 3. Apply system-wide changes
killall Finder                      # Restart Finder to apply
killall Dock                        # Restart Dock to apply
```

**Use when**: Provisioning macOS machines, standardizing dev configs, batch system administration.

**Common issues:**

- Some defaults require restart to apply
- `defaults write` doesn't validate syntax → typos silently ignored
- User approval required for accessibility/privacy changes → can't automate

### Scenario 6: Cross-Platform CLI Output Parsing (jc with Multiple Formats)

```bash
# 1. Parse multiple command outputs into consistent JSON
{
  ps=$(ps aux | jc --ps | jq '.[] | {pid, cmd: .command, cpu: .cpu_percent}')
  disk=$(df -h | jc --df | jq '.[] | {filesystem, use_percent}')
  net=$(netstat -an | jc --netstat | jq '.[] | {proto: .protocol, state}')
  echo "{processes: $ps, disks: $disk, network: $net}" | jq .
}

# 2. On Linux, compare outputs across distributions
# jc parsing differs slightly: Debian df vs RHEL df
ssh debian-host 'df -h' | jc --df > debian-df.json
ssh rhel-host 'df -h' | jc --df > rhel-df.json
diff <(jq '.[] | .filesystem' debian-df.json) <(jq '.[] | .filesystem' rhel-df.json)

# 3. Store normalized results in 1Password for audit
op item create --template=login --title="Disk Report $(date)" --vault=Audit
```

**Use when**: Cross-platform inventory, compliance reporting, multi-system diagnostics.

---

## Progress

- [x] Phase 1: Description optimization (trigger queries, multi-run testing)
- [x] Phase 2: Master SKILL.md + quick reference
- [x] Phase 3: Write reference modules (7 files)
- [x] Phase 4: Create scripts (4 executable files)
- [x] Phase 5: Evaluation setup (6 quality cases + trigger query sets)
- [ ] Phase 6: Validate & iterate (pass rates, timing, baseline comparison)
