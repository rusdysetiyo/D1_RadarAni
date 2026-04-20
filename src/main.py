import flet as ft

import sys

import os



sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))



from src.managers.data_manager import DataManager

from src.managers.auth_manager import AuthManager

from src.managers.screen_manager import ScreenManager





def main(page: ft.Page):

    page.title       = "RadarAni"

    page.window_width  = 1100

    page.window_height = 750

    page.window_min_width  = 900

    page.window_min_height = 600

    page.padding     = 0

    page.spacing     = 0

    page.bgcolor     = "#FCF8FA"

    page.fonts       = {

        "Sora": "https://fonts.gstatic.com/s/sora/v12/xMQOuFFYT72X5wkB_18qmnndmSdSn3-KIwNhBti0.woff2"

    }

    page.theme = ft.Theme(font_family="Sora")



    data_manager   = DataManager()

    auth_manager   = AuthManager(data_manager)

    screen_manager = ScreenManager(page, data_manager, auth_manager)



    screen_manager.tampilkan_dashboard()

    page.update()





if __name__ == "__main__":
    ft.run(main)