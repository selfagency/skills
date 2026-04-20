# Safe Filename Handling in Shell Strings

When zx auto-escapes interpolated values (`` $`cmd ${userInput}` ``), it protects against shell injection for those specific values. But shell strings that handle **filenames** have additional hazards: spaces, newlines, leading dashes, control characters, and non-UTF-8 bytes.

Source: [Filenames and Pathnames in Shell](https://dwheeler.com/essays/filenames-in-shell.html) — D.A. Wheeler (CC-BY-SA, 2025)
Security context: OWASP CWE-78 (OS Command Injection), CWE-73 (Relative Path Traversal), CWE-116

---

## What Makes Filenames Dangerous

POSIX allows filenames to contain almost any byte except `/` and NUL. That includes:

- Spaces (anywhere, including at start/end)
- Newlines and tabs
- Leading dashes (`-file.txt` → parsed as option flag)
- Shell metacharacters (`*`, `?`, `[`, `;`, `&`)
- Terminal escape sequences (security vulnerability if logged/displayed unfiltered)
- Non-UTF-8 bytes

---

## zx Protects You — But Only for Interpolated Values

```js
const userFile = 'my file with spaces.txt';
await $`cat ${userFile}`; // SAFE: zx escapes → cat 'my file with spaces.txt'
await $`cat "${userFile}"`; // WRONG: breaks zx escaping
```

**But** inside the shell string itself, you are still writing bash. All the classic bash filename hazards apply:

```js
// DANGEROUS: glob expansion, unquoted variable, IFS splitting
await $`for f in *; do process $f; done`;

// SAFE: proper quoting, prefixed glob, existence check
await $`for f in ./*; do [ -e "$f" ] && process "$f"; done`;
```

---

## Rule 1: Always Double-Quote Variable References Inside Shell Strings

Inside `$` template literals, any bash variable you use must be quoted:

```bash
# WRONG — fails on filenames with spaces, tabs, or glob chars
for f in $files; do cat $f; done

# RIGHT
for f in $files; do cat "$f"; done
```

```js
// In zx — the bash string itself still needs internal quoting
await $`
  while IFS= read -r -d "" file; do
    process "$file"          # "$file" quoted — not $file
  done < <(find . -print0)
`;
```

---

## Rule 2: Prefix Globs with `./` to Avoid Leading-Dash Filenames

Never begin a glob with `*` or `?`. Always prepend `./` so expanded filenames can't start with `-` (which would be parsed as a flag).

```bash
# WRONG — a file named "-rf something" would be passed as flags
cat *
for f in *.log; do ...

# RIGHT
cat ./*
for f in ./*.log; do ...
```

```js
// zx: safe glob patterns inside shell strings
await $`for f in ./*.json; do [ -e "$f" ] && jq . "$f"; done`;
await $`for f in ./**/*.ts; do wc -l "$f"; done`;
```

> The zx `glob()` JS function (`glob('**/*.ts')`) sidesteps this entirely because it returns an array of safe JS strings, not a bash glob. Prefer `glob()` over bash globs for recursive matching.

---

## Rule 3: Handle Empty Glob Matches

By default, an unmatched glob like `./*.pdf` returns the literal string `./*.pdf` as if it were a filename — almost never what you want.

```js
// Option A: check for existence in loop (portable)
await $`for f in ./*.log; do [ -e "$f" ] && process "$f"; done`;

// Option B: enable nullglob (bash extension)
await $`
  shopt -s nullglob
  for f in ./*.log; do process "$f"; done
`;

// Option C: use zx's glob() instead (JS-land, no bash glob hazards)
const files = await glob('./*.log');
for (const f of files) {
  await $`process ${f}`; // zx escapes each path safely
}
```

---

## Rule 4: Use `find -print0` + `read -d ""` for Recursive File Processing

The only fully safe way to pass filenames with arbitrary characters between programs is NUL (`\0`) separation — filenames can never contain NUL.

```js
// SAFE: NUL-delimited find output
await $`
  find . -name "*.log" -print0 |
  while IFS="" read -r -d "" file; do
    process "$file"
  done
`;

// SAFE: process substitution variant (bash, zsh, ksh93 — not dash)
await $`
  while IFS="" read -r -d "" file <&4; do
    process "$file"
  done 4< <(find . -name "*.log" -print0)
`;

// SAFE: find -exec (simplest, spawns one process per file)
await $`find . -name "*.log" -exec process {} \;`;

// SAFE: find -exec with + (batches multiple files per invocation)
await $`find . -name "*.log" -exec cat {} \+`;

// ALSO SAFE via xargs -0
await $`find . -name "*.log" -print0 | xargs -0 process`;
```

**Why not `find . | while read file`?**

- `read` without `-d ""` splits on newlines — filenames _can_ contain newlines
- `read` without `IFS=""` strips leading/trailing whitespace from filenames

---

## Rule 5: Set IFS to Newline+Tab in Shell Strings Handling Files

Spaces in IFS cause field-splitting that corrupts space-containing filenames. Setting IFS to just newline and tab provides partial protection when you can't use `read -d ""`:

```bash
IFS=$'\n\t'
```

```js
await $`
  IFS=$'\n\t'
  set -f          # disable glob expansion on variables
  for f in $(find . -name "*.log"); do
    process "$f"
  done
`;
```

> This only helps when filenames don't contain tabs or newlines. For full safety, use `find -print0` + `read -d ""` (Rule 4) or zx's `glob()` (Rule 3, Option C).

---

## Rule 6: Check for Leading Dash When Accepting Filename Input

When a pathname comes from user input, an argument, or any untrusted source, check for and sanitize leading dashes:

```js
// Sanitize before passing to shell
function safePath(p) {
  if (p.startsWith('-')) return `./${p}`;
  return p;
}

const userPath = argv.file;
await $`cat ${safePath(userPath)}`;
```

In bash, same pattern:

```bash
# Prepend ./ if path starts with -
[[ "$file" == -* ]] && file="./$file"
cat "$file"
```

---

## Rule 7: Filter Control Characters Before Displaying or Logging Filenames

Filenames can contain terminal escape sequences. Logging or printing them unfiltered can corrupt terminals or — in some cases — execute commands via terminal escape injection.

```js
// Strip control chars before logging (POSIX approach)
await $`printf '%s' ${filename} | LC_ALL=POSIX tr -d '[:cntrl:]'`;

// Or in JS — strip non-printable ASCII before logging
const safeForLog = filename.replace(/[\x00-\x1F\x7F]/g, '?');
console.log(`Processing: ${safeForLog}`);
```

---

## Rule 8: Prefer `--` as Defense-in-Depth, Not as Primary Countermeasure

`--` signals end-of-options to many commands. It helps, but:

- Many programs don't support `--` (including `echo`)
- It must be applied consistently everywhere, without exception — not practical
- **Primary defense**: prefix globs with `./` and prepend `./` to dash-leading paths (Rules 2 and 6)

```bash
# -- as additional protection where supported
grep -- "$pattern" "$file"
rm -- "$file"
```

---

## Quick-Reference: Common Mistakes vs. Safe Patterns

| Situation             | Wrong                        | Right                                            |
| --------------------- | ---------------------------- | ------------------------------------------------ |
| Loop over files       | `for f in *`                 | `for f in ./*`                                   |
| Loop body             | `process $f`                 | `process "$f"`                                   |
| Read from find        | `find . \| while read f`     | `find . -print0 \| while IFS="" read -r -d "" f` |
| xargs with find       | `find . \| xargs cmd`        | `find . -print0 \| xargs -0 cmd`                 |
| File content          | `cat $(find . -type f)`      | `find . -type f -exec cat {} \+`                 |
| Log filename          | `echo "file: $f"`            | strip control chars first                        |
| User-provided path    | `cat "$path"`                | prepend `./` if starts with `-`                  |
| Recursive match in zx | bash `**` glob               | `await glob('**/*.ts')`                          |
| Check file exists     | `for f in ./*` (empty match) | add `[ -e "$f" ] &&` or use nullglob             |

---

## zx-Specific Safety Shortcuts

zx provides safer JS-side alternatives for many risky bash filename operations:

```js
import { glob, fs } from 'zx';

// glob() — safe recursive matching, no bash glob hazards
const tsFiles = await glob('src/**/*.ts');

// fs — direct file I/O without spawning shell subprocesses
const content = await fs.readFile('path/to/file', 'utf8');
const lines = content.split('\n');

// Process files with full JS safety
for (const file of tsFiles) {
  await $`wc -l ${file}`; // zx handles escaping
}
```

For any operation where you're iterating over files, prefer `glob()` + JS iteration over bash `for f in *` patterns. Reserve bash file loops for cases where you need shell-native features like `find`'s `-mtime`, `-perm`, or complex `-prune` logic.
