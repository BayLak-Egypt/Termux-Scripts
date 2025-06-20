from telethon import TelegramClient, events
from telethon.tl.types import InputPeerChannel
from telethon.errors import FloodWaitError
import asyncio, json, os, re, time, socket, random, string, shutil, sys, subprocess

config_path = 'config.js'
group_path = 'group.js'
log_file = 'log.txt'
used_tokens = set()

def print_ascii_banner():
    RED = "\033[91m"
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"
    terminal_width = shutil.get_terminal_size().columns
    if terminal_width < 70:
        print(f"{CYAN}🔎 {RED}TGBotSniper{RESET} - {GREEN}Telegram Token Auto Sniper{RESET}")
        print(f"{YELLOW}MyTg: {GREEN}@BayLaks{RESET}")
    else:
        banner = rf"""{CYAN}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⣴⣾⣿⣿⣿⡄
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣴⣶⣿⣿⡿⠿⠛⢙⣿⣿⠃
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⣶⣾⣿⣿⠿⠛⠋⠁⠀⠀⠀⣸⣿⣿⠀
⠀⠀⠀⠀⣀⣤⣴⣾⣿⣿⡿⠟⠛⠉⠀⠀⣠⣤⠞⠁⠀⠀⣿⣿⡇⠀
⠀⣴⣾⣿⣿⡿⠿⠛⠉⠀⠀⠀⢀⣠⣶⣿⠟⠁⠀⠀⠀⢸⣿⣿⠀⠀
⠸⣿⣿⣿⣧⣄⣀⠀⠀⣀⣴⣾⣿⣿⠟⠁⠀⠀⠀⠀⠀⣼⣿⡿⠀⠀
⠀⠈⠙⠻⠿⣿⣿⣿⣿⣿⣿⣿⠟⠁⠀⠀⠀⠀⠀⠀⢠⣿⣿⠇⠀⠀
⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⡇⠀⣀⣄⡀⠀⠀⠀⠀⢸⣿⣿⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠸⣿⣿⣿⣠⣾⣿⣿⣿⣦⡀⠀⠀⣿⣿⡏⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣿⣿⡿⠋⠈⠻⣿⣿⣦⣸⣿⣿⠁⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠛⠁⠀⠀⠀⠀⠈⠻⣿⣿⣿⠏⠀⠀⠀{YELLOW}MyTg: {GREEN}@BayLaks{CYAN}

  {RED}🔎 TGBotSniper{RESET} - {GREEN}Telegram Token Auto Sniper{RESET}
"""
        print(banner)

if os.path.exists(log_file):
    with open(log_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if ':' in line:
                used_tokens.add(line)

def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def read_config():
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            json_data = content.replace('module.exports =', '').strip()
            return json.loads(json_data)
    return None

def write_config(config):
    with open(config_path, 'w', encoding='utf-8') as f:
        f.write('module.exports = ' + json.dumps(config, indent=2))

def read_groups():
    if os.path.exists(group_path):
        with open(group_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        if content.startswith('module.exports'):
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            json_data = content[json_start:json_end]
            try:
                groups = json.loads(json_data)
                return [g.lstrip('@') for g in groups]
            except json.JSONDecodeError as e:
                print(f"[❌] JSON decode error: {e}")
    return []

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3)
        return True
    except OSError:
        return False

async def resolve_channels(client, usernames):
    entities = {}
    for username in usernames:
        try:
            entity = await client.get_input_entity(username)
            if isinstance(entity, InputPeerChannel):
                entities[username] = InputPeerChannel(entity.channel_id, entity.access_hash)
                print(f"[✅] Resolved @{username}")
        except FloodWaitError as e:
            print(f"[⏳] Wait @{username}: {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except Exception as e:
            print(f"[⚠️] Failed @{username}: {e}")
    return entities

async def setup(client, usernames):
    entities = await resolve_channels(client, usernames)

    @client.on(events.NewMessage(chats=[entities[u] for u in entities]))
    async def handler(event):
        try:
            message_text = event.raw_text
            match = re.search(r'https://t\.me/([\w\d_]+)[/\?]start=([\w\d]+)', message_text)
            if match:
                bot_username = match.group(1)
                token = match.group(2)
                if len(token) < 30:
                    return

                unique_id = f'{bot_username}:{token}'
                if unique_id in used_tokens:
                    return
                try:
                    await client.send_message(bot_username, f'/start {token}')
                    print(f"[🚀] @{bot_username} ← /start {token}")
                    used_tokens.add(unique_id)
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(unique_id + '\n')
                except FloodWaitError as e:
                    print(f"[⏳] Wait @{bot_username}: {e.seconds}s")
                    await asyncio.sleep(e.seconds)
                except Exception as e:
                    print(f"[⚠️] Error @{bot_username}: {e}")
        except Exception as e:
            print(f"[‼️] Handler error: {e}")

    me = await client.get_me()
    print(f"[👁️] Logged in as @{me.username} | Watching {len(entities)} channels...")

async def main_loop():
    print_ascii_banner()
    while True:
        if not is_connected():
            print("[🌐] No internet connection. Retrying in 10s...")
            await asyncio.sleep(10)
            continue

        try:
            config = read_config()
            if not config:
                print("[⚙️] First-time setup:")
                api_id = int(input("Enter API ID: "))
                api_hash = input("Enter API Hash: ")
                phone = input("Enter Phone Number (with +): ")
                session_name = f"{phone}-{generate_random_string()}"
                config = {
                    "api_id": api_id,
                    "api_hash": api_hash,
                    "phone": phone,
                    "session_name": session_name
                }
                write_config(config)
                print("[✅] Config saved.")
            else:
                api_id = config["api_id"]
                api_hash = config["api_hash"]
                phone = config["phone"]
                session_name = config["session_name"]

            usernames = read_groups()
            print("[🔁] Starting client...")
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                print("[🔐] Logging in...")
                await client.start(phone=phone)

            await setup(client, usernames)
            await client.run_until_disconnected()

        except Exception as e:
            print(f"[💥] Exception: {e}")
            print("[🕓] Reconnecting in 20s...")
            await asyncio.sleep(20)

if __name__ == "__main__":
    if '-r' in sys.argv:
        print("[⚙️] Running scan.py first...")
        subprocess.run(["python", "scan.py"])

    while True:
        try:
            asyncio.run(main_loop())
        except Exception as e:
            print(f"[🔄] Restarting loop after error: {e}")
            time.sleep(15)
