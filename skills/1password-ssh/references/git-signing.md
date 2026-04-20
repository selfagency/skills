# Git Commit Signing with SSH

## Minimum

- Git 2.34+

## Core git config

```text
gpg.format ssh
user.signingkey <ssh-public-key>
commit.gpgsign true
gpg.ssh.program <1password-op-ssh-sign-path>
```

## Typical program paths

- macOS: `/Applications/1Password.app/Contents/MacOS/op-ssh-sign`
- WSL path differs (`op-ssh-sign-wsl.exe` integration path)

## Register signing key

- GitHub: add as **Signing key**
- GitLab: set usage to include signing
- Bitbucket: register SSH key for signature verification

## Local verification

- Configure `gpg.ssh.allowedSignersFile`
- Add trusted `email + public key` pairs to allowed signers file

## Common failures

- Commit email mismatch with provider account email
- Local repo overrides conflicting with global git config
- Outdated Git reporting unsupported `gpg.format ssh`
