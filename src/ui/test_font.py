import flet as ft
import os

print(os.path.abspath("assets/fonts/Bonbon-Regular.ttf"))
print(os.path.exists("assets/fonts/Bonbon-Regular.ttf"))


def main(page: ft.Page):

    page.fonts = {
        "Kiwisoda": "/fonts/Kiwisoda.ttf",
        "Rascal": "/fonts/RASCAL_.ttf",
        "Mofuji04": "/fonts/mofuji04.ttf",
    }

    page.add(
        ft.Text(
            "abc",
            font_family="Rascal",
            size=40,
        )
    )

    page.add(
        ft.Text(
            "レーダアニ",
            font_family="Kiwisoda",
            size=40,
        )
    )

    page.add(
        ft.Text(
            "レーダアニ",
            font_family="Mofuji04",
            size=40,
        )
    )

ft.app(target=main, assets_dir="assets")