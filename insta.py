import requests
import json
import os
import time
import random
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

if os.path.exists(COOKIES_FILE):
    with open(COOKIES_FILE, "r") as file:
        COOKIES = json.load(file)
else:
    print("❌ Cookies tidak ditemukan! Harap masukkan sessionid secara manual.")
    exit()

SESSION_ID = COOKIES.get("sessionid")
CSRF_TOKEN = COOKIES.get("csrftoken", "")

if not SESSION_ID:
    print("❌ Session ID tidak ditemukan dalam cookies.json! Pastikan valid.")
    exit()

HEADERS = {
    "User-Agent": "Instagram 320.0.0.12 Android (30/9; 480dpi; 1080x1920; Samsung; SM-G991B; o1s; qcom; en_US)",
    "Referer": "https://www.instagram.com/",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "X-CSRFToken": CSRF_TOKEN,
    "X-IG-App-ID": "936619743392459",
}

session = requests.Session()
session.cookies.set("sessionid", SESSION_ID, domain=".instagram.com")
session.headers.update(HEADERS)

def countdown_timer(seconds):
    """Menampilkan hitungan mundur sebelum eksekusi berikutnya."""
    for remaining in range(seconds, 0, -1):
        console.print(f"⏳ Menunggu {remaining} detik sebelum lanjut...", end="\r", style="bold cyan")
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
            followers = get_followers_count(user_id)
            following = get_following_count(user_id)
            
            return username, user_id, followers, following
        except (json.JSONDecodeError, KeyError):
            pass

    print("❌ Session kadaluarsa! Update sessionid di cookies.json.")
    return None, None, None, None

def get_followers_count(user_id):
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
    response = session.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data["user"]["follower_count"]
        except (json.JSONDecodeError, KeyError):
            return "Tidak diketahui"
    return "Gagal mengambil data"

def get_following_count(user_id):
    url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
    response = session.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return data["user"]["following_count"]
        except (json.JSONDecodeError, KeyError):
            return "Tidak diketahui"
    return "Gagal mengambil data"

def get_user_id(username):
    url = f"https://i.instagram.com/api/v1/users/web_profile_info/?username={username}"
    response = session.get(url)

    if response.status_code == 200:
        try:
            data = response.json()
            return data["data"]["user"]["id"]
        except (json.JSONDecodeError, KeyError):
            print(f"❌ Gagal mendapatkan user ID untuk: {username}")
    return None

def show_max_follow_limit(username, user_id, followers, following):
    max_follow_limit = max(7500 - following, 0)  # Instagram membatasi 7500 following

    print(f"\n✅ Login sebagai: {username}")  
    print(f"👥 Followers: {followers} ➡️ Following: {following}")  
    print(f"📌 Maksimum yang bisa di-follow: {max_follow_limit} akun\n")

def auto_follow_popular():
    if not os.path.exists(USERNAMES_FILE):
        print("❌ File usernames.txt tidak ditemukan! Harap buat file terlebih dahulu.")
        return

    with open(USERNAMES_FILE, "r") as file:
        popular_accounts = [line.strip() for line in file.readlines() if line.strip()]

    print(f"🔄 Memulai auto-follow untuk {len(popular_accounts)} akun populer...")

    followed = 0
    already_followed = 0

    for username in popular_accounts:
        user_id = get_user_id(username)
        if user_id:
            # Mengecek apakah sudah di-follow sebelumnya
            check_url = f"https://i.instagram.com/api/v1/friendships/show/{user_id}/"
            check_response = session.get(check_url)

            if check_response.status_code == 200:
                try:
                    check_data = check_response.json()
                    if check_data.get("following"):
                        print(f"✅ Sudah ada di folowers: {username}")
                        already_followed += 1
                        continue
                except json.JSONDecodeError:
                    pass

            # Jika belum di-follow, maka follow akun
            url = f"https://i.instagram.com/api/v1/friendships/create/{user_id}/"
            response = session.post(url)

            if response.status_code == 200:
                print(f"✅ Berhasil follow: {username}")
                followed += 1
            else:
                error_message = response.json().get("message", "Gagal follow akun ini.")
                print(f"❌ Gagal follow {username}: {error_message}")

            # Menunggu dengan countdown
            countdown_timer(random.randint(2, 10))  # Hindari spam

    print(f"\n🎉 Selesai! Total {followed} akun baru di-follow, {already_followed} akun sudah di-follow sebelumnya.")

def get_following_list(user_id):
    url = f"https://i.instagram.com/api/v1/friendships/{user_id}/following/?count=200"
    response = session.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            return [user["username"] for user in data["users"]]
        except (json.JSONDecodeError, KeyError):
            return []
    return []

def unfollow_all():
    username, user_id, _, following = check_login()
    if not username:
        return

    following_list = get_following_list(user_id)
    total_following = len(following_list)

    if total_following == 0:
        print("⚠️ Tidak ada akun yang sedang diikuti.")
        return

    print(f"🔍 Mengambil daftar following... Total: {total_following} akun")

    try:
        num_unfollow = int(input(f"Masukkan jumlah unfollow (Maks {total_following}): "))
    except ValueError:
        print("❌ Input tidak valid! Masukkan angka.")
        return

    if num_unfollow > total_following:
        print(f"⚠️ Jumlah terlalu banyak, akan meng-unfollow semua akun yang tersedia.")
        num_unfollow = total_following

    unfollowed = 0
    for username in following_list[:num_unfollow]:
        user_id = get_user_id(username)
        if user_id:
            url = f"https://i.instagram.com/api/v1/friendships/destroy/{user_id}/"
            response = session.post(url)
            if response.status_code == 200:
                print(f"✅ Berhasil unfollow: {username}")
                unfollowed += 1
            else:
                print(f"❌ Gagal unfollow {username}: Terlalu banyak permintaan, coba lagi nanti.")

        # Menunggu dengan countdown
        countdown_timer(random.randint(2, 10))  # Hindari spam

    print(f"🎉 Selesai! Total {unfollowed} akun telah di-unfollow.")

def main_menu():
    banner()
    username, user_id, followers, following = check_login()
    if not username:
        exit()

    show_max_follow_limit(username, user_id, followers, following)  # Menampilkan jumlah maksimum yang bisa di-follow

    while True:
        print("\n📌 PILIH MENU 📌")
        print("1️⃣ Auto-Follow Akun Populer")
        print("2️⃣ Auto-Unfollow Semua Following")
        print("3️⃣ Keluar")

        choice = input("Pilih menu: ")

        if choice == "1":
            auto_follow_popular()
        elif choice == "2":
            unfollow_all()
        elif choice == "3":
            print("👋 Keluar dari program. Sampai jumpa lagi!")
            break

if __name__ == "__main__":
    main_menu()
