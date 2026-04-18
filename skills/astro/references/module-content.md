# Module: Content Collections

This module centralizes content modeling and querying in Astro 6.

## Core rule

Use loader-based config:

- Build-time collections: `src/content.config.ts`
- Live runtime collections: `src/live.config.ts`

Import `z` from `astro/zod`.

## Build-time collections

```ts
import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/data/blog' }),
  schema: z.object({ title: z.string(), pubDate: z.coerce.date(), draft: z.boolean().default(false) }),
});

const authors = defineCollection({
  loader: file('src/data/authors.json'),
  schema: z.object({ name: z.string() }),
});

export const collections = { blog, authors };
```

## Query and render

```astro
---
import { getCollection, getEntry, render } from 'astro:content';
const posts = (await getCollection('blog', ({ data }) => !data.draft))
  .sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
const post = await getEntry('blog', 'hello-world');
const { Content } = await render(post);
---
```

## References

Use `reference('collection')` in schemas and resolve with `getEntry()` / `getEntries()`.

## Live collections

Use `defineLiveCollection()` and query with `getLiveCollection()` / `getLiveEntry()` on SSR routes.

## Route generation

Use collection IDs in `getStaticPaths()` to generate content routes.

## Load next (if needed)

- `content-collections.md` for loader options, schema details, live errors
- `markdown-mdx.md` for Markdown/MDX/Markdoc rendering patterns
