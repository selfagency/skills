# jc Parser Reference

## Critical Gotchas (Read First)

### Output Format Variation by Locale

- **DANGER**: jc sorts output by locale. `en_US.UTF-8` vs `C` vs `POSIX` produce different ordering
- **FIX**: Always prefix with `LC_ALL=C` for reproducible output: `LC_ALL=C ps aux | jc --ps`
- **Why**: Fields like `command` or `filesystem` sort differently; your filters may fail to match

### Version Differences

- jc v1.18 and v1.20 produce different field names (e.g., `state` vs `stat`)
- **FIX**: Pin jc version in scripts: `pip install jc==1.21.0`
- Test with specific version: `jc --version` before relying on field names

### Empty Output Edge Case

- If no matches, jc outputs `[]` (empty array). Piping to `jq` without handling breaks parsing
- **FIX**: Use `jq '.[] // empty'` or check length first: `jq 'if length > 0 then .[0] else "No results" end'`

### Nested Object Complexity

- Some parsers (e.g., `git-log`) output nested objects 5+ levels deep
- **FIX**: Flatten with jq's `@csv` or `@json`: `jq -r '.[] | "\(.commit),\(.author)"'`

## Top 5 Essential Parsers

### ps (Process List)

```bash
# List all running processes as JSON
ps aux | jc --ps

# Example output:
# [
#   {
#     "user": "root",
#     "pid": 1,
#     "cpu_percent": 0.0,
#     "mem_percent": 0.1,
#     "command": "/sbin/init"
#   }
# ]

# Find processes using over 50% CPU
ps aux | jc --ps | jq '.[] | select(.cpu_percent > 50) | {pid: .pid, cmd: .command, cpu: .cpu_percent}'

# Find processes matching pattern
ps aux | jc --ps | jq '.[] | select(.command | contains("node")) | .pid'
```

### df (Disk Usage)

```bash
# Show filesystem usage as JSON
df -h | jc --df

# Example output:
# [
#   {
#     "filesystem": "/dev/sda1",
#     "size": "100G",
#     "used": "50G",
#     "available": "50G",
#     "use_percent": 50
#   }
# ]

# Find filesystems > 80% full
df -h | jc --df | jq '.[] | select(.use_percent > 80) | {fs: .filesystem, usage: .use_percent}'

# Alert if any filesystem full
df -h | jc --df | jq 'if any(.use_percent > 95) then "CRITICAL: Disk almost full!" else "OK" end'
```

### netstat (Network Connections)

```bash
# Show network connections as JSON
netstat -an | jc --netstat

# Example output:
# [
#   {
#     "protocol": "tcp",
#     "recv_q": 0,
#     "send_q": 0,
#     "local_address": "127.0.0.1",
#     "local_port": 5432,
#     "remote_address": "0.0.0.0",
#     "remote_port": "*",
#     "state": "LISTEN"
#   }
# ]

# Find open listening ports
netstat -an | jc --netstat | jq '.[] | select(.state == "LISTEN") | {port: .local_port, proto: .protocol}'

# Count ESTABLISHED connections
netstat -an | jc --netstat | jq '[.[] | select(.state == "ESTABLISHED")] | length'
```

### ls (Directory Listing)

```bash
# List files as JSON
ls -la | jc --ls

# Example output:
# [
#   {
#     "filename": "test.txt",
#     "size": 1024,
#     "permissions": "-rw-r--r--",
#     "owner": "user",
#     "group": "staff"
#   }
# ]

# Find files larger than 1MB
ls -lR /var/log | jc --ls | jq '.[] | select(.size > 1048576) | {file: .filename, size: .size}'

# Check SSH key permissions (should be exactly 0600)
ls -la ~/.ssh | jc --ls | jq '.[] | select(.filename | contains("id_")) | {file: .filename, perms: .permissions}'
```

### dig (DNS Queries)

```bash
# Query DNS as JSON
dig google.com | jc --dig

# Example output:
# {
#   "status": "NOERROR",
#   "queries": [{"name": "google.com", "class": "IN", "type": "A"}],
#   "answers": [
#     {
#       "name": "google.com",
#       "type": "A",
#       "address": "142.251.41.14"
#     }
#   ]
# }

# Extract IP address from DNS query
dig google.com | jc --dig | jq '.answers[0].address'

# Batch DNS lookups and store results
for domain in google.com github.com aws.amazon.com; do
  ip=$(dig +short "$domain" | jc --dig | jq -r '.answers[0].address // "FAILED"')
  echo "$domain: $ip"
done
```

## Common Parsing Patterns

### Selecting with Conditions

```bash
# Filter by exact match
command | jc --parser | jq '.[] | select(.field == "value")'

# Filter by number comparison
command | jc --parser | jq '.[] | select(.number > 100)'

# Filter by string contains
command | jc --parser | jq '.[] | select(.command | contains("python"))'

# Combine multiple conditions (AND)
command | jc --parser | jq '.[] | select(.cpu > 50 and .mem > 20)'

# OR conditions
command | jc --parser | jq '.[] | select(.status == "ERROR" or .status == "FAILED")'
```

### Transforming Output

```bash
# Extract specific fields only
command | jc --parser | jq '.[] | {name: .username, id: .uid}'

# Sort by field
command | jc --parser | jq 'sort_by(.size) | reverse'

# Group by field
command | jc --parser | jq 'group_by(.status) | map({status: .[0].status, count: length})'

# Count occurrences
command | jc --parser | jq 'group_by(.type) | map({type: .[0].type, count: length})'
```

### Aggregation

```bash
# Sum values
command | jc --parser | jq '[.[] | .size] | add'  # Sum all sizes

# Average values
command | jc --parser | jq '[.[] | .cpu_percent] | add / length'

# Min/Max
command | jc --parser | jq 'min_by(.size), max_by(.size)'

# Unique values
command | jc --parser | jq 'map(.status) | unique'
```

## Integration with 1Password CLI

### Storing Parse Results as Secrets

```bash
# Parse system info and store in 1Password vault
hostname=$(hostname | jc --generic)
ip=$(dig +short @8.8.8.8 google.com | jc --dig | jq -r '.answers[0].address')

# Create item with results
op item create --template=login \
  --title="System Inventory $(date)" \
  --vault=Audit \
  --username="$hostname" \
  --password="$ip"
```

### Combining jc Output with Secrets

```bash
# Fetch SSH key from 1Password, use it in command
key=$(op read op://personal/ssh-key/private_key)

# Parse remote ps output with that key
ssh -i <(echo "$key") user@host 'ps aux' | jc --ps | jq '.[] | select(.command | contains("app"))'
```

## Streaming Mode

### Using -s Flag for Large Outputs

```bash
# Streaming: outputs one record at a time instead of full array
ps aux | jc -s --ps | jq .

# Useful for very large process lists (avoids loading entire array in memory)
# Output: one JSON object per line (JSONL format)
```

### Processing Streaming Output

```bash
# Each line is one object; filter streaming output
ps aux | jc -s --ps | jq 'select(.cpu_percent > 50)'
```

## Summary

- **Always use `LC_ALL=C`** for reproducible locale-independent parsing
- **Pin jc version** in production: `pip install jc==1.21.0`
- **Test field names** before writing filters (they vary by version)
- **Handle empty output**: check `length` before indexing
- **Flatten complex nested** output with jq transformations
- **Combine jc + jq** for powerful filtering: `command | jc --parser | jq 'filter | transform'`
