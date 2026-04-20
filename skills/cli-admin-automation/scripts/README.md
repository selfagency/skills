# CLI Admin Automation Scripts

Bundled helper scripts for system administration tasks with structured output and deterministic behavior.

## Scripts

### 1. `validate-jc-output.py`

Validate JSON output from `jc` command-line parser. Ensures output conforms to expected schemas and contains required fields.

**Usage:**

```bash
ps aux | jc --ps | validate-jc-output.py ps
validate-jc-output.py df --input df-output.json --pretty
```

**Modes:**

- Default: Validate and output compact JSON to stdout
- `--pretty`: Pretty-print validated JSON
- `--input FILE`: Read JSON from file instead of stdin

**Supported Parsers:** ps, df, netstat, ls (extensible)

**Exit Codes:**

- 0: Valid JSON
- 1: Invalid JSON or schema violation

---

### 2. `parse-homebrew-bundle.sh`

Analyze and validate Homebrew `Brewfile` for team environments. Check installation status, generate reports, and plan installations.

**Usage:**

```bash
parse-homebrew-bundle.sh Brewfile --check
parse-homebrew-bundle.sh Brewfile --report > status.json
parse-homebrew-bundle.sh Brewfile --dry-run
```

**Modes:**

- `--check`: Verify all packages are installed (JSON status output)
- `--report`: Generate JSON report of package status with timestamps
- `--dry-run`: Show what would be installed without installing

**Output Format (JSON):**

```json
{
  "status": "complete|incomplete",
  "total": 42,
  "missing": ["package-name"],
  "brewfile": "Brewfile"
}
```

**Exit Codes:**

- 0: All packages installed or operation successful
- 1: Missing packages or brewfile error

---

### 3. `monitor-system-health.py`

Real-time system health monitoring dashboard. Continuous monitoring or single JSON snapshot of system metrics.

**Usage:**

```bash
monitor-system-health.py                    # Full dashboard, update every 5 seconds
monitor-system-health.py --interval 2       # Faster updates
monitor-system-health.py --json             # Output JSON snapshot once and exit
monitor-system-health.py --disk --memory    # Only specific metrics
```

**Metrics Included:**

- CPU: Usage percentage, core count, time breakdown
- Memory: Physical and swap usage with percentages
- Disk: All partitions with usage and mount points
- Network: Total bytes sent/received, packet counts
- Processes: Top CPU-consuming processes

**Output Format:**

- Default: ANSI formatted table (continuous updates)
- `--json`: JSON snapshot with all metrics

**Options:**

- `--interval N`: Update interval in seconds (default: 5)
- `--cpu|--memory|--disk|--network`: Include only specific metrics
- `--json`: Single JSON output and exit

**Exit Codes:**

- 0: Monitoring completed or JSON output successful
- 1: Error (missing dependencies, permission denied)

---

### 4. `validate-env-vars.py`

Validate environment variables against a schema file. Supports multiple validation rules and outputs detailed reports.

**Usage:**

```bash
validate-env-vars.py config/env-schema.json
validate-env-vars.py config/env-schema.json --env-file .env.production --strict
validate-env-vars.py config/env-schema.json --json > validation-report.json
```

**Schema Format (JSON):**

```json
{
  "required": ["API_KEY", "DATABASE_URL"],
  "optional": ["LOG_LEVEL"],
  "rules": {
    "API_KEY": {
      "type": "string",
      "min_length": 10,
      "max_length": 100,
      "pattern": "^[a-zA-Z0-9_]+$"
    },
    "PORT": {
      "type": "integer",
      "min": 1024,
      "max": 65535
    },
    "LOG_LEVEL": {
      "type": "choice",
      "values": ["debug", "info", "warn", "error"]
    }
  }
}
```

**Rule Types:**

- `string`: Text with optional length and regex pattern validation
- `integer`: Numbers with optional min/max bounds
- `choice`: Enumerated values

**Output Format:**

- Default: Human-readable summary with checkmarks/warnings
- `--json`: Structured JSON report

**Options:**

- `--env-file FILE`: Load variables from .env file (default: .env)
- `--strict`: Fail on first error (default: collect all errors)
- `--json`: Output JSON report

**Exit Codes:**

- 0: All variables valid
- 1: Validation failed
- 2: Schema file error

---

## Installation & Dependencies

### validate-jc-output.py

```bash
pip install jsonschema>=4.0.0
```

### parse-homebrew-bundle.sh

- No external dependencies (uses standard Homebrew commands)
- Requires: `brew` command available in PATH

### monitor-system-health.py

```bash
pip install psutil>=5.9.0
```

### validate-env-vars.py

```bash
pip install jsonschema>=4.0.0
```

---

## Integration Examples

### CI/CD Pipeline

**Validate environment before deployment:**

```bash
#!/bin/bash
validate-env-vars.py config/prod-env-schema.json \
  --env-file .env.production \
  --strict \
  --json > env-report.json

if [ $? -ne 0 ]; then
  echo "Environment validation failed"
  exit 1
fi
```

**Check system resources before running load test:**

```bash
monitor-system-health.py --json | jq '.disk.partitions[0].percent'
if [ $? -gt 80 ]; then
  echo "Insufficient disk space"
  exit 1
fi
```

**Verify team package consistency:**

```bash
parse-homebrew-bundle.sh Brewfile --check --json
# Use in GitHub Actions to enforce team tooling
```

### Local Development

**Validate output from system commands:**

```bash
ps aux | jc --ps | validate-jc-output.py ps --pretty
```

**Monitor during development:**

```bash
while true; do
  monitor-system-health.py --interval 10 --memory --cpu
done
```

---

## Testing

Each script includes built-in help:

```bash
validate-jc-output.py --help
parse-homebrew-bundle.sh --help
monitor-system-health.py --help
validate-env-vars.py --help
```

---

## Error Handling

All scripts provide:

- Meaningful error messages to stderr
- Structured JSON output on success
- Clear exit codes for scripting
- Graceful handling of missing dependencies
- Permission-denied and file-not-found handling
