# Homebrew Workflows

## Critical Gotchas (Read First)

### GitHub Token Authentication (Silent Failures)

- Private taps require GitHub authentication. Without token, tap fails silently (no error)
- **DANGER**: Storing token in `.gitconfig` or scripts = credential leak
- **FIX**: Store token in 1Password vault, export before running brew

  ```bash
  export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)
  brew bundle install --file Brewfile
  ```

- **Verify**: Run `brew tap list` after setting token; if private tap missing, token not set

### Brewfile Version Mismatches

- Brewfile format changed between Homebrew versions (v3.0 vs v4.0)
- **FIX**: Don't commit Brewfile without version lock: `brew bundle dump --file Brewfile --describe`
- Pin versions in Brewfile:

  ```text
  brew "node@16"    # Specific version
  brew "yarn"       # Latest
  ```

### Cask vs Formula Distinction

- Formulas = CLI tools (installed to `/usr/local/bin`)
- Casks = GUI apps (installed to `/Applications`) - requires user approval in CI
- **FIX**: In CI environments, set `HOMEBREW_NO_INSTALL_CLEANUP=1` and skip casks

### Analytics and Telemetry

- Homebrew sends analytics by default (slows down CI)
- **FIX**: Disable explicitly: `export HOMEBREW_NO_ANALYTICS=1`
- Add to CI: `HOMEBREW_NO_ANALYTICS=1 brew bundle install`

## Brewfile Format

### Basic Structure

```bash
# Formulae (CLI tools)
brew "node"
brew "node@16"         # Specific major version
brew "git"
brew "jq"

# Taps (third-party repositories)
tap "homebrew/cask-versions"
tap "owner/private-repo", "https://github.com/owner/private-repo"  # Private tap with URL

# Casks (GUI applications)
cask "docker"
cask "vscode"
cask "slack"

# Mac App Store applications (requires mas-cli)
mas "Xcode", id: 497799835
mas "1Password 7", id: 1352778147

# Optional: brewfile options
options no_lock: true    # Don't create lock file
```

### Private Tap Example

```bash
# In Brewfile
tap "myorg/tools"

# Before running brew bundle:
export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)
brew bundle install --file Brewfile
```

## Common Commands

### Creating Brewfile

```bash
# Generate from current installation
brew bundle dump --file Brewfile --describe

# --describe adds comments explaining each package
# Useful for team onboarding
```

### Installing from Brewfile

```bash
# Install all packages from Brewfile
brew bundle install --file Brewfile

# Verbose output (shows each package as it installs)
brew bundle install --file Brewfile --verbose

# Simulate (dry-run) to see what would install
brew bundle install --file Brewfile --no-upgrade --no-cleanup --verbose
```

### Checking Installation Status

```bash
# Show what's missing/outdated
brew bundle check --file Brewfile

# Output shows: missing formula, outdated package, unexpected package

# Or script to check programmatically
bash scripts/parse-homebrew-bundle.sh Brewfile --check
```

### Updating Packages

```bash
# Update all formulas
brew bundle install --file Brewfile --upgrade

# Update specific formula only
brew upgrade node

# List outdated packages
brew outdated
```

### Cleaning Up

```bash
# Remove packages not in Brewfile
brew bundle cleanup --file Brewfile --force

# Removes older versions
brew cleanup

# Free disk space
brew cleanup --prune=all
```

## Team Environment Setup

### Reproducible Team Deps (Full Workflow)

**Step 1: Generate Brewfile from lead machine**

```bash
brew bundle dump --file Brewfile --describe
git add Brewfile Brewfile.lock
git commit -m "Add team dependencies"
git push
```

**Step 2: Team member installs**

```bash
cd project
export HOMEBREW_NO_ANALYTICS=1
export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)  # If using private taps
brew bundle install --file Brewfile
```

**Step 3: Validate installation**

```bash
# Check all packages installed
brew bundle check --file Brewfile

# Or use provided script
bash scripts/parse-homebrew-bundle.sh Brewfile --check
```

**Step 4: CI/CD integration**

```yaml
# GitHub Actions example
name: Setup
jobs:
  build:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: |
          export HOMEBREW_NO_ANALYTICS=1
          brew bundle install --file Brewfile
```

## Advanced Patterns

### Conditional Package Installation

```bash
# Install different packages by OS
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS only
  brew install iterm2
else
  # Linux
  apt install iterm2-equivalent
fi
```

### Dependency Linking (for Development)

```bash
# After installing package, link it to use in project
brew install postgresql@11

# Link to make available in PATH
brew link postgresql@11 --force

# Or use directly
/usr/local/opt/postgresql@11/bin/psql --version
```

### Multiple Brewfile Variants

```bash
# Team baseline (Brewfile)
# Development additions (Brewfile.dev)
# CI/CD minimal (Brewfile.ci)

# Install with overrides
brew bundle install --file Brewfile
brew bundle install --file Brewfile.dev  # Additive
```

## Troubleshooting

### "tap not found" with Private Repo

```bash
# Problem: Private tap missing after brew bundle install
# Cause: GitHub token not exported

# Fix: Set token and retry
export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)
brew tap myorg/tools  # Test tap manually first
brew bundle install --file Brewfile
```

### "Permission denied" on Cask Installation

```bash
# Problem: Cask install fails with permission error
# Cause: GUI app requires user approval, or file permission issue

# Fix: Run without casks in CI, skip in automation
brew bundle install --file Brewfile --skip=cask
```

### Locale/Build Failures

```bash
# Problem: Formula fails to build (compiler error, locale issue)
# Cause: Missing dependencies or build tools

# Fix: Install Xcode command line tools
xcode-select --install

# Or precompiled binary
brew install -v formula  # -v for verbose; shows what's happening
```

## Integration with 1Password

### Storing Installation Evidence

```bash
# After installation, create 1Password record
installed_date=$(date)
versions=$(brew list --versions)

op item create --template=login \
  --title="Homebrew Setup $installed_date" \
  --vault=Audit \
  --username="$(hostname)" \
  --password="Installed ${#versions[@]} packages"
```

### Using Secrets in Brewfile

```bash
# Brewfile can't directly reference 1Password
# So instead: inject secrets at runtime

export HOMEBREW_GITHUB_TOKEN=$(op read op://work/github/token)
export HOMEBREW_GITHUB_API_TOKEN=$(op read op://work/github/api-token)
brew bundle install --file Brewfile
```

## Summary

- **Always set `HOMEBREW_GITHUB_TOKEN`** before private taps
- **Disable analytics in CI**: `export HOMEBREW_NO_ANALYTICS=1`
- **Pin versions** in Brewfile for reproducibility
- **Use `brew bundle check`** to validate installation
- **Store Brewfile** in version control with lock file
- **Skip casks in CI/CD** environments (require GUI approval)
- **Test Brewfile locally** before committing to team
