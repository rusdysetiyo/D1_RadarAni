import flet as ft

class HeroBanner(ft.Container):
    def __init__(self, theme, on_click_callback):
        super().__init__()
        self.theme = theme
        self.on_click_callback = on_click_callback
        self.anime_id = None

        self._rec_title = ft.Text("—", size=28, color="#FFFFFF", weight=ft.FontWeight.BOLD, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS)
        self._rec_reason = ft.Text("Based on your top dimension", size=12, color="#CCFFFFFF")
        self._rec_synopsis = ft.Text("", size=12, color="#CCCCCC", max_lines=3, overflow=ft.TextOverflow.ELLIPSIS)
        self._rec_image = ft.Image(src=None, width=36, height=50, fit="cover", visible=False)
        self._rec_image_container = ft.Image(src=None, visible=False, width=float("inf"), height=340, fit=ft.BoxFit.COVER, expand=True)
        self._rec_btn_ref = ft.Ref[ft.ElevatedButton]()

        self.height = 340
        self.border_radius = 16
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.on_hover = self._banner_hover
        self.animate = ft.Animation(duration=250, curve=ft.AnimationCurve.EASE_OUT)
        self.scale = 1.0
        self.shadow = ft.BoxShadow(spread_radius=0, blur_radius=24, color="#22000000", offset=ft.Offset(0, 6))

        self.content = ft.Stack(
            expand=True,
            controls=[
                self._rec_image_container,
                ft.Container(expand=True, bgcolor=ft.Colors.with_opacity(0.2, ft.Colors.BLACK)),
                ft.Container(
                    expand=True,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment(-1.0, 0), end=ft.Alignment(1.0, 0),
                        colors=["#F2000000", "#B3000000", "#4D000000", ft.Colors.TRANSPARENT],
                        stops=[0.0, 0.45, 0.8, 1.0],
                    ),
                ),
                ft.Container(
                    expand=True, padding=ft.padding.only(left=50, right=50, top=0, bottom=0),
                    alignment=ft.Alignment.CENTER_LEFT,
                    content=ft.Column(
                        width=600, alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.START,
                        controls=[
                            ft.Container(
                                content=ft.Row([
                                    ft.Container(width=3, height=14, bgcolor=self.theme["primary"], border_radius=2),
                                    ft.Text("RECOMMENDED FOR YOU", size=10, color=self.theme["primary"], weight=ft.FontWeight.W_800),
                                ], spacing=6),
                            ),
                            ft.Container(height=8),
                            self._rec_title,
                            ft.Container(height=4),
                            self._rec_reason,
                            ft.Container(height=12),
                            self._rec_synopsis,
                            ft.Container(height=24),
                            ft.ElevatedButton(
                                ref=self._rec_btn_ref, visible=False,
                                content=ft.Row([
                                    ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=20),
                                    ft.Text("View Details", size=14, weight=ft.FontWeight.W_700),
                                ], spacing=6, tight=True),
                                style=ft.ButtonStyle(
                                    bgcolor={ft.ControlState.DEFAULT: self.theme["primary"], ft.ControlState.HOVERED: ft.Colors.WHITE},
                                    color={ft.ControlState.DEFAULT: self.theme["bg"], ft.ControlState.HOVERED: self.theme["primary"]},
                                    side={ft.ControlState.HOVERED: ft.BorderSide(1.5, self.theme["primary"]), ft.ControlState.DEFAULT: ft.BorderSide(0, ft.Colors.TRANSPARENT)},
                                    shape=ft.RoundedRectangleBorder(radius=6), padding=ft.padding.symmetric(horizontal=24, vertical=14), elevation=0,
                                ),
                                on_click=lambda _: self.on_click_callback(),
                            ),
                        ], spacing=0,
                    ),
                ),
            ],
        )

    def _banner_hover(self, e):
        is_hover = str(e.data).lower() == "true"
        self.scale = 1.01 if is_hover else 1.0
        try:
            if self.page: self.update()
        except: pass

    def _hide_rec_empty_state(self):
        self._rec_image_container.visible = False
        if self._rec_btn_ref.current:
            self._rec_btn_ref.current.visible = False

    def _show_rec_content(self):
        self._rec_image_container.visible = True
        if self._rec_btn_ref.current:
            self._rec_btn_ref.current.visible = True