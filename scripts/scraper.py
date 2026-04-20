import json
import time
import random
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Konfigurasi Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class RadarAniScraper:
    def __init__(self, target_pages: int = 10):
        self.base_url = "https://myanimelist.net/topanime.php?type=bypopularity"
        self.target_pages = target_pages
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }

        # Setup Paths menggunakan pathlib
        self.base_dir = Path(__file__).resolve().parent
        self.root_dir = self.base_dir.parent
        self.assets_dir = self.root_dir / "assets"
        self.thumb_dir = self.assets_dir / "thumbnails"
        self.cover_dir = self.assets_dir / "covers"
        self.data_dir = self.root_dir / "data"

        self.checkpoint_file = self.data_dir / 'anime_list_checkpoint.json'
        self.final_json_path = self.data_dir / 'anime_list.json'

        self.session = self._create_robust_session()
        self._setup_folders()

    def _setup_folders(self) -> None:
        """Memastikan semua direktori yang dibutuhkan tersedia."""
        for directory in [self.thumb_dir, self.cover_dir, self.data_dir]:
            directory.mkdir(parents=True, exist_ok=True)

    def _create_robust_session(self) -> requests.Session:
        """Menginisiasi sesi HTTP dengan strategi Retry."""
        session = requests.Session()
        session.headers.update(self.headers)
        retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1.5
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def get_soup(self, url: str) -> Optional[BeautifulSoup]:
        """Mengambil dan mem-parsing halaman web."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'lxml')
        except requests.exceptions.RequestException as e:
            logger.error(f"Gagal mengambil URL {url}: {e}")
            return None

    def download_image(self, url: str, target_folder: Path, filename: str) -> str:
        """Mengunduh gambar dan meretur path relatifnya terhadap root."""
        if not url:
            return "N/A"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                file_path = target_folder / filename
                file_path.write_bytes(response.content)
                # Meretur path relatif dengan format posix (menggunakan '/')
                return str(file_path.relative_to(self.root_dir).as_posix())
        except Exception as e:
            logger.error(f"Gagal mengunduh gambar {url}: {e}")
        return "N/A"

    @staticmethod
    def extract_sidebar_info(soup: BeautifulSoup, label: str) -> str:
        """Metode statis pembantu untuk ekstraksi teks sidebar."""
        element = soup.find('span', string=label)
        if element and element.parent:
            return element.parent.get_text(strip=True).replace(label, "").strip()
        return "N/A"

    def parse_anime_details(self, detail_url: str, counter: int) -> Optional[Dict[str, Any]]:
        """Mengekstraksi seluruh metadata dari halaman detail anime."""
        soup = self.get_soup(detail_url)
        if not soup:
            return None

        try:
            mal_id = int(detail_url.split('/')[4])
        except (IndexError, ValueError):
            mal_id = None
            logger.warning(f"Gagal mengekstrak MAL ID dari URL: {detail_url}")

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

        cover_tag = soup.find('img', itemprop='image')
        cover_url = cover_tag.get('data-src') or cover_tag.get('src') if cover_tag else ""
        cover_path = self.download_image(cover_url, self.cover_dir, f"CIMG{counter:03d}.jpg")

        score_container = soup.find('div', class_='fl-l score')
        global_score = 0.0
        if score_container:
            score_label = score_container.find('div', class_=lambda x: x and 'score-label' in x)
            if score_label:
                score_text = score_label.get_text(strip=True)
                if score_text != 'N/A':
                    try:
                        global_score = float(score_text)
                    except ValueError:
                        pass

        synopsis_tag = soup.find('p', itemprop='description')

        return {
            "anime_id": f"A{counter:03d}",
            "mal_id": mal_id,  # --- DITAMBAHKAN DI SINI ---
            "title": main_title,
            "en_title": en_title,
            "global_score": global_score,
            "genre": [g.text for g in soup.find_all('span', itemprop='genre')],
            "synopsis": synopsis_tag.get_text(strip=True) if synopsis_tag else "No synopsis.",
            "studio": self.extract_sidebar_info(soup, "Studios:"),
            "type": self.extract_sidebar_info(soup, "Type:"),
            "episodes": self.extract_sidebar_info(soup, "Episodes:"),
            "cover_path": cover_path
        }

    def _simpan_checkpoint(self, data_list: List[Dict], resume_page: int, current_counter: int) -> None:
        """Menyimpan status progres sementara ke JSON."""
        checkpoint_data = {
            "resume_page": resume_page,
            "next_counter": current_counter,
            "anime_list": data_list
        }
        self.checkpoint_file.write_text(json.dumps(checkpoint_data, indent=4, ensure_ascii=False), encoding='utf-8')
        logger.info(
            f"Checkpoint disimpan: {len(data_list)} anime. (Titik Lanjut: Halaman {resume_page + 1}, ID: A{current_counter:03d})")

    def load_checkpoint(self) -> tuple[List[Dict], int, int]:
        """Memuat data dari checkpoint jika ada."""
        if self.checkpoint_file.exists():
            logger.info("Menemukan file checkpoint! Memulihkan data...")
            data = json.loads(self.checkpoint_file.read_text(encoding='utf-8'))

            # Dukungan backward compatibility jika masih pakai file checkpoint lama
            if "last_page_completed" in data:
                return data["anime_list"], data["last_page_completed"] + 1, data["next_counter"]

            return data["anime_list"], data.get("resume_page", 0), data.get("next_counter", 1)
        return [], 0, 1

    def run(self) -> None:
        """Fungsi utama untuk mengeksekusi pipeline scraping."""
        logger.info(f"=== Memulai Mining RadarAni (Target: {self.target_pages} Halaman) ===")

        anime_list, start_page, global_counter = self.load_checkpoint()
        if start_page > 0 or global_counter > 1:
            logger.info(f"Melanjutkan dari Halaman {start_page + 1}, ID Mulai: A{global_counter:03d}")

        for page in range(start_page, self.target_pages):
            offset = page * 50
            current_url = f"{self.base_url}&limit={offset}" if offset > 0 else self.base_url

            logger.info(f">>> Memproses Halaman {page + 1} (Offset: {offset})")
            main_soup = self.get_soup(current_url)

            if not main_soup:
                # REVISI: Hentikan paksa jika halaman utama gagal
                logger.error(
                    f"FATAL: Gagal memuat halaman utama {page + 1}. Menyimpan checkpoint dan menghentikan skrip.")
                self._simpan_checkpoint(anime_list, page, global_counter)
                return

            anime_rows = main_soup.find_all('tr', class_="ranking-list")

            # REVISI: Kalkulasi baris yang harus dilewati jika kita melanjutkan di tengah halaman
            items_done_in_page = (global_counter - 1) % 50
            if items_done_in_page > 0:
                logger.info(f"Memulihkan progres: Melewati {items_done_in_page} anime pertama di halaman ini.")
                anime_rows = anime_rows[items_done_in_page:]

            for row in anime_rows:
                img_tag = row.find('img')
                thumb_url = ""
                if img_tag:
                    thumb_url = img_tag.get('data-srcset') or img_tag.get('srcset') or img_tag.get(
                        'data-src') or img_tag.get('src')
                    if thumb_url and '2x' in thumb_url:
                        thumb_url = thumb_url.split(',')[-1].replace('2x', '').strip()

                link_tag = row.find('h3', class_="fl-l fs14 fw-b anime_ranking_h3").find('a')
                if not link_tag:
                    continue

                delay = random.uniform(2.0, 4.5)
                time.sleep(delay)

                anime_data = self.parse_anime_details(link_tag['href'], global_counter)

                if anime_data:
                    path_thumb = self.download_image(thumb_url, self.thumb_dir, f"TIMG{global_counter:03d}.jpg")
                    anime_data["thumbnail_path"] = path_thumb
                    anime_list.append(anime_data)
                    logger.info(
                        f"[{anime_data['anime_id']}] Berhasil: {anime_data['title'][:30]}... (Delay: {delay:.2f}s)")
                    global_counter += 1
                else:
                    # REVISI: Hentikan paksa jika halaman detail gagal
                    logger.error(
                        f"FATAL: Gagal mengekstrak detail anime ID A{global_counter:03d}. Menyimpan checkpoint dan menghentikan skrip.")
                    self._simpan_checkpoint(anime_list, page, global_counter)
                    return

            # Simpan checkpoint normal saat satu halaman (50 anime) penuh selesai dieksekusi
            self._simpan_checkpoint(anime_list, page + 1, global_counter)

            page_delay = random.uniform(6.0, 10.0)
            logger.info(f"--- Halaman {page + 1} Selesai. Jeda {page_delay:.2f} detik... ---")
            time.sleep(page_delay)

        self.final_json_path.write_text(json.dumps(anime_list, indent=4, ensure_ascii=False), encoding='utf-8')

        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()

        logger.info(f"=== Selesai! Total {len(anime_list)} anime berhasil disimpan ===")


if __name__ == "__main__":
    scraper = RadarAniScraper(target_pages=10)
    scraper.run()