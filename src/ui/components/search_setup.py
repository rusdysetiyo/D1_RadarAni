import flet as ft


class SearchManager:
    def __init__(self, page: ft.Page, theme, on_search_callback):
        self.page = page
        self.theme = theme
        self.on_search_callback = on_search_callback

        self.search_input = ft.TextField(
            hint_text="Ketik judul anime...",
            border=ft.InputBorder.NONE,
            color=self.theme["text_main"],
            cursor_color=self.theme["primary"],
            text_size=16,
            autofocus=True,
            expand=True,
            on_submit=self._handle_submit
        )

        self.search_box = ft.Container(
            content=ft.Row([
                ft.Icon(ft.Icons.SEARCH_ROUNDED, color=self.theme["primary"]),
                self.search_input,
                ft.IconButton(
                    icon=ft.Icons.CLOSE_ROUNDED,
                    icon_color=self.theme["text_secondary"],
                    on_click=lambda _: self.hide()
                )
            ]),
            width=500,
            bgcolor=self.theme["card"],
            padding=ft.padding.symmetric(horizontal=15, vertical=5),
            border_radius=30,
            border=ft.border.all(1, self.theme["border_color"]),
            shadow=ft.BoxShadow(blur_radius=30, color=ft.Colors.BLACK45)
        )

        self.backdrop = ft.Container(
            content=ft.Row([self.search_box], alignment=ft.MainAxisAlignment.CENTER),
            left=0, right=0, top=80,
            visible=False
        )

        self.page.overlay.append(self.backdrop)
        self.page.update()

    def _handle_submit(self, e):
        query = self.search_input.value
        self.hide()

        if query and query.strip():
            self.on_search_callback(query.strip())

        self.search_input.value = ""
        self.page.update()

    def show(self):
        self.backdrop.visible = True
        self.page.update()

    def hide(self):
        self.backdrop.visible = False
        self.page.update()

    def apply_theme(self, new_theme):
        self.theme = new_theme

        self.search_box.bgcolor = self.theme["card"]
        self.search_box.border = ft.border.all(1, self.theme["border_color"])

        self.search_input.color = self.theme["text_main"]
        self.search_input.cursor_color = self.theme["primary"]

        row_controls = self.search_box.content.controls
        row_controls[0].color = self.theme["primary"]
        row_controls[2].icon_color = self.theme["text_secondary"]

        self.backdrop.update()