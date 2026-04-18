# Build Configuration and Environment Variables

Astro 6 build + env reference.

## Build commands

```bash
npx astro dev
npx astro build
npx astro preview
```

## Output modes

- `static`
- `server`
- `hybrid`

## Type-safe env (`astro:env`)

Define `env.schema` in `astro.config.mjs` with `envField`.

```js
import { defineConfig, envField } from 'astro/config';

export default defineConfig({
  env: {
    schema: {
      DATABASE_URL: envField.string({ context: 'server', access: 'secret' }),
      PUBLIC_API_URL: envField.string({ context: 'client', access: 'public' }),
    },
  },
});
```

## `import.meta.env`

Still available for MODE/DEV/PROD/SITE/BASE_URL and PUBLIC-prefixed vars.

## `.env` files

- `.env`
- `.env.development`
- `.env.production`
- `.env.local`
