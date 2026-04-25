import sys
import os
import flet as ft
import flet.canvas as cv
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from managers.data_manager import DataManager
from managers.auth_manager import AuthManager
from managers.screen_manager import ScreenManager

def main(page: ft.Page):
    

    page.title = "Anime Detail"
    page.bgcolor = "#F4F3F8"
    page.fonts = {
        "Poppins": "https://fonts.gstatic.com/s/poppins/v20/pxiEyp8kv8JHgFVrJJfecg.woff2",
    }
    page.theme = ft.Theme(font_family="Poppins")
    page.padding = 0
    page.scroll = "auto"

    data_manager   = DataManager()

    auth_manager   = AuthManager(data_manager)

    screen_manager = ScreenManager(page, data_manager, auth_manager)

    screen_manager.tampilkan_detail( "A034")

    
    page.update()

if __name__ == "__main__":
    ft.app(target=main)