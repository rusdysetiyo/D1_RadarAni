import json
import requests
import time
import os

# --- PENGATURAN PATH OTOMATIS ---
# Karena script ini ada di dalem folder 'scripts', kita mundur 1 folder ke belakang buat masuk ke 'data'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FILE_JSON = os.path.join(DATA_DIR, "anime_list.json")


def suntik_gambar_hd():
    print(f"[*] Membaca file database: {FILE_JSON}")
    try:
        with open(FILE_JSON, 'r', encoding='utf-8') as f:
            data_anime = json.load(f)
    except FileNotFoundError:
        print("[-] File JSON gak ketemu bang! Cek path-nya lagi.")
        return

    print(f"[*] Total ada {len(data_anime)} anime. Mulai nyari gambar HD...")

    for anime in data_anime:
        mal_id = anime.get('mal_id')

        # Kalau udah punya cover_url_hd, skip aja biar cepet kalau mau dilanjutin nanti
        if not mal_id or 'cover_url_hd' in anime:
            continue

        print(f"  -> Ngecek {anime['title'][:30]}...")
        url_jikan = f"https://api.jikan.moe/v4/anime/{mal_id}"

        try:
            response = requests.get(url_jikan)
            if response.status_code == 200:
                data_jikan = response.json()
                # Ambil URL gambar ukuran L (Large)
                gambar_hd = data_jikan['data']['images']['jpg']['large_image_url']

                # Bikin key baru di JSON lu
                anime['cover_url_hd'] = gambar_hd
                print(f"     [+] Dapet link HD: {gambar_hd}")
            else:
                print(f"     [-] Gagal dapet. Status: {response.status_code}")
        except Exception as e:
            print(f"     [!] Error koneksi: {e}")

        # WAJIB KASIH JEDA 1 DETIK BIAR GAK DIBLOKIR JIKAN API (MAL)!
        time.sleep(1.2)

        # Tiap dapet 1, langsung save aja buat jaga-jaga kalau internet mati
        with open(FILE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data_anime, f, indent=4, ensure_ascii=False)

    print("\n[+] MANTAP BANG! Semua link gambar HD udah kesimpen di anime_list.json!")


if __name__ == "__main__":
    suntik_gambar_hd()