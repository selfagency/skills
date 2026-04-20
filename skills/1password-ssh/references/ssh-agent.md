# SSH Agent Setup

## Socket paths

- macOS: `~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock`
- Linux: `~/.1password/agent.sock`
- Windows: `\\.\\pipe\\openssh-ssh-agent`

## SSH config (Mac/Linux)

Use `IdentityAgent` in `~/.ssh/config`:

```text
Host *
  IdentityAgent ~/.1password/agent.sock
```

(Use the macOS path above if you do not symlink.)

## Alternative env var (Mac/Linux)

- `SSH_AUTH_SOCK` can point to the same agent socket.

## Eligibility

- Key types: Ed25519 preferred; RSA 2048/3072/4096 supported.
- Keys must be active and in eligible/configured vaults.

## Agent config file (optional)

- `~/.config/1Password/ssh/agent.toml`
- Use `[[ssh-keys]]` sections with `item`, `vault`, and `account` filters.

## Troubleshooting

- If key list is empty, run `ssh-add -l` against the correct socket/pipe.
- On Windows, disable built-in OpenSSH Authentication Agent service if it conflicts.
- If using many keys, map host-to-key to avoid auth failures.
