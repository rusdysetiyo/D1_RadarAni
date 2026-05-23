import flet as ft

class RadarAniLogo(ft.Column):
    def __init__(self, theme, font_size=24, subtitle_size=10, alignment=ft.CrossAxisAlignment.START):
        self.theme = theme
        is_centered = alignment in [ft.CrossAxisAlignment.CENTER, "center"]

        logo_row = ft.Row(
            controls=[
                ft.Text(
                    huruf,
                    font_family="Hitchcut",
                    size=font_size,
                    color=self.theme["logo_1" if i % 2 == 0 else "logo_2"]
                )
                for i, huruf in enumerate("RadarAni")
            ],
            spacing=0,
            tight=True,
            alignment=ft.MainAxisAlignment.CENTER if alignment == ft.CrossAxisAlignment.CENTER else ft.MainAxisAlignment.START
        )

        subtitle = ft.Text(
            "レーダアニ",
            font_family="Mofuji04",
            size=subtitle_size,
            color=self.theme["text_muted"],
            text_align = ft.TextAlign.CENTER if is_centered else ft.TextAlign.LEFT
        )

        super().__init__(
            controls=[logo_row, subtitle],
            spacing=0,
            tight=True,
            horizontal_alignment=alignment
        )