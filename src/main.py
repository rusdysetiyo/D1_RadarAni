import flet as ft
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.managers.data_manager import DataManager
from src.managers.auth_manager import AuthManager
from src.managers.screen_manager import ScreenManager


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.LIGHT
    page.title = "RadarAni"
    page.padding = 0
    page.spacing = 0


    page.bgcolor = "transparent"

    page.decoration = ft.BoxDecoration(
        gradient=ft.LinearGradient(
            begin=ft.Alignment(-1.0, -1.0),
            end=ft.Alignment(1.0, 1.0),
            colors=["#E0F2FE", "#FDF2F8"],
        )
    )

    page.fonts = {
        "Zen Maru": "/fonts/ZenMaruGothic-Regular.ttf",
        "M Plus": "/fonts/MPLUSRounded1c-Regular.ttf"
    }
    page.theme = ft.Theme(font_family="Zen Maru")

    try:
        page.window.width = 1100
        page.window.height = 750
        page.window.min_width = 900
        page.window.min_height = 600
    except AttributeError:
        page.window_width = 1100
        page.window_height = 750
        page.window_min_width = 900
        page.window_min_height = 600

    data_manager = DataManager()
    auth_manager = AuthManager(data_manager)
    screen_manager = ScreenManager(page, data_manager, auth_manager)

    screen_manager.tampilkan_login()


if __name__ == "__main__":
    assets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
    ft.run(main, assets_dir="assets")