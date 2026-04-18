# SSR Endpoints Reference

API routes and on-demand rendering for Astro 6.

## Static endpoint

```ts
// src/pages/data.json.ts
export function GET() {
  return new Response(JSON.stringify({ hello: 'world' }), {
    headers: { 'Content-Type': 'application/json' },
  });
}
```

## Type-safe endpoint

```ts
import type { APIRoute } from 'astro';

export const GET = (({ request }) => {
  return new Response(JSON.stringify({ path: new URL(request.url).pathname }));
}) satisfies APIRoute;
```

## SSR endpoint

```ts
export const prerender = false;
import type { APIRoute } from 'astro';

export const GET: APIRoute = async ({ params }) => {
  const user = await db.users.findById(params.id);
  if (!user) return new Response(null, { status: 404 });
  return new Response(JSON.stringify(user), {
    headers: { 'Content-Type': 'application/json' },
  });
};
```

## HTTP methods

`GET`, `POST`, `PUT`, `PATCH`, `DELETE`, and `ALL` are supported.

## Request data

- `await request.json()`
- `await request.formData()`
- headers via `request.headers`

## Output mode behavior

- `static`: prerender by default
- `server`: on-demand by default
- `hybrid`: prerender default + per-route SSR opt-in
