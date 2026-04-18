# Module: Islands

This module centralizes selective hydration and server island guidance for Astro 6.

## Core rule

Default Astro output ships zero JS. Add `client:*` directives only where interactivity is required.

## Client directives

| Directive | Hydrates when | Use for |
| --- | --- | --- |
| `client:load` | Immediately on load | Above-the-fold interactive UI |
| `client:idle` | Browser idle | Lower-priority interactions |
| `client:visible` | Enters viewport | Below-the-fold widgets |
| `client:media="(query)"` | Media query matches | Responsive-only widgets |
| `client:only="framework"` | Client only | Browser-only components |

```astro
<Counter client:load />
<Chart client:idle />
<Chart client:visible />
<MobileMenu client:media="(max-width: 768px)" />
<ReactDatePicker client:only="react" />
```

## `client:only` values

- `react`
- `vue`
- `svelte`
- `solid-js`
- `preact`

## Props and state

- Island props must be serializable.
- Islands are isolated; shared state should use Nano Stores, URL state, or custom events.

## Server islands

Use `server:defer` on `.astro` components to defer expensive/personalized server work:

```astro
<PersonalGreeting server:defer>
  <p slot="fallback">Loading greeting…</p>
</PersonalGreeting>
```

Key constraints:

- Works on `.astro` components (not framework components)
- Fallback should avoid CLS
- Request-time data requires an SSR adapter

## Load next (if needed)

- `client-directives.md` for directive options like `rootMargin`
- `server-islands.md` for runtime/caching/session details
