import os
import argparse
import hashlib
import urllib.request
import pickle
import shutil
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

DB_FILE = "hashes.bin"
SEEN_LINKS_FILE = "seen_links.txt"

def get_terminal_width():
    return shutil.get_terminal_size().columns

def print_banner():
    width = get_terminal_width()
    if width < 65:
        print(f"{Fore.CYAN}" + "=" * width)
        print(f"{Fore.MAGENTA}      HASH-CRACKER TermuX")
        print(f"{Fore.YELLOW}      Made by BayLak")
        print(f"{Fore.CYAN}" + "=" * width)
    else:
        banner = r"""
    __  __           __      ______                __             
   / / / /___ ______/ /_    / ____/________ ______/ /_____  _____ 
  / /_/ / __ `/ ___/ __ \  / /   / ___/ __ `/ ___/ //_/ _ \/ ___/ 
 / __  / /_/ (__  ) / / / / /___/ /  / /_/ / /__/ ,< /  __/ /     
/_/ /_/\__,_/____/_/ /_/  \____/_/   \__,_/\___/_/|_|\___/_/      
                                                                  
            >> Made by BayLak | Mobile Ready <<
        """
        print(f"{Fore.CYAN}{banner}")
        print(f"{Fore.MAGENTA}    " + "=" * 55 + "\n")

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "rb") as f:
            try: return pickle.load(f)
            except: return {}
    return {}

def save_db(db):
    with open(DB_FILE, "wb") as f:
        pickle.dump(db, f)

def load_seen_links():
    if os.path.exists(SEEN_LINKS_FILE):
        with open(SEEN_LINKS_FILE, "r") as f:
            return set(line.strip() for line in f)
    return set()

def save_seen_link(link):
    with open(SEEN_LINKS_FILE, "a") as f:
        f.write(link + "\n")

def compute_hash(word, algo):
    h = hashlib.new(algo)
    h.update(word.encode())
    return h.hexdigest()

def update_database(algo, target_hash=None):
    if not os.path.exists("links.txt"):
        print(f"{Fore.RED}[!] Error: links.txt not found.")
        return False
    
    db = load_db()
    if target_hash and target_hash in db: return True

    seen_links = load_seen_links()
    with open("links.txt", "r") as f:
        links = [line.strip() for line in f if line.strip()]

    for link in links:
        if link in seen_links: continue
        try:
            filename = link.split('/')[-1][:15]
            print(f"\n{Fore.CYAN}[+] List: {filename}")
            
            response = urllib.request.urlopen(link, timeout=7)
            content = response.read().decode(errors='ignore').splitlines()
            
            width = get_terminal_width()
            for pwd in tqdm(content, desc="   Cracking", unit="w", leave=False, ncols=min(width, 80)):
                if not pwd: continue
                h = compute_hash(pwd, algo)
                if h not in db: db[h] = pwd
                if target_hash and h == target_hash:
                    save_db(db)
                    return True
            
            save_seen_link(link)
            save_db(db)
        except:
            print(f"{Fore.YELLOW}[!] Skipping unavailable link")
            continue
    return False

def find_hash(hash_value, algo):
    db = load_db()
    if hash_value in db:
        width = min(get_terminal_width(), 50)
        print(f"\n{Fore.GREEN}{'='*width}")
        print(f"{Fore.GREEN}[✓] SUCCESS!")
        print(f"{Fore.WHITE}Pass: {Fore.YELLOW}{db[hash_value]}")
        print(f"{Fore.GREEN}{'='*width}")
        return True
    return False

if __name__ == "__main__":
    print_banner()
    
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--algo", required=True)
    parser.add_argument("-H", "--hash")
    args = parser.parse_args()

    algo = args.algo.lower()
    
    if args.hash:
        target = args.hash.lower()
        print(f"{Fore.BLUE}[*] Checking local...")
        if not find_hash(target, algo):
            print(f"{Fore.BLUE}[*] Searching online lists...")
            if update_database(algo, target):
                find_hash(target, algo)
            else:
                print(f"\n{Fore.RED}[×] Not found.")
    else:
        update_database(algo)
        print(f"\n{Fore.GREEN}[✓] Updated.")
