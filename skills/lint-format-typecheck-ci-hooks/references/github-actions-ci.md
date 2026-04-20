# GitHub Actions CI reference

Use this when the user asks to add GitHub Actions CI for typechecking, linting, formatting, or Markdown lint checks.

## CI posture

- CI should be check-only.
- Do not add autofix steps.
- Do not add `autofix.ci`.
- Run `typecheck` before lint/format checks.

## Recommended step order

1. Checkout repository
2. Setup package manager / runtime
3. Install dependencies
4. Run `typecheck`
5. Run lint check
6. Run format check
7. Run optional Markdown lint check

## Recommended package scripts

- `typecheck`: `tsc --noEmit`
- `lint`: tool-specific lint command
- `format:check`: tool-specific formatter check command
- optional `lint:md`: Markdown lint command

## Tool-specific CI commands

### ESLint + Prettier

- `typecheck`: `tsc --noEmit`
- `lint`: `eslint .`
- `format:check`: `prettier . --check --ignore-unknown`

### Biome

- `typecheck`: `tsc --noEmit`
- `lint+format`: `biome ci .`

Prefer `biome ci .` in CI because it is designed for CI environments and emits GitHub-friendly diagnostics.

### Oxc

- `typecheck`: `tsc --noEmit`
- `lint`: `oxlint .`
- `format:check`: `oxfmt --check .`

### Rumdl

- `lint:md`: `rumdl check .`
- Optional official action: `rvben/rumdl@v0`

When using the Rumdl action, keep it in lint/check mode only.

## GitHub Actions notes

- Use `actions/checkout`.
- Use the repo's package manager and lockfile-aware install command.
- Keep permissions minimal (`contents: read` is often enough).
- Prefer pinned dependency versions in the repository over floating tool installs where practical.

## Official documentation

- [Prettier CI](https://prettier.io/docs/ci)
- [Biome continuous integration](https://biomejs.dev/recipes/continuous-integration/)
- [Oxlint CI](https://oxc.rs/docs/guide/usage/linter/ci.html)
- [Oxfmt CI](https://oxc.rs/docs/guide/usage/formatter/ci.html)
- [Rumdl CI/CD](https://rumdl.dev/usage/ci-cd/)
