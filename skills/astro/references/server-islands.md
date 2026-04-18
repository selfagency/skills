# Server Islands Reference

Server islands (`server:defer`) defer server-rendered content until after initial HTML response.

## How it works

1. Initial page HTML renders with fallback.
2. Deferred component is fetched server-side.
3. Fallback is replaced.

## Basic pattern

```astro
---
import UserGreeting from '../components/UserGreeting.astro';
---

<UserGreeting server:defer>
  <span slot="fallback">Loading…</span>
</UserGreeting>
```

## Fallback best practices

- Keep fallback lightweight
- Match expected dimensions to avoid CLS
- Treat it as always briefly visible

## Server context availability

Deferred components can access:

- `Astro.request`
- `Astro.locals`
- `Astro.cookies`

## Constraints

- Works on `.astro` components only
- Not for framework components directly
- Design around fallback UX
