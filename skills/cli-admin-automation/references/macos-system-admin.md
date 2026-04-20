# macOS System Administration

## Critical Gotchas (Read First)

### Defaults Write Silent Failures

- `defaults write` doesn't validate syntax. Typos silently ignored, setting never applied
- **FIX**: Always verify with `defaults read`:

  ```bash
  defaults write com.apple.dock autohide -bool true
  defaults read com.apple.dock autohide  # Verify it was set
  ```

### Changes Don't Apply Immediately

- Some defaults require process restart (Finder, Dock, etc.) to take effect
- **FIX**: Kill the process after writing default

  ```bash
  defaults write com.apple.finder ShowHiddenFiles -bool true
  killall Finder  # Force restart
  ```

### System Integrity Protection (SIP)

- Many settings require user approval or SIP disabling
- **DANGER**: Disabling SIP requires restart into Recovery mode—not scriptable in CI
- **FIX**: Use only non-SIP settings, or provide manual steps for sensitive changes

### m-cli Requires CLI Tools

- m-cli depends on XCode Command Line Tools
- **FIX**: Install first: `xcode-select --install`

## m-cli Essential Commands

### System Information

```bash
# Show basic system info
m system info

# Example output:
# System:
#  Model Name: MacBook Pro
#  OS Version: 13.5
#  Processor: M2 Max

# Show specific info
m system name
m system cpu
m system memory
m system volume
```

### Battery & Power

```bash
# Show battery status
m battery

# Example output:
# Battery:
#  Current Charge: 85%
#  Health: Normal
#  Condition: Normal

# Get specific value
m battery health
m battery percentage
```

### WiFi Management

```bash
# Show connected WiFi
m wifi

# Show WiFi information
m wifi name                    # Current network name
m wifi password               # Show network password (careful!)

# Connect to WiFi network
m wifi connect SSID password  # Requires sudo in most cases

# List nearby networks
m wifi scan
```

### Dock Management

```bash
# Show dock items
m dock show

# Add app to dock
m dock add "/Applications/Visual Studio Code.app"

# Remove app from dock
m dock remove "Slack"

# Set dock size
m dock size 40

# Enable autohide
m dock autohide true
```

### Finder Settings

```bash
# Show hidden files
m finder show hidden

# Hide hidden files
m finder hide hidden

# Show path bar in Finder
m finder show path

# Show full POSIX path in Finder title
m finder show desktop
```

### Volume & Sound

```bash
# Show volume
m volume

# Set volume to specific level (0-100)
m volume 50

# Mute
m volume mute

# Unmute
m volume unmute

# Get volume level programmatically
volume=$(m volume | grep -oE '[0-9]+%' | tr -d '%')
echo "Current volume: $volume"
```

## Using `defaults write` Directly

### Common Useful Defaults

**Finder Settings**

```bash
# Show hidden files
defaults write com.apple.finder AppleShowAllFiles -bool true

# Show file extensions
defaults write NSGlobalDomain AppleShowAllExtensions -bool true

# Use list view by default
defaults write com.apple.finder FXPreferredViewStyle -string "Nlsv"
```

**Dock Settings**

```bash
# Auto-hide dock
defaults write com.apple.dock autohide -bool true

# Show dock on right side
defaults write com.apple.dock orientation -string right

# Set dock size (in pixels)
defaults write com.apple.dock tilesize -int 64

# Remove delay when showing dock
defaults write com.apple.dock autohide-delay -float 0

# Apply changes
killall Dock
```

**Safari Settings**

```bash
# Show full URL in address bar
defaults write com.apple.Safari ShowFullURLInSmartSearchField -bool true

# Enable developer tools
defaults write com.apple.Safari IncludeDevelopMenu -bool true
defaults write com.apple.Safari WebKitDeveloperExtensionsEnabledPreferenceKey -bool true

# Privacy: don't send search queries to Apple
defaults write com.apple.Safari UniversalSearchEnabled -bool false
```

**System Performance**

```bash
# Disable Spotlight indexing on external drives
defaults write /Library/Preferences/com.apple.SpotlightServer.plist ExternalVolumesDefaultPrivacy -array "/Volumes/*"

# Disable animations for accessibility
defaults write com.apple.universalaccess reduceMotionEnabled -bool true

# Faster keyboard repeat rate
defaults write NSGlobalDomain KeyRepeat -int 2
defaults write NSGlobalDomain InitialKeyRepeat -int 25
```

### Reading Defaults

```bash
# Read single setting
defaults read com.apple.dock autohide

# List all settings for app
defaults read com.apple.finder

# Find if setting exists
defaults read com.apple.finder | grep -i hidden

# Export all defaults to file (backup)
defaults read > ~/defaults-backup.plist

# Compare before/after
defaults read > before.plist
# Make changes
killall Finder
defaults read > after.plist
diff before.plist after.plist
```

## Batch macOS Configuration

### Full Setup Script

```bash
#!/bin/bash
set -euo pipefail

# Install Xcode command line tools (prerequisite for m-cli)
xcode-select --install 2>/dev/null || true

# Install m-cli if not present
if ! command -v m &> /dev/null; then
  curl -fsSL https://raw.githubusercontent.com/rgcr/m-cli/master/install.sh | bash
fi

# System settings
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write NSGlobalDomain AppleShowAllExtensions -bool true
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock orientation -string bottom

# Apply changes
killall Finder
killall Dock

# Verify settings
echo "Finder hidden files: $(defaults read com.apple.finder AppleShowAllFiles)"
echo "Dock autohide: $(defaults read com.apple.dock autohide)"

# Store in 1Password for team (optional)
export SETUP_DATE=$(date)
op item create --template=login \
  --title="macOS Setup $SETUP_DATE" \
  --vault=Audit \
  --username="$(hostname)" \
  --password="Setup completed successfully"
```

### Team Provisioning Template

```bash
#!/bin/bash
# team-provision.sh - Configure macOS for development team

set -euo pipefail

# Step 1: Install Homebrew and core tools
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Step 2: Install from Brewfile
export HOMEBREW_NO_ANALYTICS=1
export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)
brew bundle install --file Brewfile

# Step 3: Configure system defaults
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock tilesize -int 48

# Step 4: Set up SSH key from 1Password
mkdir -p ~/.ssh
op read op://personal/ssh-key/private_key > ~/.ssh/id_ed25519
chmod 0600 ~/.ssh/id_ed25519  # CRITICAL: Must be exactly 0600

# Step 5: Restart UI
killall Finder Dock

echo "macOS provisioning complete. Please restart your machine."
```

## Troubleshooting

### "NSGlobalDomain" not Found

```bash
# Problem: defaults read shows no results for NSGlobalDomain
# Cause: Domain uses different internal name

# Fix: Use full path
defaults read -g  # -g for global domain
defaults write -g AppleShowAllExtensions -bool true
```

### Dock Won't Update After killall

```bash
# Problem: killall Dock doesn't immediately update display
# Cause: Dock restarting asynchronously

# Fix: Add delay
killall Dock
sleep 2
# Or use launchctl
launchctl stop com.apple.Dock.agent
launchctl start com.apple.Dock.agent
```

### SIP Prevents Setting

```bash
# Problem: "Operation not permitted" when writing default
# Cause: System Integrity Protection blocks the setting

# Fix: Either disable SIP (requires Recovery mode) or choose different setting
# Check if setting is SIP-protected:
csrutil status
```

## Integration with 1Password

### SSH Key Setup from 1Password

```bash
# Fetch SSH private key from 1Password vault
op read op://personal/ssh-key/private_key > ~/.ssh/id_ed25519

# CRITICAL: SSH requires exactly 0600 permissions
chmod 0600 ~/.ssh/id_ed25519

# Verify permissions
ls -la ~/.ssh/id_ed25519  # Should show: -rw------- (0600)

# Test SSH connection
ssh -i ~/.ssh/id_ed25519 user@host

# Store key reference in 1Password agent for automatic SSH (no passphrase typing)
export SSH_AUTH_SOCK=/run/user/$(id -u)/1password/agent.sock
ssh user@host  # Now uses 1Password agent automatically
```

## Summary

- **Always verify** `defaults write` with `defaults read`
- **Kill processes** after changing defaults for immediate effect
- **Use m-cli** for common macOS tasks (simpler than defaults write)
- **Check SIP status** before attempting protected settings
- **Store SSH keys** with exactly 0600 permissions (test with `ls -la`)
- **Backup defaults** before batch changes: `defaults read > backup.plist`
- **Test on one machine** before deploying to team
