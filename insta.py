import requests
import json
import os
import time
import random
import signal
import sys
from rich.console import Console

console = Console()

def banner():
    console.print(r"""
[bold yellow]
╦┌┐┌┌─┐┌┬┐┌─┐  ╔═╗┌─┐┬  ┬  ┌─┐┬ ┬
║│││└─┐ │ ├─┤  ╠╣ │ ││  │  │ ││││
╩┘└┘└─┘ ┴ ┴ ┴  ╚  └─┘┴─┘┴─┘└─┘└┴┘
Auto Followers & Unfollow by @0x29p
[/]
""", justify="center")

COOKIES_FILE = "cookies.json"
USERNAMES_FILE = "usernames.txt"
follow_count = 0
unfollow_count = 0

# --- Load Cookies ---
if os.path.exists(COOKIES_FILE):
    with open(COOKIES_FILE, "r") as file:
        COOKIES = json.load(file)
else:
    console.print("❌ [bold red]Cookies tidak ditemukan! Harap masukkan sessionid secara manual.[/]")
    exit()

SESSION_ID = COOKIES.get("sessionid")
CSRF_TOKEN = COOKIES.get("csrftoken", "")

if not SESSION_ID:
    console.print("❌ [bold red]Session ID tidak ditemukan dalam cookies.json! Pastikan valid.[/]")
    exit()

HEADERS = {
    "User-Agent": "Instagram 320.0.0.12 Android",
    "Referer": "https://www.instagram.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-CSRFToken": CSRF_TOKEN,
    "X-IG-App-ID": "936619743392459",
}

session = requests.Session()
session.cookies.set("sessionid", SESSION_ID, domain=".instagram.com")
session.headers.update(HEADERS)


# Fungsi untuk menangani Ctrl+C
def handle_ctrl_c(signal_received, frame):
    global follow_count, unfollow_count

    try:
        username, user_id, followers, following = check_login()
    except:
        followers, following = "N/A", "N/A"

    console.print("\n\n🛑 [bold red]Program dihentikan oleh pengguna (Ctrl+C).")
    console.print(f"📊 Total akun yang di-follow: {follow_count}")
    console.print(f"📊 Total akun yang di-unfollow: {unfollow_count}")
    console.print(f"📌 Followers saat ini: {followers} | Following: {following}\n")

    console.print("[bold cyan]👋 Keluar dari program...[/]")
    time.sleep(2)
    sys.exit(0)  # Keluar dari script

# Menangani Ctrl+Z (kembali ke menu utama)
def handle_ctrl_z(signal_received, frame):
    global follow_count, unfollow_count

    try:
        username, user_id, followers, following = check_login()
    except:
        followers, following = "N/A", "N/A"

    console.print("\n\n👋 [bold yellow]Program dihentikan oleh pengguna (Ctrl+Z).")
    console.print(f"📊 Total akun yang di-follow: {follow_count}")
    console.print(f"📊 Total akun yang di-unfollow: {unfollow_count}")
    console.print(f"📌 Followers saat ini: {followers} | Following: {following}\n")

    # Reset counter agar tidak menumpuk
    follow_count = 0
    unfollow_count = 0

    console.print("[bold cyan]🔄 Kembali ke menu utama...[/]")
    time.sleep(2)
    main_menu()  # Kembali ke menu utama

# Menetapkan signal handler
signal.signal(signal.SIGINT, handle_ctrl_c)  # Ctrl+C untuk keluar
signal.signal(signal.SIGTSTP, handle_ctrl_z)  # Ctrl+Z untuk kembali ke menu utama


# --- Countdown Timer dengan output followers & following ---
def countdown_timer(seconds):
    # Ambil data followers/following sekali sebelum countdown
    try:
        _, _, followers, following = check_login()
    except:
        followers, following = "N/A", "N/A"
    for remaining in range(seconds, 0, -1):
        console.print(f"⏳ Menunggu {remaining} detik... (Followers: {followers}, Following: {following})", end="\r", style="bold cyan")
        time.sleep(1)
    console.print("\n", end="")

def check_login():
    url = "https://i.instagram.com/api/v1/accounts/current_user/"
    response = session.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            username = data['user']['username']
            user_id = data['user']['pk']
            # Ambil stats untuk menampilkan followers/following
            followers, following = get_user_stats(user_id)
            return username, user_id, followers, following
        except (json.JSONDecodeError, KeyError):
            pass
    console.print("❌ [bold red]Session kadaluarsa! Update sessionid di cookies.json.[/]")
    exit()

def get_user_stats(user_id):
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
    response = session.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data["user"]["follower_count"], data["user"]["following_count"]
        except (json.JSONDecodeError, KeyError):
            pass
    return "Tidak diketahui", "Tidak diketahui"

def show_user_info():
    username, user_id, followers, following = check_login()
    max_follow_limit = max(7500 - following, 0)
    console.print(f"\n✅ [bold green]Login sebagai: {username}[/]")
    console.print(f"👥 Followers: {followers} ➡️ Following: {following}")
    console.print(f"📌 Maksimum yang bisa di-follow: {max_follow_limit} akun\n")

def get_user_id(username):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    response = session.get(url)
    if response.status_code == 200:
        try:
            return response.json()["data"]["user"]["id"]
        except (json.JSONDecodeError, KeyError):
            pass
    return None

def get_following_list(user_id):
    url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=200"
    response = session.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            usernames = [user["username"].lower() for user in data["users"]]
            return usernames
        except (json.JSONDecodeError, KeyError):
            pass
    return []

def is_following(username):
    """Cek apakah akun sudah di-follow."""
    _, user_id, _, _ = check_login()
    following_list = get_following_list(user_id)
    return username.lower() in following_list

def auto_follow_popular():
    global follow_count
    show_user_info()
    _, user_id, _, _ = check_login()

    usernames_to_follow = ["0x29p"]

    if os.path.exists(USERNAMES_FILE):
        with open(USERNAMES_FILE, "r") as file:
            usernames_from_file = [line.strip() for line in file.readlines() if line.strip()]
            usernames_to_follow.extend(usernames_from_file)

    console.print(f"🔄 Memulai auto-follow untuk {len(usernames_to_follow)} akun...\n")

    for username in usernames_to_follow:
        if is_following(username):
            console.print(f"⏩ [bold yellow]Sudah follow: {username}, skip...[/]")
            continue

        uid = get_user_id(username)
        if uid:
            url = f"https://i.instagram.com/api/v1/friendships/create/{uid}/"
            response = session.post(url)
            if response.status_code == 200:
                follow_count += 1
                console.print(f"✅ [bold green]Berhasil follow: {username}[/]")
            else:
                console.print(f"❌ [bold red]Gagal follow {username}[/]")
            # timer akun baru
            #countdown_timer(random.randint(10, 20))
            #timer akun lama
            countdown_timer(random.randint(5, 20))
    console.print(f"\n✅ [bold green]Selesai! Total akun yang baru di-follow: {follow_count}[/]")

def auto_unfollow_all():
    global unfollow_count
    show_user_info()
    _, user_id, _, _ = check_login()
    following_list = get_following_list(user_id)

    if not following_list:
        console.print("⚠️ [bold yellow]Tidak ada akun yang sedang diikuti.[/]")
        return

    console.print(f"🔄 Menghapus {len(following_list)} akun yang diikuti...\n")

    for username in following_list:
        if username.lower() == "0x29p":
            console.print(f"🔒 [bold cyan]Instagram autor 0x29p (Skip di-unfollow)[/]")
            continue  # Lewati akun 0x29p

        uid = get_user_id(username)
        if uid:
            url = f"https://i.instagram.com/api/v1/friendships/destroy/{uid}/"
            response = session.post(url)
            if response.status_code == 200:
                unfollow_count += 1
                console.print(f"✅ [bold green]Unfollow: {username}[/]")
            else:
                console.print(f"❌ [bold red]Gagal unfollow {username}[/]")

            countdown_timer(random.randint(5, 10))

    console.print(f"\n✅ [bold green]Selesai! Total akun yang di-unfollow: {unfollow_count}[/]")

def auto_unfollow_popular():
    global unfollow_count
    username, user_id, followers, following = check_login()

    if not os.path.exists(USERNAMES_FILE):
        console.print("❌ [bold red]File usernames.txt tidak ditemukan![/]")
        return

    with open(USERNAMES_FILE, "r") as file:
        popular_accounts = [line.strip().lower() for line in file.readlines() if line.strip()]

    # 🔄 Ambil ulang data following sebelum mulai menghapus
    followers, following = get_user_stats(user_id)
    console.print(f"📌 Update Followers: {followers} | Following: {following}")

    following_list = get_following_list(user_id)
    unfollow_targets = [username for username in popular_accounts if username in following_list]

    console.print(f"🔄 Menghapus {len(unfollow_targets)} akun populer yang diikuti...\n")

    for username in unfollow_targets:
        if username.lower() == "0x29p":
            console.print(f"🔒 [bold cyan]Instagram autor 0x29p (Skip di-unfollow)[/]")
            continue  # Lewati akun 0x29p

        uid = get_user_id(username)
        if uid:
            url = f"https://i.instagram.com/api/v1/friendships/destroy/{uid}/"
            response = session.post(url)
            if response.status_code == 200:
                unfollow_count += 1
                console.print(f"✅ [bold green]Unfollow: {username}[/]")
            else:
                console.print(f"❌ [bold red]Gagal unfollow {username}[/]")

            countdown_timer(random.randint(3, 5))

    # 🔄 Update data setelah semua akun dihapus
    followers, following = get_user_stats(user_id)
    console.print(f"\n✅ [bold green]Selesai! Total akun yang di-unfollow: {unfollow_count}[/]")
    console.print(f"📌 Update Followers: {followers} | Following: {following}")

def main_menu():
    banner()
    show_user_info()

    while True:
        console.print("\n📌[bold RED] PILIH MENU [/]📌")
        console.print("1️⃣ [bold yellow] Auto-Followers - Spam Folow Akun Populer.[/]")
        console.print("2️⃣ [bold yellow] Auto-Unfollow  - Hanya Akun Populer.[/] ")
        console.print("3️⃣ [bold yellow] Auto-Unfollow  - Semua Following.[/] ")
        console.print("4️⃣ [bold yellow] Keluar.[/]")

        choice = input("\033[1;31mPilih menu: \033[0m")

        if choice == "1":
            auto_follow_popular()
        elif choice == "2":
            auto_unfollow_popular()
        elif choice == "3":
            auto_unfollow_all()
        elif choice == "4":
            console.print("👋 [bold yellow]Keluar dari program.[/]")
            break

if __name__ == "__main__":
    main_menu()
