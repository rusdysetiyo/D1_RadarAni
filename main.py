import flet as ft
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.managers.data_manager import DataManager
from src.managers.auth_manager import AuthManager
from src.managers.screen_manager import ScreenManager
from src.managers.keyboard_manager import KeyboardManager


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "RadarAni"
    page.padding = 0
    page.spacing = 0

    page.fonts = {
        "Yomogi": "fonts/Yomogi/Yomogi-Regular.ttf",
        "Soopafresh": "fonts/soopafresh/soopafre.ttf",
        "DotGothic16": "fonts/DotGothic16/DotGothic16-Regular.ttf",
        "Mofuji04": "fonts/Mofuji/mofuji04.ttf",
        "Hitchcut": "fonts/Hitchcut/Hitchcut-Regular.ttf",
        "KiwiSoda": "fonts/KiwiSoda/KiwiSoda.ttf",
        "Clayful": "fonts/Clayful.ttf",
    }

    page.bgcolor = "transparent"
    page.decoration = ft.BoxDecoration(
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1.0, -1.0),
            end=ft.Alignment(1.0, 1.0),
            colors=["#E0F2FE", "#FDF2F8"],
        )
    )

    page.theme = ft.Theme(font_family="IBMPlexSansJP")

    try:
        page.window.width, page.window.height = 1100, 750
        page.window.min_width, page.window.min_height = 900, 600
    except AttributeError:
        page.window_width, page.window_height = 1100, 750
        page.window_min_width, page.window_min_height = 900, 600

    data_manager = DataManager()
    auth_manager = AuthManager(data_manager)
    screen_manager = ScreenManager(page, data_manager, auth_manager)
    kb_manager = KeyboardManager(page, screen_manager)

    screen_manager.tampilkan_login()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")