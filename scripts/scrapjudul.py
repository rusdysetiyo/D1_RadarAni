import os
import time
import urllib.parse

import requests
from PIL import Image
from scripts.scraper import RadarAniScraper
from scripts.userScraper import generate_5d_scores
from src.managers.data_manager import DataManager

# Domain unik untuk URL anime MAL yang valid
_MAL_ANIME_DOMAIN = "myanimelist.net/anime/"


class DynamicAnimeScraper(RadarAniScraper):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()

    def _generate_next_anime_id(self):
        semua_anime = self.data_manager._read_json(self.data_manager.anime_file) or []
        if not semua_anime:
            return 1

        angka_id = [
            int(anime["anime_id"][1:]) for anime in semua_anime
            if anime.get("anime_id", "").startswith("A") and anime["anime_id"][1:].isdigit()
        ]
        return max(angka_id) + 1 if angka_id else 1

    def _cek_duplikasi(self, mal_id):
        semua_anime = self.data_manager._read_json(self.data_manager.anime_file) or []
        for anime in semua_anime:
            if anime.get("mal_id") == mal_id:
                return True, anime.get("title")
        return False, None

    def parse_anime_details(self, detail_url, counter):
        anime_data = super().parse_anime_details(detail_url, counter)
        if not anime_data:
            return None

        soup = self.get_soup(detail_url)
        if soup:
            try:
                anime_data["mal_id"] = int(detail_url.split('/')[4])
            except (IndexError, ValueError):
                anime_data["mal_id"] = None

        return anime_data

    def buat_thumbnail_lokal(self, cover_rel_path, id_number):
        """Membaca cover besar, mengubah ukurannya ke 100x140, dan menyimpannya sebagai thumbnail."""
        if not cover_rel_path or cover_rel_path == "N/A":
            return "N/A"

        # Ambil path fisik dari cover yang baru saja diunduh
        # Sesuaikan 'self.root_dir' dengan nama variabel yang Anda gunakan di class induk
        cover_abs_path = os.path.join(self.root_dir, cover_rel_path)

        thumb_filename = f"TIMG{id_number:03d}.jpg"
        thumb_abs_path = os.path.join(self.thumb_dir, thumb_filename)

        try:
            with Image.open(cover_abs_path) as img:
                # Konversi ke RGB untuk mencegah error jika aslinya PNG transparan
                img = img.convert("RGB")

                # Menggunakan LANCZOS untuk kualitas downscaling/kompresi terbaik
                img_resized = img.resize((100, 140), Image.Resampling.LANCZOS)

                # Simpan dengan kualitas 85 (cukup baik untuk thumbnail kecil)
                img_resized.save(thumb_abs_path, "JPEG", quality=85)

            # Kembalikan path relatif untuk disimpan di JSON
            return os.path.relpath(thumb_abs_path, self.root_dir).replace("\\", "/")

        except Exception as e:
            print(f"[!] Gagal membuat thumbnail lokal: {e}")
            return cover_rel_path  # Fallback: pakai path cover asli jika gagal

    # ------------------------------------------------------------------ #
    #  Validasi & Klasifikasi Input                                        #
    # ------------------------------------------------------------------ #

    @staticmethod
    def validasi_input(query: str) -> None:
        """
        Memvalidasi input pengguna sebelum pencarian dilakukan.
        Raise ValueError dengan pesan informatif jika input tidak valid.
        """
        # Tolak HTML mentah
        if "<" in query and ">" in query:
            raise ValueError(
                "Input tidak valid: terdeteksi konten HTML. "
                "Masukkan judul anime atau URL MyAnimeList yang valid."
            )

        is_url = query.lower().startswith("http://") or query.lower().startswith("https://")

        # Tolak URL yang bukan dari domain MAL
        if is_url and _MAL_ANIME_DOMAIN not in query:
            raise ValueError(
                "URL tidak valid. Harap masukkan URL detail anime dari MyAnimeList, "
                "contoh: https://myanimelist.net/anime/20"
            )

        # Tolak teks terlalu pendek (hanya berlaku untuk pencarian judul, bukan URL)
        if not is_url and len(query) < 3:
            raise ValueError(
                "Input minimal 3 karakter. "
                "Jika judul memang sangat pendek, harap gunakan URL MyAnimeList."
            )

    @staticmethod
    def is_mal_anime_url(query: str) -> bool:
        """Mengembalikan True jika query adalah URL anime MAL."""
        return _MAL_ANIME_DOMAIN in query

    # ------------------------------------------------------------------ #
    #  Pencarian                                                           #
    # ------------------------------------------------------------------ #

    def cari_dari_url(self, url: str) -> tuple:
        """
        Mencari info anime dari URL MAL.
        Normalisasi URL → ekstrak mal_id → cek duplikasi → ambil info halaman.

        Returns:
            (judul: str, thumb_url: str | None, is_duplicate: bool, normalized_url: str)

        Raises:
            ValueError      — jika format URL tidak dapat diparsing
            ConnectionError — jika halaman MAL gagal dimuat
        """
        normalized_url = self.normalize_mal_url(url)

        parts = normalized_url.split("/")
        # Struktur: ['https:', '', 'myanimelist.net', 'anime', '<id>', ...]
        if len(parts) < 5 or not parts[4].isdigit():
            raise ValueError(
                "Format URL MAL tidak valid — ID anime tidak ditemukan. "
                "Contoh yang benar: https://myanimelist.net/anime/20"
            )

        mal_id = int(parts[4])
        is_duplicate, _ = self._cek_duplikasi(mal_id)
        judul, thumb_url = self.dapatkan_info_dari_url(normalized_url)

        return judul, thumb_url, is_duplicate, normalized_url

    def dapatkan_kandidat_judul(self, judul_input: str) -> list:
        """
        Mencari daftar kandidat anime di MAL berdasarkan judul.

        Returns:
            list of (judul, url, thumb_url)  — bisa kosong jika tidak ada hasil.

        Raises:
            ConnectionError — jika gagal terhubung ke server MAL.
        """
        query_aman = urllib.parse.quote(judul_input)
        search_url = f"https://myanimelist.net/anime.php?q={query_aman}&cat=anime"

        soup = self.get_soup(search_url)
        if not soup:
            raise ConnectionError(
                "Gagal terhubung ke MyAnimeList. "
                "Periksa koneksi internet Anda atau coba lagi nanti."
            )

        hasil_tr = soup.find_all('tr')
        kandidat_list = []

        for row in hasil_tr:
            a_tag = row.find('a', class_='hoverinfo_trigger fw-b fl-l')
            if not a_tag:
                continue

            judul_kandidat = a_tag.get_text(strip=True)
            url_kandidat = a_tag['href']

            img_tag = row.find('img')
            thumb_url = ""
            if img_tag:
                thumb_url = img_tag.get('data-srcset') or img_tag.get('srcset') or img_tag.get('data-src') or img_tag.get('src')
                if thumb_url and '2x' in thumb_url:
                    thumb_url = thumb_url.split(',')[-1].replace('2x', '').strip()
                elif thumb_url and '1x' in thumb_url:
                    thumb_url = thumb_url.split(',')[0].replace('1x', '').strip()

            kandidat_list.append((judul_kandidat, url_kandidat, thumb_url))
            if len(kandidat_list) >= 10:
                break

        return kandidat_list

    @staticmethod
    def normalize_mal_url(url):
        """
        Memotong sub-tab MAL dari URL anime.
        """
        SUB_TABS = {
            "moreinfo", "pics", "clubs", "forum", "news",
            "stacks", "userrecs", "reviews", "stats",
            "video", "episode", "characters",
        }
        # Buang query string dan fragment terlebih dahulu
        clean = url.split('?')[0].split('#')[0].rstrip('/')
        parts = clean.split('/')
        # Struktur: ['https:', '', 'myanimelist.net', 'anime', '<id>', '<judul>', '<sub_tab?>']
        # Index 6 (jika ada) adalah kandidat sub-tab
        if len(parts) >= 7 and parts[6].lower() in SUB_TABS:
            parts = parts[:6]  # buang sub-tab
        return '/'.join(parts)

    def dapatkan_info_dari_url(self, url: str) -> tuple:
        """
        Mengambil judul dan URL thumbnail dari halaman detail anime MAL.

        Returns:
            (judul: str, thumb_url: str | None)

        Raises:
            ConnectionError — jika halaman gagal dimuat (network error / diblokir).
        """
        soup = self.get_soup(url)
        if not soup:
            raise ConnectionError(
                "Gagal memuat halaman MAL. Periksa koneksi internet Anda "
                "atau coba lagi beberapa saat kemudian."
            )

        judul = "N/A"
        title_container = soup.find('div', itemprop='name')
        if title_container:
            h1 = title_container.find('h1', class_='title-name')
            if h1:
                judul = h1.get_text(strip=True)

        thumb_url = None
        cover_tag = soup.find('img', itemprop='image')
        if cover_tag:
            cover_url = cover_tag.get('data-src') or cover_tag.get('src')
            thumb_url = self._cover_to_thumb_url(cover_url)

        return judul, thumb_url

    def cari_dan_validasi_judul(self, judul_input):
        print(f"\n[*] Mencari '{judul_input}' di MyAnimeList...")
        kandidat_list = self.dapatkan_kandidat_judul(judul_input)

        if not kandidat_list:
            print("[-] Tidak ada hasil yang ditemukan.")
            return None

        for idx, kandidat in enumerate(kandidat_list, 1):
            print(f"    {idx}. {kandidat[0]}")

        print("    0. Tidak ada yang cocok (Batal)")

        while True:
            try:
                pilihan = int(input(f"\nMasukkan angka pilihan (0-{len(kandidat_list)}): "))

                if pilihan == 0:
                    print("[-] Scraping dibatalkan.")
                    return None
                elif 1 <= pilihan <= len(kandidat_list):
                    terpilih = kandidat_list[pilihan - 1]
                    print(f"[+] Anda memilih: {terpilih[0]}")
                    return terpilih[1], terpilih[2]  # Mengembalikan URL Detail DAN URL Thumbnail
                else:
                    print("[!] Pilihan di luar jangkauan. Silakan coba lagi.")
            except ValueError:
                print("[!] Harap masukkan angka yang valid.")

    def _cover_to_thumb_url(self, cover_url):
        if not cover_url:
            return None
        if 'cdn.myanimelist.net/images/' in cover_url:
            return cover_url.replace(
                'cdn.myanimelist.net/images/',
                'cdn.myanimelist.net/r/96x136/images/'
            )
        return cover_url

    def _injeksi_rating_awal(self, anime_id, global_score, genres):
        """
        Menginjeksikan rating dari 10 user pertama (U001–U010) ke anime yang baru
        ditambahkan. Hanya dijalankan jika anime memiliki skor MAL yang valid (> 0).
        Rating 5 dimensi dihasilkan via algoritma generate_5d_scores dan disimpan
        melalui DataManager.simpan_rating() agar cache stats terupdate otomatis.
        """
        if global_score <= 0:
            print("[~] Skor MAL N/A — injeksi rating dilewati.")
            return

        semua_users = self.data_manager._read_json(self.data_manager.users_file) or []
        # Ambil user U001–U010 (10 penilai pertama)
        target_users = [u for u in semua_users if u.get("user_id", "") in
                        {f"U{i:03d}" for i in range(1, 11)}]

        if not target_users:
            print("[!] Tidak ada user U001–U010 ditemukan, injeksi rating dilewati.")
            return

        print(f"[*] Menginjeksikan rating dari {len(target_users)} user ke '{anime_id}'...")
        for user in target_users:
            user_id = user["user_id"]
            skor_5d = generate_5d_scores(
                mal_score=0,          # mal_score 0 → pakai global_score sebagai base
                global_score=global_score,
                anime_genres=genres
            )
            self.data_manager.simpan_rating(user_id, anime_id, skor_5d)
            print(f"    [+] {user_id}: plot={skor_5d['plot']} visual={skor_5d['visual']} "
                  f"audio={skor_5d['audio']} char={skor_5d['characterization']} dir={skor_5d['direction']}")

        print(f"[+] Injeksi rating selesai untuk '{anime_id}'.")

    def _fetch_banner_from_anilist(self, mal_id, anime_id) -> str:
        if not mal_id:
            return ""
        query = '''
        query ($idMal: Int) {
          Media (idMal: $idMal, type: ANIME) {
            bannerImage
          }
        }
        '''
        try:
            response = requests.post(
                'https://graphql.anilist.co',
                json={'query': query, 'variables': {'idMal': mal_id}},
                timeout=10
            )
            if response.status_code == 429:
                print("[!] Rate limit Anilist, tunggu 5 detik...")
                time.sleep(5)
                return ""
            if response.status_code == 200:
                media = response.json().get('data', {}).get('Media')
                if media and media.get('bannerImage'):
                    return self.download_image(media['bannerImage'], self.banner_dir, f"{anime_id}_BANNER.jpg")
        except Exception as e:
            print(f"[!] Gagal fetch banner Anilist: {e}")
        return ""

    def eksekusi_tambah_anime(self, url: str, thumb_url: str | None = None) -> dict:
        """
        Mengekstraksi data, mengecek duplikasi, dan menyimpan ke database.

        Returns:
            dict — data anime yang berhasil ditambahkan.

        Raises:
            ValueError      — URL tidak valid atau anime sudah ada di database.
            RuntimeError    — gagal mengekstraksi data dari halaman MAL.
            ConnectionError — gagal terhubung ke MAL (diteruskan dari parse_anime_details).
        """
        try:
            mal_id = int(url.split('/')[4])
        except (IndexError, ValueError):
            raise ValueError(
                "URL tidak valid — tidak dapat menemukan MAL ID. "
                "Contoh URL yang benar: https://myanimelist.net/anime/20"
            )

        is_duplicate, judul_terdaftar = self._cek_duplikasi(mal_id)
        if is_duplicate:
            raise ValueError(
                f"Anime sudah ada di database dengan judul: '{judul_terdaftar}'"
            )

        print("[*] Mengekstraksi data anime dari halaman detail...")
        next_id_number = self._generate_next_anime_id()

        anime_data = self.parse_anime_details(url, next_id_number)

        if not anime_data:
            raise RuntimeError(
                "Gagal mengekstraksi data dari halaman MAL. Periksa koneksi anda. "
                "Halaman mungkin tidak dapat diakses atau strukturnya berubah."
            )

        # Penanganan thumbnail
        if thumb_url:
            path_thumb = self.download_image(thumb_url, self.thumb_dir, f"TIMG{next_id_number:03d}.jpg")
            anime_data["thumbnail_path"] = path_thumb
        elif anime_data.get("cover_path") and anime_data["cover_path"] != "N/A":
            print("[*] Membuat thumbnail 100x140 dari gambar cover...")
            path_thumb = self.buat_thumbnail_lokal(anime_data["cover_path"], next_id_number)
            anime_data["thumbnail_path"] = path_thumb
        else:
            anime_data["thumbnail_path"] = "N/A"
        print("[*] Mencari banner dari Anilist...")
        time.sleep(1)
        banner_path = self._fetch_banner_from_anilist(anime_data.get("mal_id"), anime_data["anime_id"])
        anime_data["banner_path"] = banner_path
        if banner_path:
            print(f"[+] Banner didapat: {banner_path}")
        else:
            print("[-] Banner tidak tersedia di Anilist.")
        # Pastikan field cache rating ada sebelum disimpan
        anime_data.setdefault("rating_count", 0)
        anime_data.setdefault("global_score_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])

        print("[*] Menyimpan ke database...")
        semua_anime = self.data_manager._read_json(self.data_manager.anime_file) or []
        semua_anime.append(anime_data)
        self.data_manager._write_json(self.data_manager.anime_file, semua_anime)

        print(f"[+] SUKSES! '{anime_data['title']}' berhasil ditambahkan dengan ID {anime_data['anime_id']}.")

        # Injeksi rating dari 10 user pertama jika skor MAL valid
        self._injeksi_rating_awal(
            anime_id=anime_data["anime_id"],
            global_score=anime_data.get("global_score", 0.0),
            genres=anime_data.get("genre", [])
        )

        return anime_data


def run_terminal_interface():
    scraper = DynamicAnimeScraper()

    print("=========================================")
    print("   RADARANI - TAMBAH ANIME ON-DEMAND     ")
    print("=========================================")

    while True:
        user_input = input("\nMasukkan URL MAL atau Judul Anime (Ketik 'exit' untuk keluar): ").strip()

        if user_input.lower() == 'exit':
            break

        if not user_input:
            continue

        target_url = None
        target_thumb_url = None

        if "http" in user_input:
            if "myanimelist.net/anime/" in user_input:
                target_url = DynamicAnimeScraper.normalize_mal_url(user_input)
                if target_url != user_input:
                    print(f"[~] URL dinormalisasi ke: {target_url}")
                # Karena input URL langsung, kita biarkan thumb_url None (nanti fallback ke cover)
            else:
                print("[!] URL tidak valid. Harap masukkan URL detail anime dari MyAnimeList.")
                continue
        else:
            if len(user_input) < 3:
                print("[!] Judul terlalu pendek. Masukkan minimal 3 karakter.")
                continue
            else:
                hasil_cari = scraper.cari_dan_validasi_judul(user_input)
                if hasil_cari:
                    target_url, target_thumb_url = hasil_cari  # Ekstrak kedua return value

        if target_url:
            scraper.eksekusi_tambah_anime(target_url, target_thumb_url)


if __name__ == "__main__":
    run_terminal_interface()