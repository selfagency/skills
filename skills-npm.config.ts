import { defineConfig } from 'skills-npm';

export default defineConfig({
  source: 'package.json',
  recursive: true,
  gitignore: true,
  yes: true,
  dryRun: false,
});
