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

    test_user_id = "U001"
    auth_manager.set_user_aktif(test_user_id)
    screen_manager.tampilkan_home()

if __name__ == '__main__':
    ft.run(main)
