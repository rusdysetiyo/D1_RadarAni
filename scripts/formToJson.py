import csv
import json
import re
import os
from datetime import datetime

# --- PENGATURAN PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")


# ==========================================
# FUNGSI UTILITAS (Diambil dari skrip referensi)
# ==========================================

def load_json(filepath, default_val):
    """Membaca JSON jika ada, dan memastikan tipe datanya sesuai dengan default_val."""
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # VALIDASI KRUSIAL: Pastikan tipe data file sama dengan tipe data yang diharapkan
                if isinstance(data, type(default_val)):
                    return data
                else:
                    print(f"Peringatan: Tipe data {filepath} salah. Mereset ke struktur bawaan.")
                    return default_val

        except json.JSONDecodeError:
            pass  # Abaikan jika file kosong atau rusak, biarkan return default_val

    return default_val


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_next_user_id(users_data):
    """Mencari ID terbesar di database dan melanjutkannya."""
    existing_ids = []
    for user in users_data:
        uid = user.get("user_id", "")
        if uid.startswith("U") and uid[1:].isdigit():
            existing_ids.append(int(uid[1:]))

    if not existing_ids:
        return "U001"
    return f"U{max(existing_ids) + 1:03d}"


def format_timestamp(raw_timestamp):
    """Mengubah format waktu Form (termasuk AM/PM) menjadi standar ISO 8601."""
    if not raw_timestamp:
        return datetime.now().isoformat()

    raw_timestamp = raw_timestamp.strip()

    # Kumpulan format yang sering dikeluarkan oleh Google Forms
    formats = [
        '%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S',
        '%m/%d/%Y %I:%M:%S %p', '%d/%m/%Y %I:%M:%S %p', '%Y/%m/%d %I:%M:%S %p',
        '%Y-%m-%d %H:%M:%S'
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(raw_timestamp, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    # Fallback aman: Jika format super aneh, gunakan waktu eksekusi skrip
    return datetime.now().isoformat()


def generate_password(name, total_anime):
    return f"Rad123{name}{total_anime}@#"


def load_anime_mapping(anime_json_path):
    try:
        with open(anime_json_path, 'r', encoding='utf-8') as f:
            anime_data = json.load(f)
            return {item['title'].strip().lower(): item['anime_id'] for item in anime_data}
    except FileNotFoundError:
        print(f"Error: File '{anime_json_path}' tidak ditemukan!")
        return None


# ==========================================
# FUNGSI PEMROSESAN INTI (Smart Update)
# ==========================================

def parse_and_merge_csv(csv_path, title_to_id, users_db, ratings_db):
    """Menggabungkan data CSV ke dalam database yang sudah ada."""
    dim_map = {
        "story": "plot", "visual": "visual", "audio/music": "audio",
        "characterization": "characterization", "direction": "direction"
    }
    required_dims = {"plot", "visual", "audio", "characterization", "direction"}

    # Pemetaan user berdasarkan nama agar tidak ada duplikat jika CSV dijalankan berulang
    existing_users_map = {u['username'].lower(): u for u in users_db}

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for row in reader:
            name = row.get('Name', '').strip()
            name_lower = name.lower()
            total_anime = row.get('Total Completed Anime', '').strip()
            waktu_standar = format_timestamp(row.get('Timestamp', ''))

            # 1. Update atau Buat User Baru
            if name_lower in existing_users_map:
                # Patch/Perbaiki user lama (Misal: User dari form yang belum punya Bio/ISO date)
                user_obj = existing_users_map[name_lower]
                user_id = user_obj['user_id']

                # Paksa update format waktu jika masih menggunakan format lama (tidak ada huruf 'T')
                if 'T' not in user_obj.get('created_at', ''):
                    user_obj['created_at'] = waktu_standar
                    user_obj['last_login'] = waktu_standar

                # Injeksi key baru jika tidak ada
                user_obj['bio'] = user_obj.get('bio', "Halo! Saya penikmat anime dan pengguna baru RadarAni.")
                user_obj['favorit'] = user_obj.get('favorit', [])
            else:
                # Daftarkan user baru dengan ID yang berurutan
                user_id = get_next_user_id(users_db)
                user_obj = {
                    "user_id": user_id,
                    "username": name,
                    "password": generate_password(name, total_anime),
                    "created_at": waktu_standar,
                    "last_login": waktu_standar,
                    "bio": "Halo! Saya penikmat anime dan pengguna baru RadarAni.",
                    "favorit": []
                }
                users_db.append(user_obj)
                existing_users_map[name_lower] = user_obj  # Catat di memori

            # 2. Update Laci Rating User
            if user_id not in ratings_db:
                ratings_db[user_id] = {}

            temp_user_ratings = {}

            for column_name, value in row.items():
                match = re.match(r"(.+)\s\[(.+)\]", column_name)
                if match and value.strip():
                    raw_title = match.group(1).strip().lower()
                    raw_dim = match.group(2).strip().lower()

                    if raw_dim in dim_map:
                        dimension = dim_map[raw_dim]
                        if raw_title not in temp_user_ratings:
                            temp_user_ratings[raw_title] = {}
                        temp_user_ratings[raw_title][dimension] = int(value)

            for title_key, scores in temp_user_ratings.items():
                if title_key in title_to_id and required_dims.issubset(scores.keys()):
                    anime_id = title_to_id[title_key]
                    ratings_db[user_id][anime_id] = scores
                elif title_key not in title_to_id:
                    pass  # Abaikan judul yang tidak ada di katalog tanpa memenuhi konsol

    return users_db, ratings_db


def process_radarani_data(csv_filename, anime_list_filename):
    print("--- Memulai Sinkronisasi Data Form CSV ---")
    csv_path = os.path.join(DATA_DIR, csv_filename)
    anime_json_path = os.path.join(DATA_DIR, anime_list_filename)
    users_path = os.path.join(DATA_DIR, 'users.json')
    ratings_path = os.path.join(DATA_DIR, 'ratings.json')

    title_to_id = load_anime_mapping(anime_json_path)
    if not title_to_id:
        return

    # Muat database yang sudah ada (sehingga aman dijalankan walau skrip MAL sudah pernah di-run)
    users_db = load_json(users_path, [])
    ratings_db = load_json(ratings_path, {})

    users_db, ratings_db = parse_and_merge_csv(csv_path, title_to_id, users_db, ratings_db)

    save_json(users_path, users_db)
    save_json(ratings_path, ratings_db)
    print(f"[✓] Berhasil! Data selaras dan tersimpan di: {DATA_DIR}")


if __name__ == "__main__":
    process_radarani_data('RadarAni (Jawaban) - Form Responses 1.csv', 'anime_list.json')