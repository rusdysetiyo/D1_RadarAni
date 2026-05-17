import flet as ft
from src.ui.ui_loading import buat_bloom_screen, animasi_bloom
from src.config.theme import ThemeManager
from src.ui.components.guide_setup import GuideManager
from src.ui.components.search_setup import SearchManager

class ScreenManager:
    def __init__(self, page: ft.Page, data_manager, auth_manager):
        self.page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.halaman_terakhir = "home"
        self.filter_terakhir = "all"
        self.tema_aktif = "1"
        self.theme = ThemeManager.get_theme(self.tema_aktif)
        self.current_view_instance = None
        self.guide_manager = GuideManager(self.page, self.theme)

        def on_search_submit(query):
            self.tampilkan_katalog(filter_kategori="all", search_query=query)
        self.search_manager = SearchManager(self.page, self.theme, on_search_submit)
        self.guide_manager = GuideManager(self.page, self.theme)

    def update_theme(self, pilihan_tema):
        self.tema_aktif = pilihan_tema
        self.theme = ThemeManager.get_theme(self.tema_aktif)
        if self.guide_manager:
            self.guide_manager.apply_theme(self.theme)
        if hasattr(self, "search_manager") and self.search_manager:
            self.search_manager.apply_theme(self.theme)

    def bersihkan_layar(self):
        dlg = getattr(self.page, "dialog", None)
        if dlg:
            try:
                dlg.open = False
            except:
                pass
        self.page.controls.clear()
        self.page.update()

    async def _jalankan_transisi(self, pesan, target_class, *args, **kwargs):
        if hasattr(self, "search_manager") and self.search_manager:
            self.search_manager.hide()

        if hasattr(self, "guide_manager") and self.guide_manager:
            self.guide_manager.set_visible(False)

        layar, petals, circle, dots = buat_bloom_screen(pesan, self.theme)
        self.bersihkan_layar()
        self.page.add(layar)
        await animasi_bloom(petals, circle, dots)
        self.bersihkan_layar()

        self.current_view_instance = target_class(
            self.page, self.data_manager, self.auth_manager,
            self, self.theme, *args, **kwargs
        )
        self.page.add(self.current_view_instance)

        if self.guide_manager:
            halaman_diizinkan = ["UIHome", "UIKatalog"]
            if target_class.__name__ in halaman_diizinkan:
                self.guide_manager.set_visible(True)
            else:
                self.guide_manager.set_visible(False)
            # -----------------------------------------

        self.page.update()

        if hasattr(self.current_view_instance, '_muat_sections'):
            self.page.run_task(self.current_view_instance._muat_sections)

    def tampilkan_home(self, pilihan_tema=None):
        self.halaman_terakhir = "home"
        if pilihan_tema: self.update_theme(pilihan_tema)
        from src.ui.ui_home import UIHome
        self.page.run_task(self._jalankan_transisi, "Entering RadarAni...", UIHome)

    def tampilkan_katalog(self, filter_kategori="all", search_query=""):
        self.halaman_terakhir = "katalog"
        self.filter_terakhir = filter_kategori
        from src.ui.ui_katalog import UIKatalog
        self.page.run_task(self._jalankan_transisi, "Browsing Anime...", UIKatalog,
                           filter_kategori=filter_kategori, search_query=search_query)

    def tampilkan_login(self):
        self.halaman_terakhir = "login"
        if hasattr(self, "guide_manager") and self.guide_manager:
            self.guide_manager.set_visible(False)
        if hasattr(self, "search_manager") and self.search_manager:
            self.search_manager.hide()

        from src.ui.ui_login import UILogin
        self.bersihkan_layar()
        login_view = UILogin(self.page, self.data_manager, self.auth_manager, self, self.theme)
        self.page.add(login_view)
        self.page.update()

    def tampilkan_detail(self, anime_id: str):
        self.halaman_terakhir = "detail"
        from src.ui.ui_detail import UIDetail
        self.page.run_task(self._jalankan_transisi, "Opening Anime Data...", UIDetail, anime_id)

    def tampilkan_profil(self):
        self.halaman_terakhir = "profil"
        from src.ui.ui_profile import UIProfile
        self.page.run_task(self._jalankan_transisi, "Loading Your Space...", UIProfile)

    def tampilkan_analytics(self):
        self.halaman_terakhir = "analytics"
        from src.ui.ui_analytics import UIAnalytics
        self.page.run_task(self._jalankan_transisi, "Analyzing Your Taste...", UIAnalytics)

    def tampilkan_scraping(self):
        self.halaman_terakhir = "scraping"
        from src.ui.ui_scraping import UIScraping
        self.page.run_task(self._jalankan_transisi, "Fetching Anime Data...", UIScraping)

    def kembali_ke_asal(self):
        if self.halaman_terakhir == "katalog":
            self.tampilkan_katalog(filter_kategori=self.filter_terakhir)
        elif self.halaman_terakhir == "analytics":
            self.tampilkan_analytics()
        else:
            self.tampilkan_home()

    def buka_pencarian_global(self):
        if getattr(self, "halaman_terakhir", "") == "login":
            return

        if hasattr(self, "search_manager") and self.search_manager:
            self.search_manager.show()