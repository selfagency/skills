# Module: Deployment

This module centralizes Astro 6 deployment and environment configuration.

## Output modes

- `static` (default): fully prerendered
- `server`: full SSR/on-demand
- `hybrid`: prerender by default, opt routes into SSR

Per route:

```ts
export const prerender = false; // opt into SSR in static/hybrid
export const prerender = true;  // opt into static in server
```

## Adapters

Add with:

```bash
npx astro add cloudflare
npx astro add netlify
npx astro add vercel
npx astro add node
```

## Type-safe env vars (`astro:env`)

Define schema with `envField` in `astro.config.mjs`, then import from:

- `astro:env/server`
- `astro:env/client`

## Build & preview

```bash
npx astro build
npx astro preview
```

## Cloudflare note

Astro 6 expects `@astrojs/cloudflare` v13+.

## Load next (if needed)

- `adapters.md` for host-specific adapter config
- `build-and-env.md` for build options and env strategies
