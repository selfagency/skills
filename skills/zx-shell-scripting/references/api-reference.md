# zx API Reference

## Tagged Template: `$`

```js
// Async — returns ProcessPromise
const p = $`command arg1 ${interpolated}`;

// Sync — returns ProcessOutput directly (blocks event loop — use sparingly)
const out = $.sync`command arg`;
```

### Interpolation Rules

| Input type           | How zx handles it                                 |
| -------------------- | ------------------------------------------------- |
| `string`             | Shell-quoted via `shq()` — safe against injection |
| `number`             | Stringified, then quoted                          |
| `string[]`           | Each element quoted, joined with space            |
| `ProcessOutput`      | `.toString()` used (trimmed stdout+stderr)        |
| `undefined` / `null` | Throws — validate before interpolating            |

```js
const args = ['--verbose', '--color=always'];
await $`ls ${args}`; // → ls --verbose --color=always (each quoted)

const count = 42;
await $`dd bs=${count} if=/dev/zero`; // → dd bs=42 if=/dev/zero
```

---

## ProcessPromise

`$` returns a `ProcessPromise`. It extends `Promise<ProcessOutput>` with chainable methods.

### Chainable Methods

| Method                             | Description                                                   |
| ---------------------------------- | ------------------------------------------------------------- |
| `.pipe(dest)`                      | Pipe stdout to another `$`, `Writable`, or `ReadableStream`   |
| `.nothrow()`                       | Suppress throw on non-zero exit; resolve with `ProcessOutput` |
| `.quiet()`                         | Suppress stdout/stderr echoing for this command               |
| `.verbose(enabled?)`               | Force verbose/quiet for this command only                     |
| `.timeout(ms, signal?)`            | Kill process after `ms` milliseconds                          |
| `.kill(signal?)`                   | Send signal (default `SIGTERM`) to the process                |
| `.abort()`                         | Abort via internal `AbortController`                          |
| `.stdio(stdin?, stdout?, stderr?)` | Override stdio configuration                                  |
| `.lines()`                         | Resolve to `string[]` — one entry per stdout line             |
| `.text(encoding?)`                 | Resolve to decoded `string`                                   |
| `.json<T>()`                       | Resolve to `T` — parses stdout as JSON                        |
| `.buffer()`                        | Resolve to `Buffer` (binary output)                           |
| `.blob()`                          | Resolve to `Blob`                                             |

### Properties

```js
const p = $`long-running-command`;

p.stdin; // Writable — write to process stdin
p.stdout; // Readable — process stdout stream
p.stderr; // Readable — process stderr stream
p.exitCode; // Promise<number | null>
p.pid; // number | undefined — process ID after spawn
```

### Async Iteration (Streaming)

```js
// Iterate stdout lines as they arrive
for await (const line of $`tail -f /var/log/syslog`) {
  console.log(line);
}

// With timeout and abort
const p = $`watch -n 1 date`.timeout(10_000);
for await (const line of p) {
  console.log(line);
}
```

---

## ProcessOutput

Resolved value of an awaited `ProcessPromise`.

```js
const out = await $`command`;
```

| Property / Method | Type             | Description                                      |
| ----------------- | ---------------- | ------------------------------------------------ |
| `.stdout`         | `string`         | Raw stdout (with trailing newline)               |
| `.stderr`         | `string`         | Raw stderr                                       |
| `.exitCode`       | `number \| null` | Exit code (null if killed by signal)             |
| `.signal`         | `string \| null` | Signal name if killed (`'SIGTERM'`, etc.)        |
| `.ok`             | `boolean`        | `true` if `exitCode === 0`                       |
| `.toString()`     | `string`         | Combined stdout+stderr, trimmed                  |
| `.valueOf()`      | `string`         | Same as `toString()` — used in template literals |
| `.json<T>()`      | `T`              | Parse stdout as JSON                             |
| `.text()`         | `string`         | stdout as string                                 |
| `.lines()`        | `string[]`       | stdout split by newline                          |
| `.buffer()`       | `Buffer`         | Raw stdout buffer                                |

When a command fails (non-zero exit + throw not suppressed), the caught error IS a `ProcessOutput`:

```js
try {
  await $`false`;
} catch (err) {
  // err is ProcessOutput
  console.log(err.exitCode); // 1
  console.log(err.stderr); // any stderr output
  console.log(err.message); // formatted error string
}
```

---

## Configuration: `$.`

Mutate globals or use factory presets (preferred for scoped config).

| Property          | Default                | Description                                          |
| ----------------- | ---------------------- | ---------------------------------------------------- |
| `$.shell`         | `which bash`           | Shell binary                                         |
| `$.prefix`        | `'set -euo pipefail;'` | Prepended to every command                           |
| `$.postfix`       | `''`                   | Appended to every command                            |
| `$.verbose`       | `false`                | Echo commands before running                         |
| `$.quiet`         | `false`                | Suppress stdout/stderr output                        |
| `$.nothrow`       | `false`                | Global nothrow (resolve instead of throw on failure) |
| `$.cwd`           | `process.cwd()`        | Working directory                                    |
| `$.env`           | `process.env`          | Environment variables                                |
| `$.timeout`       | `0`                    | Default timeout in ms (0 = none)                     |
| `$.timeoutSignal` | `'SIGTERM'`            | Signal sent on timeout                               |
| `$.delimiter`     | `'\n'`                 | Line delimiter for `.lines()`                        |
| `$.preferLocal`   | `false`                | Resolve binaries from `node_modules/.bin`            |
| `$.log`           | function               | Custom logging function                              |

### Factory Preset (Recommended Pattern)

Creates a scoped `$` variant without mutating globals:

```js
// Immutable options object
const $$ = $({
  quiet: true,
  nothrow: true,
  cwd: '/var/log',
  env: { ...process.env, LANG: 'C' },
  timeout: 5_000,
});

// Chain from existing preset
const $prod = $$({ verbose: true, cwd: '/app' });

// All options available per-call via object syntax
await $({ quiet: true })`noisy-command`;
```

---

## Globals (`.mjs` — no imports needed)

### Execution

| Global     | Signature                 | Description                                               |
| ---------- | ------------------------- | --------------------------------------------------------- |
| `$`        | `` $`cmd` ``              | Spawn subprocess                                          |
| `cd`       | `cd(path)`                | Change `process.cwd()` globally                           |
| `within`   | `within(async fn)`        | Scoped context — restores `$.cwd`, `$.env`, etc. after fn |
| `sleep`    | `sleep(ms)`               | `setTimeout` as a promise                                 |
| `echo`     | `echo(...args)`           | `console.log` with chalk support                          |
| `stdin`    | `stdin()`                 | Read all of process stdin as string                       |
| `question` | `question(prompt, opts?)` | Interactive readline prompt                               |

### Filesystem

| Global                    | Description                                                                               |
| ------------------------- | ----------------------------------------------------------------------------------------- |
| `glob(pattern, opts?)`    | Glob file paths (returns `string[]`)                                                      |
| `fs`                      | `fs-extra` — all Node.js `fs` methods + `ensureDir`, `copy`, `remove`, `outputFile`, etc. |
| `tmpdir(prefix?)`         | Create temp directory, returns path                                                       |
| `tmpfile(ext?, content?)` | Create temp file, returns path                                                            |
| `path`                    | Node.js `path` module                                                                     |
| `os`                      | Node.js `os` module                                                                       |

### Process

| Global               | Description                                              |
| -------------------- | -------------------------------------------------------- |
| `which(bin)`         | Resolve binary path (throws if not found)                |
| `ps`                 | Cross-platform process list (`ps.lookup()`, `ps.kill()`) |
| `kill(pid, signal?)` | Kill process by PID                                      |

### UX / Flow Control

| Global                    | Description                                                            |
| ------------------------- | ---------------------------------------------------------------------- |
| `spinner(title, fn)`      | Run `fn` with an animated spinner; returns fn's result                 |
| `retry(count, delay, fn)` | Retry `fn` up to `count` times with `delay` between attempts           |
| `chalk`                   | Terminal string styling (`chalk.green('ok')`, `chalk.bold.red('err')`) |

### Data / Config

| Global     | Description                               |
| ---------- | ----------------------------------------- |
| `YAML`     | YAML parse/stringify                      |
| `MAML`     | MAML parse/stringify                      |
| `dotenv`   | `dotenv` — `dotenv.config()` loads `.env` |
| `minimist` | Argument parser                           |
| `argv`     | Parsed `process.argv` via minimist        |
| `fetch`    | `node-fetch` — HTTP requests              |

### Shell Variants

```js
useBash(); // Switch to bash (default)
usePowerShell(); // Windows PowerShell
usePwsh(); // PowerShell Core (cross-platform)
```

---

## ProcessPromise: `pipe` in Depth

```js
// Pipe to another ProcessPromise
await $`cat file.txt`.pipe($`wc -l`);

// Pipe to Node.js Writable
import { createWriteStream } from 'fs';
await $`curl -L https://example.com/archive.tar.gz`.pipe(createWriteStream('archive.tar.gz'));

// Multi-stage pipeline
const result = await $`find . -name "*.log"`
  .pipe($`xargs grep -l "ERROR"`)
  .pipe($`sort`)
  .lines();

// Pipe from Node.js Readable (to process stdin)
import { createReadStream } from 'fs';
const count = await $`wc -l`.pipe(createReadStream('file.txt'));
```

---

## `retry` in Depth

```js
// retry(attempts, delay, fn)
// delay: number (ms) | string ('500ms', '1s', '2m') | ExponentialBackoff
import { retry, expBackoff } from 'zx';

// Fixed delay
await retry(3, 1000, () => $`curl -sf https://api.example.com`);

// String delay
await retry(5, '2s', () => $`connect-to-db`);

// Exponential backoff (zx 8+)
await retry(6, expBackoff(), () => $`flaky-cmd`);
```

---

## `within` in Depth

```js
// Scopes: $.cwd, $.env, $.shell, $.prefix, $.verbose, $.quiet, $.nothrow, $.timeout
await within(async () => {
  $.cwd = '/tmp';
  $.env = { ...process.env, CI: 'true' };
  $.verbose = true;

  await $`pwd`; // /tmp
  await $`echo $CI`; // true
});

await $`pwd`; // original cwd restored
```
