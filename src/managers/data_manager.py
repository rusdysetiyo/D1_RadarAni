import json
import os
from datetime import datetime
from collections import Counter

class DataManager:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(BASE_DIR, "..", "..", "data")

        self.anime_file = os.path.join(self.data_dir, 'anime_list.json')
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self.ratings_file = os.path.join(self.data_dir, 'ratings.json')
        self.session_file = os.path.join(self.data_dir, 'session.json')

        os.makedirs(self.data_dir, exist_ok=True)
        self._inisialisasi_file_dasar()

    # ==========================================
    # FUNGSI UTILITAS & INISIALISASI
    # ==========================================

    def _inisialisasi_file_dasar(self):
        """Memastikan ketersediaan file JSON dengan struktur data bawaan yang tepat."""
        file_defaults = {
            self.users_file: [],
            self.ratings_file: {},
            self.session_file: {"active_user_id": None}
        }

        for filepath, default_data in file_defaults.items():
            if not os.path.exists(filepath):
                self._write_json(filepath, default_data)

    def _read_json(self, filepath):
        """Membaca dan mengembalikan data dari file JSON. Mengembalikan None jika gagal."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    def _write_json(self, filepath, data):
        """Menimpa data ke dalam file JSON secara aman."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except IOError:
            pass

    # ==========================================
    # MANAJEMEN DATA ANIME (READ-ONLY)
    # ==========================================

    def get_semua_anime(self):
        """Mengembalikan seluruh katalog anime atau list kosong jika tidak tersedia."""
        return self._read_json(self.anime_file) or []

    def get_detail_anime(self, anime_id):
        """Mencari spesifikasi satu anime secara efisien menggunakan generator."""
        semua_anime = self.get_semua_anime()
        return next((anime for anime in semua_anime if anime.get("anime_id") == anime_id), None)

    def cari_anime(self, kata_kunci):
        """
        Mencari anime berdasarkan kata kunci pada judul utama atau judul bahasa Inggris.
        Pencarian bersifat case-insensitive (mengabaikan huruf besar/kecil).
        """
        semua_anime = self.get_semua_anime()

        # Jika kata kunci kosong, kembalikan semua data agar tabel kembali seperti semula
        if not kata_kunci or kata_kunci.strip() == "":
            return semua_anime

        kata_kunci_lower = kata_kunci.strip().lower()
        hasil_pencarian = []

        for anime in semua_anime:
            judul_utama = anime.get("title")
            judul_inggris = anime.get("en_title")

            # Mencegah error AttributeError jika json berisi null (None di Python)
            judul_utama_lower = judul_utama.lower() if judul_utama else ""
            judul_inggris_lower = judul_inggris.lower() if judul_inggris else ""

            # Jika kata kunci ditemukan di salah satu judul, masukkan ke hasil
            if kata_kunci_lower in judul_utama_lower or kata_kunci_lower in judul_inggris_lower:
                hasil_pencarian.append(anime)

        return hasil_pencarian

    # ==========================================
    # MANAJEMEN PENGGUNA (AUTENTIKASI & AKUN)
    # ==========================================

    def cek_username_ada(self, username):
        """Memeriksa eksistensi username secara case-insensitive."""
        users = self._read_json(self.users_file) or []
        return any(user.get("username", "").lower() == username.lower() for user in users)

    def cek_kredensial(self, username, password):
        """Memvalidasi kombinasi username dan password, mengembalikan user_id jika sukses."""
        users = self._read_json(self.users_file) or []

        for user in users:
            if user.get("username", "").lower() == username.lower() and user.get("password") == password:
                return user.get("user_id")

        return None  # Return None jika kombinasi salah

    def update_last_login(self, user_id):
        """Memperbarui waktu login terakhir pengguna ke waktu saat ini."""
        users = self._read_json(self.users_file) or []
        user_found = False

        for user in users:
            if user.get("user_id") == user_id:
                # Menggunakan format ISO 8601 agar seragam dengan fungsi pembuatan akun
                user["last_login"] = datetime.now().isoformat()
                user_found = True
                break

        if user_found:
            self._write_json(self.users_file, users)
            return True

        return False

    def generate_user_id(self):
        """Menghasilkan ID pengguna sekuensial (contoh: U003) berdasarkan data yang ada."""
        users = self._read_json(self.users_file) or []

        angka_id = [
            int(user["user_id"][1:]) for user in users
            if user.get("user_id", "").startswith("U") and user["user_id"][1:].isdigit()
        ]

        angka_tertinggi = max(angka_id) if angka_id else 0
        return f"U{angka_tertinggi + 1:03d}"

    def simpan_user_baru(self, data_user_baru):
        """Mendaftarkan pengguna baru ke database."""
        users = self._read_json(self.users_file) or []
        users.append(data_user_baru)
        self._write_json(self.users_file, users)
        return True

    def hapus_user_dan_rating(self, user_id):
        """Menghapus akun pengguna beserta seluruh data rating terkait (Cascading Delete)."""
        # 1. Membersihkan data dari users.json
        users = self._read_json(self.users_file) or []
        users_baru = [user for user in users if user.get("user_id") != user_id]

        if len(users) == len(users_baru):
            return False  # Target penghapusan tidak ditemukan

        self._write_json(self.users_file, users_baru)

        # 2. Membersihkan laci data di ratings.json
        ratings = self._read_json(self.ratings_file) or {}
        if user_id in ratings:
            del ratings[user_id]
            self._write_json(self.ratings_file, ratings)

        return True

    # ==========================================
    # MANAJEMEN SESI LOKAL
    # ==========================================

    def simpan_sesi(self, user_id):
        """Mencatat ID pengguna agar sesi login bertahan setelah aplikasi ditutup."""
        self._write_json(self.session_file, {"active_user_id": user_id})
        return True

    def baca_sesi(self):
        """Membaca ID pengguna dari sesi lokal yang tersimpan."""
        data = self._read_json(self.session_file) or {}
        return data.get("active_user_id")

    def hapus_sesi(self):
        """Membersihkan memori sesi lokal (Logout)."""
        self._write_json(self.session_file, {"active_user_id": None})
        return True

    # ==========================================
    # MANAJEMEN RATING (CRUD)
    # ==========================================

    def get_rating_user(self, user_id, anime_id):
        """Mengambil skor multidimensi secara instan (Time Complexity O(1))."""
        ratings = self._read_json(self.ratings_file) or {}
        return ratings.get(user_id, {}).get(anime_id)

    def hitung_skor_personal(self, user_id, anime_id):
        """Menghitung rata-rata dari 5 dimensi skor milik satu pengguna untuk satu anime."""
        skor_dict = self.get_rating_user(user_id, anime_id)

        # Jika user belum menilai anime tersebut, kembalikan None
        # Ini akan mempermudah UI (ui_dashboard) untuk memunculkan teks "N/A"
        if not skor_dict:
            return None

        total_skor = sum(skor_dict.values())
        jumlah_dimensi = len(skor_dict)

        return round(total_skor / jumlah_dimensi, 2)

    def simpan_rating(self, user_id, anime_id, skor_dict):
        """Menyimpan atau memperbarui data skor multidimensi."""
        ratings = self._read_json(self.ratings_file) or {}

        # setdefault() secara otomatis membuat dictionary {} untuk user baru jika belum ada
        ratings.setdefault(user_id, {})[anime_id] = skor_dict

        self._write_json(self.ratings_file, ratings)
        return True

    def hapus_rating(self, user_id, anime_id):
        """Mencabut satu data rating spesifik dari pengguna."""
        ratings = self._read_json(self.ratings_file) or {}

        if user_id in ratings and anime_id in ratings[user_id]:
            del ratings[user_id][anime_id]
            self._write_json(self.ratings_file, ratings)
            return True

        return False

    def hitung_skor_global(self, anime_id):
        """Mengakumulasi dan mengalkulasi rata-rata skor keseluruhan untuk satu anime."""
        ratings = self._read_json(self.ratings_file) or {}

        # Mengumpulkan rata-rata skor dari setiap user yang menilai anime ini
        skor_semua_user = [
            sum(anime_dict[anime_id].values()) / len(anime_dict[anime_id])
            for anime_dict in ratings.values()
            if anime_id in anime_dict and anime_dict[anime_id]
        ]

        if not skor_semua_user:
            return 0.0

        return round(sum(skor_semua_user) / len(skor_semua_user), 2)

    # ===========================
    # MANAJEMEN PROFIL & ANALITIK
    # ===========================

    def get_profil_user(self, user_id):
        """Mengambil data profil pengguna (Bio, Favorit, Last Login, dll) tanpa password."""
        users = self._read_json(self.users_file) or []

        for user in users:
            if user.get("user_id") == user_id:
                profil = user.copy()
                # Hapus key 'password' dari dictionary sebelum dikirim ke UI demi keamanan
                profil.pop("password", None)
                return profil

        return None

    def get_avg_dimensi_user(self, user_id):
        """Menghitung rata-rata per dimensi dari SELURUH anime yang dinilai user untuk Bar Chart."""
        ratings = self._read_json(self.ratings_file) or {}
        user_ratings = ratings.get(user_id, {})

        total_anime = len(user_ratings)

        avg_dimensi = {
            "visual": 0.0,
            "plot": 0.0,
            "audio": 0.0,
            "characterization": 0.0,
            "direction": 0.0
        }

        if total_anime == 0:
            return avg_dimensi

        # Akumulasi nilai untuk setiap dimensi
        for skor_dict in user_ratings.values():
            for dimensi, nilai in skor_dict.items():
                if dimensi in avg_dimensi:
                    avg_dimensi[dimensi] += nilai

        for dimensi in avg_dimensi:
            avg_dimensi[dimensi] = round(avg_dimensi[dimensi] / total_anime, 2)

        return avg_dimensi

    def get_top_genre_user(self, user_id):
        """Mencari 5 genre paling banyak ditonton beserta persentasenya untuk Pie Chart."""
        ratings = self._read_json(self.ratings_file) or {}
        user_ratings = ratings.get(user_id, {})

        if not user_ratings:
            return []

        semua_anime = self.get_semua_anime()
        anime_genre_map = {anime.get("anime_id"): anime.get("genre", []) for anime in semua_anime}

        semua_genre_user = []
        for anime_id in user_ratings.keys():
            genres = anime_genre_map.get(anime_id, [])
            semua_genre_user.extend(genres)

        if not semua_genre_user:
            return []

        hitung_genre = Counter(semua_genre_user)
        top_5 = hitung_genre.most_common(5)

        total_genre = sum(hitung_genre.values())
        hasil_akhir = []

        for genre, jumlah in top_5:
            persentase = round((jumlah / total_genre) * 100, 1)
            hasil_akhir.append({
                "genre": genre,
                "jumlah": jumlah,
                "persentase": persentase
            })

        return hasil_akhir

# ===============
# BLOK PENGUJIAN
# ===============
if __name__ == "__main__":
    dm = DataManager()

    user_tes = "U001"
    anime_tes = "A001"
    anime_belum_dinilai = "A999"

    print("--- MENGUJI hitung_skor_personal dan global---")

    skor_mentah = dm.get_rating_user(user_tes, anime_tes)
    print(f"\n[GET] Skor Mentah {user_tes} untuk {anime_tes}:")
    print(f"Hasil: {skor_mentah}")

    rata_rata_personal = dm.hitung_skor_personal(user_tes, anime_tes)
    print(f"\n[CALC] Rata-rata Skor Personal {user_tes} untuk {anime_tes}:")
    if rata_rata_personal is not None:
        print(f"Hasil: {rata_rata_personal} / 10")
    else:
        print("Hasil: N/A (Belum dinilai)")

    rata_rata_kosong = dm.hitung_skor_personal(user_tes, anime_belum_dinilai)
    print(f"\n[CALC] Rata-rata Skor Personal {user_tes} untuk {anime_belum_dinilai}:")
    if rata_rata_kosong is not None:
        print(f"Hasil: {rata_rata_kosong} / 10")
    else:
        print("Hasil: N/A (Belum dinilai)")

    skor_global = dm.hitung_skor_global(anime_tes)
    print(f"\n[CALC] Skor Global (Komunitas) untuk {anime_tes}:")
    print(f"Hasil: {skor_global} / 10")