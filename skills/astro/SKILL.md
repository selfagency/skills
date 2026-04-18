---
name: astro
description: >
  Unified Astro 6 skill covering components, islands, routing, content
  collections, integrations, and deployment under a single skill directory.
  Use this as the single entry point for Astro questions. Route to internal
  module reference files on demand for topic-specific guidance. Requires
  Node.js v22.12.0+.
---

# Astro 6

## Topic routing (single-skill modules)

| Task | Module reference |
| --- | --- |
| `.astro` component syntax, props, slots, styling | `references/module-components.md` |
| React/Vue/Svelte hydration, `client:*`, `server:defer` | `references/module-islands.md` |
| Routing, dynamic paths, middleware, endpoints | `references/module-routing.md` |
| Content collections, loaders, Markdown/MDX | `references/module-content.md` |
| Integrations, adapters, `astro add` | `references/module-integrations.md` |
| Output modes, env, deployment | `references/module-deployment.md` |
| Starwind UI component usage in Astro | `references/module-starwind.md` |

## Project structure

```text
my-project/
├── src/
│   ├── pages/            # File-based routes (.astro, .md, .mdx, .ts)
│   ├── layouts/          # Reusable layout components
│   ├── components/       # Astro + framework components
│   ├── content/          # (Legacy) content — prefer content.config.ts
│   ├── content.config.ts # Build-time collection definitions (Astro 6)
│   ├── live.config.ts    # Runtime (live) collection definitions
│   ├── middleware.ts      # Request middleware (defineMiddleware)
│   ├── assets/           # Images processed by <Image />
│   └── styles/           # Global CSS
├── public/               # Copied as-is to dist/ (no processing)
├── astro.config.mjs      # Project configuration
├── tsconfig.json         # TypeScript config
└── package.json
```

## `astro.config.mjs` quick reference

```js
import { defineConfig, envField } from 'astro/config';
import react from '@astrojs/react';
import cloudflare from '@astrojs/cloudflare';

export default defineConfig({
  // Deployment target
  site: 'https://example.com',
  base: '/',

  // Output mode
  output: 'static',         // 'static' | 'server' | 'hybrid'
  adapter: cloudflare(),    // Required for 'server' or 'hybrid'

  // Integrations
  integrations: [react()],

  // Type-safe env vars
  env: {
    schema: {
      DATABASE_URL: envField.string({ context: 'server', access: 'secret' }),
      PUBLIC_API: envField.string({ context: 'client', access: 'public' }),
    },
  },

  // Image optimization
  image: {
    remotePatterns: [{ hostname: '*.cloudinary.com' }],
  },

  // i18n routing
  i18n: {
    defaultLocale: 'en',
    locales: ['en', 'fr', 'de'],
  },

  // Build config
  build: {
    inlineStylesheets: 'auto',
  },
});
```

## Starting a new project

```bash
# Create new project
npm create astro@latest

# Add integrations
npx astro add react cloudflare mdx

# Dev server
npm run dev

# Build
npm run build

# Preview built output
npm run preview
```

## Key Astro 6 changes from v4/v5

- Content collections: use `src/content.config.ts` with `glob()` / `file()` loaders from `astro/loaders`
- `z` must be imported from `astro/zod` (not `zod`)
- `render()` is a standalone import from `astro:content` (not a method on entries)
- Live collections: `src/live.config.ts` with `defineLiveCollection()`
- Cloudflare adapter v13+ required
- Server islands: `server:defer` directive on `.astro` components
- `astro:env` with `envField` is the recommended env var approach

## Reference files

Core:

- [project-structure.md](references/project-structure.md) — Detailed file and folder conventions
- [astro-config.md](references/astro-config.md) — All `defineConfig()` options

Module routers:

- [module-components.md](references/module-components.md)
- [module-islands.md](references/module-islands.md)
- [module-routing.md](references/module-routing.md)
- [module-content.md](references/module-content.md)
- [module-integrations.md](references/module-integrations.md)
- [module-deployment.md](references/module-deployment.md)
- [module-starwind.md](references/module-starwind.md)

Detailed module references:

- [component-syntax.md](references/component-syntax.md)
- [styling-patterns.md](references/styling-patterns.md)
- [client-directives.md](references/client-directives.md)
- [server-islands.md](references/server-islands.md)
- [routing-patterns.md](references/routing-patterns.md)
- [ssr-and-endpoints.md](references/ssr-and-endpoints.md)
- [content-collections.md](references/content-collections.md)
- [markdown-mdx.md](references/markdown-mdx.md)
- [framework-components.md](references/framework-components.md)
- [official-integrations.md](references/official-integrations.md)
- [adapters.md](references/adapters.md)
- [build-and-env.md](references/build-and-env.md)
- [starwind-components.md](references/starwind-components.md)
