"""
proxy_scanner.py
Fetch free proxy lists from public sources, test them concurrently,
and export valid proxies with latency info.

© 2025 Mohammad Jabbary
"""
import requests
import time
import argparse
import sys
import itertools
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from colorama import Fore, Style, init as colorama_init

colorama_init(autoreset=True)

# Default sources (plain text lists or simple API endpoints returning ip:port per line)
SOURCES = {
    "http": [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/proxy.txt",
        "https://www.proxy-list.download/api/v1/get?type=http"
    ],
    "https": [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=https&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/https.txt",
        "https://www.proxy-list.download/api/v1/get?type=https"
    ],
    "socks4": [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks4&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
        "https://www.proxy-list.download/api/v1/get?type=socks4"
    ],
    "socks5": [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=socks5&timeout=5000&country=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
        "https://www.proxy-list.download/api/v1/get?type=socks5"
    ]
}

TEST_URL = "https://httpbin.org/ip"   # endpoint to verify proxy (returns IP)
DEFAULT_WORKERS = 40

def fetch_list(url, timeout=10):
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent": "proxy-scanner/1.0"})
        if r.status_code == 200:
            text = r.text.strip()
            lines = [line.strip() for line in text.splitlines() if line.strip() and ':' in line.strip()]
            return lines
    except Exception:
        return []
    return []

def gather_sources(types, timeout=8):
    proxies = set()
    for t in types:
        urls = SOURCES.get(t, [])
        for url in urls:
            try:
                lst = fetch_list(url, timeout=timeout)
                for p in lst:
                    p = p.strip()
                    if p.startswith("http://") or p.startswith("https://") or p.startswith("socks5://") or p.startswith("socks4://"):
                        p = p.split("://", 1)[1]
                    proxies.add((p, t))
            except Exception:
                continue
    return list(proxies)

def build_proxy_dict(proxy_hostport, ptype):
    hostport = proxy_hostport.strip()
    if ptype in ("http", "https"):
        p = f"http://{hostport}"
        return {"http": p, "https": p}
    if ptype == "socks4":
        return {"http": f"socks4://{hostport}", "https": f"socks4://{hostport}"}
    if ptype == "socks5":
        return {"http": f"socks5h://{hostport}", "https": f"socks5h://{hostport}"}
    return {}

def test_proxy(proxy_tuple, timeout=8, verify_ssl=True):
    """
    proxy_tuple: (host:port, type)
    returns: dict or None
    """
    hostport, ptype = proxy_tuple
    proxies = build_proxy_dict(hostport, ptype)
    start = time.perf_counter()
    try:
        r = requests.get(TEST_URL, proxies=proxies, timeout=timeout, verify=verify_ssl, headers={"User-Agent":"proxy-scanner/1.0"})
        latency = time.perf_counter() - start
        if r.status_code == 200:
            ipinfo = r.json()
            return {
                "proxy": hostport,
                "type": ptype,
                "latency": round(latency, 3),
                "status": "ok",
                "origin": ipinfo.get("origin")
            }
    except Exception as e:
        return {"proxy": hostport, "type": ptype, "latency": None, "status": "fail", "error": str(e)}
    return {"proxy": hostport, "type": ptype, "latency": None, "status": "fail", "error": "bad_status"}

def save_results(valid_list, out_prefix="valid_proxies"):
    txt_path = f"{out_prefix}.txt"
    csv_path = f"{out_prefix}.csv"
    with open(txt_path, "w") as f:
        for p in valid_list:
            f.write(f"{p['proxy']},{p['type']},{p['latency']}\n")
    with open(csv_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["proxy","type","latency","origin"])
        writer.writeheader()
        for p in valid_list:
            writer.writerow({
                "proxy": p.get("proxy"),
                "type": p.get("type"),
                "latency": p.get("latency"),
                "origin": p.get("origin","")
            })
    return txt_path, csv_path

def main(args):
    types = [t.strip().lower() for t in args.types.split(",") if t.strip()]
    print(Fore.CYAN + "[*] Fetching proxy lists for types: " + ", ".join(types))
    proxies = gather_sources(types, timeout=10)
    print(Fore.YELLOW + f"[i] Collected {len(proxies)} candidate proxies from sources (deduped).")

    if not proxies:
        print(Fore.RED + "[!] No proxies fetched. Exiting.")
        return

    workers = max(4, args.workers)
    timeout = args.timeout
    verify_ssl = not args.insecure

    valid = []
    failed_count = 0

    print(Fore.CYAN + f"[*] Testing proxies with {workers} workers, timeout={timeout}s ...")
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(test_proxy, p, timeout, verify_ssl): p for p in proxies}
        for fut in tqdm(as_completed(futures), total=len(futures), desc="Testing", unit="proxy"):
            try:
                res = fut.result()
            except Exception as e:
                failed_count += 1
                continue
            if res and res.get("status") == "ok":
                valid.append(res)
            else:
                failed_count += 1

    print(Fore.GREEN + f"[+] Valid proxies: {len(valid)}")
    print(Fore.RED + f"[-] Failed/Dead: {failed_count}")

    valid_sorted = sorted(valid, key=lambda x: (x.get("latency") is None, x.get("latency", 9999)))

    out_txt, out_csv = save_results(valid_sorted, args.output)
    print(Fore.CYAN + f"[i] Saved results -> {out_txt}, {out_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and test free proxies (http/https/socks4/socks5).")
    parser.add_argument("--types", default="http,https,socks4,socks5",
                        help="Comma-separated proxy types to fetch/test (http,https,socks4,socks5).")
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="Number of concurrent workers.")
    parser.add_argument("--timeout", type=int, default=8, help="Timeout per proxy test in seconds.")
    parser.add_argument("--output", default="valid_proxies", help="Output prefix (txt & csv).")
    parser.add_argument("--insecure", action="store_true", help="Allow insecure SSL for test requests (verify=False).")
    args = parser.parse_args()
    try:
        main(args)
    except KeyboardInterrupt:
        print("\n" + Fore.RED + "[!] Interrupted by user.")
        sys.exit(1)
