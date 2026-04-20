# SDK Patterns for AI Agents

## Recommended flow

1. Create a least-privilege service account.
2. Export token to `OP_SERVICE_ACCOUNT_TOKEN`.
3. Authenticate SDK client.
4. Resolve explicit references using `secrets.resolve("op://...")`.
5. Pass resolved values only into sensitive runtime boundaries.

## Security boundary rule

Keep secret-reference resolution in static controller code.

Do not let model-generated code construct arbitrary secret references at runtime.

## Python sketch

```text
client = await Client.authenticate(OP_SERVICE_ACCOUNT_TOKEN, "app-name", "v1")
api_key = await client.secrets.resolve("op://vault/item/field")
```

## Validation

- Verify service account identity first.
- Handle missing/invalid references explicitly.
- Avoid logging resolved values.
