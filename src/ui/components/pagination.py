import flet as ft
import math

class PaginationBar(ft.Container):
    def __init__(self, theme, on_page_change):
        super().__init__()
        self.theme = theme
        self.on_page_change = on_page_change
        self._halaman = 1
        self._total_pg = 1
        self._is_expanded = False

        self._pagination_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=5)
        self._pill_container = ft.Container(
            content=self._pagination_row, bgcolor=theme["card"],
            padding=ft.padding.symmetric(horizontal=8, vertical=6), border_radius=30,
            opacity=0, offset=ft.Offset(0, 0.4), disabled=True,
            animate_opacity=250, animate_offset=ft.Animation(250, ft.AnimationCurve.DECELERATE),
        )

        self._dropdown_text = ft.Text("01", size=13, weight=ft.FontWeight.BOLD, color=theme["text_main"])
        self._dropdown_icon = ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=theme["text_main"], rotate=0,
                                      animate_rotation=ft.Animation(250, ft.AnimationCurve.DECELERATE))

        select_page_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Page:", size=12, weight=ft.FontWeight.W_500, color=theme["text_secondary"]),
                ft.Container(
                    content=ft.Row([self._dropdown_text, self._dropdown_icon], spacing=2, alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=theme["primary_light"], padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    border=ft.border.all(1, theme["border_color"]), border_radius=16, ink=True, on_click=self._toggle_expand
                )
            ]
        )

        self.padding = ft.Padding.only(top=10, bottom=40)
        self.alignment = ft.Alignment.CENTER
        self.content = ft.Stack(
            width=400, height=100,
            controls=[
                ft.Container(content=select_page_row, alignment=ft.Alignment.BOTTOM_CENTER, bottom=0, left=0, right=0),
                ft.Container(content=ft.Row([self._pill_container], alignment=ft.MainAxisAlignment.CENTER), alignment=ft.Alignment.BOTTOM_CENTER, bottom=40, left=0, right=0)
            ]
        )

    def _toggle_expand(self, e=None):
        self._is_expanded = not self._is_expanded
        self._pill_container.opacity = 1 if self._is_expanded else 0
        self._pill_container.offset = ft.Offset(0, 0) if self._is_expanded else ft.Offset(0, 0.4)
        self._pill_container.disabled = not self._is_expanded
        self._dropdown_icon.rotate = math.pi if self._is_expanded else 0
        try:
            self._dropdown_icon.update()
            self._pill_container.update()
        except: pass

    def tutup_expand(self):
        if self._is_expanded:
            self._toggle_expand()

    def render_pages(self, current_page, total_pages):
        self._halaman = current_page
        self._total_pg = total_pages
        self._dropdown_text.value = f"{self._halaman:02d}"

        self._pagination_row.controls.clear()
        self._pagination_row.controls.append(
            ft.Container(
                content=ft.Icon(ft.Icons.CHEVRON_LEFT, size=20, color=self.theme["text_main"] if self._halaman > 1 else self.theme["border_color"]),
                ink=self._halaman > 1, padding=10, border_radius=20,
                on_click=lambda _: self.on_page_change(self._halaman - 1) if self._halaman > 1 else None)
        )

        start_page = max(1, self._halaman - 2)
        end_page = min(self._total_pg, start_page + 4)
        if end_page - start_page < 4 and self._total_pg >= 5: start_page = max(1, end_page - 4)

        for i in range(start_page, end_page + 1):
            is_active = (i == self._halaman)
            self._pagination_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{i:02d}", size=13, weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500, color=ft.Colors.WHITE if is_active else self.theme["text_secondary"]),
                    bgcolor=self.theme["primary"] if is_active else ft.Colors.TRANSPARENT, width=36, height=36, border_radius=18,
                    alignment=ft.Alignment.CENTER, ink=True, on_click=lambda e, num=i: self.on_page_change(num)
                )
            )

        self._pagination_row.controls.append(
            ft.Container(content=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20, color=self.theme["text_main"] if self._halaman < self._total_pg else self.theme["border_color"]),
                         ink=self._halaman < self._total_pg, padding=10, border_radius=20,
                         on_click=lambda _: self.on_page_change(self._halaman + 1) if self._halaman < self._total_pg else None)
        )
        try:
            self._pagination_row.update()
            self._dropdown_text.update()
        except: pass