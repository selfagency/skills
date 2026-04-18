# `defineConfig()` Options Reference

All top-level options available in `astro.config.mjs` for Astro 6.

## Root options

```js
import { defineConfig } from 'astro/config';

export default defineConfig({
  root: '.',                  // Project root (default: process.cwd())
  srcDir: './src',            // Source directory
  publicDir: './public',      // Static assets directory
  outDir: './dist',           // Build output directory
  cacheDir: './node_modules/.astro', // Build cache
  site: 'https://example.com',      // Full deployment URL (for sitemaps, canonical)
  base: '/',                  // Base path if not deployed at root, e.g. '/docs'
  trailingSlash: 'ignore',   // 'always' | 'never' | 'ignore'
  output: 'static',          // 'static' | 'server' | 'hybrid'
  adapter: undefined,        // SSR adapter (required for server/hybrid)
  integrations: [],          // Plugin integrations
});
```

## `server` — Dev server options

```js
server: {
  host: false,               // true/'0.0.0.0' to expose to network
  port: 4321,
  open: false,               // Open browser on dev start
  headers: {},               // Custom response headers in dev
  allowedHosts: [],          // Restrict to specific hostnames
}
```

## `build` — Build options

```js
build: {
  format: 'directory',       // 'file' | 'directory' | 'preserve'
  client: './dist/client',   // Client assets output (SSR)
  server: './dist/server',   // Server output (SSR)
  assets: '_astro',          // Sub-directory for hashed assets
  assetsPrefix: '',           // Prefix for asset URLs (CDN)
  serverEntry: 'entry.mjs',  // SSR entry file name
  redirects: true,           // Generate redirect config for adapters
  inlineStylesheets: 'auto', // 'always' | 'never' | 'auto'
  concurrency: 1,            // Parallel page build count
}
```

## `image` — Image optimization

```js
image: {
  service: {
    entrypoint: 'astro/assets/services/sharp', // or 'astro/assets/services/noop'
    config: {},
  },
  remotePatterns: [
    {
      protocol: 'https',
      hostname: '*.cloudinary.com',
      pathname: '/images/**',
      port: '',
    },
  ],
  domains: ['example.com'],         // Legacy hostname allowlist
  experimentalObjectFit: 'fill',    // Default object-fit for <Image />
  experimentalObjectPosition: 'center',
}
```

## `markdown` — Markdown processing

```js
markdown: {
  syntaxHighlight: 'shiki',  // 'shiki' | 'prism' | false
  shikiConfig: {
    theme: 'github-dark',
    themes: { light: 'github-light', dark: 'github-dark' },
    langs: [],
    wrap: false,
    transformers: [],
  },
  remarkPlugins: [],
  rehypePlugins: [],
  remarkRehype: {},
  gfm: true,                 // GitHub Flavored Markdown
  smartypants: true,         // Smart quotes/dashes
}
```

## `i18n` — Internationalization

```js
i18n: {
  defaultLocale: 'en',
  locales: ['en', 'fr', 'de', { codes: ['zh-CN', 'zh-Hans'], path: 'zh' }],
  routing: {
    prefixDefaultLocale: false,  // Prefix /en/ on default locale
    redirectToDefaultLocale: true,
    fallbackType: 'redirect',    // 'redirect' | 'rewrite'
    strategy: 'pathname',
  },
  fallback: {
    fr: 'en',   // Fallback fr → en for missing translations
  },
}
```

## `redirects` — Static redirects

```js
redirects: {
  '/old': '/new',
  '/blog/[slug]': '/posts/[slug]',
  '/moved': {
    status: 301,
    destination: '/new-location',
  },
}
```

## `env` — Type-safe environment variables

```js
import { defineConfig, envField } from 'astro/config';

export default defineConfig({
  env: {
    schema: {
      SECRET_KEY: envField.string({ context: 'server', access: 'secret' }),
      PUBLIC_URL: envField.string({ context: 'client', access: 'public' }),
      PORT: envField.number({ context: 'server', access: 'secret', default: 3000 }),
      DEBUG: envField.boolean({ context: 'server', access: 'secret', default: false }),
      TIER: envField.enum({
        context: 'server',
        access: 'secret',
        values: ['free', 'pro', 'enterprise'],
      }),
    },
    validateSecrets: false,  // Skip secret validation at build time
  },
})
```

## `vite` — Vite passthrough config

```js
vite: {
  plugins: [],
  resolve: {
    alias: { '@': '/src' },
  },
  optimizeDeps: {
    include: ['lodash-es'],
  },
  ssr: {
    noExternal: ['some-package'],
  },
}
```

## `experimental` — Opt-in experimental features

Experimental flags change between releases. Check the Astro changelog before using:

```js
experimental: {
  contentIntellisense: true,
  fonts: true,
}
```
