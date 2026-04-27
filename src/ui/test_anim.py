import flet as ft


def main(page: ft.Page):
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 50
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    daftar_kotak = []

    def animasikan(e, kotak_terpilih):
        # FIX: Tangkap sensor mau dia berupa teks "true" atau boolean True
        is_hover = str(e.data).lower() == "true"

        for k in daftar_kotak:
            if is_hover:
                if k == kotak_terpilih:
                    k.scale = 1.05  # Balik pakai desimal biasa, aman!
                    k.opacity = 1.0
                else:
                    k.scale = 0.85
                    k.opacity = 0.3
            else:
                k.scale = 1.0
                k.opacity = 1.0
            k.update()

    def bikin_kotak(warna, teks):
        kotak = ft.Container(
            content=ft.Text(teks, size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            width=700, height=180,
            bgcolor=warna,
            border_radius=15,
            alignment=ft.Alignment(0, 0),
            scale=1.0,
            opacity=1.0,
            # FIX: Tulis durasi angkanya aja (300 milidetik), gak usah pakai ft.Animation
            animate_scale=300,
            animate_opacity=300,
        )
        kotak.on_hover = lambda e: animasikan(e, kotak)
        return kotak

    daftar_kotak.extend([
        bikin_kotak("#C07090", "🔥 Global Trending"),
        bikin_kotak("#9060A0", "⭐ Your Recent Ratings"),
        bikin_kotak("#C08030", "🎌 Top Unrated")
    ])

    page.add(ft.Column(daftar_kotak, spacing=30))


if __name__ == "__main__":
    try:
        ft.run(main)
    except AttributeError:
        ft.app(target=main)