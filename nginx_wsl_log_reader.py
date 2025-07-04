import re
import os
import requests
from collections import Counter
from dotenv import load_dotenv

# Load .env config
load_dotenv()
log_path = rf'{os.getenv("NGINX_LOG_PATH")}'

# Regex for typical NGINX access log
log_pattern = re.compile(
    r'(?P<ip>\S+) - - \[(?P<time>[^\]]+)\] "(?P<method>\S+)\s(?P<path>\S+)[^"]*" (?P<status>\d{3})'
)

# Tracking counters
ips = Counter()
paths = Counter()
statuses = Counter()
total = 0

if not os.path.exists(log_path):
    print(f"[!] Log file not found: {log_path}")
    exit(1)

print(f"[+] Reading WSL log file: {log_path}")

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

# Geolocation with ip-api.com
def get_geo(ip):
    if ip.startswith(("127.", "192.168.", "10.", "172.")):
        return "Private IP"
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        if res.status_code == 200:
            data = res.json()
            if data.get("status") == "success":
                return f"{data.get('city', '')}, {data.get('regionName', '')}, {data.get('country', '')}".strip(", ")
            else:
                return "Lookup Failed"
        else:
            return "Request Failed"
    except Exception:
        return "Lookup Error"

# Output
print(f"\n[✓] Total Requests: {total}")
print(f"[✓] Unique IPs: {len(ips)}")

print("\n🌍 Top 5 IPs (with location):")
for ip, count in ips.most_common(5):
    location = get_geo(ip)
    print(f"  {ip:15} → {count:4} requests from {location}")

print("\n📄 Top 5 Paths:")
for path, count in paths.most_common(5):
    print(f"  {path:30} → {count} hits")

print("\n📊 Status Codes:")
for status, count in sorted(statuses.items()):
    print(f"  HTTP {status} → {count}")
