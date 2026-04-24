import json
import os
from datetime import datetime

class DataManager:
    def __init__(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.root_dir = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))
        self.data_dir = os.path.join(self.root_dir, "data")

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
            # Pengecualian dibisukan untuk produksi; integrasikan logging library jika perlu.
            pass

    # ==========================================
    # MANAJEMEN DATA ANIME (READ-ONLY)
    # ==========================================

    def get_semua_anime(self):
        """Mengembalikan seluruh katalog anime atau list kosong jika tidak tersedia."""
        anime_list = self._read_json(self.anime_file) or []

        # Inject key berisi path absolut agar UI langsung bisa pakai
        for anime in anime_list:
            if "thumbnail_path" in anime:
                anime["thumbnail_path_abs"] = self.get_absolute_image_path(anime["thumbnail_path"])
            if "cover_path" in anime:
                anime["cover_path_abs"] = self.get_absolute_image_path(anime.get("cover_path"))

        return anime_list

    def get_detail_anime(self, anime_id):
        """Mencari spesifikasi satu anime secara efisien menggunakan generator."""
        semua_anime = self.get_semua_anime()
        return next((anime for anime in semua_anime if anime.get("anime_id") == anime_id), None)

    def get_absolute_image_path(self, relative_path):
        """Menerjemahkan path relatif JSON menjadi path absolut di komputer."""
        if not relative_path or relative_path == "N/A":
            return None  # Bisa diganti path placeholder gambar default jika ada

        abs_path = os.path.join(self.root_dir, relative_path)
        # Ganti backslash windows ke forward slash agar aman di semua OS
        return abs_path.replace("\\", "/")

    def cari_anime(self, kata_kunci):
        """
        Mencari anime berdasarkan kecocokan kata kunci pada judul utama atau bahasa Inggris.
        Pencarian bersifat case-insensitive.
        """
        semua_anime = self.get_semua_anime()

        # Jika kata kunci kosong atau hanya berisi spasi, kembalikan seluruh katalog
        if not kata_kunci or not kata_kunci.strip():
            return semua_anime

        kunci_lower = kata_kunci.strip().lower()
        hasil_pencarian = []

        for anime in semua_anime:
            # Ambil judul dan ubah ke huruf kecil
            judul_utama = anime.get("title", "").lower()

            # Tangani kemungkinan en_title bernilai None di JSON
            en_title_raw = anime.get("en_title")
            judul_inggris = en_title_raw.lower() if en_title_raw else ""

            # Jika kata kunci ada di judul utama ATAU judul bahasa Inggris
            if kunci_lower in judul_utama or kunci_lower in judul_inggris:
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
                return user.get("user_id")  # <-- Mengembalikan "U001" (bukan True)

        return None  # Mengembalikan None jika gagal/tidak cocok

    def update_last_login(self, user_id):
        """Memperbarui kolom last_login dengan waktu saat ini (ISO 8601)."""
        users = self._read_json(self.users_file) or []
        berhasil_update = False

        for user in users:
            if user.get("user_id") == user_id:
                user["last_login"] = datetime.now().isoformat()
                berhasil_update = True
                break  # Berhenti mencari jika user sudah ditemukan

        if berhasil_update:
            self._write_json(self.users_file, users)

        return berhasil_update

    def generate_user_id(self):
        """Menghasilkan ID pengguna sekuensial (contoh: U003) berdasarkan data yang ada."""
        users = self._read_json(self.users_file) or []

        # Ekstraksi angka dari ID yang valid menggunakan list comprehension
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
        # Mempermudah UI (ui_dashboard) untuk memunculkan teks "N/A"
        if not skor_dict:
            return None

        total_skor = sum(skor_dict.values())
        jumlah_dimensi = len(skor_dict)

        return round(total_skor / jumlah_dimensi, 2)

    def simpan_rating(self, user_id, anime_id, skor_dict):
        """Menyimpan atau memperbarui data skor multidimensi."""
        ratings = self._read_json(self.ratings_file) or {}

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