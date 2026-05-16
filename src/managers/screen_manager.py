import flet as ft

class ScreenManager:
    def __init__(self, page: ft.Page, data_manager, auth_manager):
        self.page         = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.halaman_terakhir = "home"
        self.filter_terakhir = "all"
        self._detail_stack = []

    def bersihkan_layar(self):
        self.page.controls.clear()

    def tampilkan_login(self):
        from src.ui.ui_login import UILogin
        
        self.bersihkan_layar()
        self.page.add(UIDashboard(self.page, self.data_manager, self.auth_manager, self))
        self.page.update()

    def tampilkan_detail(self, anime_id: str):
        from src.ui.ui_detail import UIDetail
        
        # Push anime_id yang sedang aktif ke stack sebelum pindah
        if self.halaman_terakhir == "detail" and hasattr(self, '_current_anime_id'):
            self._detail_stack.append(self._current_anime_id)
        else:
            # Masuk detail dari halaman lain → reset stack
            self._detail_stack.clear()
            self._halaman_sebelum_detail = self.halaman_terakhir
        
        self._current_anime_id = anime_id
        self.halaman_terakhir = "detail"
        self.page.run_task(self._jalankan_transisi, "Opening Anime Data...", UIDetail, anime_id=anime_id)

    def tampilkan_profil(self):
        from src.ui.ui_profile import UIProfile
        self.page.run_task(self._jalankan_transisi, "Loading Your Space...", UIProfile)

    def tampilkan_analytics(self):
        self.halaman_terakhir = "analytics"

        from src.ui.ui_analytics import UIAnalytics
        self.page.run_task(
            self._jalankan_transisi,
            "Analyzing Your Taste...",
            UIAnalytics
        )

    def tampilkan_scraping(self):
        from src.ui.ui_scraping import UIScraping
        self.page.run_task(self._jalankan_transisi, "Fetching Anime Data...", UIScraping)

    def kembali_ke_asal(self):
        if self._detail_stack:
            prev_anime_id = self._detail_stack.pop()
            self._current_anime_id = prev_anime_id
            from src.ui.ui_detail import UIDetail
            self.page.run_task(self._jalankan_transisi, "Going Back...", UIDetail, anime_id=prev_anime_id)
            return
        
        asal = getattr(self, '_halaman_sebelum_detail', None)
        if asal == "katalog":
            self.tampilkan_katalog(filter_kategori=self.filter_terakhir)
        elif asal == "analytics":
            self.tampilkan_analytics()
        else:
            self.tampilkan_home()