import flet as ft
from src.ui.ui_loading import buat_bloom_screen, animasi_bloom

# ── Section: Theme & Colors ──────────────────────────────────────────────────
C_SAKURA = "#C07090"
C_TEXT3 = "#4A4A4A"
C_SAKURA_LT = "#D890A8"


# ── Section: Main Screen Manager ─────────────────────────────────────────────
class ScreenManager:
    def __init__(self, page: ft.Page, data_manager, auth_manager):
        self.page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager

    def bersihkan_layar(self):
        self.page.controls.clear()
        self.page.update()

    async def _jalankan_transisi(self, pesan, target_class, *args, **kwargs):
        layar, petals, circle, dots = buat_bloom_screen(pesan)
        self.bersihkan_layar()
        self.page.add(layar)

        # 1. Biarkan Bloom jalan tanpa beban, dijamin 100% mulus!
        await animasi_bloom(petals, circle, dots)

        self.bersihkan_layar()

        # 2. BIKIN FRESH: Halaman selalu dibikin baru biar bukan Zombie
        halaman_baru = target_class(self.page, self.data_manager, self.auth_manager, self, *args, **kwargs)
        self.page.add(halaman_baru)
        self.page.update()

        # 3. SETELAH terpasang sempurna di layar, baru tarik datanya!
        # Dijamin rating dari Detail langsung nongol tanpa error!
        if hasattr(halaman_baru, '_muat_sections'):
            self.page.run_task(halaman_baru._muat_sections)

    def tampilkan_home(self):
        from src.ui.ui_home import UIHome
        self.page.run_task(self._jalankan_transisi, "Preparing Home...", UIHome)

    def tampilkan_katalog(self, filter_kategori=None):
        from src.ui.ui_katalog import UIKatalog
        self.page.run_task(self._jalankan_transisi, "Loading Catalog...", UIKatalog, filter_kategori)

    def tampilkan_login(self):
        from src.ui.ui_login import UILogin
        self.bersihkan_layar()
        login_view = UILogin(self.page, self.data_manager, self.auth_manager, self)
        self.page.add(login_view)
        self.page.update()

    def tampilkan_detail(self, anime_id: str):
        from src.ui.ui_detail import UIDetail
        self.page.run_task(self._jalankan_transisi, "Opening Details...", UIDetail, anime_id=anime_id)

    def tampilkan_profil(self):
        from src.ui.ui_profile import UIProfile
        self.page.run_task(self._jalankan_transisi, "Loading Profile...", UIProfile)

    def tampilkan_scraping(self):
        from src.ui.ui_scraping import UIScraping
        self.page.run_task(self._jalankan_transisi, "Loading Scraper...", UIScraping)

    def tampilkan_analytics(self):
        from src.ui.ui_analytics import UIAnalytics
        self.page.run_task(self._jalankan_transisi, "Loading Analytics...", UIAnalytics)