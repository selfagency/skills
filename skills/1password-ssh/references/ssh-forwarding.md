# SSH Agent Forwarding

Use forwarding when remote environments need local 1Password-backed auth.

## Single session

- `ssh -A user@host`

## Per-host config (recommended)

```text
Host trusted.example.com
  ForwardAgent yes
```

## Do not do this

```text
Host *
  ForwardAgent yes
```

Global forwarding increases blast radius.

## Verify forwarding

On remote host:

- `echo $SSH_AUTH_SOCK`
- `ssh-add -l`

If keys are listed, forwarded auth is available.

## Server prerequisite

Remote SSHD must allow forwarding (`AllowAgentForwarding yes`).
