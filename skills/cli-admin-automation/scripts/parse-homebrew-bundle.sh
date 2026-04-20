#!/bin/bash
# parse-homebrew-bundle.sh - Analyze and validate Homebrew Brewfile

set -euo pipefail

# Help text
show_help() {
  cat << 'EOF'
Usage: parse-homebrew-bundle.sh <brewfile> [--check|--report|--dry-run]

Analyze and validate Homebrew Brewfile for team environments.

Modes:
  --check      Verify all packages in Brewfile are installed (exit code 0 if all installed, 1 if missing)
  --report     Generate JSON report of package status
  --dry-run    Show what would be installed without actually installing

Examples:
  parse-homebrew-bundle.sh Brewfile --check
  parse-homebrew-bundle.sh Brewfile --report > status.json
  parse-homebrew-bundle.sh Brewfile --dry-run

Exit codes:
  0  All packages installed or operation successful
  1  Missing packages or brewfile error

Output (JSON):
  {"status": "complete", "installed": N, "missing": [], "errors": []}
EOF
}

# Parse arguments
BREWFILE="${1:-Brewfile}"
MODE="${2:-}"

if [ -z "$MODE" ]; then
  MODE="--check"
fi

if [ "$MODE" = "--help" ] || [ "$MODE" = "-h" ]; then
  show_help
  exit 0
fi

# Validate brewfile exists
if [ ! -f "$BREWFILE" ]; then
  echo "{\"error\": \"Brewfile not found: $BREWFILE\"}" | jq .
  exit 1
fi

# Parse brewfile and extract packages
parse_packages() {
  local file="$1"
  grep -E "^brew|^cask|^tap|^mas" "$file" | sed 's/^[a-z]*[[:space:]]*"\([^"]*\)".*/\1/' | grep -v '^#'
}

# Check if package installed
is_installed() {
  local pkg="$1"
  local type="$2"

  case "$type" in
    "brew")
      brew list "$pkg" &>/dev/null && return 0 || return 1
      ;;
    "cask")
      brew list --cask "$pkg" &>/dev/null && return 0 || return 1
      ;;
    "tap")
      brew tap | grep -q "^$pkg$" && return 0 || return 1
      ;;
    *)
      return 1
      ;;
  esac
}

# Determine package type
get_package_type() {
  local line="$1"

  if echo "$line" | grep -q '^brew'; then
    echo "brew"
  elif echo "$line" | grep -q '^cask'; then
    echo "cask"
  elif echo "$line" | grep -q '^tap'; then
    echo "tap"
  elif echo "$line" | grep -q '^mas'; then
    echo "mas"
  else
    echo "unknown"
  fi
}

# Main logic

case "$MODE" in
  "--check")
    # Check mode: verify all packages installed
    missing=()
    total=0

    while IFS= read -r line; do
      [ -z "$line" ] && continue
      pkg_name=$(echo "$line" | sed 's/^[a-z]*[[:space:]]*"\([^"]*\)".*/\1/')
      pkg_type=$(get_package_type "$line")
      total=$((total + 1))

      if ! is_installed "$pkg_name" "$pkg_type"; then
        missing+=("$pkg_name")
      fi
    done < <(grep -E "^brew|^cask|^tap|^mas" "$BREWFILE" | grep -v '^#')

    if [ ${#missing[@]} -eq 0 ]; then
      echo "{\"status\": \"complete\", \"total\": $total, \"missing\": []}"
      exit 0
    else
      echo "{\"status\": \"incomplete\", \"total\": $total, \"missing\": [$(printf '\"%s\",' "${missing[@]}" | sed 's/,$//')], \"count\": ${#missing[@]}}" | jq .
      exit 1
    fi
    ;;

  "--report")
    # Report mode: generate JSON status for all packages
    echo "{"
    echo '  "brewfile": "'"$BREWFILE"'",'
    echo '  "timestamp": "'"$(date -u +%Y-%m-%dT%H:%M:%SZ)"'",'
    echo '  "packages": ['

    first=true
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      pkg_name=$(echo "$line" | sed 's/^[a-z]*[[:space:]]*"\([^"]*\)".*/\1/')
      pkg_type=$(get_package_type "$line")

      if [ "$first" = false ]; then
        echo ","
      fi
      first=false

      if is_installed "$pkg_name" "$pkg_type"; then
        status="installed"
      else
        status="missing"
      fi

      printf '    {"name": "%s", "type": "%s", "status": "%s"}' "$pkg_name" "$pkg_type" "$status"
    done < <(grep -E "^brew|^cask|^tap|^mas" "$BREWFILE" | grep -v '^#')

    echo ""
    echo "  ]"
    echo "}"
    exit 0
    ;;

  "--dry-run")
    # Dry-run mode: show what would be installed
    echo "{\"dry_run\": true, \"brewfile\": \"$BREWFILE\", \"would_install\": [" >&2

    first=true
    while IFS= read -r line; do
      [ -z "$line" ] && continue
      pkg_name=$(echo "$line" | sed 's/^[a-z]*[[:space:]]*"\([^"]*\)".*/\1/')
      pkg_type=$(get_package_type "$line")

      if ! is_installed "$pkg_name" "$pkg_type"; then
        if [ "$first" = false ]; then
          echo "," >&2
        fi
        first=false
        printf '  {"name": "%s", "type": "%s"}' "$pkg_name" "$pkg_type" >&2
      fi
    done < <(grep -E "^brew|^cask|^tap|^mas" "$BREWFILE" | grep -v '^#')

    echo "" >&2
    echo "]}" >&2

    # Show brew bundle command that would be run
    echo "Command: brew bundle install --file $BREWFILE"
    exit 0
    ;;

  *)
    echo "Unknown mode: $MODE" >&2
    show_help
    exit 1
    ;;
esac
