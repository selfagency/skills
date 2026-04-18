# Astro Routing Patterns Reference

Advanced routing patterns for Astro 6.

## `getStaticPaths()` with props

```astro
---
export async function getStaticPaths() {
  const products = await fetchProducts();
  return products.map(product => ({
    params: { id: product.id },
    props: { product, relatedIds: product.relatedIds },
  }));
}
const { product, relatedIds } = Astro.props;
---
```

## Pagination with `paginate()`

```astro
---
import { getCollection } from 'astro:content';

export async function getStaticPaths({ paginate }) {
  const posts = await getCollection('blog');
  const sorted = posts.sort((a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf());
  return paginate(sorted, { pageSize: 10 });
}

const { page } = Astro.props;
---

{page.url.prev && <a href={page.url.prev}>← Previous</a>}
{page.url.next && <a href={page.url.next}>Next →</a>}
```

Use `[...page].astro` or `[page].astro`.

## i18n helpers

`getRelativeLocaleUrl()` and `Astro.currentLocale` support locale-aware links and rendering.

## `Astro.params` vs `Astro.props`

- `Astro.params`: URL segments from route pattern
- `Astro.props`: data passed from `getStaticPaths()` or component parent

## Partials

Set `export const partial = true` for pages intended for htmx/Unpoly partial updates.
