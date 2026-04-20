# 1Password CLI Get Started

## Install

- macOS (Homebrew): install `1password-cli`.
- Verify with `op --version`.

## Desktop app integration

- Enable CLI integration in the 1Password desktop app.
- Keep the app unlocked during first sign-in.

## Sign-in basics

- Single account: `op signin`
- Multi-account: use `--account` or set `OP_ACCOUNT`.
- Verify auth state: `op whoami`.

## First secure reads

- Read one value: `op read op://vault/item/field`
- Run command with injected vars: `op run --env-file=.env.op -- <command>`

## Security checklist

- Never commit plaintext secrets.
- Keep `.env`, `.env.op`, and resolved config outputs in `.gitignore`.
- Rotate leaked or overscoped tokens immediately.
