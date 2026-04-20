# Oxc setup reference

Use this when toolchain is **Oxc**.

## Install

- Dev dependencies:
  - `oxlint`
  - `oxfmt`
  - `husky`
  - `lint-staged`

## Scripts

Add/update scripts:

- `lint`: `oxlint .`
- `lint:fix`: `oxlint --fix .`
- `format`: `oxfmt --no-error-on-unmatched-pattern .`
- `format:check`: `oxfmt --check .`

## Config files

- Lint config: `.oxlintrc.json` (or `oxlint.config.ts`)
- Formatter config: `.oxfmtrc.json`

Generate defaults if missing:

- `oxlint --init`
- `oxfmt --init`

## lint-staged templates

### check mode

- JS/TS: run `oxlint` without `--fix`
- Non-Markdown supported files: run `oxfmt --check`
- If Rumdl is selected: Markdown files run via `rumdl check`

### fix mode

- JS/TS: run `oxlint --fix`
- Non-Markdown supported files: run `oxfmt --no-error-on-unmatched-pattern`
- If Rumdl is selected: Markdown files run via `rumdl check --fix` then `rumdl fmt`

## Coverage mapping

- `oxlint`: JS/TS linting
- `oxfmt`: TS/JS/YAML/JSON formatting (plus Markdown when Rumdl is not selected)

## CI guidance

- Run `typecheck` first: `tsc --noEmit`
- Lint in CI: `oxlint`
- Format check in CI: `oxfmt --check`
- CI should be check-only; do not add formatter autofix steps

## Caveats

- Oxfmt has compatibility limitations vs Prettier plugins; do not assume plugin parity.
- Keep lint and format commands separate for clear error reporting.
- If Rumdl is selected, remove Markdown extensions from Oxfmt lint-staged patterns.

## Official documentation

- [Oxc docs home](https://oxc.rs/docs/guide/introduction)
- [Oxlint quickstart](https://oxc.rs/docs/guide/usage/linter/quickstart.html)
- [Oxlint configuration](https://oxc.rs/docs/guide/usage/linter/config)
- [Oxlint CI and integrations](https://oxc.rs/docs/guide/usage/linter/ci.html)
- [Oxfmt quickstart](https://oxc.rs/docs/guide/usage/formatter/quickstart.html)
- [Oxfmt configuration](https://oxc.rs/docs/guide/usage/formatter/config)
- [Oxfmt CI and integrations](https://oxc.rs/docs/guide/usage/formatter/ci.html)
- [Oxfmt unsupported features](https://oxc.rs/docs/guide/usage/formatter/unsupported-features)
- [Oxc compatibility matrix](https://oxc.rs/compatibility)
