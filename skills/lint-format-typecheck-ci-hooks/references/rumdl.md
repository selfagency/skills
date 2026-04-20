# Rumdl setup reference

Use this when Markdown authority is set to **Rumdl**.

## Install

Install Rumdl so `rumdl` is available on PATH.

Official options include:

- Homebrew: `brew install rvben/tap/rumdl`
- Cargo/pip/uv/mise/Nix (see Rumdl installation docs)

Verify:

- `rumdl --version`

## Core commands

- Check Markdown: `rumdl check .`
- Auto-fix with linting: `rumdl check --fix .`
- Format mode: `rumdl fmt .`
- Initialize config: `rumdl init`

Exit behavior:

- `rumdl check`: exits `1` when violations exist
- `rumdl fmt`: formatter mode, exits `0`

## Configuration files

Prefer one of:

- `.rumdl.toml`
- `pyproject.toml` (`[tool.rumdl]`)

Useful global settings (from Rumdl docs):

- `exclude`
- `include`
- `respect-gitignore`
- `line-length`
- `flavor`
- `output-format`

## lint-staged integration patterns

### check mode

- `*.{md,markdown,mdx}`: `rumdl check`

### fix mode

- `*.{md,markdown,mdx}`: `rumdl check --fix`
- `*.{md,markdown,mdx}`: `rumdl fmt`

Use ordered arrays in lint-staged for the same Markdown glob.

## Supersedence rule

When Rumdl is selected with another JS/TS stack:

- Route Markdown globs to Rumdl only.
- Remove Markdown globs from Prettier/Oxfmt/Biome lint-staged commands.

This keeps Markdown lint/format behavior deterministic and avoids cross-tool conflicts.

## CI guidance

- Run Markdown checks in CI with `rumdl check .`
- If using the official action, keep it in check/annotation mode only
- CI should be check-only; do not add formatting autofix steps

## Official documentation

- [Rumdl installation](https://rumdl.dev/getting-started/installation/)
- [Rumdl quickstart](https://rumdl.dev/getting-started/quickstart/)
- [Rumdl pre-commit integration](https://rumdl.dev/usage/pre-commit/)
- [Rumdl CI/CD integration](https://rumdl.dev/usage/ci-cd/)
- [Rumdl global settings reference](https://rumdl.dev/global-settings/)
