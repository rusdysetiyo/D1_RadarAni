import flet as ft
from .palette import C_WHITE, C_SAKURA_DK, C_TEXT, C_TEXT3

class Tooltip(ft.Container):
    def __init__(self):
        super().__init__(
            visible=False,
            bgcolor=C_WHITE,
            border=ft.border.all(1, "#E0C8D4"),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            shadow=ft.BoxShadow(blur_radius=14, color="#25C07090",
                                offset=ft.Offset(0, 3)),
            left=0, top=0,
            content=ft.Column(spacing=3, tight=True),
        )
        self._current_title = None
        self._current_rows = None

    def show_at(self, x: float, y: float, title: str, rows: list):
        changed_content = False
        if title != self._current_title or rows != self._current_rows:
            self._current_title = title
            self._current_rows = rows
            self.content.controls = [
                ft.Text(title, size=12, weight=ft.FontWeight.BOLD, color=C_SAKURA_DK),
                *[ft.Row([
                    ft.Text(lbl, size=11, color=C_TEXT3, expand=True),
                    ft.Text(val, size=11, color=C_TEXT, weight=ft.FontWeight.W_600),
                ], spacing=8) for lbl, val in rows],
            ]
            changed_content = True

        new_left = min(x + 12, 280)
        new_top  = max(0, y - 8)
        changed_pos = abs(self.left - new_left) > 1 or abs(self.top - new_top) > 1

        if changed_content or changed_pos or not self.visible:
            self.left = new_left
            self.top = new_top
            self.visible = True
            self.update()

    def hide(self):
        if self.visible:
            self.visible = False
            self.update()
