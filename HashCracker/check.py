import requests
from tqdm import tqdm
import os

def load_links(file_path):
    with open(file_path, "r") as f:
        return list(set(line.strip() for line in f if line.strip()))

def is_valid_txt_link(session, url):
    try:
        response = session.head(url, timeout=10, allow_redirects=True)
        content_type = response.headers.get("Content-Type", "")
        return response.status_code == 200 and ("text/plain" in content_type or url.endswith(".txt"))
    except:
        return False

def download_wordlist(session, url):
    try:
        response = session.get(url, timeout=20)
        if response.status_code == 200 and len(response.text.strip()) > 0:
            return response.text.splitlines()
    except:
        return []
    return []

def main():
    links = load_links("links.txt")
    session = requests.Session()
    all_passwords = set()

    print(f"[+] Total links to check: {len(links)}\n")
    for link in tqdm(links, desc="Checking & Downloading", ncols=80):
        if is_valid_txt_link(session, link):
            words = download_wordlist(session, link)
            if words:
                all_passwords.update(word.strip() for word in words if word.strip())

    if all_passwords:
        with open("passwords.txt", "w", encoding="utf-8") as out:
            out.write("\n".join(sorted(all_passwords)))
        print(f"\n[✓] Saved {len(all_passwords)} unique passwords to passwords.txt")
    else:
        print("\n[!] No passwords found.")

if __name__ == "__main__":
    main()