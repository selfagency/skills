#!/usr/bin/env node

/**
 * Render lint-staged config fragment for a selected stack and mode.
 *
 * Output: JSON object on stdout
 * Diagnostics: stderr
 * Exit codes:
 *  - 0 success
 *  - 2 invalid args
 */

const HELP = `Usage:
  node scripts/render-lintstaged-config.mjs --stack <oxc|biome|eslint-prettier> --mode <check|fix> [--markdown <default|rumdl>]

Options:
  --stack   Toolchain variant: oxc | biome | eslint-prettier
  --mode    Hook mode: check | fix
  --markdown  Markdown authority: default | rumdl (default: default)
  --help    Show this help
`

function parseArgs(argv) {
  const args = { stack: '', mode: '', markdown: 'default' }
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i]
    if (token === '--help' || token === '-h') return { help: true }
    if (token === '--stack') {
      args.stack = argv[i + 1] || ''
      i += 1
      continue
    }
    if (token === '--mode') {
      args.mode = argv[i + 1] || ''
      i += 1
      continue
    }
    if (token === '--markdown') {
      args.markdown = argv[i + 1] || ''
      i += 1
      continue
    }
    process.stderr.write(`Unknown argument: ${token}\n`)
    return { error: true }
  }
  return args
}

function buildConfig(stack, mode, markdown) {
  const markdownGlob = '*.{md,markdown,mdx,mkdn,mdown}'
  const nonMarkdownDataGlob = '*.{yaml,yml,json,jsonc}'
  const jsTsGlob = '*.{js,jsx,ts,tsx,mjs,cjs,mts,cts}'

  if (stack === 'oxc') {
    if (mode === 'check') {
      const config = {
        [jsTsGlob]: ['oxlint'],
        [`*.{js,jsx,ts,tsx,mjs,cjs,mts,cts,yaml,yml,json,jsonc}`]: ['oxfmt --check --no-error-on-unmatched-pattern'],
      }
      if (markdown === 'rumdl') {
        config[markdownGlob] = ['rumdl check']
      } else {
        config[markdownGlob] = ['oxfmt --check --no-error-on-unmatched-pattern']
      }
      return config
    }
    const config = {
      [jsTsGlob]: ['oxlint --fix', 'oxfmt --no-error-on-unmatched-pattern'],
      [nonMarkdownDataGlob]: ['oxfmt --no-error-on-unmatched-pattern'],
    }
    if (markdown === 'rumdl') {
      config[markdownGlob] = ['rumdl check --fix', 'rumdl fmt']
    } else {
      config[markdownGlob] = ['oxfmt --no-error-on-unmatched-pattern']
    }
    return config
  }

  if (stack === 'biome') {
    if (mode === 'check') {
      const config = {
        [`*.{js,jsx,ts,tsx,mjs,cjs,mts,cts,yaml,yml,json,jsonc}`]: ['biome check --files-ignore-unknown=true --no-errors-on-unmatched'],
      }
      if (markdown === 'rumdl') {
        config[markdownGlob] = ['rumdl check']
      } else {
        config[markdownGlob] = ['biome check --files-ignore-unknown=true --no-errors-on-unmatched']
      }
      return config
    }
    const config = {
      [`*.{js,jsx,ts,tsx,mjs,cjs,mts,cts,yaml,yml,json,jsonc}`]: ['biome check --write --files-ignore-unknown=true --no-errors-on-unmatched'],
    }
    if (markdown === 'rumdl') {
      config[markdownGlob] = ['rumdl check --fix', 'rumdl fmt']
    } else {
      config[markdownGlob] = ['biome check --write --files-ignore-unknown=true --no-errors-on-unmatched']
    }
    return config
  }

  if (stack === 'eslint-prettier') {
    if (mode === 'check') {
      const config = {
        [jsTsGlob]: ['eslint --max-warnings=0'],
        [`*.{js,jsx,ts,tsx,mjs,cjs,mts,cts,yaml,yml,json,jsonc}`]: ['prettier --check --ignore-unknown'],
      }
      if (markdown === 'rumdl') {
        config[markdownGlob] = ['rumdl check']
      } else {
        config[markdownGlob] = ['prettier --check --ignore-unknown']
      }
      return config
    }
    const config = {
      [jsTsGlob]: ['eslint --fix', 'prettier --write --ignore-unknown'],
      [nonMarkdownDataGlob]: ['prettier --write --ignore-unknown'],
    }
    if (markdown === 'rumdl') {
      config[markdownGlob] = ['rumdl check --fix', 'rumdl fmt']
    } else {
      config[markdownGlob] = ['prettier --write --ignore-unknown']
    }
    return config
  }

  throw new Error(`Unsupported stack: ${stack}`)
}

const parsed = parseArgs(process.argv)

if (parsed.help) {
  process.stdout.write(HELP)
  process.exit(0)
}

if (parsed.error) {
  process.stderr.write(HELP)
  process.exit(2)
}

const allowedStacks = new Set(['oxc', 'biome', 'eslint-prettier'])
const allowedModes = new Set(['check', 'fix'])
const allowedMarkdownModes = new Set(['default', 'rumdl'])

if (!allowedStacks.has(parsed.stack)) {
  process.stderr.write(`Invalid --stack: ${parsed.stack}\n`)
  process.stderr.write(HELP)
  process.exit(2)
}

if (!allowedModes.has(parsed.mode)) {
  process.stderr.write(`Invalid --mode: ${parsed.mode}\n`)
  process.stderr.write(HELP)
  process.exit(2)
}

if (!allowedMarkdownModes.has(parsed.markdown)) {
  process.stderr.write(`Invalid --markdown: ${parsed.markdown}\n`)
  process.stderr.write(HELP)
  process.exit(2)
}

const config = buildConfig(parsed.stack, parsed.mode, parsed.markdown)
process.stdout.write(`${JSON.stringify(config, null, 2)}\n`)
