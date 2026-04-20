# Cherri Automation

## Critical Gotchas (Read First)

### macOS-Only Language

- **Cherri compiles to `.shortcut` binary** for Siri Shortcuts, which is **macOS/iOS exclusive**
- **No Linux support**. For Linux automation, use Bash/Python instead
- **DANGER**: Deploying Cherri scripts to CI/CD systems without macOS runners = instant failure

### Compilation Requirement

- Cherri source code is not executable. Must compile to `.shortcut` binary first
- **FIX**: Always compile during build step

  ```bash
  cherri compile script.cherri -o script.shortcut
  ```

- Shortcut binary is binary format (not human-readable), slowing development cycle vs Shortcuts.app GUI

### Type System Strictness

- Cherri enforces strong typing. `String` cannot be implicitly converted to `Int`
- **FIX**: Explicit type conversion required

  ```cherri
  let str = "42"
  let num = Int(str)!  // ! unwraps optional
  ```

### Execution Context (App Limitations)

- Cherri Shortcuts run in Shortcuts app sandbox. File system access restricted
- Cannot access arbitrary files. Must use `FileURL` or `Bookmark` API
- **FIX**: Use 1Password CLI for secrets instead of reading from files

### Shell Command Integration

- Cherri can shell out via `executeCommand()`, but stdout/stderr capture differs from native Bash
- **DANGER**: Error handling in shell commands returns exit code only, not stderr text
- **FIX**: Parse stdout for errors, not stderr

## Cherri Basics

### Function Definition

```cherri
func greet(name: String) -> String {
  return "Hello, \(name)"
}

// Call function
let greeting = greet(name: "World")
print(greeting)
```

### Variables & Types

```cherri
// Immutable (preferred)
let name = "Alice"
let age = 30

// Mutable
var counter = 0
counter = counter + 1

// Type annotations (optional—inferred if obvious)
let email: String = "user@example.com"
let count: Int = 42
let active: Bool = true
```

### Conditionals

```cherri
if age > 18 {
  print("Adult")
} else if age > 13 {
  print("Teenager")
} else {
  print("Child")
}

// Guard statement (early exit)
guard let name = maybeName else {
  print("Name is nil")
  return
}
print("Name is: \(name)")
```

### Loops

```cherri
// For loop with range
for i in 1...5 {
  print("Number: \(i)")
}

// For-in with array
let fruits = ["apple", "banana", "cherry"]
for fruit in fruits {
  print(fruit)
}

// While loop
var count = 0
while count < 3 {
  print(count)
  count = count + 1
}
```

### Arrays & Dictionaries

```cherri
// Array
let numbers = [1, 2, 3, 4, 5]
let first = numbers[0]  // 1
let count = numbers.count  // 5

// Dictionary
let person = ["name": "Alice", "age": "30"]
let name = person["name"]  // "Alice"

// Array operations
var items = ["a", "b"]
items.append("c")
items.remove(at: 0)
```

## Shell Integration (Executing Commands)

### Basic Shell Execution

```cherri
func checkDiskSpace() -> String {
  let result = executeCommand("df -h")
  return result
}

// Usage
let diskInfo = checkDiskSpace()
print(diskInfo)
```

### Shell with 1Password Integration

```cherri
// Fetch secret and use in command
func deployWithSecret(host: String) -> Bool {
  // Get secret from 1Password
  let apiKey = executeCommand("op read op://prod/api/key")

  // Execute remote command with secret
  let cmd = "ssh user@\(host) 'API_KEY=\(apiKey) /opt/deploy.sh'"
  let result = executeCommand(cmd)

  return result.contains("SUCCESS")
}
```

### Parsing Shell Output

```cherri
// Run command and parse result
func getInstalledPackages() -> [String] {
  let output = executeCommand("brew list")

  // Split by newline and filter
  let packages = output
    .split(separator: "\n")
    .map { String($0) }
    .filter { !$0.isEmpty }

  return packages
}
```

## Control Flow Patterns

### Retry Logic

```cherri
func executeWithRetry(command: String, maxRetries: Int = 3) -> String {
  var attempt = 0
  var lastError = ""

  while attempt < maxRetries {
    let result = executeCommand(command)

    if !result.contains("Error") {
      return result  // Success
    }

    lastError = result
    attempt = attempt + 1

    if attempt < maxRetries {
      print("Attempt \(attempt) failed, retrying...")
      sleep(2)  // Wait 2 seconds before retry
    }
  }

  return "Failed after \(maxRetries) attempts: \(lastError)"
}
```

### Conditional Execution

```cherri
func backupIfNeeded(source: String, destination: String) -> Bool {
  // Check if backup needed
  let isOutdated = executeCommand("test -f \(destination) && find \(destination) -mtime +1").isEmpty

  if isOutdated {
    print("Backup outdated, running backup...")
    let result = executeCommand("cp -r \(source) \(destination)")
    return !result.contains("error")
  }

  print("Backup is current, skipping.")
  return true
}
```

### Error Handling

```cherri
func safeExecute(command: String) -> (success: Bool, output: String) {
  let result = executeCommand(command)

  // Check for common error indicators
  if result.contains("error") || result.contains("failed") || result.contains("Error") {
    return (false, result)
  }

  return (true, result)
}

// Usage
let (success, output) = safeExecute(command: "some-command")
if success {
  print("Output: \(output)")
} else {
  print("Command failed: \(output)")
}
```

## Workflow Examples

### Example 1: System Health Check

```cherri
func systemHealthCheck() -> [String: String] {
  var results = [String: String]()

  // Check disk usage
  let df = executeCommand("df -h / | tail -1")
  results["disk"] = df

  // Check CPU usage
  let top = executeCommand("top -l1 | grep 'CPU usage'")
  results["cpu"] = top

  // Check memory
  let mem = executeCommand("vm_stat | grep 'Pages active'")
  results["memory"] = mem

  return results
}

// Execute and print results
let health = systemHealthCheck()
for (key, value) in health {
  print("\(key): \(value)")
}
```

### Example 2: Automated Backup with Notification

```cherri
func backupWithNotification(source: String, destination: String) -> Bool {
  print("Starting backup...")

  // Run backup
  let backupCmd = "rsync -av \(source) \(destination)"
  let result = executeCommand(backupCmd)

  if result.contains("error") {
    // Send failure notification via 1Password webhook
    let webhook = executeCommand("op read op://work/slack/webhook")
    executeCommand("curl -X POST -d 'Backup failed' \(webhook)")
    return false
  }

  // Send success notification
  let webhook = executeCommand("op read op://work/slack/webhook")
  executeCommand("curl -X POST -d 'Backup completed' \(webhook)")

  return true
}
```

### Example 3: Fleet Monitor

```cherri
func monitorFleet(servers: [String]) -> [String: String] {
  var statuses = [String: String]()

  for server in servers {
    let sshCmd = "ssh -o ConnectTimeout=5 user@\(server) 'uptime'"
    let status = executeCommand(sshCmd)

    if status.isEmpty {
      statuses[server] = "OFFLINE"
    } else {
      statuses[server] = status
    }
  }

  return statuses
}

// Usage
let servers = ["web01.example.com", "web02.example.com", "db01.example.com"]
let fleet = monitorFleet(servers: servers)
for (server, status) in fleet {
  print("\(server): \(status)")
}
```

## Compiling & Executing Cherri

### Compile to Shortcut

```bash
# Install Cherri (via package manager or from source)
brew install cherri  # macOS

# Compile script to executable shortcut
cherri compile backup-script.cherri -o backup-script.shortcut

# Execute shortcut from shell
open -a Shortcuts backup-script.shortcut

# Or directly run (if configured)
cherri run backup-script.cherri
```

### Integration with Shell Scripts

```bash
#!/bin/bash
# shell-wrapper.sh - Orchestrate Cherri shortcut from shell

set -euo pipefail

CHERRI_SCRIPT="fleet-monitor.cherri"
SHORTCUT_BINARY="fleet-monitor.shortcut"

# Step 1: Compile Cherri to shortcut
echo "Compiling $CHERRI_SCRIPT..."
cherri compile "$CHERRI_SCRIPT" -o "$SHORTCUT_BINARY"

# Step 2: Execute shortcut
echo "Executing $SHORTCUT_BINARY..."
open -a Shortcuts "$SHORTCUT_BINARY"

# Step 3: Wait for completion and capture results
# (Note: Shortcuts app doesn't easily return stdout; may need file-based handoff)
sleep 5
if [ -f results.json ]; then
  cat results.json
fi
```

## Troubleshooting

### "Command not found" on Linux

```text
Error: Cherri not found on Linux
```

**Cause**: Cherri is macOS-only

**Fix**: Use Bash or Python for Linux automation instead

### Shell Command Hangs

```cherri
// Problem: executeCommand("slow-command") blocks forever

// Fix: Use timeout wrapper
func executeWithTimeout(command: String, timeout: Int = 30) -> String {
  let timedCmd = "timeout \(timeout) \(command)"
  return executeCommand(timedCmd)
}
```

### Type Mismatch Error

```text
Error: Cannot assign String to Int
```

**Fix**: Explicit type conversion

```cherri
let str = "42"
let num = Int(str)!  // ! unwraps optional; use do-try-catch if uncertain
```

## Integration with 1Password & SSH

### Full Automation Example

```cherri
func deployToProduction(host: String, service: String) -> Bool {
  // 1. Fetch credentials from 1Password
  let sshKey = executeCommand("op read op://prod/ssh/key")
  let dbPassword = executeCommand("op read op://prod/db/password")

  // 2. Write SSH key temporarily
  executeCommand("echo '\(sshKey)' > /tmp/deploy_key")
  executeCommand("chmod 0600 /tmp/deploy_key")

  // 3. SSH and deploy with secrets
  let deployCmd = """
  ssh -i /tmp/deploy_key -o StrictHostKeyChecking=no user@\(host) \
    'export DB_PASSWORD=\(dbPassword) && systemctl restart \(service)'
  """
  let result = executeCommand(deployCmd)

  // 4. Cleanup key
  executeCommand("rm -f /tmp/deploy_key")

  // 5. Verify success
  let success = !result.contains("error")

  if success {
    executeCommand("curl -X POST -d 'Deployment successful' \(executeCommand("op read op://work/slack/webhook"))")
  }

  return success
}
```

## Summary

- **Cherri is macOS-only** — no Linux support; use Bash/Python for cross-platform automation
- **Always compile before executing**: `cherri compile script.cherri -o script.shortcut`
- **Use strong types** — Cherri enforces type safety; explicit conversions required
- **Shell integration** via `executeCommand()` — capture output, parse for errors
- **1Password secrets** for secure credential injection (not file-based)
- **Error handling** requires checking output strings, not just exit codes
- **Test on macOS first** before assuming compatibility
