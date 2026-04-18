# Starwind Components Reference (Astro)

Reference for using Starwind UI in Astro projects, based on the provided Starwind documentation.

## Overview

Starwind UI is an open-source Astro component library styled with Tailwind CSS v4. Components are added directly to your codebase via CLI.

Core idea:

- Similar to shadcn-style workflow
- Own the source code after adding components
- Customize in-project component files

## Prerequisites

- Astro project
- Tailwind CSS v4
- Node.js

For pnpm projects, use `.npmrc`:

```ini
auto-install-peers=true
node-linker=hoisted
lockfile=true
```

## CLI commands

### Initialize

```bash
pnpx starwind@latest init
# or
npx starwind@latest init
# or
yarn dlx starwind@latest init
```

### Add components

```bash
npx starwind@latest add button
npx starwind@latest add button card dialog
```

### Update/remove components

```bash
npx starwind@latest update button
npx starwind@latest remove button
```

## Import pattern

All components follow:

```astro
---
import { ComponentName } from "@/components/starwind/component-name";
---
```

Example:

```astro
---
import { Button } from "@/components/starwind/button";
---

<Button variant="primary" size="md">Click me</Button>
```

## Compound component pattern

Many Starwind components are composed of parent + child parts.

### Tooltip

```astro
---
import { Button } from "@/components/starwind/button";
import { Tooltip, TooltipTrigger, TooltipContent } from "@/components/starwind/tooltip";
---

<Tooltip>
  <TooltipTrigger>
    <Button>Hover me</Button>
  </TooltipTrigger>
  <TooltipContent>Add to library</TooltipContent>
</Tooltip>
```

### Pagination

```astro
---
import {
  Pagination,
  PaginationContent,
  PaginationItem,
  PaginationLink,
  PaginationPrevious,
  PaginationNext,
  PaginationEllipsis,
} from "@/components/starwind/pagination";
---

<Pagination>
  <PaginationContent>
    <PaginationItem><PaginationPrevious href="#">Prev</PaginationPrevious></PaginationItem>
    <PaginationItem><PaginationLink href="#">1</PaginationLink></PaginationItem>
    <PaginationItem><PaginationLink href="#" isActive>2</PaginationLink></PaginationItem>
    <PaginationItem><PaginationLink href="#">3</PaginationLink></PaginationItem>
    <PaginationItem><PaginationEllipsis /></PaginationItem>
    <PaginationItem><PaginationNext href="#">Next</PaginationNext></PaginationItem>
  </PaginationContent>
</Pagination>
```

## Common props

### Variants

Common variant values:

- `default`
- `primary`
- `secondary`
- `outline`
- `ghost`
- `info`
- `success`
- `warning`
- `error`

### Sizes

Common size values:

- `sm`
- `md` (typical default)
- `lg`

## Theming notes

Starwind uses CSS variables for tokens, including:

- Base: `--background`, `--foreground`
- Semantic: `--primary`, `--secondary`, `--accent`, `--muted`
- Feedback: `--info`, `--success`, `--warning`, `--error`
- Utility: `--border`, `--input`, `--outline`, `--radius`

Dark mode is class-based via `.dark`.

## Component categories (high level)

- Form & Input: button, checkbox, input, select, textarea, switch, slider, etc.
- Navigation: breadcrumb, dropdown, pagination, sidebar, tabs, theme-toggle
- Overlay & Disclosure: accordion, dialog, alert-dialog, popover, sheet, tooltip
- Feedback & Status: alert, progress, skeleton, spinner, toast
- Layout & Structure: aspect-ratio, card, item, separator, table
- Content & Media: avatar, badge, carousel, image, prose, video

## Best practices

1. Keep Starwind accessibility behavior intact while customizing.
2. Use the generated local component source as your customization point.
3. Keep imports consistent from `@/components/starwind/*`.
4. Use compound component hierarchy exactly as documented.
5. Prefer token/theming changes over one-off styling hacks.

## Scope note

This reference is for usage and integration in Astro projects. For exhaustive per-component props, examples, and updates, consult official docs:

- <https://starwind.dev/docs/getting-started>
- <https://starwind.dev/docs/components>
