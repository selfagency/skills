# Module: Integrations

This module centralizes Astro 6 integration setup and adapter selection.

## Add integrations

Preferred:

```bash
npx astro add react
npx astro add cloudflare
npx astro add mdx
```

## Framework integrations

- `@astrojs/react`
- `@astrojs/vue`
- `@astrojs/svelte`
- `@astrojs/solid-js`
- `@astrojs/preact`
- `@astrojs/alpinejs`

Multiple frameworks can coexist.

## SSR adapters

- `@astrojs/cloudflare`
- `@astrojs/netlify`
- `@astrojs/vercel`
- `@astrojs/node`

Adapters require `output: 'server'` or `output: 'hybrid'`.

## Other official integrations

- `@astrojs/mdx`
- `@astrojs/markdoc`
- `@astrojs/partytown`
- `@astrojs/sitemap`
- `@astrojs/db`

## Upgrade flow

```bash
npx @astrojs/upgrade
```

## Load next (if needed)

- `framework-components.md` for framework-component usage in `.astro`
- `official-integrations.md` for per-package config details
