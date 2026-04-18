# Astro Project Structure Reference

Conventions for files and directories in an Astro 6 project.

## `src/pages/` — Route definitions

Every file in `src/pages/` becomes a public route based on its path:

| File | Route |
| --- | --- |
| `src/pages/index.astro` | `/` |
| `src/pages/about.astro` | `/about` |
| `src/pages/blog/index.astro` | `/blog` |
| `src/pages/blog/[slug].astro` | `/blog/:slug` |
| `src/pages/blog/[...path].astro` | `/blog/*` (rest) |
| `src/pages/api/data.json.ts` | `/api/data.json` |

Supported page formats: `.astro`, `.md`, `.mdx`, `.mdoc`, `.html`, `.ts`, `.js`

## `src/layouts/` — Layout components

Layouts are regular `.astro` components but by convention wrap entire pages. They use `<slot />` for the page content:

```astro
---
// src/layouts/BaseLayout.astro
const { title } = Astro.props;
---
<html>
  <head><title>{title}</title></head>
  <body><slot /></body>
</html>
```

Layouts can be nested: a blog post layout wraps its content in a base layout.

## `src/components/` — Reusable components

Conventions used by the community:

- `src/components/` — Astro components (`.astro`)
- `src/components/react/` or `src/components/Counter.tsx` — Framework components
- `src/components/ui/` — Shared UI primitives

No enforced structure — organize by feature or type based on project size.

## `src/content.config.ts` — Content collection definitions

Defines build-time collections using loaders. Required filename; the old `src/content/config.ts` is deprecated in Astro 6:

```ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z.object({ title: z.string() }),
});

export const collections = { blog };
```

## `src/live.config.ts` — Live collection definitions

Defines runtime collections (fetched on each request):

```ts
import { defineLiveCollection } from 'astro:content';

const products = defineLiveCollection({
  loader: myApiLoader(),
});

export const collections = { products };
```

## `src/middleware.ts` — Request middleware

```ts
import { defineMiddleware } from 'astro:middleware';

export const onRequest = defineMiddleware(async (context, next) => {
  context.locals.startTime = Date.now();
  const response = await next();
  return response;
});
```

## `src/assets/` — Images and media

Files in `src/assets/` are processed by Vite and optimized by `<Image />`. Not served at a fixed URL — import them:

```astro
---
import heroImage from '../assets/hero.jpg';
import { Image } from 'astro:assets';
---
<Image src={heroImage} alt="Hero" />
```

## `public/` — Static assets

Files in `public/` are copied to `dist/` without processing. Use for:

- `public/favicon.ico` → accessible at `/favicon.ico`
- `public/robots.txt` → accessible at `/robots.txt`
- Files that need stable URLs and no processing

Do NOT put images here if you want `<Image />` optimization — use `src/assets/` instead.

## `tsconfig.json`

Astro provides starter configs:

```json
{
  "extends": "astro/tsconfigs/strict"
}
```

Variants: `base`, `strict`, `strictest`

The `strict` or `strictest` variants are required for content collections to infer types correctly.

## `astro.config.mjs`

Must use ES module syntax (`.mjs`) or set `"type": "module"` in `package.json`. See [astro-config.md](astro-config.md) for all options.

## Naming conventions

- Layouts: PascalCase — `BaseLayout.astro`, `BlogLayout.astro`
- Pages: lowercase-kebab — `about-us.astro`, `privacy-policy.md`
- Components: PascalCase — `Header.astro`, `Button.tsx`
- API endpoints: lowercase-kebab — `send-email.ts`
