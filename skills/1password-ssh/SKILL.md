---
name: 1password-ssh
description: Use this skill when setting up the 1Password SSH agent, generating or importing SSH keys into 1Password, configuring SSH clients to authenticate through 1Password (IdentityAgent, SSH_AUTH_SOCK), setting up Git commit signing with SSH keys from 1Password, configuring SSH agent forwarding for cloud development environments or remote workstations, or troubleshooting SSH authentication failures. Private keys never leave 1Password.
---

# 1Password SSH

Use this skill for SSH and Git workflows backed by the 1Password SSH agent.

## Core rule

Private keys never leave 1Password. Configure clients to request signing/auth via the agent.

## What this skill covers

- SSH key generation/import requirements.
- 1Password SSH agent setup per OS.
- SSH client configuration (`IdentityAgent` / `SSH_AUTH_SOCK`).
- Git commit signing with SSH.
- SSH agent forwarding for remote workflows.
- Six-key server limit mitigation.

## Setup flow

1. Ensure 1Password desktop app and SSH agent are enabled.
2. Generate or import supported SSH key types.
3. Configure SSH client to use the 1Password socket/pipe.
4. Test with `ssh-add -l` and a host auth check.
5. Configure Git signing if needed.

## Gotchas

- Linux Flatpak/Snap app installs do not support the SSH agent.
- Windows may require disabling the OpenSSH Authentication Agent service so 1Password can own the pipe.
- OpenSSH servers often enforce six auth attempts (`MaxAuthTries=6`), so map keys to hosts.
- Do not enable agent forwarding globally (`Host * ForwardAgent yes`). Scope to trusted hosts.

## Companion skills

- `1password` for CLI/service accounts/shell plugins.
- `1password-environments` for local FIFO `.env` and hooks.
- `1password-secrets-in-code` for MCP/SDK/CI patterns.

## References

- [SSH agent setup](references/ssh-agent.md)
- [Git signing](references/git-signing.md)
- [SSH forwarding](references/ssh-forwarding.md)
