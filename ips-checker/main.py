import ipaddress
import urllib.request
import json
import sys
import concurrent.futures
import time
import subprocess
import socket
import argparse

# الحقول الأساسية
FIELDS = ["IP", "Country", "City", "ORG/ISP", "Location", "Source"]

# ================== SECURITY TOOLS ==================
def check_ping(ip):
    command = ['ping', '-c', '1', '-W', '1', ip]
    try:
        res = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "ALIVE" if res == 0 else "DEAD"
    except:
        return "ERROR"

def get_host_info(ip):
    try:
        host = socket.gethostbyaddr(ip)[0]
        return host
    except:
        return "N/A"

def scan_ports(ip, ports=[80, 443, 21, 22, 3389]):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)
                if s.connect_ex((ip, port)) == 0:
                    open_ports.append(str(port))
        except:
            pass
    return ", ".join(open_ports) if open_ports else "CLOSED/FILTERED"

# ================== SERVERS ==================
def from_ipapi(ip):
    try:
        url = f"http://ip-api.com/json/{ip}"
        with urllib.request.urlopen(url, timeout=5) as r:
            d = json.loads(r.read().decode())
            if d.get("status") == "success":
                return {
                    "IP": ip, "Country": d.get("country"), "City": d.get("city"),
                    "ORG/ISP": d.get("org") or d.get("isp"),
                    "Location": f"{d.get('lat')},{d.get('lon')}", "Source": "IP-API"
                }
    except: return None

def from_ipwhois(ip):
    try:
        url = f"https://ipwho.is/{ip}"
        with urllib.request.urlopen(url, timeout=5) as r:
            d = json.loads(r.read().decode())
            if d.get("success"):
                return {
                    "IP": ip, "Country": d.get("country"), "City": d.get("city"),
                    "ORG/ISP": d.get("connection", {}).get("org"),
                    "Location": f"{d.get('latitude')},{d.get('longitude')}", "Source": "IPWhois"
                }
    except: return None

# ================== MAIN FETCH LOGIC ==================
def fetch(ip, args):
    data = None
    for server in [from_ipapi, from_ipwhois]:
        data = server(ip)
        if data: break
    
    if not data:
        data = {"IP": ip, "Source": "None"}

    current_fields = FIELDS.copy()
    
    if args.ping:
        data["Ping"] = check_ping(ip)
        current_fields.append("Ping")
        
    if args.host or args.domain:
        data["Hostname/Domain"] = get_host_info(ip)
        current_fields.append("Hostname/Domain")

    if args.ports:
        data["Open Ports"] = scan_ports(ip)
        current_fields.append("Open Ports")

    return table_for_ip(data, current_fields)

def table_for_ip(data, fields):
    clean_data = {f: str(data.get(f, "N/A")) for f in fields}
    w1 = max(len(k) for k in fields)
    w2 = max(len(v) for v in clean_data.values())
    line = "+" + "-"*(w1+2) + "+" + "-"*(w2+2) + "+"
    out = [line]
    for k in fields:
        out.append(f"| {k.ljust(w1)} | {clean_data[k].ljust(w2)} |")
    out.append(line)
    return "\n".join(out)

# ================== MAIN ==================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BayLak Security Scanner")
    parser.add_argument("target", help="IP, CIDR, or Range")
    parser.add_argument("--ping", action="store_true")
    parser.add_argument("--host", action="store_true")
    parser.add_argument("--domain", action="store_true")
    parser.add_argument("--ports", action="store_true", help="Scan common ports")
    
    args = parser.parse_args()
    print(f"[*] Scanning {args.target}...\n")
    
    # تحسين الـ Generator للتعامل مع النطاقات
    try:
        if "-" in args.target:
            start, end = args.target.split("-")
            ips = [str(ipaddress.IPv4Address(i)) for i in range(int(ipaddress.IPv4Address(start)), int(ipaddress.IPv4Address(end)) + 1)]
        elif "/" in args.target:
            ips = [str(ip) for ip in ipaddress.ip_network(args.target, strict=False).hosts()]
        else:
            ips = [args.target]
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
        futures = [executor.submit(fetch, ip, args) for ip in ips]
        for future in concurrent.futures.as_completed(futures):
            print(future.result())
            print()
