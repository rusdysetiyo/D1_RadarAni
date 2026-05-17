import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FILE_JSON = os.path.join(DATA_DIR, "anime_list.json")

FIELDS_TO_REMOVE = ["cover_url_hd", "cover_path_hd"]

with open(FILE_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

for anime in data:
    for field in FIELDS_TO_REMOVE:
        anime.pop(field, None)

with open(FILE_JSON, "w", encoding="utf-8") as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print(f"Done. {len(data)} entries cleaned.")