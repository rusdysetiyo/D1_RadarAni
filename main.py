import flet as ft
from src.managers.data_manager import DataManager
from src.managers.auth_manager import AuthManager
from src.managers.screen_manager import ScreenManager

def main(page: ft.Page):
    page.title = "RadarAni"
    page.window.width = 1280
    page.window.height = 720
    page.padding = 0
    page.bgcolor = "#F5EEF2"

    data_manager = DataManager()
    auth_manager = AuthManager(data_manager)
    screen_manager = ScreenManager(page, data_manager, auth_manager)

    # Cek apakah ada user yang sudah login sebelumnya (sesi tersimpan)
    user_id_tersimpan = data_manager.baca_sesi()

    if user_id_tersimpan:
        # Jika ada sesi, set user aktif dan langsung ke Home
        auth_manager.set_user_aktif(user_id_tersimpan)
        screen_manager.tampilkan_home()
    else:
        # Jika tidak ada sesi, tampilkan layar login
        screen_manager.tampilkan_login()

if __name__ == '__main__':
    ft.run(main)
