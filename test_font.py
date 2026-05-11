import flet as ft


C_BORDER = "#EDE0E8"
C_BG2    = "#F5EEF2"
C_TEXT2  = "#8B6A7A"


def main(page: ft.Page):
    page.title  = "Hover Animation Test"
    page.bgcolor = "#FCF8FA"
    page.padding = 40

    class TestCard(ft.Container):
        def __init__(self):
            super().__init__()
            self.width         = 140
            self.border        = ft.border.all(1, C_BORDER)
            self.border_radius = 10
            self.clip_behavior = ft.ClipBehavior.HARD_EDGE
            self.on_hover      = self._on_hover
            self.scale         = 1.0
            self.shadow        = None
            self.animate       = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
            self.animate_scale = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)

            # Status pill
            self._status_pill = ft.Container(
                content=ft.Text("not rated", size=8, color=C_TEXT2,
                                weight=ft.FontWeight.BOLD),
                bgcolor=ft.Colors.with_opacity(0.9, C_BG2),
                border_radius=12,
                padding=ft.padding.symmetric(horizontal=6, vertical=3),
                top=8, right=8,
                opacity=1.0,
                animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            )

            # Fav icon — pakai offset bukan top
            self._fav_icon = ft.Container(
                content=ft.Text("★", size=20, color="#EC407A"),
                top=8, right=8,
                opacity=0,
                offset=ft.Offset(0, -1),
                rotate=ft.Rotate(angle=-1, alignment=ft.Alignment(0, 0)),
                animate_offset=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
                animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
                animate_rotation=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
            )

            # Poster placeholder
            poster = ft.Container(
                width=140, height=162,
                bgcolor="#EDE0E8",
                content=ft.Text("Anime Poster", size=9, color=C_TEXT2,
                                text_align=ft.TextAlign.CENTER),
                alignment=ft.Alignment(0, 0),
            )

            # Info bawah
            info = ft.Container(
                padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
                bgcolor="#FFFFFF",
                content=ft.Column(
                    controls=[
                        ft.Text("Anime Title", size=10, color="#3D2535",
                                weight=ft.FontWeight.BOLD),
                        ft.Text("★ 8.5  ·  you: N/A", size=9, color="#B0909A"),
                    ],
                    spacing=2, tight=True,
                ),
            )

            self.content = ft.Column(
                controls=[
                    ft.Stack(
                        controls=[poster, self._status_pill, self._fav_icon],
                        width=140, height=162,
                    ),
                    info,
                ],
                spacing=0, tight=True,
            )

        def _on_hover(self, e):
            is_hovered = str(e.data).lower() == "true"

            if is_hovered:
                self._status_pill.opacity = 0
                self._fav_icon.opacity    = 1.0
                self._fav_icon.offset     = ft.Offset(0, 0)
                self._fav_icon.rotate     = ft.Rotate(angle=0, alignment=ft.Alignment(0, 0))
            else:
                self._status_pill.opacity = 1.0
                self._fav_icon.opacity    = 0
                self._fav_icon.offset     = ft.Offset(0, -1)
                self._fav_icon.rotate     = ft.Rotate(angle=-1, alignment=ft.Alignment(0, 0))

            self.border = ft.border.all(
                1.5 if is_hovered else 1,
                "#EC407A" if is_hovered else C_BORDER,
            )
            self.scale  = 1.03 if is_hovered else 1.0
            self.shadow = ft.BoxShadow(
                spread_radius=1, blur_radius=12,
                color=ft.Colors.with_opacity(0.3, "#EC407A"),
                offset=ft.Offset(0, 4),
            ) if is_hovered else None

            self._status_pill.update()
            self._fav_icon.update()
            self.update()

    page.add(
        ft.Row(
            controls=[TestCard(), TestCard(), TestCard()],
            spacing=16,
        )
    )


ft.app(target=main)