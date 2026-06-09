import subprocess
import re
import time
import os
title = "Bore Tunnel (Stable)"
def start(port):
    tmp_link_file = "/tmp/bore_link.txt"
    if os.path.exists(tmp_link_file):
        os.remove(tmp_link_file)
    cmd = f"bore local {port} --to bore.pub > {tmp_link_file} 2>&1"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for i in range(10):
        time.sleep(1)
        if os.path.exists(tmp_link_file):
            with open(tmp_link_file, "r") as f:
                content = f.read()
                m = re.search(r"bore\.pub[:/](\d+)", content)
                if m:
                    return f"http://bore.pub:{m.group(1)}"
    return None