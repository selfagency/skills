# Copilot and Claude hooks for typecheck/lint/format

Use this reference when users want quality gates enforced through agent lifecycle hooks instead of (or alongside) Git hooks and CI.

## Runtime matrix (must choose first)

Hook formats are **not interchangeable**. Pick the correct format for each runtime.

| Runtime | Config files | Event names | Command fields | Tool input shape |
| --- | --- | --- | --- | --- |
| **Copilot CLI / Cloud agent** | `.github/hooks/*.json` (must be on default branch for cloud) | lowerCamelCase: `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `preToolUse`, `postToolUse`, `errorOccurred`, `agentStop`, `subagentStop` | `bash`, `powershell`, `cwd`, `env`, `timeoutSec` (default 30) | Top-level `toolName` (string) + `toolArgs` (**double-encoded** JSON string — must parse twice) |
| **VS Code Copilot hooks (Preview)** | `.github/hooks/*.json` AND Claude-style files by default | PascalCase: `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `PreCompact`, `SubagentStart`, `SubagentStop`, `Stop` | `command` (+ optional `windows`/`linux`/`osx`, `cwd`, `env`, `timeout`) | `tool_name` + object `tool_input` with **camelCase** values (e.g., `filePath`) |
| **Claude Code** | `.claude/settings.json`, `.claude/settings.local.json`, `~/.claude/settings.json` | PascalCase: `PreToolUse`, `PostToolUse`, `SessionStart`, `Stop`, etc. | `type: "command"`, `command` string (+ `shell`, `timeout`, `async`) | `tool_name` + object `tool_input` with **snake_case** values (e.g., `file_path`) |

### Critical differences to get right

- Copilot uses **lowerCamelCase** event keys; VS Code and Claude use **PascalCase**.
- `"version": 1` is **required** in every `.github/hooks/*.json` file or the hooks will be ignored.
- Copilot `toolArgs` is a **stringified JSON string** — you must call `JSON.parse()` or `jq -r . | jq` twice.
- VS Code **matchers are parsed but not enforced** (all hooks run regardless of matcher value in the current preview). Do not rely on matcher for security policy.
- Claude `PreToolUse` can block via **exit code 2** (stderr goes to Claude as error message) or by writing `{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"..."}}` to stdout. Only `"deny"` stops the tool call.
- Copilot `preToolUse` blocks by writing `{"permissionDecision":"deny","permissionDecisionReason":"..."}` to **stdout** as a single compact line. Only `"deny"` is currently processed — `"allow"` and `"ask"` have no effect.
- Claude provides `$CLAUDE_PROJECT_DIR` env var for script paths.

## VS Code tool name mapping

VS Code tool names differ from Claude tool names. A hook that matches by tool name must use the correct name for the runtime.

| Operation | Claude tool name | VS Code tool name |
| --- | --- | --- |
| Edit existing file | `Edit` | `editFiles` |
| Create new file | `Write` | `create_file` |
| Replace in file | `Edit` | `replace_string_in_file` |
| Read file | `Read` | `readFile` |
| Run command | `Bash` | `runInTerminal` |

## Which events to use for quality gates

- **Post-edit quality checks** (typecheck/lint/format): `PostToolUse` / `postToolUse`
- **Policy deny before risky tool call**: `PreToolUse` / `preToolUse`
- **Session quality reminder / injected context**: `SessionStart` / `sessionStart`
- **Last-chance gate before finish**: `Stop` / `agentStop` (use sparingly; guard against infinite loops)

## Check vs fix behavior (must stay aligned)

- **check mode (non-mutating)**
  - `tsc --noEmit`
  - `eslint .` or `eslint "$FILE"` (file-scoped)
  - `prettier --check "$FILE"`
  - `oxlint "$FILE"` + `oxfmt --check "$FILE"`
  - `biome check` or `biome ci` (CI)
  - `rumdl check "$FILE"`
- **fix mode (mutating)**
  - `eslint --fix "$FILE"`
  - `prettier --write "$FILE"`
  - `oxfmt "$FILE"` (write mode)
  - `biome check --write "$FILE"`
  - `rumdl check --fix "$FILE"` then `rumdl fmt "$FILE"`

## Preferred implementation pattern

1. Put deterministic logic in repository scripts (e.g., `scripts/hooks/quality-gate.sh`).
2. Call the script from the hook config rather than embedding long inline shell.
3. Scope checks to the changed file path when the event payload provides one.
4. Keep full-repo checks (`tsc --noEmit`) in CI; scope hook checks to the edited file for speed.
5. Always exit 0 after a non-blocking informational check.

## Claude Code configuration

### Config file (`.claude/settings.json`)

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/hooks/quality-gate.sh",
            "timeout": 60
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/hooks/final-check.sh"
          }
        ]
      }
    ]
  }
}
```

### Quality gate script (`scripts/hooks/quality-gate.sh`)

Hook receives context on stdin as JSON. Read `tool_input.file_path` (snake_case).

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

# Skip non-TS/JS files
if [[ -z "$FILE" ]] || [[ "$FILE" != *.ts && "$FILE" != *.tsx && "$FILE" != *.js ]]; then
  exit 0
fi

# Run checks; failures print to stderr (surfaced by Claude) and exit non-zero
npx tsc --noEmit --project tsconfig.json 2>&1 | head -20
npx eslint "$FILE" 2>&1
npx prettier --check "$FILE" 2>&1
```

### PreToolUse blocking (deny pattern)

Claude Code recognizes either of these patterns to block a tool call:

- **Exit code 2**: stderr message is shown to the user; Claude retries or stops.
- **Stdout JSON** (preferred): emit `{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Reason here"}}` as the only stdout output.

```bash
#!/usr/bin/env bash
INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.tool_name')
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')

if [[ "$TOOL" == "Write" && "$FILE" == *.lock ]]; then
  echo '{"hookSpecificOutput":{"permissionDecision":"deny","permissionDecisionReason":"Direct edits to lockfiles are not allowed."}}'
  exit 0
fi
```

### Stop hook — guard against infinite loops

If the Stop hook itself triggers another agent action that fires Stop again, use the `stop_hook_active` env var guard:

```bash
#!/usr/bin/env bash
# Guard: Claude sets CLAUDE_STOP_HOOK_ACTIVE to prevent Stop hook re-entry
if [[ "${CLAUDE_STOP_HOOK_ACTIVE:-}" == "1" ]]; then
  exit 0
fi
npx tsc --noEmit 2>&1 | tail -5
```

### Async hooks (non-blocking background checks)

For slow checks that should not block Claude:

```json
{
  "type": "command",
  "command": "\"$CLAUDE_PROJECT_DIR\"/scripts/hooks/slow-check.sh",
  "async": true
}
```

## Copilot CLI/cloud configuration

### Config file (`.github/hooks/quality-gate.json`)

`"version": 1` is required. Use lowerCamelCase event names.

```json
{
  "version": 1,
  "hooks": {
    "postToolUse": [
      {
        "bash": "./scripts/hooks/copilot-quality-gate.sh",
        "powershell": "./scripts/hooks/copilot-quality-gate.ps1",
        "cwd": ".",
        "timeoutSec": 60
      }
    ]
  }
}
```

### Quality gate script (`scripts/hooks/copilot-quality-gate.sh`)

`toolArgs` is a **double-encoded JSON string**. Parse it with `jq` twice (or `jq -r . | jq`).

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // empty')
# toolArgs is a JSON-encoded string — must parse twice
FILE=$(echo "$INPUT" | jq -r '.toolArgs' | jq -r '.filePath // .file_path // empty' 2>/dev/null || true)

# Only run on edit tools; exit 0 silently for others
case "$TOOL_NAME" in
  editFiles|create_file|replace_string_in_file) ;;
  *) exit 0 ;;
esac

if [[ -z "$FILE" ]] || [[ "$FILE" != *.ts && "$FILE" != *.tsx && "$FILE" != *.js ]]; then
  exit 0
fi

npx tsc --noEmit 2>&1 | head -20
npx eslint "$FILE" 2>&1
npx prettier --check "$FILE" 2>&1
```

### PreToolUse deny (Copilot)

Emit a **single compact JSON line** to stdout. Only `"deny"` is processed; `"allow"` and `"ask"` have no effect in current Copilot versions.

```bash
#!/usr/bin/env bash
INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.toolName // empty')
FILE=$(echo "$INPUT" | jq -r '.toolArgs' | jq -r '.filePath // .file_path // empty' 2>/dev/null || true)

if [[ "$TOOL_NAME" == "create_file" && "$FILE" == *.lock ]]; then
  printf '{"permissionDecision":"deny","permissionDecisionReason":"Direct edits to lockfiles are not allowed."}\n'
  exit 0
fi
```

## VS Code Copilot hooks configuration (Preview)

### Config file (`.github/hooks/quality-gate.json`)

VS Code reads `.github/hooks/*.json` using PascalCase event names. Matchers are parsed but **not enforced** — hooks always run regardless of matcher value.

```json
{
  "version": 1,
  "hooks": {
    "PostToolUse": [
      {
        "type": "command",
        "command": "./scripts/hooks/vscode-quality-gate.sh",
        "timeout": 60
      }
    ]
  }
}
```

### Quality gate script (`scripts/hooks/vscode-quality-gate.sh`)

VS Code provides `tool_input` with **camelCase** field names (`filePath`, not `file_path`).

```bash
#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
# VS Code uses camelCase in tool_input
FILE=$(echo "$INPUT" | jq -r '.tool_input.filePath // .tool_input.file_path // empty')

if [[ -z "$FILE" ]] || [[ "$FILE" != *.ts && "$FILE" != *.tsx && "$FILE" != *.js ]]; then
  exit 0
fi

npx tsc --noEmit 2>&1 | head -20
npx eslint "$FILE" 2>&1
npx prettier --check "$FILE" 2>&1
```

## Portable file-path extraction (shared scripts across runtimes)

When one script must handle all runtimes, parse defensively in priority order:

```bash
#!/usr/bin/env bash
INPUT=$(cat)

FILE=$(
  # 1. Claude: snake_case
  echo "$INPUT" | jq -r '.tool_input.file_path // empty' 2>/dev/null ||
  # 2. VS Code: camelCase
  echo "$INPUT" | jq -r '.tool_input.filePath // empty' 2>/dev/null ||
  # 3. Copilot CLI: double-encoded toolArgs
  echo "$INPUT" | jq -r '.toolArgs' 2>/dev/null | jq -r '.filePath // .file_path // empty' 2>/dev/null ||
  echo ""
)

if [[ -z "$FILE" ]]; then
  # No path found — fall back to fast repo-level check or skip
  exit 0
fi
```

## Reliability and safety requirements

- Validate all hook JSON configs before committing (`jq . < file.json`).
- Ensure hook scripts are executable (`chmod +x`) and have a valid shebang line.
- **Security (command injection)**: always double-quote dynamic shell variables (`"$FILE"`, not `$FILE`).
- **Secret leakage** (principal threat): never log env vars or hook input — they may contain tokens.
- Keep deny-decision JSON single-line and syntactically valid; malformed output is ignored by runtimes.
- VS Code only: do not rely on `matcher` for security enforcement — matchers are not applied in the current preview.
- Claude Stop hooks: guard against re-entry with `CLAUDE_STOP_HOOK_ACTIVE` env var check.
- Use `async: true` for slow checks in Claude Code to avoid blocking the agent unnecessarily.

## Documentation references

- Copilot CLI hooks: `https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-hooks`
- Copilot cloud hooks: `https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-hooks`
- Copilot hook schema/reference: `https://docs.github.com/en/copilot/reference/hooks-configuration`
- Copilot hooks concept: `https://docs.github.com/en/copilot/concepts/agents/cloud-agent/about-hooks`
- VS Code hooks: `https://code.visualstudio.com/docs/copilot/customization/hooks`
- Claude Code guide: `https://code.claude.com/docs/en/hooks-guide`
- Claude Code reference: `https://code.claude.com/docs/en/hooks`
