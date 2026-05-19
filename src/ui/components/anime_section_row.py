import flet as ft


class AnimeSectionRow(ft.Container):
    def __init__(self, judul, kategori_katalog, theme, screen_manager, hover_callback):
        super().__init__()
        self.theme = theme

        self.inner_row = ft.Row(scroll=ft.ScrollMode.ALWAYS, spacing=14)

        self.padding = ft.padding.only(top=10)
        self.opacity = 1.0
        self.animate_opacity = 300
        self.scale = 1.0
        self.animate_scale = 300
        self.on_hover = lambda e: hover_callback(e, self)

        header = ft.Container(
            padding=ft.padding.only(left=20, right=20, top=20, bottom=8),
            content=ft.Row(
                controls=[
                    ft.Container(width=4, height=16, bgcolor=theme["primary"], border_radius=4),
                    ft.Text(judul, font_family="Soopafresh", size=18, color=theme["text_main"]),
                    ft.Container(expand=True),
                    ft.TextButton(
                        "View All →",
                        style=ft.ButtonStyle(
                            overlay_color=ft.Colors.TRANSPARENT,
                            color={
                                ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, theme["primary"]),
                                ft.ControlState.DEFAULT: theme["primary"],
                            },
                            padding=ft.padding.all(0),
                        ),
                        on_click=lambda _: screen_manager.tampilkan_katalog(filter_kategori=kategori_katalog),
                    ),
                ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self.content = ft.Column(
            controls=[
                header,
                ft.Container(content=self.inner_row, padding=ft.padding.only(left=24, right=24, top=5, bottom=15)),
            ], spacing=0,
        )