import subprocess
import re
import time
import os
title = "Pinggy Tunnel (Auto HTTPS)"
def start(port):
    tmp_link_file = "/tmp/pinggy_link.txt"
    if os.path.exists(tmp_link_file):
        os.remove(tmp_link_file)
    cmd = f"ssh -p 443 -o StrictHostKeyChecking=no -R0:localhost:{port} a.pinggy.io > {tmp_link_file} 2>&1"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(15):
        time.sleep(1)
        if os.path.exists(tmp_link_file):
            with open(tmp_link_file, "r") as f:
                content = f.read()
                m = re.search(r"https://[a-zA-Z0-9-]+\.run\.pinggy-free\.link", content)
                if m:
                    return m.group(0)
    return None