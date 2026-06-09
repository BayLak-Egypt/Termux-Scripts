import subprocess
import re
import sys
title = "Cloudflare Tunnel (Official)"
def start(port):
    cmd = ["cloudflared", "tunnel", "--url", f"http://127.0.0.1:{port}"]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    while True:
        line = proc.stdout.readline()
        if not line: break
        m = re.search(r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com", line)
        if m:
            return m.group(0)
    return None