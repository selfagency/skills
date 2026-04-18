# Astro Component Syntax Reference

Full syntax reference for `.astro` component files. Target: Astro 6.

## File structure

```astro
---
// Frontmatter (server-side JS/TS)
import Foo from './Foo.astro';
const data = await fetch('…').then(r => r.json());
---
<!-- Template (HTML + expressions) -->
<Foo value={data} />
```

Everything between `---` fences runs **once at render time** on the server (or at build time for static output). The template below is standard HTML with embedded expressions using `{}`.

## Expressions

```astro
---
const name = "Astro";
const items = ["a", "b", "c"];
const isVisible = true;
---

<p>Hello {name}</p>

{isVisible && <span>Visible</span>}
{isVisible ? <span>Yes</span> : <span>No</span>}

<ul>
  {items.map(item => <li>{item}</li>)}
</ul>
```

Expressions can only contain **statements**, not blocks. Use `.map()`, ternary, and `&&` for flow control.

## Importing components

```astro
---
import Header from '../components/Header.astro';
import Card from '../components/Card.astro';
import Button from '../components/Button.tsx'; // React/Svelte/Vue also work
---

<Header />
<Card title="Hello" />
<Button client:load>Click me</Button>
```

## Props declaration

```astro
---
interface Props {
  title: string;
  description?: string;
  count: number;
  tags: string[];
  variant?: 'primary' | 'secondary';
}

const {
  title,
  description = 'Default description',
  count,
  tags,
  variant = 'primary',
} = Astro.props;
---
```

## Spread props

```astro
---
interface Props {
  id: string;
  class?: string;
  [key: string]: unknown;  // catch-all for HTML attributes
}

const { id, class: className, ...rest } = Astro.props;
---

<div {id} class={className} {...rest}>
  <slot />
</div>
```

## Conditional class names

```astro
---
const { active, size = 'md' } = Astro.props;
---

<button class:list={['btn', `btn-${size}`, { 'btn-active': active }] }>
  <slot />
</button>
```

`class:list` accepts strings, objects, and arrays — falsy values are ignored.

## Data attributes

```astro
<div data-theme="dark" data-count={42}>…</div>
```

## `set:html` (raw HTML injection)

```astro
---
const content = await getMarkdownContent(); // already sanitized
---

<article set:html={content} />
```

> Warning: Only use `set:html` with trusted content. XSS risk if user-supplied.

## `set:text` (escape text)

```astro
<p set:text={userInput} />
```

Equivalent to `<p>{userInput}</p>` — HTML-escaped by default.

## Astro global

Key properties available in frontmatter:

| Property | Description |
| --- | --- |
| `Astro.props` | Component props |
| `Astro.slots` | Slot introspection (`has`, `render`) |
| `Astro.request` | Current `Request` object |
| `Astro.url` | Current page URL |
| `Astro.params` | Dynamic route params |
| `Astro.redirect(url)` | Return a redirect response |
| `Astro.locals` | Request-scoped data (set by middleware) |
| `Astro.cookies` | Cookie helpers |
| `Astro.site` | Site URL from config |
| `Astro.generator` | `"Astro v6.x.x"` |

## Render a slot programmatically

```astro
---
const renderedSlot = await Astro.slots.render('default');
---

<div set:html={renderedSlot} />
```

## `CollectionEntry` typing

Use when accepting collection entries as props:

```astro
---
import type { CollectionEntry } from 'astro:content';

interface Props {
  post: CollectionEntry<'blog'>;
}

const { post } = Astro.props;
---

<h1>{post.data.title}</h1>
```
