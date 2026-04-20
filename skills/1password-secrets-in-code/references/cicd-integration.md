# CI/CD Integration

## GitHub Actions

Use:

- `1password/load-secrets-action/configure@v2`
- `1password/load-secrets-action@v2`

Use repository secret `OP_SERVICE_ACCOUNT_TOKEN` (or Connect token/host).

Notes:

- Action supports Linux/macOS runners; not Windows runners.
- Secret references use `op://vault/item/field` format.

## CircleCI

Use orb: `onepassword/secrets`.

- `1password/install-cli` first
- `1password/exec` masks secrets in logs
- `1password/export` does not mask printed values

## Jenkins

Use 1Password plugin with `withSecrets` pattern and scoped credentials.

## Precedence gotcha

If Connect env vars are present (`OP_CONNECT_HOST`, `OP_CONNECT_TOKEN`), they take precedence over `OP_SERVICE_ACCOUNT_TOKEN`.
