<<<<<<< Updated upstream
#screen_manager
=======
import flet as ft

class ScreenManager:
    def __init__(self, page: ft.Page, data_manager, auth_manager):
        self.page         = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager

    def bersihkan_layar(self):
        self.page.controls.clear()

    def tampilkan_login(self):
        print("Pindah ke layar: Login (belum ada UI-nya)")
        # from src.ui.ui_login import UILogin
        # self.bersihkan_layar()
        # self.page.add(UILogin(self.page, self.auth_manager, self))
        # self.page.update()

    def tampilkan_dashboard(self):
        from ui.ui_dashboard import UIDashboard
        self.bersihkan_layar()
        self.page.add(UIDashboard(self.page, self.data_manager, self.auth_manager, self))
        self.page.update()

    def tampilkan_detail(self, anime_id: str):
        print(f"Pindah ke layar: Detail Anime -> {anime_id}")
        from ui.ui_detail import UIDetail
        self.bersihkan_layar()
        
        layout_detail = ft.Column(          # ← Column TIDAK punya bgcolor
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            controls=[
                ft.Container(               # ← bgcolor ada di Container, bukan Column
                    bgcolor="#F4F3F8",
                    padding=ft.padding.all(24),
                    content=UIDetail(self.page, self.data_manager, self, anime_id)
                )
            ]
        )

        self.page.add(layout_detail)        
        self.page.update()


    def tampilkan_profil(self):
        print("Pindah ke layar: Profil User")
>>>>>>> Stashed changes
