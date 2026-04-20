# Local `.env` Files (1Password Environments)

## Key behavior

- Mounted `.env` files are FIFO-backed and not plaintext-at-rest.
- Secrets are returned on read after approval/unlock.

## Platform support

- Supported: macOS, Linux
- Not supported: Windows (for local mounted `.env`)

## Limits and caveats

- Up to 10 enabled local `.env` destinations per device.
- Concurrent access can fail or delay; avoid multiple readers on the same mounted file.
- Some file watchers treat FIFO activity as file changes.

## Dotenv compatibility highlights

- Node.js: `dotenv` compatible
- Python: `python-dotenv` compatible (v1.2.1+)
- Go: `godotenv` compatible

## Git behavior note

If an existing tracked `.env` file is replaced by a mount, remove and commit deletion first to avoid noisy git state.
