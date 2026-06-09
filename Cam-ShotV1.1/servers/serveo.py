import subprocess
import re
import os
title = "Serveo Tunnel (No Warning)"
def start(port):
    cmd = ["ssh", "-q", "-o", "StrictHostKeyChecking=no", "-o", "ServerAliveInterval=60", "-R", f"80:localhost:{port}", "serveo.net"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    for line in proc.stdout:
        m = re.search(r"https://[a-zA-Z0-9.-]+\.serveousercontent\.com", line)
        if m:
            return m.group(0)
    return None