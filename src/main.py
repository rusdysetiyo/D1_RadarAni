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

    # Cek apakah ada sesi aktif yang tersimpan, langsung masuk jika ada
    sesi_user_id = data_manager.baca_sesi()
    if sesi_user_id and data_manager.get_user_by_id(sesi_user_id):
        auth_manager.set_user_aktif(sesi_user_id)
        screen_manager.tampilkan_home()
    else:
        screen_manager.tampilkan_login()

if __name__ == '__main__':
    ft.run(main)
