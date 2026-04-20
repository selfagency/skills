#!/usr/bin/env node

/**
 * Validate config file paths provided by user.
 *
 * Output: JSON object on stdout
 * Diagnostics: stderr
 * Exit codes:
 *  - 0 all files exist and are regular files
 *  - 1 one or more files missing/invalid
 *  - 2 invalid usage
 */

import fs from 'node:fs'
import path from 'node:path'

const HELP = `Usage:
  node scripts/validate-config-paths.mjs --paths <path1,path2,...>

Options:
  --paths   Comma-separated file paths
  --help    Show this help
`

function parseArgs(argv) {
  let rawPaths = ''
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i]
    if (token === '--help' || token === '-h') return { help: true }
    if (token === '--paths') {
      rawPaths = argv[i + 1] || ''
      i += 1
      continue
    }
    process.stderr.write(`Unknown argument: ${token}\n`)
    return { error: true }
  }
  return { rawPaths }
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

if (!parsed.rawPaths) {
  process.stderr.write('Missing required --paths\n')
  process.stderr.write(HELP)
  process.exit(2)
}

const items = parsed.rawPaths
  .split(',')
  .map((entry) => entry.trim())
  .filter(Boolean)

if (items.length === 0) {
  process.stderr.write('No valid paths provided\n')
  process.exit(2)
}

const results = items.map((p) => {
  const resolved = path.resolve(p)
  try {
    const stat = fs.statSync(resolved)
    return {
      input: p,
      resolved,
      exists: true,
      isFile: stat.isFile(),
      valid: stat.isFile(),
    }
  } catch {
    return {
      input: p,
      resolved,
      exists: false,
      isFile: false,
      valid: false,
    }
  }
})

const summary = {
  total: results.length,
  valid: results.filter((r) => r.valid).length,
  invalid: results.filter((r) => !r.valid).length,
}

process.stdout.write(`${JSON.stringify({ summary, results }, null, 2)}\n`)
process.exit(summary.invalid > 0 ? 1 : 0)
