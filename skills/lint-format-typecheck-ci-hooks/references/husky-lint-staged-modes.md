# Husky + lint-staged modes reference

Use this for hook installation and mode-specific lint-staged configuration.

## Husky setup

1. Install Husky as dev dependency.
2. Ensure `prepare` script runs Husky setup.
3. Initialize Husky and create `.husky/pre-commit`.
4. Put `typecheck` first, then `lint-staged` invocation in pre-commit hook.

Example pre-commit hook content:

`pnpm run typecheck && pnpm exec lint-staged`

Use package-manager equivalent if not using pnpm.

Expected script in `package.json`:

- `typecheck`: `tsc --noEmit`

## lint-staged config location

Use one of:

- `package.json` `lint-staged` field
- `lint-staged.config.{js,mjs,cjs}`
- `.lintstagedrc.{json,yaml,yml,js,mjs,cjs}`

## Mode templates

### check mode

- Commands must not write files.
- Commit fails on lint/format diffs or lint violations.
- If Rumdl is selected, run Rumdl on Markdown globs in check mode.
- Run `typecheck` before `lint-staged`.

### fix mode

- Commands may write files (`--fix`, `--write`).
- lint-staged re-stages modifications automatically.
- If Rumdl is selected, use ordered Markdown commands: `rumdl check --fix` then `rumdl fmt`.
- Run `typecheck` before `lint-staged`.

### Rumdl markdown supersedence

When Rumdl is selected with another stack:

- Markdown globs (`*.md`, `*.markdown`, `*.mdx`) must be handled by Rumdl.
- Remove Markdown extensions from Prettier/Oxfmt/Biome commands.
- Keep JS/TS/YAML/JSON on the selected JS/TS stack.

Example (ESLint + Prettier + Rumdl in fix mode):

- `*.{js,jsx,ts,tsx,mjs,cjs,mts,cts}`: `["eslint --fix", "prettier --write --ignore-unknown"]`
- `*.{yaml,yml,json,jsonc}`: `["prettier --write --ignore-unknown"]`
- `*.{md,markdown,mdx}`: `["rumdl check --fix", "rumdl fmt"]`

## Race-condition-safe patterns

- Avoid overlapping write commands on separate globs that can hit same files.
- For same file family, use an array to enforce order.

Good pattern:

- `*.{ts,tsx,js,jsx}`: `["eslint --fix", "prettier --write --ignore-unknown"]`

Avoid:

- `*`: `prettier --write`
- `*.ts`: `eslint --fix`

This can race on `.ts` files.

## Safety notes

- Do not add `git add` in lint-staged tasks.
- lint-staged stashes and restores state by default to reduce data loss risk.
- In GUI clients, Husky may need shell init in user Husky startup file for Node version managers.
- `rumdl fmt` exits 0 by design; use `rumdl check`/`rumdl check --fix` for enforcement semantics.

## Official documentation

- [lint-staged README](https://github.com/lint-staged/lint-staged)
- [Husky get started](https://typicode.github.io/husky/get-started.html)
- [Husky how-to](https://typicode.github.io/husky/how-to.html)
- [Husky troubleshoot](https://typicode.github.io/husky/troubleshoot.html)
