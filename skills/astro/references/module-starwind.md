# Module: Starwind Components

This module covers using Starwind UI components in Astro projects.

## When to load this module

Load for requests mentioning any of:

- "Starwind", "Starwind UI", `starwind`
- `pnpx starwind@latest init`, `starwind add`, `starwind update`, `starwind remove`
- imports from `@/components/starwind/*`
- Starwind compound component usage patterns (e.g. Tooltip, Dialog, Pagination)

## Core workflow

1. Ensure project prerequisites:
   - Astro project
   - Tailwind CSS v4
   - Node.js
1. Initialize Starwind:

```bash
pnpx starwind@latest init
```

1. Add needed components:

```bash
npx starwind@latest add button card dialog
```

1. Import and use components from generated local files:

```astro
---
import { Button } from "@/components/starwind/button";
---

<Button variant="primary">Click me</Button>
```

## Key guidance

- Starwind components are added as source code to your project (not consumed as a runtime UI package).
- Preserve accessibility attributes and keyboard behavior when customizing.
- Prefer theme variables and Tailwind utility classes over hard-coded colors.
- Use compound components as documented (trigger/content/item patterns).

## Related detailed reference

- `references/starwind-components.md` — detailed CLI, component list, patterns, and examples
