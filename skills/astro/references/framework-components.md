# Using Framework Components in Astro

Reference for React/Vue/Svelte/Solid/Preact components in `.astro` files.

## Basic usage

Import framework components in `.astro` and add `client:*` when interactive.

```astro
<ReactCounter client:load />
<VueWidget client:visible />
<SvelteCard client:idle />
```

Without `client:*`, components render static HTML only.

## Props

Props are passed as attributes. Interactive island props must be serializable.

## Children/slots

Framework slot semantics apply (`children` in React, slots in Vue/Svelte).

## Mixed frameworks

Multiple frameworks can coexist on one page, each as isolated islands.

## Browser-only components

Use `client:only` with explicit framework value:

- `client:only="react"`
- `client:only="vue"`
- `client:only="svelte"`
- `client:only="solid-js"`
- `client:only="preact"`
