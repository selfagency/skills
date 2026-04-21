---
name: lint-format-typecheck-ci-hooks
description: Install and configure JavaScript/TypeScript typechecking, linting, formatting, Git pre-commit hooks, and GitHub Actions CI checks. Use this skill when the user asks to set up or migrate code quality tooling with Husky and lint-staged, choose between Oxc (oxlint+oxfmt), Biome, or ESLint+Prettier, optionally select Rumdl as Markdown linter/formatter, add `tsc --noEmit` typechecking, configure GitHub Actions CI for check-only validation, copy existing config files, generate new configs, or enforce either check-only or auto-fix pre-commit behavior for TS/JS/YAML/JSON/Markdown files.
---

# Lint + Format + Typecheck + CI + Hooks Setup

## Outcome

Provision one toolchain and one hook mode:

1. **Toolchain**
   - Oxc (`oxlint` + `oxfmt`)
   - Biome (`@biomejs/biome`)
   - ESLint + Prettier (`eslint` + `typescript-eslint` + `prettier`)
2. **Hook mode**
   - **check**: fail commit on lint/format issues
   - **fix**: auto-fix/format before commit
3. **Markdown authority (optional override)**
   - default stack formatter/linter handling
   - Rumdl override for Markdown

Always ensure support for **TS, JS, YAML, JSON, Markdown** by combining tools correctly.

## Defaults

- Default package manager: detect from lockfile (`pnpm-lock.yaml`, `yarn.lock`, `package-lock.json`, `bun.lockb`).
- Default hook manager: Husky + lint-staged.
- Default operation: prefer reusing existing configs if user provides paths; otherwise generate minimal safe configs.

## Load references on demand

- Read `references/oxc.md` when toolchain is Oxc.
- Read `references/biome.md` when toolchain is Biome.
- Read `references/eslint-prettier.md` when toolchain is ESLint+Prettier.
- Read `references/typescript.md` when TypeScript install/config setup is requested.
- Read `references/github-actions-ci.md` when GitHub Actions CI setup is requested.
- Read `references/rumdl.md` when user selects Rumdl for Markdown lint/format.
- Read `references/husky-lint-staged-modes.md` for hook setup, race-safe task ordering, and mode templates.
- Read `references/tooling-docs.md` when you need authoritative online configuration references for any tool.
- Read `references/copilot-claude-hooks.md` when the user asks to enforce typecheck/lint/format via agent hooks in Claude Code, GitHub Copilot CLI/cloud, or VS Code Copilot hooks.

## Workflow

1. Detect workspace package manager and whether the repo is initialized with Git.
2. Ask user to choose:
   - toolchain (`oxc`, `biome`, `eslint-prettier`)
   - markdown authority (`default`, `rumdl`)
   - TypeScript setup (`leave-as-is`, `install+init-tsconfig`, `install+use-existing-tsconfig`)
   - config strategy (`copy-existing`, `generate-new`)
   - hook mode (`check`, `fix`)
3. If `copy-existing`, ask for config file paths and validate they exist.
4. Install selected dependencies and add or update package scripts.
5. Create/update config files.
6. Configure Husky and lint-staged for the selected mode, with pre-commit typecheck before lint-staged.
7. If requested, configure GitHub Actions CI for typecheck + lint/format checks.
8. If requested, configure agent hooks for Claude Code and/or Copilot to enforce typecheck/lint/format at agent lifecycle events.
   - Select runtime target explicitly: Claude Code, Copilot CLI/cloud, VS Code Copilot hooks (Preview), or multiple.
   - If Copilot is selected, clarify whether target is CLI/cloud hooks schema, VS Code hooks schema, or both.
   - Use runtime-native schema/event names (do not mix PascalCase and lowerCamelCase events).
9. Validate by running lint/format/typecheck check commands.
10. Report exactly what changed and how to switch modes later.

## Required questions

Ask these before mutating files:

1. **Toolchain**: Oxc, Biome, or ESLint+Prettier?
2. **Markdown authority**: Keep stack default handling, or use Rumdl for Markdown lint/format?
3. **TypeScript setup** (user-initiated only):
   - `leave-as-is`
   - `install+init-tsconfig`
   - `install+use-existing-tsconfig`
4. **Config source**: Copy existing config files or generate new ones?
5. **Pre-commit mode**:
   - `check` (block commit on issues)
   - `fix` (auto-fix and stage updated files)
6. **Scope preference** (if ambiguous): staged files only (recommended) or whole-repo commands in pre-commit (slower).
7. **Agent hook target** (optional): none, Claude Code, Copilot CLI/cloud, VS Code Copilot hooks, or multiple?
8. **Copilot runtime scope** (if Copilot hooks enabled): CLI/cloud schema, VS Code schema, or both?
9. **Hook enforcement style** (if hooks enabled):
   - post-edit checks only (`PostToolUse`), or
   - include pre-tool deny/ask controls (`PreToolUse`) for policy enforcement?

## TypeScript setup and tsconfig

- Do not install TypeScript or initialize `tsconfig.json` unless the user explicitly asks.
- If user initiates TypeScript setup:
  - Install local dev dependency `typescript`.
  - Choose one path:
    - Initialize config (`tsc --init`) and then tailor minimal options.
    - Use existing user-provided `tsconfig` path/content.
- If user selects `install+use-existing-tsconfig`, validate provided path exists before applying.
- Prefer project-local TypeScript over global install for reproducibility.
- Pre-commit ordering: run `typecheck` before `lint-staged`.
- Preferred `typecheck` script is `tsc --noEmit`.

## GitHub Actions CI

- CI guidance in this skill is check-only.
- Do not add autofix steps or `autofix.ci` workflows.
- Run `typecheck` before lint/format checks in CI.
- Prefer separate, explicit steps in GitHub Actions:
  - `typecheck`
  - linter check
  - formatter check
  - optional Markdown lint check
- For Biome in CI, prefer `biome ci .` over `biome check .`.
- For Oxc in CI, use check commands only (`oxlint`, `oxfmt --check`).
- For Prettier in CI, use `prettier --check`, not `--write`.
- For Rumdl in CI, use `rumdl check .` or the official GitHub Action in check mode only.

## Agent hooks for Claude and Copilot (optional)

- Use this only when user explicitly asks to enforce checks through agent hooks.
- Load `references/copilot-claude-hooks.md` before writing hook files.
- Always state which runtime config is being produced:
  - Claude Code (`.claude/settings*.json`, PascalCase events)
  - Copilot CLI/cloud (`.github/hooks/*.json`, `version: 1`, lowerCamelCase events)
  - VS Code Copilot hooks (Preview; validate behavior with hook logs)
- For Copilot guidance, keep CLI/cloud and VS Code command schemas separate:
  - CLI/cloud: `bash`/`powershell` + `timeoutSec`
  - VS Code: `command` (+ optional `windows`/`linux`/`osx`) + `timeout`
- Keep hook commands deterministic and non-interactive.
- Prefer repository-local scripts under `scripts/` for reusable logic, then call those scripts from hook configs.
- Enforce check vs fix semantics consistently with selected mode:
  - `check` mode: non-mutating commands only (`--check`, no `--write` / `--fix` unless user asks to change behavior)
  - `fix` mode: allow mutating format/fix commands where user requested
- Preserve stack boundaries:
  - Oxc: `oxlint` + `oxfmt` roles unchanged
  - Biome: `biome ci` for CI checks; `biome check` / `biome check --write` by mode
  - ESLint+Prettier: keep ESLint-before-Prettier ordering on overlapping JS/TS files
  - Rumdl override: Markdown handled by Rumdl when selected
- For performance, scope hook actions to changed file(s) when platform supports per-tool file metadata.

## Coverage rules by toolchain

### Oxc

- Use `oxlint` for JS/TS linting.
- Use `oxfmt` for formatting JS/TS/YAML/JSON and Markdown unless Rumdl is selected.
- Do not claim `oxlint` handles YAML/JSON/Markdown linting.

### Biome

- Use `biome check` in check mode.
- Use `biome check --write` in fix mode.
- Include hook-safe flags where relevant:
  - `--files-ignore-unknown=true`
  - `--no-errors-on-unmatched`
- If Rumdl is selected, route Markdown files to Rumdl and keep Biome on non-Markdown files.

### ESLint + Prettier

- Use ESLint for JS/TS linting.
- Use Prettier for JS/TS/YAML/JSON and Markdown unless Rumdl is selected.
- In lint-staged fix mode, run ESLint before Prettier on overlapping JS/TS globs.

### Rumdl Markdown override

- If user selects Rumdl, Rumdl becomes the Markdown linter/formatter.
- Supersede stack Markdown handling for `*.md`, `*.markdown`, and `*.mdx`.
- Use:
  - check mode: `rumdl check`
  - fix mode: `rumdl check --fix` then `rumdl fmt`

## Gotchas

- `lint-staged` passes matched staged files automatically to command strings.
- Avoid overlapping write tasks running concurrently on same files; use ordered arrays for same glob.
- Do not add `git add` inside lint-staged tasks; lint-staged handles re-staging.
- Husky hooks can fail in GUI terminals if Node version manager init is missing.
- If user chooses “whole repo in pre-commit,” warn about slower commits.
- `rumdl fmt` exits 0 by design; use `rumdl check`/`rumdl check --fix` when you need lint enforcement.
- Typecheck runs on the whole project and can be slower than lint-staged; keep it first so commits fail early on type errors.

## Optional helper scripts

- `scripts/validate-config-paths.mjs`: validate provided config paths.
- `scripts/render-lintstaged-config.mjs`: generate deterministic lint-staged config fragment for selected stack, mode, and markdown authority.

Run helpers non-interactively with flags only.

## Completion checklist

- Dependencies installed for selected stack.
- Config files copied or generated.
- `package.json` scripts updated.
- Husky initialized and `.husky/pre-commit` present.
- Pre-commit hook runs `typecheck` before `lint-staged`.
- lint-staged config written with selected mode.
- GitHub Actions CI uses check-only commands with `typecheck` before linting.
- Validation command run successfully.
