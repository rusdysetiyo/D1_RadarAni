import json
import requests
import time
import os

# --- PENGATURAN PATH OTOMATIS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
ASSETS_DIR = os.path.join(BASE_DIR, "..", "assets")
# KITA BIKIN FOLDER BARU KHUSUS BANNER SULTAN
BANNERS_DIR = os.path.join(ASSETS_DIR, "banners")

FILE_JSON = os.path.join(DATA_DIR, "anime_list.json")


def download_banner_sultan():
    if not os.path.exists(BANNERS_DIR):
        os.makedirs(BANNERS_DIR)

    print(f"[*] Membaca database: {FILE_JSON}")
    try:
        with open(FILE_JSON, 'r', encoding='utf-8') as f:
            data_anime = json.load(f)
    except FileNotFoundError:
        print("[-] File JSON gak ketemu bang!")
        return

    print(f"[*] Total ada {len(data_anime)} anime. Mulai berburu Banner HD...")

    # Query GraphQL buat Anilist
    query = '''
    query ($idMal: Int) {
      Media (idMal: $idMal, type: ANIME) {
        bannerImage
      }
    }
    '''

    for anime in data_anime:
        mal_id = anime.get('mal_id')
        anime_id = anime.get('anime_id')

        # Skip kalau ga ada mal_id atau udah punya banner
        if not mal_id or 'banner_path' in anime:
            continue

        nama_file = f"{anime_id}_BANNER.jpg"
        path_simpan_absolut = os.path.join(BANNERS_DIR, nama_file)
        path_di_json = f"assets/banners/{nama_file}"

        print(f"  -> Nyari banner buat {anime['title'][:30]}...")

        # Nembak Anilist API
        url_anilist = 'https://graphql.anilist.co'
        variables = {'idMal': mal_id}

        try:
            response = requests.post(url_anilist, json={'query': query, 'variables': variables})
            if response.status_code == 200:
                data_anilist = response.json()
                media = data_anilist.get('data', {}).get('Media')

                if media and media.get('bannerImage'):
                    banner_url = media['bannerImage']
                    print(f"     [+] Wih dapet banner gede! Downloading...")

                    # Download bannernya
                    img_response = requests.get(banner_url, stream=True)
                    if img_response.status_code == 200:
                        with open(path_simpan_absolut, 'wb') as img_file:
                            for chunk in img_response.iter_content(1024):
                                img_file.write(chunk)

                        anime['banner_path'] = path_di_json
                        print(f"     [+] Berhasil disave di {path_di_json}")
                    else:
                        print("     [-] Gagal download bannernya.")
                else:
                    print("     [-] Sedih bang, Anilist gak punya banner buat anime ini.")
                    # Biar gak dilooping terus kalau emang kosong, kita kasih flag kosong
                    anime['banner_path'] = ""
            elif response.status_code == 429:
                print("     [!] Kena Limit! Istirahat bentar 5 detik...")
                time.sleep(5)
                continue
            else:
                print(f"     [-] Gagal API Anilist. Status: {response.status_code}")

        except Exception as e:
            print(f"     [!] Error koneksi: {e}")

        # Jeda biar ga diblokir Anilist (Rate limitnya sekitar 90 per menit)
        time.sleep(1)

        # Auto save
        with open(FILE_JSON, 'w', encoding='utf-8') as f:
            json.dump(data_anime, f, indent=4, ensure_ascii=False)

    print("\n[+] KELAR! Coba lu cek folder assets/banners sekarang, sizenya pasti mantap!")


if __name__ == "__main__":
    download_banner_sultan()