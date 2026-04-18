# Astro Client Directives Reference

Detailed reference for all `client:*` hydration directives. Target: Astro 6.

## `client:load`

Hydrates the component as soon as the page loads.

```astro
<Counter client:load />
```

## `client:idle`

Hydrates when browser thread becomes idle.

```astro
<NewsletterForm client:idle />
```

## `client:visible`

Hydrates when component enters viewport.

```astro
<LazyChart client:visible />
<LazyChart client:visible={{ rootMargin: "200px" }} />
```

Options:

- `rootMargin`
- `threshold`

## `client:media`

Hydrates when media query matches.

```astro
<MobileNav client:media="(max-width: 768px)" />
```

## `client:only`

Skips SSR; browser-only rendering:

```astro
<ReactDatePicker client:only="react" />
<VueMap client:only="vue" />
<SvelteRichEditor client:only="svelte" />
```

Use when browser APIs are required and SSR fails.

## Props serialization

Island props must be JSON-serializable.

## View transitions persistence

```astro
<MusicPlayer client:load transition:persist />
```
