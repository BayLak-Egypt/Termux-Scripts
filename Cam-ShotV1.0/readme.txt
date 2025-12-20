# 🛡️ Advanced Multi-Tracker & Snapper
# Cam-Shot Tools v1.0 By BayLak
An advanced professional tool built with **Python** and **PHP** to track visitors, fetch their geolocation data, and automatically capture camera snapshots (upon permission) using **Cloudflare Tunneling** technology.



## 🚀 Key Features
* **Real IP Tracking:** Extracts the visitor's actual IP address even behind Cloudflare.
* **Deep Geo-Analysis:** Provides (Country, City, and ISP) information.
* **VPN/Proxy Detection:** Alerts you if the visitor is using anonymization tools.
* **Intelligent Camera Snapping:** Automatically captures 5 consecutive images and saves them locally.
* **Trustworthy UI:** Features a clean, official "Security Verification" white-themed web page to increase success rates.
* **Terminal Dashboard:** Displays all data in an organized table with a Progress Spinner.
* **No Filters:** Real-time monitoring for every single hit, including bots and self-visits.

## 🛠️ Requirements
The script automatically attempts to install these dependencies if they are missing:
* Python 3.x
* PHP
* Cloudflared

## 📥 Installation

1. Clone or download the script as `cam-shot-termux.py`.
2. For **Termux** users, ensure storage permissions are granted:
   ```bash
   termux-setup-storage
