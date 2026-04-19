# Safety and guardrails

Use this file before high-impact mutations.

## Confirmation-required actions

Require explicit user confirmation before:

- delete actions on resources/integrations
- stop-all or broad-scope shutdown actions
- destructive backup schedule changes
- actions that affect multiple production resources at once

## Pre-action message template

Before destructive execution, state:

1. exact target(s)
2. exact operation
3. expected impact
4. rollback/recovery considerations

## Least-risk preference order

Prefer:

1. read/diagnose
2. targeted restart/redeploy
3. narrow config/env change
4. broad-impact controls
5. deletions

## Post-action requirements

After any high-impact action:

- verify resulting state from MCP
- report what changed
- report what failed or remains uncertain
- suggest next safe step

## Secret handling

- Never expose real token values in chat output.
- Use placeholders in examples.
- Only report token metadata/state, not secret material.
