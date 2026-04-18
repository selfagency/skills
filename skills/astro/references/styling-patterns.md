# Astro Styling Patterns Reference

Styling options for Astro 6 components and pages.

## Scoped styles (default)

Styles in `<style>` tags are **automatically scoped** to the component. Astro adds a unique data attribute to generated HTML to isolate styles.

```astro
---
---
<p class="message">Hello</p>

<style>
  .message {
    color: blue; /* Only applies to this component */
  }
</style>
```

## Global styles

### Option 1: `:global()` modifier

```astro
<style>
  :global(body) {
    margin: 0;
  }

  /* Scope outer, global inner */
  .card :global(p) {
    color: gray;
  }
</style>
```

### Option 2: `is:global` on `<style>` tag

```astro
<style is:global>
  body { margin: 0; }
  h1 { font-size: 2rem; }
</style>
```

### Option 3: Import a global stylesheet in a layout

```astro
---
import '../styles/global.css';
---
```

## CSS variables (define + use)

```astro
<div class="themed">
  <slot />
</div>

<style>
  .themed {
    --color-accent: #7928ca;
    color: var(--color-accent);
  }
</style>
```

## Dynamic inline styles

```astro
---
const color = Astro.props.color ?? '#333';
---
<p style={{ color, fontWeight: 'bold' }}>Text</p>
```

Or as a string:

```astro
<p style={`color: ${color};`}>Text</p>
```

## CSS Modules

```astro
---
import styles from './Card.module.css';
---
<div class={styles.card}>
  <slot />
</div>
```

`Card.module.css`:

```css
.card {
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.1);
}
```

## Sass / SCSS

Install `sass` first: `npm install sass`

```astro
<style lang="scss">
  $accent: #7928ca;

  .button {
    background: $accent;

    &:hover {
      background: darken($accent, 10%);
    }
  }
</style>
```

## Tailwind CSS (v4)

With `@tailwindcss/vite` plugin installed, use utility classes directly:

```astro
<button class="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
  Click me
</button>
```

Conditional Tailwind with `class:list`:

```astro
---
const { active } = Astro.props;
---
<button class:list={['px-4 py-2 rounded', active ? 'bg-blue-600 text-white' : 'bg-gray-200']}>
  <slot />
</button>
```

## Styling child framework components

Pass a `class` prop and forward it inside the framework component:

```astro
<ReactCard class="my-custom-class" />
```

Inside `ReactCard.tsx`:

```tsx
export function ReactCard({ class: className }: { class?: string }) {
  return <div className={className}>…</div>;
}
```

> Note: Use `class` (not `className`) in `.astro` files. Astro automatically handles the mapping.

## `<link>` tag for external stylesheets

```astro
---
---
<html>
  <head>
    <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter" />
  </head>
</html>
```
