import re
from collections import Counter
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
log_path = rf'{os.getenv("NGINX_LOG_PATH")}'

# Regex pattern for standard NGINX access log
log_pattern = re.compile(
    r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] "(?P<method>\S+)\s(?P<path>\S+)[^"]*" (?P<status>\d{3})'
)

# Counters
ips = Counter()
paths = Counter()
statuses = Counter()
total = 0

if not log_path.exists():
    print(f"[!] Could not find log file: {log_path}")
    exit(1)

print(f"[+] Reading WSL log file: {log_path}")

# Read and parse log
with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        match = log_pattern.match(line)
        if match:
            total += 1
            ip = match.group("ip")
            path = match.group("path")
            status = match.group("status")

            ips[ip] += 1
            paths[path] += 1
            statuses[status] += 1

# Output
print(f"\n[✓] Total Requests: {total}")
print(f"[✓] Unique IPs: {len(ips)}")

print("\nTop 5 IPs:")
for ip, count in ips.most_common(5):
    print(f"  {ip:15} → {count} requests")

print("\nTop 5 Paths:")
for path, count in paths.most_common(5):
    print(f"  {path:30} → {count} hits")

print("\nStatus Codes:")
for status, count in sorted(statuses.items()):
    print(f"  HTTP {status} → {count}")
