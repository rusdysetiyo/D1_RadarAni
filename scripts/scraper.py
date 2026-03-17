import os
import requests
import json
import time
from bs4 import BeautifulSoup

BASE_URL = "https://myanimelist.net/topanime.php?type=bypopularity"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(BASE_DIR, "..")

# Definisi folder tujuan
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
THUMB_DIR = os.path.join(ASSETS_DIR, "thumbnails")
COVER_DIR = os.path.join(ASSETS_DIR, "covers")
DATA_DIR = os.path.join(ROOT_DIR, "data")

def setup_folders():
    os.makedirs(THUMB_DIR, exist_ok=True)
    os.makedirs(COVER_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

def get_soup(url):
    """Mengambil konten halaman dan mengembalikan objek BeautifulSoup."""
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'lxml')
    except Exception as e:
        print(f"Gagal mengambil URL {url}: {e}")
        return None


def download_image(url, physical_folder, filename):
    """Mengunduh gambar ke folder fisik,"""
    if not url:
        return "N/A"

    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        if response.status_code == 200:
            file_path_abs = os.path.join(physical_folder, filename)

            with open(file_path_abs, 'wb') as f:
                f.write(response.content)

            return os.path.relpath(file_path_abs, ROOT_DIR).replace("\\", "/")

    except Exception as e:
        print(f"Gagal download {url}: {e}")

    return "N/A"


def extract_sidebar_info(soup, label):
    """Mengekstraksi informasi dari sidebar berdasarkan label teks."""
    element = soup.find('span', string=label)
    if element:
        return element.parent.get_text(strip=True).replace(label, "").strip()
    return "N/A"


def parse_anime_details(detail_url, counter):
    """Masuk ke halaman detail dan mengekstraksi data lengkap anime."""
    soup = get_soup(detail_url)
    if not soup:
        return None

    # Ekstraksi Judul
    title_container = soup.find('div', itemprop='name')
    main_title = "N/A"
    en_title = None

    if title_container:
        h1_elem = title_container.find('h1', class_='title-name')
        if h1_elem:
            main_title = h1_elem.get_text(strip=True)

        p_en_elem = title_container.find('p', class_='title-english')
        if p_en_elem:
            en_title = p_en_elem.get_text(strip=True)

    # Ekstraksi Cover
    cover_tag = soup.find('img', itemprop='image')
    cover_url = cover_tag.get('data-src') or cover_tag.get('src') if cover_tag else ""
    cover_path = download_image(cover_url, COVER_DIR, f"CIMG{counter:03d}.jpg")

    return {
        "anime_id": f"A{counter:03d}",
        "title": main_title,
        "en_title": en_title,
        "genre": [g.text for g in soup.find_all('span', itemprop='genre')],
        "synopsis": soup.find('p', itemprop='description').get_text(strip=True) if soup.find('p',
                                                                                             itemprop='description') else "No synopsis.",
        "studio": extract_sidebar_info(soup, "Studios:"),
        "type": extract_sidebar_info(soup, "Type:"),
        "episodes": extract_sidebar_info(soup, "Episodes:"),
        "cover_path": cover_path
    }


def run_scraper():
    """Fungsi utama untuk menjalankan proses mining."""
    setup_folders()
    print("--- Memulai Mining RadarAni ---")

    main_soup = get_soup(BASE_URL)
    if not main_soup:
        return

    anime_rows = main_soup.find_all('tr', class_="ranking-list")
    anime_list = []

    for i, row in enumerate(anime_rows, 1):
        # Ambil Thumbnail dari halaman utama
        img_tag = row.find('img')
        thumb_url = ""
        if img_tag:
            thumb_url = img_tag.get('data-srcset') or img_tag.get('srcset') or img_tag.get('data-src') or img_tag.get(
                'src')
            if thumb_url and '2x' in thumb_url:
                thumb_url = thumb_url.split(',')[-1].replace('2x', '').strip()

        # Ambil URL Detail
        link_tag = row.find('h3', class_="fl-l fs14 fw-b anime_ranking_h3").find('a')
        if not link_tag:
            continue

        time.sleep(1.5)  # Delay bot-safety
        anime_data = parse_anime_details(link_tag['href'], i)

        if anime_data:
            path_thumb = download_image(thumb_url, THUMB_DIR, f"TIMG{i:03d}.jpg")
            anime_data["thumbnail_path"] = path_thumb

            anime_list.append(anime_data)
            print(f"[{anime_data['anime_id']}] Berhasil: {anime_data['title'][:30]}...")

    json_path = os.path.join(DATA_DIR, 'anime_list.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(anime_list, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    run_scraper()