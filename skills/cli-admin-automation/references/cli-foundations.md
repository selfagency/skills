# CLI Foundations

## Critical Gotchas (Read First)

### Shell Quoting & Expansion

- **Single quotes** prevent all expansion: `'$VAR'` is literal `$VAR`, not variable value
- **Double quotes** allow expansion: `"$VAR"` expands variable, but `"$(command)"` also runs command
- **Backticks vs $()**: Both run commands, but `$()` nests better: `` `echo `pwd`` ``breaks, but`$(echo $(pwd))` works
- **Word splitting**: `$VAR` without quotes splits on spaces; wrap in quotes: `"$VAR"` prevents splitting

### Pipes & Redirection

- Pipes `|` connect stdout only; stderr still appears on screen. Redirect: `command 2>&1 | jq`
- `>` overwrites file; `>>` appends. Use `>>` in loops to avoid truncating mid-execution
- File descriptors: `1` = stdout, `2` = stderr, `0` = stdin. Redirect stderr to stdout: `2>&1`

### Environment Variables

- `export VAR=value` makes variable available to child processes. Without `export`, only current shell sees it
- `env` shows all exported variables. Test secrets: `env | grep SECRET` (careful not to log!)
- `$PATH` determines where shell searches for commands. Missing PATH entry? Use absolute paths: `/usr/bin/command`

### Command Substitution Timing

- `$(command)` runs immediately during variable assignment. If command is slow, entire script waits
- For async execution, use background: `command & PID=$!` then `wait $PID` later
- Capture both stdout and stderr: `output=$(command 2>&1)` then check exit code: `echo $?`

## Essential Patterns

### Safe Script Header (Always Use)

```bash
#!/bin/bash
set -euo pipefail  # Exit on error, undefined vars, pipe failures
IFS=$'\n\t'        # Fix word splitting for newlines/tabs
trap 'echo "Error at line $LINENO"' ERR
```

### Variable Declaration

```bash
# Always quote variables
name="$1"          # Correctly quoted
count="$(echo 5)"  # Command substitution quoted
array=("${array[@]}")  # Array expansion requires special quoting
```

### Conditional Checks

```bash
# Test file exists
if [[ -f "$file" ]]; then echo "File exists"; fi

# Test variable is not empty
if [[ -n "$var" ]]; then echo "Var set"; fi

# Test two strings equal
if [[ "$a" == "$b" ]]; then echo "Equal"; fi

# Always use [[ ]] not [ ] for better behavior
```

### Error Handling Pattern

```bash
command || {
  echo "Command failed: $?"
  exit 1
}

# Or use trap for cleanup
cleanup() {
  rm -f /tmp/tempfile
}
trap cleanup EXIT
```

## Tool-Specific Patterns

### Using `set -e` (Exit on Error)

```bash
set -e
command1  # If fails, script exits immediately
command2  # Only runs if command1 succeeds
```

**Gotcha**: Pipelines often require special handling:

```bash
# This FAILS to exit on error in pipe:
false | true  # $? = 0 (true's exit code)

# Fix: use `set -o pipefail`
set -o pipefail
false | true  # Now $? = 1 (false's exit code)
```

### Looping Over Variables

```bash
# Loop over space-separated list (with proper quoting!)
for host in "server1" "server2" "server3"; do
  ssh "$host" "command"
done

# Loop over file lines (avoid while IFS= read)
mapfile -t lines < file.txt
for line in "${lines[@]}"; do
  echo "$line"
done
```

### SSH Best Practices

```bash
# Always set timeout to prevent hanging
ssh -o ConnectTimeout=5 -o BatchMode=yes user@host "command"

# Check exit code of remote command
ssh user@host "remote_command" || echo "Remote failed: $?"

# Use key-based auth with 1Password agent (not plaintext key)
export SSH_AUTH_SOCK=/run/user/$(id -u)/1password/agent.sock
ssh user@host
```

## Debugging Patterns

### Print Statements (Verbose Mode)

```bash
# Enable with -x flag: bash -x script.sh
# Or inside script: set -x
set -x  # Print each command before running
command
set +x  # Turn off verbose
```

### Check Variable Values

```bash
echo "DEBUG: var='$var', count=$count"
echo "DEBUG: Array has ${#array[@]} elements"
env | grep SECRET  # Dangerous! Only for debugging
```

### Test File Permissions

```bash
ls -la /path/to/file
# Output: -rw-r--r-- (644 for files, drwxr-xr-x for dirs)

# SSH key must be 0600
ls -l ~/.ssh/id_rsa  # Should show: -rw------- (0600)
```

## Cross-Platform Considerations

### macOS vs Linux Differences

- `sed -i` syntax differs: macOS needs `-i ''`, Linux needs `-i`
- Use `-i.bak` to work on both: `sed -i.bak 's/old/new/' file`
- `date` command differs: macOS uses BSD date, Linux uses GNU date
  - Use: `date -u +%s` for Unix timestamp (works on both)

### Use Absolute Paths

```bash
# Don't rely on $PATH or user's current directory
/usr/bin/ssh user@host        # Not: ssh
/usr/local/bin/jc --version   # Not: jc
which command                 # Verify command location
```

## Summary

- **Always quote** variables: `"$var"` not `$var`
- **Always use** `set -euo pipefail` in scripts
- **Test conditions** with `[[ ]]` not `[ ]`
- **Redirect stderr** in pipes: `command 2>&1 | next`
- **SSH keys** must be `0600` exactly, or auth silently fails
- **Use absolute paths** for installed tools in scripts
