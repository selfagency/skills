# Markdown and MDX in Astro

Authoring and rendering Markdown/MDX in Astro 6.

## Markdown pages

Markdown files in `src/pages` become routes and can declare `layout` in frontmatter.

## Content collection markdown

Frontmatter is validated by collection schema and available via `entry.data`.

## MDX

Requires `@astrojs/mdx`.

```bash
npx astro add mdx
```

MDX supports component imports and interactive islands.

## Render with custom component mapping

```astro
---
const { Content } = await render(post);
---
<Content components={{ a: CustomLink, pre: CodeBlock }} />
```

## Markdoc

Requires `@astrojs/markdoc` and `markdoc.config.mjs`.

## Headings extraction

`render()` returns `headings` for TOCs.

## Markdown plugins

Use `remarkPlugins` and `rehypePlugins` in `astro.config.mjs`.

## Syntax highlighting

Shiki by default; Prism optional via `markdown.syntaxHighlight`.
