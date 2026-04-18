# Module: Routing

This module centralizes routing behavior for Astro 6.

## Core rule

Each file in `src/pages/` maps to a route. Supported route file types include `.astro`, `.md`, `.mdx`, `.html`, and `.ts/.js` endpoints.

## File-based routes

```text
src/pages/
  index.astro       -> /
  about.astro       -> /about
  blog/[slug].astro -> /blog/:slug
  api/users.ts      -> /api/users
```

## Dynamic routes

### Static output

Use `getStaticPaths()`:

```astro
---
import { getCollection } from 'astro:content';
export async function getStaticPaths() {
  const posts = await getCollection('blog');
  return posts.map(post => ({ params: { slug: post.id }, props: { post } }));
}
const { post } = Astro.props;
---
```

### SSR/on-demand

No `getStaticPaths()` required:

```astro
---
export const prerender = false;
import { getEntry } from 'astro:content';
const post = await getEntry('blog', Astro.params.slug);
if (!post) return Astro.redirect('/404');
---
```

## Rest parameters

Use `[...path].astro` for catch-all routes.

## Middleware

Define `src/middleware.ts` with `defineMiddleware()` and optional `sequence()` chaining.

## Redirects

- Config-level redirects in `astro.config.mjs`
- Runtime redirects via `Astro.redirect()`

## `prerender` behavior

- In `static`/`hybrid`: `prerender = false` opts route into SSR
- In `server`: `prerender = true` opts route into static

## Load next (if needed)

- `routing-patterns.md` for pagination, i18n, route data passing
- `ssr-and-endpoints.md` for API routes and HTTP method handling
