---
name: zx-shell-scripting
description: 'Write advanced shell automation scripts with Google zx, a Node.js tool that wraps subprocess execution with ergonomic template literals. Use when asked to write a shell script, bash script, or automation script in Node.js; automate CLI workflows; spawn subprocesses; pipe commands; process command output; replace a bash script with modern JavaScript; write cross-platform automation; run terminal commands programmatically; or when the user mentions zx, $`command`, shell scripting, subprocess management, or Node.js scripting. Covers: subprocess execution, piping, parallel execution, error handling with nothrow and retry, streaming output, jc JSON parsing integration, and shell one-liner idioms translated to zx.'
compatibility: 'Requires: Node.js 16+, zx 8+; optional: jc (pip3 install jc or brew install jc), jq'
metadata:
  version: '1.0'
  integrations: 'zx,jc,jq,chalk,fs-extra'
---

# zx Shell Scripting

Advanced shell automation with [Google zx](https://google.github.io/zx/) — subprocess execution with the ergonomics of modern JavaScript.

## When to Use

- Writing shell scripts, bash scripts, or automation in Node.js
- Spawning subprocesses from a JS/TS project
- Piping commands, capturing output, processing CLI results
- Replacing fragile bash with type-safe, testable Node.js
- Parallel command execution, retry logic, streaming output
- Parsing CLI output as structured JSON (via `jc`)

## File Modes

```js
// Mode 1: .mjs with top-level await (all globals available, no imports)
// run: zx script.mjs  OR  node --input-type=module < script.mjs
#!/usr/bin/env zx

const out = await $`ls -la`

// Mode 2: ESM .js/.ts with explicit imports
import { $, cd, glob, retry, spinner, within } from 'zx'
```

## Key Patterns

### Basic Execution and Output

```js
// Capture stdout
const branch = await $`git branch --show-current`;
console.log(branch.stdout.trim()); // stdout only
console.log(`${branch}`); // valueOf() → trimmed stdout

// Output as array of lines
const files = await $`find . -name "*.ts"`.lines();

// Output parsed as JSON
const data = await $`curl -s https://api.example.com/data`.json();
```

### Auto-Escaping (Shell Injection Defense)

```js
// zx auto-escapes ALL interpolated values — never add extra quotes
const dir = '/path/with spaces';
const ext = '*.log';

await $`find ${dir} -name ${ext}`; // CORRECT — zx escapes both values
// await $`find "${dir}" -name "${ext}"`  WRONG — double-escapes, breaks
```

### Piping

```js
// Chain subprocesses
const errors = await $`grep -r "ERROR" ./logs`
  .pipe($`sort`)
  .pipe($`uniq -c`)
  .lines();

// Pipe from Node.js stream
import { createReadStream } from 'fs';
const result = await $`wc -l`.pipe(createReadStream('big-file.txt'));
```

### Parallel Execution

```js
// Run concurrently, collect all results
const [stats, procs, disk] = await Promise.all([$`uptime`, $`ps aux | wc -l`, $`df -h /`]);

// Parallel with nothrow — continue even if some fail
const results = await Promise.all(['host1', 'host2', 'host3'].map(h => $`ping -c 1 ${h}`.nothrow()));
const reachable = results.filter(r => r.exitCode === 0);
```

### Error Handling

```js
// Option A: nothrow — suppress throw, inspect exit code
const result = await $`which docker`.nothrow();
if (!result.ok) {
  echo('docker not found, skipping container steps');
}

// Option B: try/catch — access full ProcessOutput on error
try {
  await $`npm test`;
} catch (err) {
  console.error(`Tests failed (exit ${err.exitCode}):\n${err.stderr}`);
  process.exit(1);
}

// Option C: retry — flaky commands (network, services)
const resp = await retry(5, '2s', () => $`curl -sf https://api.example.com/health`);
```

### Scoped Context

```js
// within() — scoped cwd/config changes (safe; does NOT mutate global)
await within(async () => {
  $.cwd = '/tmp/build';
  $.env = { ...process.env, NODE_ENV: 'production' };
  await $`npm run build`;
});
// cwd is restored here

// Factory preset — reusable scoped config
const $$ = $({ quiet: true, nothrow: true, cwd: '/var/log' });
const auth = await $$`tail -n 50 auth.log`;
```

### Streaming Output

```js
// Async iteration — process lines as they arrive
for await (const line of $`tail -f /var/log/app.log`) {
  if (line.includes('ERROR')) process.stderr.write(`[ALERT] ${line}\n`);
  if (line.includes('FATAL')) break;
}
```

### jc Integration — Parse CLI Output as JSON

```js
// jc converts CLI output to structured JSON
// Install: pip3 install jc  OR  brew install jc

// Parse ps output
const procs = await $`ps axu`.pipe($`jc --ps`).json();
const zombies = procs.filter(p => p.stat === 'Z');

// Magic syntax: jc infers parser from command name
const mounts = await $`jc df -h`.json();

// Parse network connections
const conns = await $`ss -tnp`.pipe($`jc --ss`).json();
const listening = conns.filter(c => c.state === 'LISTEN');
```

## Configuration

```js
// Global defaults
$.shell = '/bin/bash'; // default: which bash
$.prefix = 'set -euo pipefail;'; // default: abort on error/unset vars
$.verbose = false; // suppress command echoing
$.quiet = true; // suppress stdout/stderr
$.cwd = process.cwd();
$.timeout = 30_000; // ms; 0 = no timeout
$.env = process.env;
$.preferLocal = true; // resolve from node_modules/.bin

// Per-command overrides (preferred over mutating globals)
await $`noisy-cmd`.quiet();
await $`might-fail`.nothrow();
await $`slow-op`.timeout(60_000);
```

## Gotchas

1. **Auto-escaping**: interpolated values are shell-escaped — adding extra quotes breaks things
2. **`set -euo pipefail` is ON by default** via `$.prefix` — scripts abort on any error or unset variable
3. **`.toString()` / string coercion** returns trimmed stdout (same as `.valueOf()`); use `.stdout` for raw stdout, `.stderr` for stderr
4. **`cd()` mutates global `process.cwd()`** — use `within()` for scoped directory changes to avoid side effects
5. **ProcessPromise executes immediately** — the subprocess starts when `$` is called, not when you `await` it
6. **`.mjs` files** get all zx globals without import; **`.ts` or `.js`** files must `import { ... } from 'zx'`
7. **`$.quiet = true`** suppresses all output globally — prefer `.quiet()` on individual commands
8. **`jc` requires Python** — `pip3 install jc` or `brew install jc`; verify with `jc --version` before use
9. **Bash globs in `$` strings are still dangerous** — always prefix with `./` (not `*`), use `read -d ""` with `find -print0`, and quote `"$file"` inside loops; prefer zx's `glob()` for recursive matching (see `references/filename-safety.md`)

## Reference Index

Load these files when you need deeper detail:

| File                            | Load When                                                                                   |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| `references/api-reference.md`   | Need full API — ProcessPromise methods, ProcessOutput properties, all globals, config table |
| `references/shell-patterns.md`  | Need real-world patterns — file ops, networking, `jc` cookbook, secrets, one-liners         |
| `references/error-handling.md`  | Need error patterns — signals, retry backoff, graceful shutdown, unhandled rejections       |
| `references/filename-safety.md` | Handling filenames with spaces/newlines/dashes/control chars safely (CWE-78, CWE-73)        |
| `references/bash-internals.md`  | Pure-bash alternatives to external processes — parameter expansion, file ops, IFS, traps    |
