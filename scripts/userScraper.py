import os
import json
import time
import random
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# --- PENGATURAN PATH ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

USERS_FILE = os.path.join(DATA_DIR, "users.json")
RATINGS_FILE = os.path.join(DATA_DIR, "ratings.json")
ANIME_LIST_FILE = os.path.join(DATA_DIR, "anime_list.json")
# Anggap list dari Kaggle disimpan di sini
KAGGLE_USERS_FILE = os.path.join(DATA_DIR, "veteran_users_data.json")
CHECKPOINT_FILE = os.path.join(DATA_DIR, "checkpoint_scraper.json")

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


# ==========================================
# FUNGSI UTILITAS & ALGORITMA
# ==========================================

def load_json(filepath, default_val):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass
    return default_val


def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def get_next_user_id(users_data):
    """Menghasilkan ID pengguna (contoh: U005) dengan mengisi celah jika ada."""
    existing_ids = []
    for user in users_data:
        uid = user.get("user_id", "")
        if uid.startswith("U") and uid[1:].isdigit():
            existing_ids.append(int(uid[1:]))

    if not existing_ids:
        return "U001"

    max_id = max(existing_ids)
    return f"U{max_id + 1:03d}"


def generate_random_date_2026():
    """Menghasilkan ISO format date antara 1 April 2026 - 31 Mei 2026."""
    start_date = datetime(2026, 4, 1)
    end_date = datetime(2026, 5, 31)

    random_days = random.randint(0, (end_date - start_date).days)
    random_time = timedelta(hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))

    final_date = start_date + timedelta(days=random_days) + random_time
    return final_date.isoformat()


def generate_5d_scores(mal_score, global_score, anime_genres):
    """Algoritma injeksi 'Jiwa' ke dalam rating (Sesuai kode Anda)."""
    base_score = mal_score if mal_score > 0 else round(global_score)
    if base_score <= 0:
        base_score = 7

    scores = {
        "plot": min(10, max(1, round(random.gauss(base_score, 1.2)))),
        "visual": min(10, max(1, round(random.gauss(base_score, 1.2)))),
        "audio": min(10, max(1, round(random.gauss(base_score, 1.2)))),
        "characterization": min(10, max(1, round(random.gauss(base_score, 1.2)))),
        "direction": min(10, max(1, round(random.gauss(base_score, 1.2))))
    }

    genres_lower = [g.lower() for g in anime_genres] if anime_genres else []

    if any(g in genres_lower for g in ["action", "sci-fi", "fantasy", "mecha", "supernatural"]):
        scores["visual"] = min(10, scores["visual"] + random.choice([0, 1]))
        scores["direction"] = min(10, scores["direction"] + random.choice([0, 1]))

    if any(g in genres_lower for g in ["drama", "psychological", "mystery", "thriller", "slice of life"]):
        scores["plot"] = min(10, scores["plot"] + random.choice([0, 1]))
        scores["characterization"] = min(10, scores["characterization"] + random.choice([0, 1]))

    if any(g in genres_lower for g in ["music", "idol", "band"]):
        scores["audio"] = min(10, scores["audio"] + random.randint(1, 2))

    current_avg = sum(scores.values()) / 5.0
    iterations = 0
    while abs(current_avg - base_score) > 0.8 and iterations < 10:
        key = random.choice(list(scores.keys()))
        if current_avg > base_score and scores[key] > 1:
            scores[key] -= 1
        elif current_avg < base_score and scores[key] < 10:
            scores[key] += 1
        current_avg = sum(scores.values()) / 5.0
        iterations += 1

    return scores


# ==========================================
# FUNGSI SCRAPING MAL
# ==========================================

def get_user_favorites(username, mal_to_anime_id_map):
    """Mengambil maksimal 5 ID anime favorit dari profil (di-map ke RadarAni ID)."""
    url = f"https://myanimelist.net/profile/{username}"
    radarani_favorites = []

    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, 'lxml')
        fav_items = soup.find_all('li', class_='btn-fav')

        for item in fav_items:
            a_tag = item.find('a')
            if a_tag and 'href' in a_tag.attrs:
                href = a_tag['href']
                # Contoh URL: https://myanimelist.net/anime/32182/Mob_Psycho_100
                try:
                    mal_id = int(href.split('/')[4])
                    # Cocokkan mal_id dengan anime_id internal kita
                    if mal_id in mal_to_anime_id_map:
                        radarani_favorites.append(mal_to_anime_id_map[mal_id])
                        if len(radarani_favorites) == 5:  # Ambil maksimal 5
                            break
                except (IndexError, ValueError):
                    continue

    except Exception as e:
        print(f"  [!] Gagal mengambil favorit untuk {username}: {e}")

    return radarani_favorites


def get_user_animelist(username):
    """Mengambil seluruh anime yang statusnya Completed (2) dari user."""
    completed_anime = []
    offset = 0

    while True:
        url = f"https://myanimelist.net/animelist/{username}/load.json?offset={offset}&status=2"
        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code == 400 or response.status_code == 403:
                print("  [!] Rate limit tercapai atau profile private.")
                break

            data = response.json()
            if not data:  # Jika JSON kosong, berarti sudah mentok
                break

            completed_anime.extend(data)

            if len(data) < 300:  # Jika kurang dari 300, berarti tidak ada halaman selanjutnya
                break

            offset += 300
            time.sleep(2)  # Delay antar offset agar tidak di-banned

        except Exception as e:
            print(f"  [!] Gagal mengambil animelist {username} pada offset {offset}: {e}")
            break

    return completed_anime


# ==========================================
# ORKESTRATOR UTAMA
# ==========================================

def run_scraper_injector():
    print("--- Memulai Proses Scraping & Injeksi User MAL ---")

    # 1. Siapkan Data Master
    anime_master = load_json(ANIME_LIST_FILE, [])
    if not anime_master:
        print("Error: anime_list.json kosong atau tidak ditemukan.")
        return

    # Buat dictionary pemetaan untuk kecepatan akses O(1)
    mal_to_anime_id = {anime["mal_id"]: anime["anime_id"] for anime in anime_master if "mal_id" in anime}
    anime_id_data = {anime["anime_id"]: {"global": anime.get("global_score", 7.0), "genre": anime.get("genre", [])} for
                     anime in anime_master}

    # 2. Siapkan File Target & Checkpoint
    users_db = load_json(USERS_FILE, [])
    ratings_db = load_json(RATINGS_FILE, {})
    kaggle_users = load_json(KAGGLE_USERS_FILE, [])

    checkpoint_data = load_json(CHECKPOINT_FILE, {"last_index": 0})
    start_index = checkpoint_data["last_index"]

    print(f"Total target: {len(kaggle_users)} user. Melanjutkan dari index: {start_index}")

    # 3. Looping Utama
    for i in range(start_index, len(kaggle_users)):
        k_user = kaggle_users[i]
        username = k_user["username"]
        user_completed_count = k_user["user_completed"]

        print(f"[{i + 1}/{len(kaggle_users)}] Memproses: {username}...")

        # Eksekusi Scraping
        time.sleep(2)  # Wajib delay antar user
        fav_anime_ids = get_user_favorites(username, mal_to_anime_id)

        time.sleep(1.5)
        raw_animelist = get_user_animelist(username)

        # Jika profile private / gagal, lewati ke user berikutnya
        if not raw_animelist:
            print(f"  [-] Lewati {username} (Data kosong/Private)")
            checkpoint_data["last_index"] = i + 1
            save_json(CHECKPOINT_FILE, checkpoint_data)
            continue

        # Siapkan User ID dan Akun
        new_user_id = get_next_user_id(users_db)
        random_waktu = generate_random_date_2026()

        user_obj = {
            "user_id": new_user_id,
            "username": username,
            "password": f"Rad123{username}{user_completed_count}@#",
            "created_at": random_waktu,
            "last_login": random_waktu,
            "bio": "Halo! Saya penikmat anime dan pengguna baru RadarAni.",
            "favorit": fav_anime_ids
        }
        users_db.append(user_obj)

        # Siapkan Laci Rating
        ratings_db[new_user_id] = {}

        # Proses Injeks Rating 5 Dimensi
        match_count = 0
        for item in raw_animelist:
            mal_id = item.get("anime_id")
            mal_score = item.get("score", 0)

            # Hanya proses anime yang ada di database kita (top 500)
            if mal_id in mal_to_anime_id:
                radar_id = mal_to_anime_id[mal_id]
                global_score = anime_id_data[radar_id]["global"]
                genres = anime_id_data[radar_id]["genre"]

                # Eksekusi Algoritma Anda
                skor_5d = generate_5d_scores(mal_score, global_score, genres)
                ratings_db[new_user_id][radar_id] = skor_5d
                match_count += 1

        print(f"  [+] Sukses injeksi {match_count} anime. Favorit: {len(fav_anime_ids)}")

        # 4. SIMPAN BERKALA (Checkpoint tiap 5 user)
        if (i + 1) % 5 == 0:
            print("  [✓] Auto-saving ke JSON...")
            save_json(USERS_FILE, users_db)
            save_json(RATINGS_FILE, ratings_db)
            checkpoint_data["last_index"] = i + 1
            save_json(CHECKPOINT_FILE, checkpoint_data)

    # Simpanan Akhir (Jika loop selesai 100%)
    print("\n--- Proses Selesai ---")
    save_json(USERS_FILE, users_db)
    save_json(RATINGS_FILE, ratings_db)
    checkpoint_data["last_index"] = len(kaggle_users)
    save_json(CHECKPOINT_FILE, checkpoint_data)


if __name__ == "__main__":
    # Pastikan file kaggle_users.json sudah Anda buat di folder data
    run_scraper_injector()