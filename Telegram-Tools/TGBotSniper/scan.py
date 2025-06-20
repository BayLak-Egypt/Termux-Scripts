from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio, json, os, re, socket, random, string

config_path = 'config.js'
group_output = 'group.js'
group_ids = []  # القائمة الفعلية للمجموعات

def print_ascii_banner():
    print("🔎 Fast Telegram Group Scanner - by @BayLaks")

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

def is_connected():
    try:
        socket.create_connection(("1.1.1.1", 53), timeout=3)
        return True
    except OSError:
        return False

def save_groups():
    with open(group_output, "w", encoding="utf-8") as f:
        f.write("module.exports = [\n")
        for i, group in enumerate(group_ids):
            if i == len(group_ids) - 1:
                f.write(f'  "{group}"\n')
            else:
                f.write(f'  "{group}",\n')
        f.write("];\n")
    print(f"[💾] Saved to {group_output}")

async def scan_chat(client, entity, seen_chats):
    try:
        history = await client(GetHistoryRequest(
            peer=entity,
            limit=10,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))

        for message in history.messages:
            if message.message:
                match = re.search(r'https://t\.me/([\w\d_]+)[/\?]start=([\w\d]+)', message.message)
                if match:
                    chat_username = getattr(entity, "username", None)
                    chat_title = getattr(entity, "title", None)

                    if chat_username:
                        group_id = f"@{chat_username}"
                    elif chat_title:
                        group_id = f"@{chat_title.replace(' ', '_')}"
                    else:
                        group_id = "@Unknown"

                    if group_id not in seen_chats:
                        seen_chats.add(group_id)
                        group_ids.append(group_id)
                        print(f"[🎯] Found in: {group_id}")
                        return
    except:
        return

async def setup(client):
    dialogs = await client.get_dialogs()
    seen_chats = set()
    sem = asyncio.Semaphore(10)

    async def limited_scan(dialog):
        async with sem:
            entity = dialog.entity
            if not getattr(entity, "bot", False):
                await scan_chat(client, entity, seen_chats)

    await asyncio.gather(*(limited_scan(dialog) for dialog in dialogs))
    save_groups()
    if not group_ids:
        print("[⚠️] No groups found.")

async def main_loop():
    print_ascii_banner()
    while True:
        if not is_connected():
            print("[🌐] No internet. Retrying in 5s...")
            await asyncio.sleep(5)
            continue

        try:
            config = read_config()
            if not config:
                print("[⚙️] Setup:")
                api_id = int(input("API ID: "))
                api_hash = input("API Hash: ")
                phone = input("Phone Number (with +): ")
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

            print("[🚀] Connecting...")
            client = TelegramClient(session_name, api_id, api_hash)
            await client.connect()

            if not await client.is_user_authorized():
                print("[🔐] Logging in...")
                await client.start(phone=phone)

            await setup(client)
            break

        except Exception as e:
            print(f"[💥] Error: {e}")
            print("[🕓] Retry in 10s...")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except Exception as e:
        print(f"[🔄] Restarting... {e}")
        import time
        time.sleep(10)