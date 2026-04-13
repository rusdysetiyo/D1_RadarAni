import csv
import json
import re
import os
from datetime import datetime  # <-- Tambahan import

# --- PENGATURAN PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")


def generate_password(name, total_anime):
    return f"Rad123{name}{total_anime}@#"


def format_timestamp(raw_timestamp):
    """Mengubah format waktu Google Form menjadi format standar ISO 8601."""
    if not raw_timestamp:
        return datetime.now().isoformat()

    # Pola format umum Google Form (Bulan/Hari/Tahun atau Hari/Bulan/Tahun)
    formats = ['%m/%d/%Y %H:%M:%S', '%d/%m/%Y %H:%M:%S', '%Y/%m/%d %H:%M:%S']

    for fmt in formats:
        try:
            # Jika berhasil diparsing, kembalikan dalam format ISO
            dt = datetime.strptime(raw_timestamp, fmt)
            return dt.isoformat()
        except ValueError:
            continue

    # Jika semua format gagal, kembalikan teks aslinya sebagai fallback
    return raw_timestamp


def load_anime_mapping(anime_json_path):
    try:
        with open(anime_json_path, 'r', encoding='utf-8') as f:
            anime_data = json.load(f)
            return {item['title'].strip().lower(): item['anime_id'] for item in anime_data}
    except FileNotFoundError:
        print(f"Error: File '{anime_json_path}' tidak ditemukan!")
        return None


def parse_csv_responses(csv_path, title_to_id):
    users = []
    ratings = {}

    dim_map = {
        "story": "plot",
        "visual": "visual",
        "audio/music": "audio",
        "characterization": "characterization",
        "direction": "direction"
    }
    required_dims = {"plot", "visual", "audio", "characterization", "direction"}

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)

        for i, row in enumerate(reader, 1):
            user_id = f"U{i:03d}"
            name = row.get('Name', '').strip()
            total_anime = row.get('Total Completed Anime', '').strip()

            # Memproses timestamp ke format standar
            waktu_standar = format_timestamp(row.get('Timestamp', ''))

            # --- PENAMBAHAN KEY BARU ---
            users.append({
                "user_id": user_id,
                "username": name,
                "password": generate_password(name, total_anime),
                "created_at": waktu_standar,
                "last_login": waktu_standar,  # Disamakan dengan saat akun dibuat
                "bio": "Halo! Saya penikmat anime dan pengguna baru RadarAni.",  # Bio Default
                "favorit": []  # List kosong untuk ID anime favorit
            })

            ratings[user_id] = {}
            temp_user_ratings = {}

            # (Sisa logika parsing rating Anda tidak berubah)
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
                    ratings[user_id][anime_id] = scores
                elif title_key not in title_to_id:
                    print(f"Peringatan: Judul '{title_key}' tidak ada di AnimeList.")

    return users, ratings


def save_json(data, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def process_radarani_data(csv_filename, anime_list_filename):
    # (Kode orkestrator Anda tidak berubah)
    csv_path = os.path.join(DATA_DIR, csv_filename)
    anime_json_path = os.path.join(DATA_DIR, anime_list_filename)
    users_path = os.path.join(DATA_DIR, 'users.json')
    ratings_path = os.path.join(DATA_DIR, 'ratings.json')

    title_to_id = load_anime_mapping(anime_json_path)
    if not title_to_id:
        return

    users, ratings = parse_csv_responses(csv_path, title_to_id)
    save_json(users, users_path)
    save_json(ratings, ratings_path)
    print(f"Berhasil! File tersimpan di: {DATA_DIR}")


if __name__ == "__main__":
    process_radarani_data('RadarAni (Jawaban) - Form Responses 1.csv', 'anime_list.json')