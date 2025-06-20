🤖 TGBotSniper
TGBotSniper is a powerful Telegram automation tool that monitors groups for exposed bot tokens and automatically snipes them.
It then sends the tokens to a specified bot to collect rewards or points.
Built for speed, precision, and stealth. 🚀

🛠️ Installation Guide (Termux)
Follow the steps below to install and run TGBotSniper on Android via Termux.

📦 Step 1: Update Your Packages
pkg update && pkg upgrade -y

🐍 Step 3: Install Dependencies
pkg install python -y
pkg install git -y

📁 Step 4: Clone the Project
git clone https://github.com/BayLak-ONE/Termux-Scripts.git
cd Termux-Scripts/Telegram-Tools/TGBotSniper

⚙️ Step 5: Configure Target Groups
Before running the tool, you must edit the list of groups to monitor:

nano group.js

📝 Add the group usernames or IDs that post bot tokens.

📦 Step 6: Install Python Requirements
pip install -r requirements.txt

🚀 Step 7: Start the Sniper
python main.py

⚠️ Important Notes
Make sure the groups you add in group.js are public or you have joined them.

The tool uses the Telegram API via Telethon, so it requires API credentials.

Works best with bots that reward you for sending valid tokens quickly.

