# 1Password CLI Examples

## Read a secret

- `op read op://AI/GitHub/token`

## Run app with referenced secrets

- `op run --env-file=.env.op -- node server.js`

## Inject template

- `op inject -i app.config.tpl -o app.config`

## Service account identity check

- `op user get --me`

## Scope item operations

- `op item list --vault app-secrets`
- `op item get <item-id> --vault <vault-id> --format json`

## Check service-account rate usage

- `op service-account ratelimit`
