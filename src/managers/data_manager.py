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
        data_user_baru.setdefault("rating_count", 0)
        data_user_baru.setdefault("average_score", 0.0)
        data_user_baru.setdefault("average_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])
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
            user_ratings = ratings.pop(user_id)
            self._write_json(self.ratings_file, ratings)

            # 3. Memperbarui statistik anime
            for anime_id, old_skor_dict in user_ratings.items():
                self._update_anime_stats(anime_id, new_skor_dict=None, old_skor_dict=old_skor_dict, is_delete=True)

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

    def get_rating_user_as_list(self, user_id, anime_id):
        """
        Mengambil skor multidimensi milik user dan mengubahnya menjadi list berurutan.
        """
        skor_dict = self.get_rating_user(user_id, anime_id)

        # Jika user belum menilai, kembalikan list berisi angka 0 agar radar chart kosong
        if not skor_dict:
            return [0, 0, 0, 0, 0]

        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]

        # Ekstrak nilai berdasarkan urutan mutlak
        return [skor_dict.get(dimensi, 0) for dimensi in urutan_dimensi]

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

        user_ratings = ratings.setdefault(user_id, {})
        is_new_rating = anime_id not in user_ratings
        old_skor_dict = user_ratings.get(anime_id, None)

        user_ratings[anime_id] = skor_dict

        self._write_json(self.ratings_file, ratings)

        self._update_anime_stats(anime_id, new_skor_dict=skor_dict, old_skor_dict=old_skor_dict, is_new=is_new_rating)
        self._update_user_stats(user_id, new_skor_dict=skor_dict, old_skor_dict=old_skor_dict, is_new=is_new_rating)

        return True

    def hapus_rating(self, user_id, anime_id):
        """Mencabut satu data rating spesifik dari pengguna."""
        ratings = self._read_json(self.ratings_file) or {}

        if user_id in ratings and anime_id in ratings[user_id]:
            old_skor_dict = ratings[user_id].pop(anime_id)
            self._write_json(self.ratings_file, ratings)

            self._update_anime_stats(anime_id, new_skor_dict=None, old_skor_dict=old_skor_dict, is_delete=True)
            self._update_user_stats(user_id, new_skor_dict=None, old_skor_dict=old_skor_dict, is_delete=True)

            return True

        return False

    def _update_anime_stats(self, anime_id, new_skor_dict=None, old_skor_dict=None, is_new=False, is_delete=False):
        """Memperbarui statistik rating secara matematis O(1) di anime_list.json."""
        anime_list = self._read_json(self.anime_file) or []
        anime = next((a for a in anime_list if a.get("anime_id") == anime_id), None)
        if not anime:
            return

        count = anime.get("rating_count", 0)
        global_score = anime.get("global_score", 0.0)
        dim_scores = anime.get("global_score_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])

        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]

        if is_delete and old_skor_dict:
            if count <= 1:
                anime["rating_count"] = 0
                anime["global_score"] = 0.0
                anime["global_score_dimensions"] = [0.0, 0.0, 0.0, 0.0, 0.0]
            else:
                old_avg = sum(old_skor_dict.values()) / len(old_skor_dict)
                anime["global_score"] = round((global_score * count - old_avg) / (count - 1), 2)
                for i, dim in enumerate(urutan_dimensi):
                    dim_scores[i] = round((dim_scores[i] * count - old_skor_dict.get(dim, 0)) / (count - 1), 2)
                anime["global_score_dimensions"] = dim_scores
                anime["rating_count"] = count - 1

        elif is_new and new_skor_dict:
            new_avg = sum(new_skor_dict.values()) / len(new_skor_dict)
            anime["global_score"] = round((global_score * count + new_avg) / (count + 1), 2)
            for i, dim in enumerate(urutan_dimensi):
                dim_scores[i] = round((dim_scores[i] * count + new_skor_dict.get(dim, 0)) / (count + 1), 2)
            anime["global_score_dimensions"] = dim_scores
            anime["rating_count"] = count + 1

        elif new_skor_dict and old_skor_dict:  # Update rating
            old_avg = sum(old_skor_dict.values()) / len(old_skor_dict)
            new_avg = sum(new_skor_dict.values()) / len(new_skor_dict)
            if count == 0: count = 1  # Fallback menghindari pembagian dengan nol
            anime["global_score"] = round((global_score * count - old_avg + new_avg) / count, 2)
            for i, dim in enumerate(urutan_dimensi):
                dim_scores[i] = round(
                    (dim_scores[i] * count - old_skor_dict.get(dim, 0) + new_skor_dict.get(dim, 0)) / count, 2)
            anime["global_score_dimensions"] = dim_scores

        self._write_json(self.anime_file, anime_list)

    def _update_user_stats(self, user_id, new_skor_dict=None, old_skor_dict=None, is_new=False, is_delete=False):
        """Memperbarui statistik rata-rata rating milik user secara matematis O(1) di users.json."""
        users = self._read_json(self.users_file) or []
        user = next((u for u in users if u.get("user_id") == user_id), None)
        if not user:
            return

        count = user.get("rating_count", 0)
        avg_score = user.get("average_score", 0.0)
        dim_scores = user.get("average_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])

        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]

        if is_delete and old_skor_dict:
            if count <= 1:
                user["rating_count"] = 0
                user["average_score"] = 0.0
                user["average_dimensions"] = [0.0, 0.0, 0.0, 0.0, 0.0]
            else:
                old_rating_avg = sum(old_skor_dict.values()) / len(old_skor_dict)
                user["average_score"] = round((avg_score * count - old_rating_avg) / (count - 1), 2)
                for i, dim in enumerate(urutan_dimensi):
                    dim_scores[i] = round((dim_scores[i] * count - old_skor_dict.get(dim, 0)) / (count - 1), 2)
                user["average_dimensions"] = dim_scores
                user["rating_count"] = count - 1

        elif is_new and new_skor_dict:
            new_rating_avg = sum(new_skor_dict.values()) / len(new_skor_dict)
            user["average_score"] = round((avg_score * count + new_rating_avg) / (count + 1), 2)
            for i, dim in enumerate(urutan_dimensi):
                dim_scores[i] = round((dim_scores[i] * count + new_skor_dict.get(dim, 0)) / (count + 1), 2)
            user["average_dimensions"] = dim_scores
            user["rating_count"] = count + 1

        elif new_skor_dict and old_skor_dict:  # Update rating
            old_rating_avg = sum(old_skor_dict.values()) / len(old_skor_dict)
            new_rating_avg = sum(new_skor_dict.values()) / len(new_skor_dict)
            if count == 0: count = 1  # Fallback menghindari pembagian dengan nol
            user["average_score"] = round((avg_score * count - old_rating_avg + new_rating_avg) / count, 2)
            for i, dim in enumerate(urutan_dimensi):
                dim_scores[i] = round(
                    (dim_scores[i] * count - old_skor_dict.get(dim, 0) + new_skor_dict.get(dim, 0)) / count, 2)
            user["average_dimensions"] = dim_scores

        self._write_json(self.users_file, users)

    def hitung_skor_global(self, anime_id):
        """Mengambil nilai rata-rata keseluruhan (O(1)) langsung dari anime_list."""
        anime = self.get_detail_anime(anime_id)
        return anime.get("global_score", 0.0) if anime else 0.0

    def get_skor_global_dimensi_as_list(self, anime_id):
        """Mengambil rata-rata skor komunitas untuk SETIAP dimensi secara O(1) dari anime_list."""
        anime = self.get_detail_anime(anime_id)
        return anime.get("global_score_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0]) if anime else [0.0, 0.0, 0.0, 0.0, 0.0]

    def get_rating_count(self, anime_id):
        """Mengambil jumlah user yang telah menilai anime tertentu."""
        anime = self.get_detail_anime(anime_id)
        return anime.get("rating_count", 0) if anime else 0

    def get_user_by_id(self, user_id):
        """Mencari data lengkap user berdasarkan user_id."""
        users = self._read_json(self.users_file) or []
        return next((u for u in users if u.get("user_id") == user_id), None)

    # ==========================================
    # MANAJEMEN FAVORIT
    # ==========================================

    def toggle_favorit(self, user_id, anime_id):
        """
        Menambahkan anime ke daftar favorit jika belum ada,
        atau menghapusnya jika sudah ada.
        Mengembalikan True jika sekarang menjadi favorit, False jika dihapus.
        """
        users = self._read_json(self.users_file) or []
        status_favorit_sekarang = False
        berhasil_update = False

        for user in users:
            if user.get("user_id") == user_id:
                # Pastikan key favorit berupa list
                list_favorit = user.setdefault("favorit", [])

                if anime_id in list_favorit:
                    list_favorit.remove(anime_id)
                    status_favorit_sekarang = False
                else:
                    list_favorit.append(anime_id)
                    status_favorit_sekarang = True

                berhasil_update = True
                break

        if berhasil_update:
            self._write_json(self.users_file, users)

        return status_favorit_sekarang

    def cek_is_favorit(self, user_id, anime_id):
        """Memeriksa apakah sebuah anime ada di dalam daftar favorit user."""
        user = self.get_user_by_id(user_id)
        if user:
            return anime_id in user.get("favorit", [])
        return False

    def get_anime_favorit_user(self, user_id):
        """
        Mengambil detail lengkap dari semua anime yang difavoritkan user.
        Digunakan untuk merender Halaman Profil.
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return []

        list_id_favorit = user.get("favorit", [])

        # Ambil detail lengkap dari setiap ID di list favorit
        anime_favorit_lengkap = []
        for anime_id in list_id_favorit:
            detail = self.get_detail_anime(anime_id)
            if detail:
                anime_favorit_lengkap.append(detail)

        return anime_favorit_lengkap

    def get_rekomendasi_multidimensi(self, dimensi_favorit, id_anime_ditonton):
        """
        [ALGORITMA REKOMENDASI]
        """
        semua_anime = self.get_semua_anime()
        if not semua_anime:
            return None

        urutan_dimensi = ["plot", "visual", "audio", "characterization", "direction"]

        index_favorit = [urutan_dimensi.index(d) for d in dimensi_favorit if d in urutan_dimensi]

        rata_rata_kandidat = {}
        jumlah_reviewer = {}
        MINIMUM_REVIEW = 3

        for anime in semua_anime:
            id_anime = anime.get("anime_id")
            if id_anime in id_anime_ditonton:
                continue  # Lewati yang udah ditonton

            count = anime.get("rating_count", 0)

            if count >= MINIMUM_REVIEW:
                # Ambil list skor 5 dimensi
                dimensi_global = anime.get("global_score_dimensions", [0.0, 0.0, 0.0, 0.0, 0.0])

                # Ekstrak nilai pada index dimensi yang disukai user
                skor_relevan = [dimensi_global[i] for i in index_favorit]

                if skor_relevan:
                    rata_rata_kandidat[id_anime] = sum(skor_relevan) / len(skor_relevan)
                    jumlah_reviewer[id_anime] = count

        if not rata_rata_kandidat:
            return None

        # mencari skor tertinggi
        skor_tertinggi = max(rata_rata_kandidat.values())
        kandidat_teratas = [id_anime for id_anime, skor in rata_rata_kandidat.items() if skor == skor_tertinggi]

        if len(kandidat_teratas) == 1:
            return kandidat_teratas[0]

        # kalau nilai rata rata global skor sama, dilihat dari jumlah reviewer
        kandidat_tahap_dua = []
        reviewer_terbanyak = -1

        for id_anime in kandidat_teratas:
            total_review = jumlah_reviewer[id_anime]

            if total_review > reviewer_terbanyak:
                reviewer_terbanyak = total_review
                kandidat_tahap_dua = [id_anime]
            elif total_review == reviewer_terbanyak:
                kandidat_tahap_dua.append(id_anime)

        if len(kandidat_tahap_dua) == 1:
            return kandidat_tahap_dua[0]

        # worst case, baru dicompare sama global score
        rekomendasi_final = kandidat_tahap_dua[0]
        skor_global_maksimal = -1

        for id_anime in kandidat_tahap_dua:
            skor_global_anime = self.hitung_skor_global(id_anime)

            if skor_global_anime > skor_global_maksimal:
                skor_global_maksimal = skor_global_anime
                rekomendasi_final = id_anime

        return rekomendasi_final


# ===============
# BLOK PENGUJIAN
# ===============
if __name__ == "__main__":
    print("Pengujian")
