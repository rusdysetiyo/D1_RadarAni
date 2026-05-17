import flet as ft


class GuideDialog(ft.AlertDialog):
    def __init__(self, theme):
        super().__init__()
        self.theme = theme
        self.bgcolor = self.theme["card"]
        self.current_section = 1

        self.content_holder = ft.Container(content=self._build_manual_section())

        self.tab_manual = ft.Text("USER MANUAL", weight="bold", color=self.theme["primary"], size=12,
                                  letter_spacing=1.2)
        self.tab_keys = ft.Text("SHORTCUTS", weight="normal", color=self.theme["text_secondary"], size=12,
                                letter_spacing=1.2)

        self.title = ft.Row([
            ft.GestureDetector(content=self.tab_manual, on_click=lambda _: self._switch_section(1)),
            ft.VerticalDivider(width=1, color=self.theme["border_color"]),
            ft.GestureDetector(content=self.tab_keys, on_click=lambda _: self._switch_section(2)),
        ], spacing=15, alignment=ft.MainAxisAlignment.CENTER)

        self.content = ft.Container(
            content=self.content_holder,
            width=380,
            height=320,
            padding=ft.padding.only(top=20)
        )

        self.actions = [
            ft.TextButton("DISMISS", on_click=lambda _: self._close())
        ]

    def _switch_section(self, section_idx):
        self.current_section = section_idx
        if section_idx == 1:
            self.tab_manual.weight = "bold"
            self.tab_manual.color = self.theme["primary"]
            self.tab_keys.weight = "normal"
            self.tab_keys.color = self.theme["text_secondary"]
            self.content_holder.content = self._build_manual_section()
        else:
            self.tab_keys.weight = "bold"
            self.tab_keys.color = self.theme["primary"]
            self.tab_manual.weight = "normal"
            self.tab_manual.color = self.theme["text_secondary"]
            self.content_holder.content = self._build_keys_section()
        self.update()

    def _build_manual_section(self):
        return ft.Column([
            self._manual_item("Explore", "Discover your favorite anime titles in the Catalog."),
            self._manual_item("Details", "Click any anime card for comprehensive information."),
            self._manual_item("Filtering", "Utilize the sidebar to filter by specific genres."),
            self._manual_item("Analytics", "Monitor your viewing habits and statistics."),
        ], spacing=15, scroll=ft.ScrollMode.AUTO)

    def _manual_item(self, title, desc):
        return ft.Column([
            ft.Text(title, weight="bold", size=13, color=self.theme["text_main"]),
            ft.Text(desc, size=12, color=self.theme["text_secondary"]),
        ], spacing=2)

    def _build_keys_section(self):
        return ft.Column([
            self._key_item("CTRL + F", "Global Search"),
            self._key_item("CTRL + T", "Cycle Themes"),
            self._key_item("CTRL + R", "Refresh Home"),
            self._key_item("ESCAPE", "Return to Home"),
            self._key_item("LEFT/RIGHT", "Catalog Pagination"),
        ], spacing=12, scroll=ft.ScrollMode.AUTO)

    def _key_item(self, key, desc):
        return ft.Row([
            ft.Container(
                content=ft.Text(key, size=10, weight="bold", color=self.theme["primary"]),
                bgcolor=ft.Colors.with_opacity(0.1, self.theme["primary"]),
                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                border_radius=5,
                border=ft.border.all(1, ft.Colors.with_opacity(0.2, self.theme["primary"]))
            ),
            ft.Text(desc, size=12, color=self.theme["text_main"])
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

    def _close(self):
        self.open = False
        self.update()