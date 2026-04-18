# Astro Adapters Reference

SSR adapter notes for Astro 6.

## Cloudflare

- Package: `@astrojs/cloudflare`
- Astro 6 requires adapter v13+
- Supports Workers runtime and bindings
- Typical mode: `output: 'server'`

## Netlify

- Package: `@astrojs/netlify`
- Supports server functions and optional image CDN behavior

## Vercel

- Package: `@astrojs/vercel`
- Supports server output and Vercel platform features

## Node

- Package: `@astrojs/node`
- `standalone` mode for self-hosted server runtime

## Minimal config

```js
export default defineConfig({
  output: 'server',
  adapter: someAdapter(),
});
```
