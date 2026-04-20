# Biome setup reference

Use this when toolchain is **Biome**.

## Install

- Dev dependencies:
  - `@biomejs/biome`
  - `husky`
  - `lint-staged`

Pin Biome version where possible.

## Initialize config

- `npx @biomejs/biome init`
- Config file: `biome.json`

## Scripts

Add/update scripts:

- `lint`: `biome lint .`
- `lint:fix`: `biome lint --write .`
- `format`: `biome format --write .`
- `format:check`: `biome format .`
- `check`: `biome check .`
- `check:fix`: `biome check --write .`

For CI parity, prefer `biome ci` in CI workflows.

## lint-staged templates

### check mode

- Non-Markdown files: `biome check --files-ignore-unknown=true --no-errors-on-unmatched`
- If Rumdl is selected: Markdown files use `rumdl check`

### fix mode

- Non-Markdown files: `biome check --write --files-ignore-unknown=true --no-errors-on-unmatched`
- If Rumdl is selected: Markdown files use `rumdl check --fix` then `rumdl fmt`

## Coverage mapping

Biome can handle JS/TS and JSON-family files directly and can process broader sets with ignore-unknown flags. If Rumdl is selected, Rumdl owns Markdown lint/format.

## CI guidance

- Run `typecheck` first: `tsc --noEmit`
- In CI, prefer `biome ci .`
- CI should be check-only; do not add `--write`

## Caveats

- Without `--no-errors-on-unmatched`, commits that stage unsupported files can fail unexpectedly.
- For mixed monorepos, keep ignores explicit in `biome.json` where needed.
- If Rumdl is selected, remove Markdown patterns from Biome lint-staged entries.

## Official documentation

- [Biome getting started](https://biomejs.dev/guides/getting-started/)
- [Biome configuration reference](https://biomejs.dev/reference/configuration)
- [Biome CLI reference](https://biomejs.dev/reference/cli)
- [Biome Git hooks recipes](https://biomejs.dev/recipes/git-hooks/)
- [Biome CI recipes](https://biomejs.dev/recipes/continuous-integration)
- [Biome language support](https://biomejs.dev/internals/language-support)
