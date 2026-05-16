import csv
import os
import json

# ==========================================
# PENGATURAN PATH
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")

INPUT_CSV = os.path.join(DATA_DIR, "users_filtered.csv")
OUTPUT_JSON = os.path.join(DATA_DIR, "veteran_users_data.json")


def extract_veteran_users(input_path, output_path, min_completed=900, max_completed=1200):
    """Membaca CSV dan mengekstrak username dengan jumlah completed dalam rentang tertentu."""
    veteran_users = []

    print(f"Membaca data dari: {input_path}...")

    try:
        with open(input_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                try:
                    username = row.get('username', '').strip()
                    completed_str = row.get('user_completed', '0').strip()

                    if not username or not completed_str:
                        continue

                    completed_count = int(float(completed_str))

                    # --- PERUBAHAN UTAMA: Membatasi rentang bawah dan atas ---
                    if min_completed <= completed_count <= max_completed:
                        veteran_users.append({
                            "username": username,
                            "user_completed": completed_count
                        })

                except ValueError:
                    continue

        # Simpan hasilnya ke dalam file JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(veteran_users, f, indent=4)

        print("-" * 40)
        print(f"Selesai! Ditemukan {len(veteran_users)} user veteran (Completed: {min_completed} - {max_completed}).")
        print(f"Hasil disimpan di: {output_path}")

    except FileNotFoundError:
        print(f"ERROR: File tidak ditemukan!")
        print(f"Pastikan file CSV diletakkan di: {input_path}")


if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    extract_veteran_users(INPUT_CSV, OUTPUT_JSON)
