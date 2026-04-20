import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    testTimeout: 300_000, // 5 min per test — copilot CLI + LLM can be slow
    hookTimeout: 30_000,
    reporters: ['verbose'],
    include: ['tests/**/*.test.ts'],
  },
});
