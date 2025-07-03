import re
import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
log_path = rf'{os.getenv("NGINX_LOG_PATH")}'
seen_lines = set()
ip_cache = {}

log_pattern = re.compile(r'(?P<ip>\d+\.\d+\.\d+\.\d+).+?"(?P<method>\w+) (?P<path>.*?) HTTP/[\d.]+" (?P<status>\d{3})')

def get_geo_info(ip):
    if ip in ip_cache:
        return ip_cache[ip]
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}", timeout=3)
        data = response.json()
        if data["status"] == "success":
            location = f"{data['city']}, {data['regionName']}, {data['country']}"
        else:
            location = "Unknown"
    except requests.RequestException:
        location = "Unknown"
    ip_cache[ip] = location
    return location

print("🌐 Monitoring access log...\n(Press Ctrl+C to stop)\n")

try:
    while True:
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line not in seen_lines:
                        seen_lines.add(line)
                        match = log_pattern.search(line)
                        if match:
                            ip = match.group("ip")
                            path = match.group("path")
                            status = match.group("status")
                            location = get_geo_info(ip)
                            print(f"[{ip} - {location}] \"{path}\" → {status}")
        except FileNotFoundError:
            print("❌ Log file not found. Retrying...")
        time.sleep(5)
except KeyboardInterrupt:
    print("\n👋 Exiting monitor.")
