import subprocess
import re
import os
title = "Localtunnel (Official)"
def start(port):
    cmd = ["lt", "--port", str(port)]
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )
    while True:
        line = proc.stdout.readline()
        if not line: break
        m = re.search(r"https://[a-zA-Z0-9-]+\.loca\.lt", line)
        if m:
            return m.group(0)
    return None