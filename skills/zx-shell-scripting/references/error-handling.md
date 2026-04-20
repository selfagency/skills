# Error Handling in zx

Comprehensive patterns for handling failures, signals, and graceful shutdown.

---

## ProcessOutput Error Anatomy

When a command exits non-zero and `.nothrow()` is NOT set, zx throws. The caught value IS a `ProcessOutput`:

```js
try {
  await $`npm test`;
} catch (err) {
  // err is ProcessOutput — same type as successful output
  console.error(`Exit code: ${err.exitCode}`); // number | null
  console.error(`Signal:    ${err.signal}`); // 'SIGTERM' | null
  console.error(`stderr:    ${err.stderr}`); // raw stderr string
  console.error(`stdout:    ${err.stdout}`); // raw stdout string
  console.error(`Message:   ${err.message}`); // formatted summary
}
```

---

## Strategy 1: `.nothrow()` — Silent Failure

Best for: optional commands, feature detection, fire-and-forget.

```js
// Check if binary exists without throwing
const docker = await $`which docker`.nothrow();
if (!docker.ok) {
  echo('Docker not available, skipping container build');
}

// Run command, inspect result manually
const result = await $`ping -c 1 -W 2 ${host}`.nothrow();
const reachable = result.exitCode === 0;

// Global nothrow via config (use sparingly)
const $check = $({ nothrow: true });
const [a, b] = await Promise.all([$check`cmd1`, $check`cmd2`]);
```

### `.ok` Property

```js
const out = await $`some-command`.nothrow();
if (out.ok) {
  // exitCode === 0
} else {
  // exitCode !== 0 or killed by signal
}
```

---

## Strategy 2: `try/catch` — Controlled Failure

Best for: critical paths, meaningful error messages, multi-step pipelines.

```js
// Basic
try {
  await $`must-succeed`;
} catch (err) {
  console.error(`Command failed (exit ${err.exitCode}): ${err.stderr.trim()}`);
  process.exit(1);
}

// Distinguish failure reasons
try {
  await $`curl -sf https://api.example.com/deploy`.timeout(30_000);
} catch (err) {
  if (err.signal === 'SIGTERM') {
    echo(chalk.yellow('Deploy timed out after 30s'));
  } else {
    echo(chalk.red(`Deploy failed (${err.exitCode}): ${err.stderr.trim()}`));
  }
  process.exit(1);
}

// Re-throw after logging
async function runStep(name, fn) {
  try {
    return await fn();
  } catch (err) {
    console.error(`Step "${name}" failed:\n  exit: ${err.exitCode}\n  ${err.stderr.trim()}`);
    throw err; // propagate — caller decides whether to abort
  }
}
```

---

## Strategy 3: `retry()` — Transient Failures

Best for: network calls, service startup, flaky external dependencies.

```js
import { retry, expBackoff } from 'zx';

// Fixed delay (3 attempts, 2s apart)
await retry(3, '2s', () => $`curl -sf https://api.example.com/health`);

// Numeric delay in ms
await retry(5, 1000, () => $`pg_isready -h localhost`);

// Exponential backoff (zx 8+)
// Starts at 100ms, doubles each attempt, optional max delay
await retry(6, expBackoff(), () => $`connect-to-service`);
await retry(6, expBackoff(1000, 30_000), () => $`flaky-cmd`); // min 1s, max 30s

// Retry with fallback on exhaustion
let deployed = false;
try {
  await retry(3, '5s', () => $`kubectl rollout status deployment/app`);
  deployed = true;
} catch {
  echo(chalk.red('Deployment did not stabilize after 3 attempts'));
  await $`kubectl rollout undo deployment/app`;
}
```

---

## Strategy 4: Timeout

Best for: commands that may hang, network-dependent operations, CI time budgets.

```js
// Per-command timeout (ms)
await $`slow-operation`.timeout(10_000);

// With custom signal
await $`blocking-cmd`.timeout(5_000, 'SIGKILL');

// Global default
$.timeout = 30_000; // all subsequent commands timeout at 30s

// Timeout in retry
await retry(3, '1s', () => $`curl -sf https://api.example.com`.timeout(5_000));

// Detect timeout vs other failure
try {
  await $`network-call`.timeout(3_000);
} catch (err) {
  if (err.signal === 'SIGTERM') {
    echo('Request timed out');
  } else {
    echo(`Request failed: exit ${err.exitCode}`);
  }
}
```

---

## Strategy 5: Abort Controller

Best for: user-cancelable operations, coordinated cancellation across multiple processes.

```js
const controller = new AbortController();

// Cancel on Ctrl+C
process.on('SIGINT', () => controller.abort());

const p = $`rsync -avz /source/ /dest/`.timeout(300_000, 'SIGTERM');

// Manual abort
setTimeout(() => controller.abort(), 60_000);

try {
  await p;
} catch (err) {
  if (err.signal) {
    echo('Transfer cancelled');
  } else {
    throw err;
  }
}
```

---

## Signal Handling and Graceful Shutdown

Best for: long-running scripts, servers, cleanup-on-exit patterns.

```js
#!/usr/bin/env zx

const processes = [];

async function cleanup(signal) {
  echo(chalk.yellow(`\nReceived ${signal}, shutting down...`));
  await Promise.allSettled(processes.map(p => p.kill('SIGTERM')));
  process.exit(0);
}

process.on('SIGINT', () => cleanup('SIGINT'));
process.on('SIGTERM', () => cleanup('SIGTERM'));

// Track spawned processes for cleanup
const worker = $`node worker.js`.nothrow();
processes.push(worker);

// Wait for readiness then do work
await retry(10, '500ms', () => $`curl -sf http://localhost:3001/health`);
await $`npm run integration-tests`;

// Cleanup on normal exit
await cleanup('EXIT');
```

### Cleanup with `trap` Equivalent

```js
// Prefix-level trap (applies to every shell command)
$.prefix = 'set -euo pipefail; trap "echo Script aborted" ERR;';

// Or per-command with inline trap
await $`set -euo pipefail; trap 'rm -f /tmp/lock' EXIT; ./risky-script.sh`;
```

---

## Unhandled Rejection Safety

Always add a top-level safety net:

```js
#!/usr/bin/env zx

process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled rejection:', reason);
  process.exit(1);
});

process.on('uncaughtException', err => {
  console.error('Uncaught exception:', err);
  process.exit(1);
});

// Main function pattern — ensures top-level await errors are caught
async function main() {
  // ... script logic
}

main().catch(err => {
  console.error(chalk.red('Fatal:'), err.message || err);
  process.exit(1);
});
```

---

## Fail Fast: Argument Validation

Validate inputs before doing any work (nodebestpractices 4.3 — fail fast):

```js
#!/usr/bin/env zx

const env = argv.env ?? argv.e;
const version = argv.version ?? argv.v;

if (!env) {
  echo(chalk.red('Error: --env is required'));
  echo('Usage: zx deploy.mjs --env=production --version=1.2.3');
  process.exit(1);
}

if (!version || !/^\d+\.\d+\.\d+$/.test(version)) {
  echo(chalk.red(`Error: --version must be semver, got: ${version}`));
  process.exit(1);
}

// Now safe to proceed
await $`deploy ${env} ${version}`;
```

---

## Operational vs Catastrophic Errors

From nodebestpractices 2.3 — distinguish recoverable from fatal:

```js
class OperationalError extends Error {
  constructor(message, context = {}) {
    super(message);
    this.name = 'OperationalError';
    this.isOperational = true;
    this.context = context;
  }
}

async function deployWithRetry(version) {
  try {
    await $`kubectl set image deployment/app app=myapp:${version}`;
    await $`kubectl rollout status deployment/app --timeout=120s`;
  } catch (err) {
    if (err.exitCode === 1) {
      // Rollout failed — operational, can retry or rollback
      throw new OperationalError('Deployment failed', { version, stderr: err.stderr });
    }
    // Unexpected error — catastrophic, rethrow for top-level handler
    throw err;
  }
}

try {
  await deployWithRetry('1.2.3');
} catch (err) {
  if (err.isOperational) {
    echo(chalk.yellow(`Operational error: ${err.message}`));
    await $`kubectl rollout undo deployment/app`;
    process.exit(1);
  }
  // Catastrophic — let unhandledRejection handler deal with it
  throw err;
}
```

---

## Structured Error Logging

```js
// Log errors with context for observability
function logError(step, err) {
  const entry = {
    timestamp: new Date().toISOString(),
    step,
    exitCode: err.exitCode ?? null,
    signal: err.signal ?? null,
    stderr: err.stderr?.trim() ?? String(err),
  };
  process.stderr.write(JSON.stringify(entry) + '\n');
}

try {
  await $`risky-command`;
} catch (err) {
  logError('risky-command', err);
  process.exit(1);
}
```

---

## Common Patterns at a Glance

| Scenario                          | Pattern                                 |
| --------------------------------- | --------------------------------------- |
| Optional command (may not exist)  | `.nothrow()` + check `.ok`              |
| Critical command (must succeed)   | `try/catch` + `process.exit(1)`         |
| Flaky network call                | `retry(n, delay, fn)`                   |
| Command that may hang             | `.timeout(ms)`                          |
| Parallel with partial failures OK | `Promise.allSettled()` + `.nothrow()`   |
| Cleanup on any exit               | `process.on('SIGINT/SIGTERM', cleanup)` |
| User input validation             | Check `argv.*` before any `$` calls     |
| Distinguish timeout vs failure    | Check `err.signal === 'SIGTERM'`        |
