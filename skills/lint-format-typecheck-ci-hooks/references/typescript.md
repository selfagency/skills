# TypeScript + tsconfig reference

Use this when the user asks for TypeScript installation, `tsconfig` initialization, or reusing an existing `tsconfig`.

## User-initiated rule

- Only install TypeScript or initialize `tsconfig.json` when the user explicitly asks.

## Install TypeScript

Preferred project-local setup:

- install local dev dependency `typescript`
- run compiler via package manager (`npx tsc` or package-manager equivalent)

Avoid relying on global TypeScript in team repos.

## tsconfig paths

### Initialize new config

- Use `tsc --init` when user chooses to initialize.
- After init, keep configuration minimal and project-specific.

### Use existing config

- Ask user for path to existing `tsconfig`.
- Validate path exists before applying.

## Typecheck script convention

Use a `typecheck` script in `package.json`:

- `typecheck`: `tsc --noEmit`

Pre-commit order should run typecheck first, then lint-staged.

## Official documentation

- [TypeScript download and install](https://www.typescriptlang.org/download/)
- [TSConfig reference](https://www.typescriptlang.org/tsconfig/)
