# Linux Remote Administration

## Critical Gotchas (Read First)

### SSH Key Permissions (Silent Auth Failures)

- SSH key **must** be exactly `0600` (readable/writable by owner only). Any other permission = silent auth failure
- **DANGER**: Permission check happens before showing error message; auth silently fails
- **FIX**: Always after fetching SSH key from 1Password:

  ```bash
  chmod 0600 ~/.ssh/id_ed25519
  ls -la ~/.ssh/id_ed25519  # Verify: -rw------- (0600)
  ```

- **Why**: SSH rejects keys with world-readable permissions as potential security risk

### SSH Connection Timeouts

- Default SSH waits indefinitely if host unreachable. Script appears to hang
- **FIX**: Always set timeout:

  ```bash
  ssh -o ConnectTimeout=5 -o BatchMode=yes user@host "command"
  ```

- `ConnectTimeout=5` = 5-second timeout
- `BatchMode=yes` = no password prompt (fail fast if auth fails)

### systemd vs init vs rc.d

- Different Linux distributions use different init systems
- **DANGER**: Assuming systemctl works on all Linux systems = failures on older systems
- **FIX**: Check init system first:

  ```bash
  if command -v systemctl &> /dev/null; then
    systemctl start service
  else
    service service start  # Fallback for systems without systemctl
  fi
  ```

### Sudo Password Requirements

- Remote commands via sudo often fail if password required but not available
- **FIX**: Use 1Password CLI to provide sudo password, or configure passwordless sudo:

  ```bash
  echo "user ALL=(ALL) NOPASSWD: /usr/bin/systemctl" | sudo tee -a /etc/sudoers.d/user
  ```

## SSH Best Practices for Scripts

### Safe SSH Connection Wrapper

```bash
#!/bin/bash
# ssh-wrapper.sh - Safe SSH with timeouts and error handling

set -euo pipefail

HOST="${1}"
COMMAND="${2}"

# Connection settings
TIMEOUT=10
MAX_RETRIES=3
RETRY_DELAY=2

attempt=0
while [ $attempt -lt $MAX_RETRIES ]; do
  if ssh -o ConnectTimeout=$TIMEOUT \
         -o BatchMode=yes \
         -o StrictHostKeyChecking=accept-new \
         user@"$HOST" "$COMMAND"; then
    exit 0
  fi

  attempt=$((attempt + 1))
  if [ $attempt -lt $MAX_RETRIES ]; then
    echo "SSH failed, retrying in ${RETRY_DELAY}s..." >&2
    sleep $RETRY_DELAY
  fi
done

echo "SSH failed after $MAX_RETRIES attempts" >&2
exit 1
```

### Batch SSH Commands (Fleet Management)

```bash
#!/bin/bash
# ssh-batch.sh - Run command on multiple hosts with error handling

set -euo pipefail

HOSTS=("server1" "server2" "server3")
COMMAND="$1"
RESULTS_FILE="ssh-results.json"

echo "[" > "$RESULTS_FILE"

for host in "${HOSTS[@]}"; do
  result=$(ssh -o ConnectTimeout=5 -o BatchMode=yes user@"$host" "$COMMAND" 2>&1 || echo "FAILED")

  echo "{\"host\": \"$host\", \"result\": \"$result\"}," >> "$RESULTS_FILE"
done

echo "]" >> "$RESULTS_FILE"

# Parse results
jq . "$RESULTS_FILE"
```

## Package Management

### APT (Debian/Ubuntu)

```bash
# Update package index (always do this first)
apt update

# Install package
apt install -y package_name

# List installed packages
apt list --installed

# Show package info
apt info package_name

# Remove package
apt remove -y package_name

# Autoremove unused packages
apt autoremove -y
```

### YUM/DNF (RHEL/CentOS/Fedora)

```bash
# Install package
yum install -y package_name
dnf install -y package_name  # dnf is newer

# List installed packages
yum list installed
dnf list installed

# Remove package
yum remove -y package_name
dnf remove -y package_name

# Search for package
yum search keyword
dnf search keyword
```

### Checking if Package Installed

```bash
#!/bin/bash
# Check if package installed (distribution-agnostic)

check_package() {
  local pkg="$1"

  if command -v apt &> /dev/null; then
    dpkg -l | grep -q "^ii.*$pkg" && echo "Installed" || echo "Not installed"
  elif command -v yum &> /dev/null; then
    yum list installed | grep -q "$pkg" && echo "Installed" || echo "Not installed"
  else
    echo "Unknown package manager"
  fi
}

check_package "curl"
```

## System Service Management

### Using systemctl

```bash
# List all services
systemctl list-units --type=service

# Start service
systemctl start service_name

# Stop service
systemctl stop service_name

# Restart service
systemctl restart service_name

# Enable service on boot
systemctl enable service_name

# Check service status
systemctl status service_name

# View service logs (last 10 lines)
journalctl -u service_name -n 10

# Follow service logs in real-time
journalctl -u service_name -f
```

### Creating Custom Service

```bash
# Create service file at /etc/systemd/system/myapp.service
[Unit]
Description=My Application
After=network.target

[Service]
Type=simple
User=appuser
WorkingDirectory=/opt/myapp
ExecStart=/usr/bin/python3 app.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable myapp
sudo systemctl start myapp
```

## Disk & Storage Management

### Monitoring Disk Usage

```bash
# Show disk usage with jc
df -h | jc --df

# Find largest directories
du -sh /path/* | sort -rh | head -10

# Show inodes usage
df -i

# Check specific filesystem
df /path/to/mount
```

### Finding Large Files

```bash
# Find files larger than 100MB
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# Or using jc (see jc-parser-reference.md)
ls -lR / | jc --ls | jq '.[] | select(.size > 104857600)'
```

### Disk Cleanup

```bash
# Clear package manager cache
apt clean                    # Debian/Ubuntu
yum clean all                # RHEL/CentOS

# Remove old log files
find /var/log -type f -mtime +30 -delete  # Files older than 30 days

# Find and remove temporary files
find /tmp -type f -atime +7 -delete       # Unused for 7+ days
```

## Networking Diagnostics

### Checking Network Connectivity

```bash
# Ping with timeout
ping -c 1 -W 5 8.8.8.8

# DNS resolution test
nslookup google.com
dig google.com

# Trace route to host
traceroute -m 15 google.com

# Show listening ports
netstat -tulpn | grep LISTEN
ss -tulpn | grep LISTEN

# Monitor network traffic
iftop -n  # Top-like tool for network
tcpdump -i eth0 -n 'tcp port 443'
```

### Network Diagnostics with jc

```bash
# Parse netstat output
netstat -an | jc --netstat | jq '.[] | select(.state == "LISTEN") | .local_port'

# Parse route table
route -n | jc --route | jq '.[] | {destination, gateway}'

# Parse interface info
ip addr show | jc --ifconfig | jq '.[] | {name: .name, ipv4_addr: .ipv4_addr}'
```

## User & Permission Management

### User Management

```bash
# Create user
sudo useradd -m -s /bin/bash username

# Set password
sudo passwd username

# Add to sudo group
sudo usermod -aG sudo username

# Delete user
sudo userdel -r username  # -r removes home directory

# List all users
cut -d: -f1 /etc/passwd
```

### File Permissions

```bash
# Change ownership
chown user:group /path/to/file
chown -R user:group /path/to/directory  # Recursive

# Change permissions
chmod 0644 /path/to/file   # rw-r--r--
chmod 0755 /path/to/script # rwxr-xr-x

# SSH key special permissions (CRITICAL)
chmod 0600 ~/.ssh/id_rsa   # Private key
chmod 0644 ~/.ssh/id_rsa.pub  # Public key
chmod 0700 ~/.ssh/         # .ssh directory
```

## Integration with Automation

### Remote Execution with 1Password Secrets

```bash
#!/bin/bash
# Deploy with secrets from 1Password

HOST="production.example.com"
DB_PASSWORD=$(op read op://prod/db/password)
API_KEY=$(op read op://prod/api/key)

# SSH with secret injection
ssh user@"$HOST" <<EOF
  export DB_PASSWORD="$DB_PASSWORD"
  export API_KEY="$API_KEY"
  /opt/app/deploy.sh
EOF
```

### Fleet Health Check

```bash
#!/bin/bash
# Check all servers and report health

SERVERS=("web01" "web02" "db01" "cache01")
REPORT="fleet-health-$(date +%Y%m%d).json"

{
  echo "["
  for server in "${SERVERS[@]}"; do
    status=$(ssh -o ConnectTimeout=5 user@"$server" "uptime" 2>&1)
    echo "{\"server\": \"$server\", \"status\": \"$status\"},"
  done
  echo "]"
} > "$REPORT"

# Store report in 1Password
op item create --template=login \
  --title="Fleet Report $(date)" \
  --vault=Audit \
  --username="$(hostname)" \
  --password="$(cat $REPORT)"
```

## Troubleshooting

### SSH Connection Refused

```bash
# Problem: Connection refused when SSHing to host
# Causes: Host not running SSH, firewall blocking, wrong port

# Check SSH service running
ssh-keyscan -t rsa host 2>/dev/null || echo "SSH not responding"

# Try different port
ssh -p 2222 user@host

# Check firewall
sudo iptables -L | grep 22
```

### "Permission denied" for sudo

```bash
# Problem: sudo command fails with "not in sudoers"

# Fix: Add user to sudoers file (on target server)
sudo usermod -aG sudo username

# Or edit sudoers safely
sudo visudo
# Add line: username ALL=(ALL) ALL
```

### Network Timeout Issues

```bash
# Problem: Script hangs when connecting to host
# Cause: No timeout set on SSH

# Fix: Always use ConnectTimeout
ssh -o ConnectTimeout=5 -o BatchMode=yes user@host "command"
```

## Summary

- **SSH key perms must be exactly 0600** — silent auth failure otherwise
- **Always set ConnectTimeout** — prevents script hanging
- **Check init system** before assuming systemctl
- **Use 1Password CLI** to inject secrets, never hardcode
- **Test on multiple Linux distributions** — behaviors vary
- **Parse systemd logs** with jc for automated error detection
- **Verify sudo/password requirements** before running batch commands
