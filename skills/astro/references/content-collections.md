# Astro Content Collections Reference

Deep reference for content collections in Astro 6.

## Schema types (`astro/zod`)

Use `z` from `astro/zod` for schema validation and typing.

## Build-time loaders

- `glob()` for directory-based entries
- `file()` for single JSON/YAML/TOML sources
- custom loaders for CMS/API/data stores

## Build-time config example

```ts
import { defineCollection } from 'astro:content';
import { glob, file } from 'astro/loaders';
import { z } from 'astro/zod';

const blog = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/data/blog' }),
  schema: z.object({ title: z.string(), pubDate: z.coerce.date() }),
});

const dogs = defineCollection({
  loader: file('src/data/dogs.json'),
  schema: z.object({ id: z.string(), breed: z.string() }),
});

export const collections = { blog, dogs };
```

## Query helpers

- `getCollection()`
- `getEntry()`
- `getEntries()`
- `render()`

Always sort explicitly after `getCollection()` if order matters.

## References between collections

Use `reference('collectionName')` in schema and resolve with `getEntry()`/`getEntries()`.

## Live collections

- config in `src/live.config.ts`
- define with `defineLiveCollection()`
- query with `getLiveCollection()` / `getLiveEntry()`
- requires on-demand rendering adapter

## Live error types

- `LiveEntryNotFoundError`
- `LiveCollectionValidationError`
- `LiveCollectionError`
