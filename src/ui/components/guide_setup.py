import flet as ft
from ui.components.sakura_anim import get_sakura_svg

class GuideManager:
    def __init__(self, page: ft.Page, theme):
        self.page = page
        self.theme = theme
        self._tab = 0
        self._tab_labels = ["Manual", "Shortcuts", "About"]
        self.manual_view    = self._build_manual()
        self.keys_view      = self._build_shortcuts()
        self.about_view     = self._build_about()

        # only manual visible on open
        self.manual_view.visible = True
        self.keys_view.visible   = False
        self.about_view.visible  = False

        self.dialog_content = ft.Container(
            content=ft.Column([
                self._build_tab_bar(),
                ft.Divider(height=1, thickness=1, color=self.theme["border_color"]),
                self.manual_view,
                self.keys_view,
                self.about_view,
            ]),
            width=490, height=470,
        )

        self.btn_close = ft.TextButton(
            "CLOSE",
            on_click=self._close_dialog,
            style=ft.ButtonStyle(color=self.theme["text_secondary"]),
        )

        self.guide_dialog = ft.AlertDialog(
            content=self.dialog_content,
            actions=[self.btn_close],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=self.theme["card"],
            shape=ft.RoundedRectangleBorder(radius=14),
        )

        self.guide_btn = ft.Container(
            content=ft.Icon(ft.Icons.QUESTION_MARK_ROUNDED, color=self.theme["primary"], size=20),
            width=45, height=45,
            bgcolor=self.theme["card"],
            border_radius=25,
            border=ft.border.all(1, self.theme["border_color"]),
            right=25, bottom=25,
            on_click=lambda _: self._open_dialog(),
            visible=False,
            shadow=ft.BoxShadow(blur_radius=10, color="black12"),
        )

        self.page.overlay.extend([self.guide_dialog, self.guide_btn])
        self.page.update()

    # ── helpers ────────────────────────────────────────────────────────────────

    def _key_badge(self, label: str) -> ft.Container:
        return ft.Container(
            content=ft.Text(label, size=10, weight="bold", color=self.theme["primary"]),
            bgcolor=self.theme.get("surface", self.theme["card"]),
            border=ft.border.all(1.2, self.theme["primary"]),
            border_radius=5,
            padding=ft.padding.symmetric(horizontal=7, vertical=3),
            shadow=ft.BoxShadow(blur_radius=2, offset=ft.Offset(0, 2), color="black26"),
        )

    def _shortcut_row(self, keys: list[str], description: str) -> ft.Container:
        badges = ft.Row([self._key_badge(k) for k in keys], spacing=4, tight=True)
        return ft.Container(
            content=ft.Row(
                [
                    badges,
                    ft.Text(":", size=11, color=self.theme["text_secondary"]),
                    ft.Text(description, size=12, color=self.theme["text_main"], expand=True),
                ],
                spacing=6,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            padding=ft.padding.symmetric(horizontal=10, vertical=5),
            border_radius=7,
            bgcolor=self.theme.get("surface", self.theme["card"]),
            border=ft.border.all(1, self.theme["border_color"]),
        )

    def _section_header(self, title: str) -> ft.Row:
        return ft.Row(
            [
                ft.Container(width=4, height=16, bgcolor=self.theme["primary"], border_radius=2),
                ft.Text(title, weight="bold", size=12, color=self.theme["primary"]),
            ],
            spacing=8,
        )

    # ── build views ────────────────────────────────────────────────────────────

    def _build_manual(self) -> ft.Column:
        items = [
            (ft.Icons.MENU_BOOK_ROUNDED,  "Browse anime titles through the Catalog"),
            (ft.Icons.TOUCH_APP_ROUNDED,  "Click any anime card to view its full details"),
            (ft.Icons.SEARCH_ROUNDED,     "Use Global Search (CTRL + F) to find anything, anywhere"),
            (ft.Icons.PALETTE_ROUNDED,    "Switch themes via CTRL + 1–8, or cycle through with CTRL + T"),
            (ft.Icons.STAR_ROUNDED,       "Rate an anime from the Detail page"),
            (ft.Icons.KEYBOARD_ROUNDED,   "Open this guide anytime using the ? button"),
        ]

        rows: list = [
            ft.Text("USER MANUAL", weight="bold", size=14, color=self.theme["primary"]),
            ft.Divider(color=self.theme["border_color"], height=1, thickness=1),
            ft.Container(height=2),
        ]

        for icon, text in items:
            rows.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Container(
                                content=ft.Icon(icon, size=16, color=self.theme["primary"]),
                                width=32, height=32,
                                bgcolor=self.theme.get("surface", self.theme["card"]),
                                border_radius=8,
                                alignment=ft.Alignment.CENTER,
                                border=ft.border.all(1, self.theme["border_color"]),
                            ),
                            ft.Text(text, size=12, color=self.theme["text_main"], expand=True),
                        ],
                        spacing=12,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    padding=ft.padding.symmetric(vertical=7, horizontal=10),
                    border_radius=8,
                    bgcolor=self.theme.get("surface", self.theme["card"]),
                    border=ft.border.all(1, self.theme["border_color"]),
                )
            )

        return ft.Column(rows, tight=False, spacing=7, scroll=ft.ScrollMode.AUTO, expand=True)

    def _build_shortcuts(self) -> ft.Column:
        sections = [
            ("GLOBAL & NAVIGATION", [
                (["ALT", "1"], "Go to Home"),
                (["ALT", "2"], "Go to Catalog"),
                (["ALT", "3"], "Go to Analytics"),
                (["ALT", "4"], "Go to Scrape"),
                (["ALT", "5"], "Go to Profile"),
                (["CTRL", "1"], "Theme: Sakura"),
                (["CTRL", "2"], "Theme: Matcha"),
                (["CTRL", "3"], "Theme: Dark"),
                (["CTRL", "4"], "Theme: Ocean"),
                (["CTRL", "5"], "Theme: Pastel"),
                (["CTRL", "6"], "Theme: Aurora"),
                (["CTRL", "7"], "Theme: Cyber"),
                (["CTRL", "8"], "Theme: Dusk"),
                (["CTRL", "T"],       "Cycle through themes in order"),
                (["CTRL", "F"],       "Open Global Search"),
                (["ESC"],             "Close pop-up"),
                (["CTRL", "R"],       "Refresh the Home page"),
            ]),
            ("CATALOG", [
                (["CTRL", "/"],       "Focus the local search bar"),
                (["CTRL", "G"],       "Toggle between Grid and List view"),
                (["SHIFT", "A/R/U"], "Filter by All / Rated / Unrated"),
                (["SHIFT", "F"],      "Open the Genre filter panel"),
                (["SHIFT", "O"],      "Cycle sort order: Title / Global Rating / Personal Rating"),
                (["◄", "►"],         "Go to previous / next page"),
            ]),
            ("DETAIL & PROFILE", [
                (["ENTER"],           "Submit input while typing"),
                (["CTRL", "L"],       "Log out of your account"),
                (["CTRL", "DEL"],     "Delete your account"),
            ]),
            ("SCROLLING", [
                (["▲", "▼"],          "Scroll up / down"),
                (["PG UP", "PG DN"], "Jump scroll up / down"),
                (["CTRL", "▲/HOME"], "Jump to the very top"),
                (["CTRL", "▼/END"],  "Jump to the very bottom"),
            ]),
        ]

        controls: list = []
        for i, (title, shortcuts) in enumerate(sections):
            if i > 0:
                controls.append(ft.Container(height=3))
            controls.append(self._section_header(title))
            controls.append(ft.Container(height=3))
            for keys, desc in shortcuts:
                controls.append(self._shortcut_row(keys, desc))

        return ft.Column(
            controls, tight=False, spacing=5,
            scroll=ft.ScrollMode.AUTO, expand=True,
        )

    def _build_about(self) -> ft.Column:
        def info_row(label: str, value: str) -> ft.Container:
            return ft.Container(
                content=ft.Row(
                    [
                        ft.Text(label, size=11, color=self.theme["text_secondary"], width=110),
                        ft.Text(value, size=11, color=self.theme["text_main"], expand=True),
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=ft.padding.symmetric(horizontal=10, vertical=6),
                bgcolor=self.theme.get("surface", self.theme["card"]),
                border=ft.border.all(1, self.theme["border_color"]),
                border_radius=7,
            )

        dimensions = ["Visual", "Plot", "Audio", "Characterization", "Direction"]
        dim_badges = ft.Row(
            [
                ft.Container(
                    content=ft.Text(d, size=10, weight="bold", color=self.theme["primary"]),
                    bgcolor=self.theme.get("surface", self.theme["card"]),
                    border=ft.border.all(1.2, self.theme["primary"]),
                    border_radius=5,
                    padding=ft.padding.symmetric(horizontal=8, vertical=3),
                )
                for d in dimensions
            ],
            wrap=True, spacing=5, run_spacing=5,
        )

        return ft.Column(
            [
                # Logo + app name
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Image(src=get_sakura_svg(80), width=52, height=52),
                            width=52, height=52,
                            border_radius=26,  # setengah dari width/height = lingkaran
                            clip_behavior=ft.ClipBehavior.HARD_EDGE,
                        ),
                        ft.Column(
                            [
                                ft.Text("RadarAni", weight="bold", size=20, color=self.theme["primary"]),
                                ft.Text("Multidimensional Anime Rating", size=11, color=self.theme["text_secondary"]),
                            ],
                            spacing=2, tight=True,
                        ),
                    ],
                    spacing=14,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),

                ft.Divider(color=self.theme["border_color"], height=1, thickness=1),

                # Description
                ft.Container(
                    content=ft.Text(
                        "RadarAni addresses the limitations of single-score platforms like MyAnimeList and AniList, "
                        "where one number often fails to capture the nuanced quality of a title. "
                        "This app lets users evaluate anime across five distinct dimensions, offering a more "
                        "transparent and structured view of what makes — or breaks — a series.",
                        size=11,
                        color=self.theme["text_main"],
                        text_align=ft.TextAlign.JUSTIFY,
                    ),
                    padding=ft.padding.symmetric(horizontal=10, vertical=8),
                    bgcolor=self.theme.get("surface", self.theme["card"]),
                    border=ft.border.all(1, self.theme["border_color"]),
                    border_radius=7,
                ),

                # Rating dimensions
                ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Container(width=4, height=14, bgcolor=self.theme["primary"], border_radius=2),
                                ft.Text("Rating Dimensions", weight="bold", size=11, color=self.theme["primary"]),
                            ],
                            spacing=8,
                        ),
                        dim_badges,
                    ],
                    spacing=7, tight=True,
                ),

                ft.Divider(color=self.theme["border_color"], height=1, thickness=1),

                # Info rows
                info_row("App",        "RadarAni"),
                info_row("Type",       "Desktop Application"),
                info_row("Built with", "Python · Flet"),
                info_row("Team",       "D1_RadarAni"),
            ],
            spacing=10, tight=False, scroll=ft.ScrollMode.AUTO, expand=True,
        )

    # ── actions ────────────────────────────────────────────────────────────────

    def _build_tab_bar(self) -> ft.Row:
        tabs = []
        for i, label in enumerate(self._tab_labels):
            is_active = i == self._tab
            tabs.append(
                ft.GestureDetector(
                    content=ft.Container(
                        content=ft.Text(
                            label, size=11,
                            weight="bold" if is_active else "normal",
                            color=self.theme["primary"] if is_active else self.theme["text_secondary"],
                        ),
                        border=ft.border.only(
                            bottom=ft.BorderSide(2 if is_active else 0, self.theme["primary"])
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=6),
                    ),
                    on_tap=lambda e, idx=i: self._go_to_tab(idx),
                )
            )
        return ft.Row(tabs, spacing=0)

    def _go_to_tab(self, idx: int):
        self._tab = idx
        self.manual_view.visible = idx == 0
        self.keys_view.visible = idx == 1
        self.about_view.visible = idx == 2
        col: ft.Column = self.dialog_content.content
        col.controls[0] = self._build_tab_bar()
        self.guide_dialog.update()

    def _open_dialog(self):
        self.guide_dialog.open = True
        self.page.update()

    def _close_dialog(self, e):
        self.guide_dialog.open = False
        self.page.update()

    def force_close(self):
        if self.guide_dialog.open:
            self.guide_dialog.open = False
            self.page.update()

    def set_visible(self, is_visible: bool):
        self.guide_btn.visible = is_visible
        self.guide_btn.update()

    # ── theme ──────────────────────────────────────────────────────────────────

    def apply_theme(self, new_theme: dict):
        self.theme = new_theme

        # Floating button
        self.guide_btn.bgcolor        = self.theme["card"]
        self.guide_btn.border         = ft.border.all(1, self.theme["border_color"])
        self.guide_btn.content.color  = self.theme["primary"]

        # Dialog base
        self.guide_dialog.bgcolor = self.theme["card"]

        # Action buttons
        self.btn_close.style  = ft.ButtonStyle(color=self.theme["text_secondary"])

        # Rebuild all three views with new theme
        new_manual = self._build_manual()
        new_keys   = self._build_shortcuts()
        new_about  = self._build_about()

        new_manual.visible = self._tab == 0
        new_keys.visible   = self._tab == 1
        new_about.visible  = self._tab == 2

        col: ft.Column = self.dialog_content.content
        col.controls = [self._build_tab_bar(), ft.Divider(height=1, thickness=1, color=self.theme["border_color"]), new_manual, new_keys, new_about]

        self.manual_view = new_manual
        self.keys_view   = new_keys
        self.about_view  = new_about

        self.guide_btn.update()
        if self.guide_dialog.open:
            self.guide_dialog.update()
        else:
            self.page.update()