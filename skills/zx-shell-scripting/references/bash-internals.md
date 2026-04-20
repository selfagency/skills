# Bash Internals for zx Authors

When you write `` $`...` `` in zx, bash executes the string. Understanding bash internals lets you write those shell strings more efficiently — fewer subshells, fewer external processes, less overhead.

Source: [pure-bash-bible](https://github.com/dylanaraps/pure-bash-bible) (archived, MIT)

---

## Core Philosophy: Avoid Unnecessary External Processes

Every `$(command)` subshell and external process call (`sed`, `awk`, `cut`, `tr`, `grep` on a variable) has overhead. In hot loops or frequently-called scripts, prefer bash builtins.

```bash
# SLOW: external process
result=$(echo "$str" | tr '[:upper:]' '[:lower:]')

# FAST: bash parameter expansion (bash 4+)
result="${str,,}"
```

In zx, apply this inside `$` strings — or better, do string manipulation in JS and only shell out for what bash is genuinely better at.

---

## Parameter Expansion Reference

The most powerful bash feature. Use inside `$` template literals.

### Replacement

| Expression                | Effect                               |
| ------------------------- | ------------------------------------ |
| `${VAR#PATTERN}`          | Remove shortest match from **start** |
| `${VAR##PATTERN}`         | Remove longest match from **start**  |
| `${VAR%PATTERN}`          | Remove shortest match from **end**   |
| `${VAR%%PATTERN}`         | Remove longest match from **end**    |
| `${VAR/PATTERN/REPLACE}`  | Replace first match                  |
| `${VAR//PATTERN/REPLACE}` | Replace all matches                  |
| `${VAR/PATTERN}`          | Remove first match                   |
| `${VAR//PATTERN}`         | Remove all matches                   |

```bash
# Strip file extension
file="archive.tar.gz"
name="${file%%.*}"          # archive
ext="${file#*.}"            # tar.gz

# Strip path prefix (alternative to basename)
path="/usr/local/bin/node"
bin="${path##*/}"           # node

# Strip directory (alternative to dirname)
dir="${path%/*}"            # /usr/local/bin
```

### Substring / Expansion

| Expression             | Effect                              |
| ---------------------- | ----------------------------------- |
| `${VAR:OFFSET}`        | Remove first N chars                |
| `${VAR:OFFSET:LENGTH}` | Substring from offset, length chars |
| `${VAR::N}`            | First N chars                       |
| `${VAR:: -N}`          | Remove last N chars                 |
| `${VAR: -N}`           | Last N chars                        |

```bash
str="Hello, World"
echo "${str:7}"         # World
echo "${str:7:5}"       # World
echo "${str::5}"        # Hello
echo "${str: -5}"       # World
```

### Case Modification (bash 4+)

| Expression | Effect               |
| ---------- | -------------------- |
| `${VAR^}`  | Uppercase first char |
| `${VAR^^}` | Uppercase all        |
| `${VAR,}`  | Lowercase first char |
| `${VAR,,}` | Lowercase all        |
| `${VAR~~}` | Reverse case all     |

```bash
name="hello world"
echo "${name^^}"        # HELLO WORLD
echo "${name^}"         # Hello world

tag="BUILD_PROD"
echo "${tag,,}"         # build_prod
```

### Default Values

| Expression       | Effect                                  |
| ---------------- | --------------------------------------- |
| `${VAR:-STRING}` | Use STRING if VAR is empty or unset     |
| `${VAR:=STRING}` | Set VAR to STRING if empty or unset     |
| `${VAR:+STRING}` | Use STRING only if VAR is **set**       |
| `${VAR:?STRING}` | Error and exit if VAR is empty or unset |

```bash
# Safe defaults in shell strings inside $``
port="${PORT:-3000}"
env="${NODE_ENV:=development}"

# Fail fast if required variable is unset
"${DEPLOY_KEY:?DEPLOY_KEY is required}"
```

### Length

```bash
str="Hello"
echo "${#str}"          # 5 (character count)

arr=(a b c d)
echo "${#arr[@]}"       # 4 (element count)
```

---

## String Operations Without External Processes

### Trim Leading and Trailing Whitespace

```bash
# No sed/awk needed
trim_string() {
  : "${1#"${1%%[![:space:]]*}"}"
  : "${_%"${_##*[![:space:]]}"}"
  printf '%s\n' "$_"
}
```

### Split String on Delimiter (bash 4+)

```bash
# Alternative to cut/awk
split() {
  IFS=$'\n' read -d "" -ra arr <<< "${1//$2/$'\n'}"
  printf '%s\n' "${arr[@]}"
}

# Usage:
split "a,b,c,d" ","
split "2024-01-15" "-"
```

### String Contains / Starts With / Ends With

```bash
# Contains (no grep needed)
if [[ $var == *sub_string* ]]; then echo "found"; fi

# Starts with
if [[ $var == prefix* ]]; then echo "starts with"; fi

# Ends with
if [[ $var == *.log ]]; then echo "log file"; fi

# Regex match (POSIX regex)
if [[ $var =~ ^[0-9]+$ ]]; then echo "is integer"; fi
```

### URL Encode/Decode

```bash
urlencode() {
  local LC_ALL=C
  for (( i = 0; i < ${#1}; i++ )); do
    : "${1:i:1}"
    case "$_" in
      [a-zA-Z0-9.~_-]) printf '%s' "$_" ;;
      *) printf '%%%02X' "'$_" ;;
    esac
  done
  printf '\n'
}

urldecode() {
  : "${1//+/ }"
  printf '%b\n' "${_//%/\\x}"
}
```

---

## File Operations Without External Processes

### Read File to String (alternative to cat)

```bash
# No cat process needed
file_content="$(<"$file")"
```

### Read File to Array by Line (bash 4+)

```bash
mapfile -t lines < "file.txt"
# lines[0] = first line, lines[1] = second, etc.
```

### Get First/Last N Lines (alternative to head/tail)

```bash
# First N lines (bash 4+)
mapfile -tn 5 head_lines < "file.txt"

# Last N lines (bash 4+)
mapfile -tn 0 all_lines < "file.txt"
tail_lines=("${all_lines[@]: -10}")
```

### Get Line Count (alternative to wc -l)

```bash
mapfile -tn 0 lines < "$file"
count="${#lines[@]}"
```

### Extract Lines Between Markers

````bash
# Extract content between delimiters (e.g., code blocks, sections)
extract() {
  while IFS=$'\n' read -r line; do
    [[ $extract && $line != "$3" ]] && printf '%s\n' "$line"
    [[ $line == "$2" ]] && extract=1
    [[ $line == "$3" ]] && extract=
  done < "$1"
}

# Example: extract bash blocks from markdown
extract README.md '```bash' '```'
````

### File Path Without External Processes

```bash
# Alternative to dirname
path="/usr/local/bin/node"
dir="${path%/*}"            # /usr/local/bin

# Alternative to basename
filename="${path##*/}"      # node

# Strip extension
name="${filename%.*}"       # node (no extension to strip here, but works)
```

---

## Conditionals and File Tests

### File Tests (inside [])

```bash
[[ -e "$file" ]]    # exists
[[ -f "$file" ]]    # regular file
[[ -d "$dir"  ]]    # directory
[[ -r "$file" ]]    # readable
[[ -w "$file" ]]    # writable
[[ -x "$file" ]]    # executable
[[ -s "$file" ]]    # non-empty (size > 0)
[[ -L "$file" ]]    # symlink
[[ -z "$var"  ]]    # string is empty
[[ -n "$var"  ]]    # string is non-empty
[[ -v var     ]]    # variable is set (bash 4.2+)
```

### Inline Conditionals

```bash
# Short-circuit (one-liner if/else)
[[ -d "$dir" ]] && mkdir -p "$dir" || echo "exists"

# One-liner with block
[[ -f "$lockfile" ]] && { echo "Already running"; exit 1; }

# Ternary in arithmetic
((result = x > y ? x : y))
```

### Case Statement (OS detection pattern)

```bash
case "$OSTYPE" in
  "darwin"*) : "macOS" ;;
  "linux"*)  : "Linux" ;;
  *"bsd"*)   : "BSD"   ;;
  *)
    printf '%s\n' "Unknown OS" >&2
    exit 1
  ;;
esac
os="$_"   # $_ holds last arg of last command
```

---

## Traps: Cleanup and Signal Handling

```bash
# Cleanup on any exit
trap 'rm -f /tmp/lockfile' EXIT

# Cleanup on error (ERR fires on non-zero exit)
trap 'echo "Error on line $LINENO" >&2' ERR

# Ignore Ctrl+C for critical sections
trap '' INT

# Restore after critical section
trap - INT

# React to terminal resize (useful for TUI scripts)
trap 'get_term_size' SIGWINCH

# Full pattern: cleanup + error info
cleanup() {
  local exit_code=$?
  rm -rf "$tmpdir"
  [[ $exit_code -ne 0 ]] && echo "Failed with exit $exit_code" >&2
}
trap cleanup EXIT
```

> In zx, prefer `process.on('SIGINT', cleanup)` for JS-level cleanup, and use bash traps for shell-level resources (temp files, locks created within the shell string).

---

## Loops Over Files and Ranges

```bash
# Range (alternative to seq)
for i in {1..100}; do echo "$i"; done
for ((i=0; i<=VAR; i++)); do echo "$i"; done

# Files in directory (do NOT use ls)
for file in /path/to/*.log; do
  [[ -f "$file" ]] && echo "$file"
done

# Recursive glob (bash 4+)
shopt -s globstar
for file in /path/**/*.ts; do echo "$file"; done
shopt -u globstar

# Loop over file contents
while IFS= read -r line; do
  echo "$line"
done < "file.txt"
```

---

## Performance Tips

### Disable Unicode When Not Needed

```bash
# Measurable speedup for ASCII-only processing
LC_ALL=C
LANG=C
```

Use inside `$` strings when processing log files, sorting, or pattern matching on ASCII data.

### Avoid Subshells in Loops

```bash
# SLOW: subshell per iteration
for item in "${arr[@]}"; do
  result=$(process "$item")
done

# FAST: use namerefs or inline parameter expansion
for item in "${arr[@]}"; do
  result="${item^^}"   # no subshell
done
```

### Check if Binary Exists (no which subprocess)

```bash
# All three are equivalent; prefer 'command -v'
command -v docker &>/dev/null || { echo "docker not found"; exit 1; }
type -p node &>/dev/null || echo "node missing"
```

In zx, use `which()` global (which wraps this safely) or check `$.shell` alternatives.

---

## Brace Expansion

```bash
# Ranges
echo {1..10}          # 1 2 3 4 5 6 7 8 9 10
echo {01..10}         # 01 02 ... 10 (zero-padded, bash 4+)
echo {a..z}           # a b c ... z
echo {1..10..2}       # 1 3 5 7 9 (step by 2)

# String lists
mkdir -p project/{src,tests,docs,scripts}
touch config.{json,yaml,toml}
cp file.txt{,.bak}    # copy file.txt to file.txt.bak
rm -rf build/{cache,tmp,artifacts}
```

Brace expansion is evaluated by bash before parameter expansion — it doesn't require a glob match.

---

## Internal Variables

Useful when writing shell strings inside `$`:

| Variable        | Value                                            |
| --------------- | ------------------------------------------------ |
| `$BASH_VERSION` | Current bash version string                      |
| `$OSTYPE`       | OS identifier (`darwin22`, `linux-gnu`)          |
| `$HOSTTYPE`     | CPU architecture (`x86_64`, `arm64`)             |
| `$HOSTNAME`     | System hostname                                  |
| `$PWD`          | Current working directory (alternative to `pwd`) |
| `$RANDOM`       | Pseudorandom integer 0–32767                     |
| `$SECONDS`      | Seconds since script started                     |
| `$LINENO`       | Current line number (useful in error traps)      |
| `$FUNCNAME[0]`  | Current function name                            |
| `$BASH_REMATCH` | Captured groups from last `[[ =~ ]]` match       |

---

## When to Use Bash vs JavaScript in zx

| Task                         | Prefer                                                                 |
| ---------------------------- | ---------------------------------------------------------------------- |
| String case conversion       | JS (`.toUpperCase()`) or bash (`${var^^}`)                             |
| File path manipulation       | JS (`path.basename()`, `path.extname()`)                               |
| JSON parsing/filtering       | JS (native) or `jq` for complex cases                                  |
| Line-by-line file reading    | JS (`fs.readFile`) for small files; bash `mapfile` for large streaming |
| Pattern matching on variable | Bash parameter expansion (no subprocess)                               |
| Complex regex with groups    | JS (full regex API)                                                    |
| Sorting/deduplication        | Bash pipeline (`sort                                                   | uniq`) for large streams; JS `.sort()` for in-memory |
| Cross-platform portability   | JS always                                                              |
| Spawning multiple processes  | zx `$` (that's what it's for)                                          |
