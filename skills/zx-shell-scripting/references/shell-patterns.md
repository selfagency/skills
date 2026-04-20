# Shell Patterns for zx

Real-world automation patterns organized by domain. All examples assume a `.mjs` file or explicit `zx` imports.

---

## File Operations

### Read, Transform, Write

```js
// Read → transform → write (via fs-extra)
const content = await fs.readFile('config.json', 'utf8');
const config = JSON.parse(content);
config.version = (await $`git describe --tags --abbrev=0`).toString();
await fs.outputFile('dist/config.json', JSON.stringify(config, null, 2));
```

### Glob + Batch Process

```js
// Process matching files in parallel
const logs = await glob('logs/**/*.log');
await Promise.all(
  logs.map(async log => {
    const errors = await $`grep -c "ERROR" ${log}`.nothrow();
    if (parseInt(errors.stdout) > 0) {
      await $`cp ${log} errors/${path.basename(log)}`;
    }
  }),
);
```

### Temp Files

```js
// tmpfile — auto-cleaned on process exit
const tmp = tmpfile('.json');
await $`curl -s https://api.example.com/data > ${tmp}`;
const data = await fs.readJson(tmp);

// tmpdir — for multi-file operations
const dir = tmpdir('build-');
await $`git clone --depth=1 https://github.com/org/repo ${dir}`;
await within(async () => {
  $.cwd = dir;
  await $`npm ci && npm run build`;
});
```

### Archive and Extract

```js
// Create tarball
const files = await glob('dist/**/*');
await $`tar -czf release.tar.gz ${files}`;

// Extract to specific dir
await $`tar -xzf archive.tar.gz -C ${tmpdir('extract-')}`;
```

---

## Network and HTTP

### curl / wget Patterns

```js
// Download with progress
await $`curl -L --progress-bar -o output.bin https://example.com/file.bin`;

// Retry on failure
const response = await retry(3, '1s', () => $`curl -sf https://api.example.com/health`);

// POST with JSON body (via fetch global)
const res = await fetch('https://api.example.com/deploy', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
  body: JSON.stringify({ version: '1.2.3' }),
});
if (!res.ok) throw new Error(`Deploy failed: ${res.status}`);
```

### Parallel Health Checks

```js
const hosts = ['api.example.com', 'db.example.com', 'cache.example.com'];
const checks = await Promise.all(
  hosts.map(async h => ({
    host: h,
    up: (await $`curl -sf --max-time 5 https://${h}/health`.nothrow()).ok,
  })),
);
const down = checks.filter(c => !c.up);
if (down.length > 0) {
  echo(chalk.red(`Down: ${down.map(c => c.host).join(', ')}`));
  process.exit(1);
}
```

---

## Process Management

### Find and Kill by Name

```js
// Use pgrep/pkill instead of ps | grep
const pid = (await $`pgrep -f "node server.js"`.nothrow()).stdout.trim();
if (pid) {
  await $`kill -TERM ${pid}`;
  await sleep(2000);
  // Force kill if still running
  await $`pgrep -f "node server.js"`.nothrow().then(r => {
    if (r.ok) $`kill -KILL ${pid}`;
  });
}
```

### Start Background Process

```js
// Detach process (fire-and-forget)
const server = $`node server.js`.nothrow();

// Wait for readiness before continuing
await retry(10, '500ms', () => $`curl -sf http://localhost:3000/health`);
echo('Server ready');

// Cleanup on exit
process.on('SIGINT', async () => {
  await server.kill();
  process.exit(0);
});
```

---

## jc: CLI Output as Structured JSON

`jc` parses 150+ CLI command outputs into JSON. Install: `pip3 install jc` or `brew install jc`.

### Essential Parsers

```js
// Disk usage
const disks = await $`df -h`.pipe($`jc --df`).json();
const full = disks.filter(d => parseInt(d.use_percent) > 80);
full.forEach(d => echo(chalk.yellow(`Warning: ${d.filesystem} at ${d.use_percent}`)));

// Running processes
const procs = await $`ps axo pid,user,pcpu,pmem,command`.pipe($`jc --ps`).json();
const heavy = procs.filter(p => parseFloat(p.cpu_percent) > 50).sort((a, b) => b.cpu_percent - a.cpu_percent);

// Network connections
const conns = await $`ss -tnp`.pipe($`jc --ss`).json();
const listening = conns.filter(c => c.state === 'LISTEN').map(c => c.local_port);

// DNS lookup
const records = await $`dig example.com A`.pipe($`jc --dig`).json();
const ips = records[0].answer.map(r => r.data);

// File listing with metadata
const entries = await $`ls -la /etc`.pipe($`jc --ls`).json();
const configs = entries.filter(e => e.name.endsWith('.conf'));
```

### Magic Syntax (jc infers parser from command)

```js
// jc reads the first token of the command to detect the parser
const mounts = await $`jc df -h`.json(); // infers --df
const processes = await $`jc ps axu`.json(); // infers --ps
const routes = await $`jc netstat -rn`.json(); // infers --netstat
const pings = await $`jc ping -c 4 8.8.8.8`.json(); // infers --ping
```

### Streaming Parsers (for large / live output)

```js
// Streaming parsers use -s suffix; add -u for unbuffered
// Memory-efficient for continuous output
const p = $`jc ping -s 8.8.8.8`; // --ping-s streaming parser
for await (const line of p) {
  const packet = JSON.parse(line);
  if (packet.bytes_received === 0) {
    echo(chalk.red('Packet loss detected'));
  }
}
```

### jc + jq Pipeline

```js
// For complex filtering, pipe jc output to jq
const topCpu = await $`ps axu`
  .pipe($`jc --ps`)
  .pipe($`jq '[.[] | select(.cpu_percent > "10.0")] | sort_by(.cpu_percent) | reverse | .[0:5]'`)
  .json();
```

### Available Parsers (subset)

| Parser        | Source command |
| ------------- | -------------- |
| `--ps`        | `ps`           |
| `--df`        | `df`           |
| `--ls`        | `ls`           |
| `--ss`        | `ss`           |
| `--netstat`   | `netstat`      |
| `--dig`       | `dig`          |
| `--ping`      | `ping`         |
| `--ifconfig`  | `ifconfig`     |
| `--arp`       | `arp`          |
| `--stat`      | `stat`         |
| `--find`      | `find`         |
| `--du`        | `du`           |
| `--lsof`      | `lsof`         |
| `--systemctl` | `systemctl`    |
| `--git-log`   | `git log`      |
| `--crontab`   | `crontab`      |
| `--csv`       | CSV files      |
| `--ini`       | INI files      |
| `--env`       | `env` / `.env` |
| `--passwd`    | `/etc/passwd`  |
| `--hosts`     | `/etc/hosts`   |

---

## Secrets and Environment

### dotenv Pattern

```js
dotenv.config(); // loads .env into process.env
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error('API_KEY is required');
```

### 1Password CLI Integration

```js
// Inject secrets at runtime (never hardcode)
const token = (await $`op read "op://vault/MyApp/api-token"`).toString();

// Inject multiple secrets into a subprocess's environment
const $secure = $({
  env: {
    ...process.env,
    DB_PASSWORD: (await $`op read "op://vault/DB/password"`).toString(),
    API_KEY: (await $`op read "op://vault/API/key"`).toString(),
  },
});
await $secure`node migrate.js`;
```

### Environment Scoping

```js
// Isolate subprocess environment (security: no ambient secrets)
const $isolated = $({
  env: {
    PATH: process.env.PATH,
    HOME: process.env.HOME,
    NODE_ENV: 'production',
  },
});
await $isolated`node server.js`;
```

---

## Shell Idioms Translated to zx

| Bash                            | zx                                                       |
| ------------------------------- | -------------------------------------------------------- |
| `cmd1 \| cmd2`                  | ``$`cmd1`.pipe($`cmd2`)``                                |
| `cmd > file.txt`                | `await $`cmd`.pipe(fs.createWriteStream('file.txt'))`    |
| `sort \| uniq`                  | ``$`sort`.pipe($`uniq`)``                                |
| `find . -print0 \| xargs -0 rm` | `` const f = await glob('**/*.tmp'); await $`rm ${f}` `` |
| `pgrep -f name`                 | ``$`pgrep -f ${name}`.nothrow()``                        |
| `diff <(cmd1) <(cmd2)`          | Write both outputs to tmpfile, diff them                 |
| `cmd 2>&1`                      | `.toString()` gives combined stdout+stderr               |
| `LC_ALL=C sort`                 | `` $({ env: { ...process.env, LC_ALL: 'C' } })`sort` ``  |

### Idiomatic One-Liners

```js
// Line count across files
const total = await $`cat ${await glob('logs/*.log')} | wc -l`;

// Sum a column with awk
const total = await $`awk '{ x += $3 } END { print x }' data.tsv`;

// Most recent git tags
const tags = await $`git tag --sort=-version:refname`.lines();
const latest = tags.slice(0, 5);

// Unique sorted values from column 2
const unique = await $`awk '{print $2}' file.txt`.pipe($`sort -u`).lines();

// Count errors by type
const counts = await $`grep "ERROR" app.log`
  .pipe($`sed 's/.*ERROR: //'`)
  .pipe($`sort`)
  .pipe($`uniq -c`)
  .pipe($`sort -rn`)
  .lines();
```

---

## Spinner and Progress

```js
// spinner(title, fn) — wraps any async operation
const result = await spinner('Building project...', () => $`npm run build`);

// With dynamic title update
const release = await spinner(chalk.blue('Deploying to production...'), async () => {
  await $`docker build -t myapp:latest .`;
  await $`docker push myapp:latest`;
  return await $`kubectl rollout status deployment/myapp`;
});
echo(chalk.green('Deploy complete'));
```

---

## Cross-Platform Portability

```js
// Detect OS and branch
if (os.platform() === 'darwin') {
  await $`brew services restart nginx`;
} else {
  await $`sudo systemctl restart nginx`;
}

// Resolve binary cross-platform
const node = await which('node');
echo(`Using Node.js at: ${node}`);

// Windows PowerShell
if (os.platform() === 'win32') {
  usePowerShell();
}
```
