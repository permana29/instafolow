# Insta Follow Bot

![Insta Follow](https://github.com/permana29/instafolow/blob/main/Screenshot_20250325_105124.jpg) 

## 📌 Tentang

**Insta Follow Bot** adalah skrip otomatisasi untuk menambah dan menghapus pengikut di Instagram menggunakan sesi login yang valid. Skrip ini memungkinkan pengguna untuk:

✅ Auto-follow akun populer  
✅ Auto-unfollow semua akun yang diikuti  
✅ Menampilkan jumlah pengikut dan akun yang diikuti  

**⚠️ PERHATIAN**  
Gunakan dengan bijak! Jangan menyalahgunakan fitur ini untuk spam atau aktivitas yang melanggar kebijakan Instagram.

---

## 📂 Struktur Repositori
📂 insta.py │── Skrip utama bot 

📂 usernames.txt │── Daftar username populer untuk di-follow

📂 cookies.json │── File sesi login Instagram

---

## 🚀 Instalasi di Android

1. **Unduh & Instal Termux**  
   Jika belum memiliki Termux, unduh dari [F-Droid](https://f-droid.org/en/packages/com.termux/) atau Play Store.

2. **Instal Python & Dependensi**  
   ```bash
   pkg update && pkg upgrade
   pkg install python
   pip install requests rich

3. Clone Repository & Masuk ke Direktori :
```bash
git clone (https://github.com/permana29/instafolow.git)
cd insta-follow-bot

4. Tambahkan cookies.json
Gunakan Kiwi Browser dengan Developer Tools untuk mendapatkan csrftoken, ds_user_id, dan sessionid:

Buka instagram.com di Kiwi Browser.

Login ke akun Instagram Anda.

Buka Developer Tools (Inspect Element).

Pergi ke Application → Storage → Cookies → www.instagram.com.

Salin nilai csrftoken, ds_user_id, dan sessionid.

Buat file cookies.json dan isi seperti berikut:

{
  "csrftoken": "isi_dengan_csrftoken",
  "ds_user_id": "isi_dengan_ds_user_id",
  "sessionid": "isi_dengan_sessionid"
}
