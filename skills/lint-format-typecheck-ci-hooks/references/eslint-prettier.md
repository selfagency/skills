# ESLint + Prettier setup reference

Use this when toolchain is **ESLint + Prettier**.

## Install

- Dev dependencies:
  - `eslint`
  - `@eslint/js`
  - `typescript`
  - `typescript-eslint`
  - `prettier`
  - `eslint-config-prettier`
  - `husky`
  - `lint-staged`

## Config files

- ESLint flat config: `eslint.config.mjs`
- Prettier config: `.prettierrc`
- Prettier ignore: `.prettierignore`

Minimal ESLint flat config combines:

- `@eslint/js` recommended
- `typescript-eslint` recommended

Apply `eslint-config-prettier` compatibility in ESLint config stack.

## Scripts

- `lint`: `eslint .`
- `lint:fix`: `eslint . --fix`
- `format`: `prettier . --write --ignore-unknown`
- `format:check`: `prettier . --check`

## lint-staged templates

### check mode

- JS/TS: `eslint --max-warnings=0`
- TS/JS/YAML/JSON: `prettier --check --ignore-unknown`
- If Rumdl is selected: Markdown files use `rumdl check`

### fix mode

- JS/TS: `eslint --fix`
- TS/JS/YAML/JSON: `prettier --write --ignore-unknown`
- If Rumdl is selected: Markdown files use `rumdl check --fix` then `rumdl fmt`

For overlapping JS/TS globs in fix mode, run ESLint first and Prettier second in the same command array. Keep Markdown globs separate when Rumdl is selected.

## Coverage mapping

- ESLint: TS/JS linting
- Prettier: TS/JS/YAML/JSON formatting (plus Markdown when Rumdl is not selected)

## CI guidance

- Run `typecheck` first: `tsc --noEmit`
- Lint in CI: `eslint .`
- Format check in CI: `prettier . --check`
- CI should be check-only; do not use `prettier --write`

## Caveats

- Keep local Prettier pinned to avoid editor/version drift.
- If using `--max-warnings=0`, ensure ignored-file warning behavior is handled in flat-config setups.
- If Rumdl is selected, remove Markdown extensions from Prettier lint-staged patterns.

## Official documentation

- [ESLint configuration files (flat config)](https://eslint.org/docs/latest/use/configure/configuration-files)
- [typescript-eslint getting started](https://typescript-eslint.io/getting-started)
- [Prettier install](https://prettier.io/docs/install)
- [Prettier CI](https://prettier.io/docs/ci)
- [Prettier pre-commit integration](https://prettier.io/docs/precommit)
- [eslint-config-prettier](https://github.com/prettier/eslint-config-prettier)
