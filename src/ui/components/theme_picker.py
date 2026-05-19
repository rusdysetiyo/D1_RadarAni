import flet as ft


class ThemePicker:
    def __init__(self, page: ft.Page, screen_manager, current_theme: dict):
        self.page = page
        self.screen_manager = screen_manager
        self.theme = current_theme

        self.TEMA_INFO = {
            "1": ("Sakura", ["#FF759E", "#C3D3B4"]),
            "2": ("Matcha", ["#5C805C", "#DDA7B0"]),
            "5": ("Pastel", ["#839CCB", "#F2A3A1"]),
            "4": ("Ocean", ["#3B82F6", "#1D4ED8"]),
            "3": ("Dark", ["#1a1a2e", "#E8CEDB"]),
            "6": ("Aurora", ["#A855F7", "#10B981"]),
            "7": ("Cyber", ["#3B82F6", "#FACC15"]),
            "8": ("Dusk", ["#F45990", "#F0C89B"]),
        }

        self.title_column = ft.Column(spacing=2, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.content_column = ft.Column(spacing=8, tight=True)

        self.dialog = ft.AlertDialog(
            title=ft.Container(
                content=self.title_column,
                padding=ft.padding.only(bottom=4),
            ),
            content=ft.Container(
                content=self.content_column,
                padding=ft.padding.symmetric(vertical=8, horizontal=4),
                width=340,
            ),
            bgcolor=self.theme["card"],
            shape=ft.RoundedRectangleBorder(radius=18),
        )

        self.page.overlay.append(self.dialog)

    def _on_theme_selected(self, e):
        pilihan = e.control.data
        self.dialog.open = False
        self.page.update()
        self.screen_manager.tampilkan_home(pilihan_tema=pilihan)

    def _section_label(self, teks):
        return ft.Container(
            content=ft.Row([
                ft.Container(width=20, height=1, bgcolor=self.theme["border_color"]),
                ft.Text(teks, size=9, color=self.theme["text_secondary"], weight=ft.FontWeight.W_600),
                ft.Container(width=20, height=1, bgcolor=self.theme["border_color"]),
            ], spacing=6, alignment=ft.MainAxisAlignment.CENTER),
            width=340,
        )

    def _bikin_card(self, key_tema, nama, warna_list, tema_aktif):
        is_active = key_tema == tema_aktif

        circle = ft.Stack(
            controls=[
                ft.Container(
                    width=44, height=44,
                    shape=ft.BoxShape.CIRCLE,
                    gradient=ft.LinearGradient(
                        begin=ft.Alignment.TOP_LEFT,
                        end=ft.Alignment.BOTTOM_RIGHT,
                        colors=warna_list,
                    ),
                ),
                ft.Container(
                    content=ft.Icon(ft.Icons.CHECK, size=8, color="#ffffff"),
                    width=14, height=14,
                    border_radius=7,
                    bgcolor=warna_list[0],
                    border=ft.border.all(2, self.theme["card"]),
                    alignment=ft.Alignment.CENTER,
                    right=0, bottom=0,
                    visible=is_active,
                ),
            ],
            width=44, height=44,
        )

        return ft.GestureDetector(
            content=ft.Container(
                content=ft.Column([
                    circle,
                    ft.Text(
                        nama, size=10,
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.NORMAL,
                        color=self.theme["primary"] if is_active else self.theme["text_main"],
                        text_align=ft.TextAlign.CENTER,
                        max_lines=1,
                    ),
                ], spacing=8, tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                width=76,
                padding=ft.padding.symmetric(horizontal=4, vertical=10),
                border_radius=12,
                bgcolor=self.theme.get("surface", self.theme["bg"]) if is_active else ft.Colors.TRANSPARENT,
                border=ft.border.all(
                    1.5 if is_active else 0.5,
                    self.theme["primary"] if is_active else self.theme["border_color"]
                ),
            ),
            data=key_tema,
            on_tap=self._on_theme_selected,
        )

    def show(self, e=None):
        tema_aktif = getattr(self.screen_manager, "tema_aktif", "1")
        nama_aktif = self.TEMA_INFO.get(tema_aktif, ("—", []))[0]

        self.title_column.controls = [
            ft.Text("Select theme", size=15, weight=ft.FontWeight.W_600, color=self.theme["text_main"],
                    text_align=ft.TextAlign.CENTER),
            ft.Text(f"Active: {nama_aktif}", size=11, color=self.theme["text_secondary"],
                    text_align=ft.TextAlign.CENTER),
        ]

        baris_light = ft.Row(
            controls=[self._bikin_card(k, v[0], v[1], tema_aktif) for k, v in self.TEMA_INFO.items() if
                      k in ["1", "2", "5", "4"]],
            alignment=ft.MainAxisAlignment.CENTER, spacing=6,
        )

        baris_dark = ft.Row(
            controls=[self._bikin_card(k, v[0], v[1], tema_aktif) for k, v in self.TEMA_INFO.items() if
                      k in ["3", "6", "7", "8"]],
            alignment=ft.MainAxisAlignment.CENTER, spacing=6,
        )

        self.content_column.controls = [
            self._section_label("Light"),
            baris_light,
            self._section_label("Dark / Dimmed"),
            baris_dark,
        ]

        self.dialog.open = True
        self.page.update()

    def get_button(self):
        return ft.IconButton(
            icon=ft.Icons.PALETTE_OUTLINED,
            tooltip="Change Theme",
            on_click=self.show,
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.TRANSPARENT,
                icon_color={
                    ft.ControlState.HOVERED: ft.Colors.with_opacity(0.8, self.theme["text_main"]),
                    ft.ControlState.DEFAULT: self.theme["text_main"],
                }
            )
        )