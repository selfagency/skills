# Module: Components

This module centralizes component authoring guidance for Astro 6.

## Core rules

1. All component logic lives in the frontmatter fence (`---` ... `---`) and runs server-side only.
2. Below the fence is the template (HTML + expressions).
3. Props are accessed via `Astro.props`; use `interface Props` for typing.
4. Slots are server-rendered; client interactivity requires islands directives.

## Quick patterns

### Minimal component

```astro
---
const { title } = Astro.props;
---
<h1>{title}</h1>
```

### Typed props

```astro
---
interface Props {
  name: string;
  greeting?: string;
}
const { name, greeting = "Hello" } = Astro.props;
---
<p>{greeting}, {name}!</p>
```

### Named slots

```astro
<header><slot name="header" /></header>
<main><slot /></main>
<footer><slot name="footer" /></footer>
```

### Slot transfer for nested layouts

```astro
---
import BaseLayout from './BaseLayout.astro';
---
<BaseLayout>
  <slot name="head" slot="head" />
  <slot />
</BaseLayout>
```

### Slot fallback

```astro
<slot name="sidebar">
  <p>Default sidebar content</p>
</slot>
```

### Check if slot exists

```astro
---
const hasExtra = Astro.slots.has('extra');
---
{hasExtra && <aside><slot name="extra" /></aside>}
```

### Dynamic HTML tag

```astro
---
const Tag = Astro.props.as ?? 'div';
---
<Tag class="wrapper"><slot /></Tag>
```

## HTML component caveats (`.html` files)

- No frontmatter
- No dynamic expressions
- Script tags are not bundled
- No Astro directives

## Load next (if needed)

- `component-syntax.md` for deeper directive and API syntax
- `styling-patterns.md` for scoped/global styling and Tailwind patterns
