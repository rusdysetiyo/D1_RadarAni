import flet as ft
from src.ui.ui_loading import buat_bloom_screen, animasi_bloom

# ── Section: Theme & Colors ──────────────────────────────────────────────────
C_SAKURA    = "#C07090"
C_TEXT3     = "#4A4A4A"
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

        await animasi_bloom(petals, circle, dots)

        self.bersihkan_layar()
        self.page.add(target_class(self.page, self.data_manager, self.auth_manager, self, *args, **kwargs))
        self.page.update()

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
        self.page.run_task(
            self._jalankan_transisi,
            "Opening Details...",
            UIDetail,
            anime_id=anime_id  # Lempar ID anime ke class UIDetail
        )

    def tampilkan_profil(self):
        from src.ui.ui_profile import UIProfile
        self.page.run_task(self._jalankan_transisi, "Loading Profile...", UIProfile)