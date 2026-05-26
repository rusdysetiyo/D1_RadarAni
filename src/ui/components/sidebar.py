# src/ui/components/sidebar.py

import flet as ft

def _nav_item(kanji, label, style, on_click):
    return ft.TextButton(
        content=ft.Row(
            controls=[
                ft.Text(kanji, font_family="DotGothic16", size=16, weight=ft.FontWeight.BOLD, width=28, text_align=ft.TextAlign.CENTER),
                ft.Text(label, size=13, weight=ft.FontWeight.W_500),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ), style=style, width=216, on_click=on_click,
    )


class Sidebar(ft.Container):
    def __init__(self, ctx, halaman_aktif="home"):
        super().__init__()
        self.ctx = ctx
        self.halaman_aktif = halaman_aktif
        self.theme = ctx.theme

        self.width = 0
        self.bgcolor = None
        self.animate_size = ft.Animation(duration=280, curve=ft.AnimationCurve.EASE_OUT)
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.content = self._build()

    def _build(self):
        nav_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: self.theme["text_main"]},
            bgcolor={ft.ControlState.HOVERED: self.theme["bg_secondary"], ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            alignment=ft.Alignment(-1, 0),
        )
        active_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: self.theme["primary"]},
            bgcolor={ft.ControlState.DEFAULT: self.theme["primary_light"]},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            alignment=ft.Alignment(-1, 0),
        )
        danger_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: self.theme["text_secondary"]},
            bgcolor={ft.ControlState.HOVERED: self.theme["bg_secondary"], ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            alignment=ft.Alignment(-1, 0),
        )

        def _s(halaman):
            return active_s if self.halaman_aktif == halaman else nav_s

        sm = self.ctx.screen_manager
        nav_items = [
            _nav_item("ホ", "Home",       _s("home"),      lambda _: sm.tampilkan_home()),
            _nav_item("覧", "Anime List", _s("katalog"),   lambda _: sm.tampilkan_katalog()),
            _nav_item("追", "Add Anime",  _s("scraping"),  lambda _: sm.tampilkan_scraping()),
            _nav_item("析", "Analytics",  _s("analytics"), lambda _: sm.tampilkan_analytics()),
            _nav_item("人", "Profile",    _s("profil"),    lambda _: sm.tampilkan_profil()),
        ]

        return ft.Container(
            width=240, expand=True,
            gradient=ft.LinearGradient(
                begin=ft.Alignment(0, -1), end=ft.Alignment(0, 1),
                colors=[self.theme["bg_secondary"], self.theme["bg"]],
            ),
            border=ft.Border(right=ft.BorderSide(1, self.theme["border_color"])),
            padding=ft.padding.only(left=12, right=12, top=24, bottom=24),
            content=ft.Column(
                controls=[
                    ft.Row(
                        [ft.IconButton(
                            icon=ft.Icons.CHEVRON_LEFT,
                            icon_size=20,
                            on_click=self.toggle,
                            style=ft.ButtonStyle(
                                overlay_color=ft.Colors.TRANSPARENT,
                                icon_color={
                                    ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, self.theme["primary"]),
                                    ft.ControlState.DEFAULT: self.theme["primary"],
                                }
                            )
                        )],
                        alignment=ft.MainAxisAlignment.END,
                    ),
                    ft.Container(height=8),
                    *nav_items,
                    ft.Container(expand=True),
                    ft.Divider(color=self.theme["border_color"], height=1, thickness=1),
                    ft.Container(height=4),
                    ft.TextButton(
                        content=ft.Row(
                            controls=[
                                ft.Text("出", font_family="DotGothic16", size=16, weight=ft.FontWeight.BOLD, width=28, text_align=ft.TextAlign.CENTER),
                                ft.Text("Log Out", size=13),
                            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ), style=danger_s, width=216,
                        on_click=self._konfirmasi_logout,
                    ),
                ], spacing=2, expand=True,
            ),
        )

    def toggle(self, e=None):
        self.width = 0 if self.width == 240 else 240
        self.update()

    def _konfirmasi_logout(self, _):
        def batal(e):
            dlg.open = False
            self.ctx.page.update()

        def ya(e):
            dlg.open = False
            self.ctx.page.update()
            self.ctx.auth_manager.logout()
            self.ctx.screen_manager.tampilkan_login()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=self.theme["primary"], size=20),
                ft.Text("Confirm Logout", weight=ft.FontWeight.W_800, color=self.theme["primary"], size=14),
            ], spacing=8),
            content=ft.Text("Are you sure you want to log out of your account?", size=12, color=self.theme["text_muted"]),
            actions=[
                ft.OutlinedButton("Cancel", on_click=batal, style=ft.ButtonStyle(
                    side=ft.BorderSide(1.5, self.theme["border_color"]),
                    shape=ft.RoundedRectangleBorder(radius=8),
                    color=self.theme["text_muted"],
                )),
                ft.ElevatedButton("Log Out", on_click=ya, style=ft.ButtonStyle(
                    bgcolor=self.theme["primary"], color=self.theme["card"],
                    shape=ft.RoundedRectangleBorder(radius=8),
                )),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=self.theme["card"],
        )
        self.ctx.page.overlay.append(dlg)
        dlg.open = True
        self.ctx.page.update()