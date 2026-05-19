import flet as ft

class CatalogActionBar(ft.Container):
    def __init__(self, theme, title, is_sub_page, initial_filter, view_mode,
                 on_filter_pill, on_genre_click, on_sort_click, on_view_click):
        super().__init__()
        self.theme = theme
        self.current_filter = initial_filter
        self.on_filter_pill = on_filter_pill
        self.on_sort_click = on_sort_click
        self.padding = ft.padding.only(left=26, right=26, top=20, bottom=10)

        # Title
        section_title = ft.Text(title, size=28, color=theme["text_main"], font_family="Clayful")

        # Filter Pills (All, Rated, Unrated)
        self.btn_all = self._filter_pill("All", "all", active=(initial_filter == "all"))
        self.btn_rated = self._filter_pill("Rated", "rated", active=(initial_filter == "rated"))
        self.btn_unrated = self._filter_pill("Unrated", "unrated", active=(initial_filter == "unrated"))
        pills_row = ft.Row(controls=[self.btn_all, self.btn_rated, self.btn_unrated] if not is_sub_page else [], spacing=10)

        # Genre Filter Button
        self.btn_filter_genre = ft.IconButton(
            icon=ft.Icons.FILTER_ALT, tooltip="Filter Genre", on_click=on_genre_click,
            style=ft.ButtonStyle(
                overlay_color=ft.Colors.TRANSPARENT,
                icon_color={ft.ControlState.HOVERED: f"{theme['text_secondary']},0.8", ft.ControlState.DEFAULT: theme["text_secondary"]}
            )
        )

        # Sort Dropdown
        self.sort_label = ft.Text("Sort: Title" if initial_filter != "trending" else "Sort: Global Score", size=11, color=theme["text_main"])
        sort_btn = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(content=ft.Text("Title"), data="title", on_click=self._handle_sort),
                ft.PopupMenuItem(content=ft.Text("Global Score"), data="global", on_click=self._handle_sort),
                ft.PopupMenuItem(content=ft.Text("Your Score"), data="personal", on_click=self._handle_sort),
            ],
            content=ft.Container(
                content=ft.Row([self.sort_label, ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=14, color=theme["text_secondary"])], spacing=2),
                padding=ft.padding.symmetric(horizontal=10, vertical=4), border=ft.border.all(1, theme["border_color"]),
                border_radius=8, bgcolor=theme["bg_secondary"]
            )
        )

        # View Mode Toggle (Grid / List)
        self.btn_grid = ft.IconButton(
            icon=ft.Icons.GRID_VIEW, on_click=lambda _: on_view_click("grid"),
            style=ft.ButtonStyle(overlay_color=ft.Colors.TRANSPARENT, icon_color={
                ft.ControlState.HOVERED: f"{theme['primary']},0.8", ft.ControlState.DEFAULT: theme["primary"] if view_mode == "grid" else theme["text_muted"]
            })
        )
        self.btn_list = ft.IconButton(
            icon=ft.Icons.LIST, on_click=lambda _: on_view_click("list"),
            style=ft.ButtonStyle(overlay_color=ft.Colors.TRANSPARENT, icon_color={
                ft.ControlState.HOVERED: f"{theme['primary']},0.8", ft.ControlState.DEFAULT: theme["primary"] if view_mode == "list" else theme["text_muted"]
            })
        )

        self.content = ft.Row(
            controls=[
                section_title,
                ft.Container(width=16) if not is_sub_page else ft.Container(),
                pills_row,
                ft.Container(expand=True),
                ft.Row(controls=[self.btn_filter_genre, ft.Container(width=4), sort_btn, ft.Container(width=4), self.btn_grid, self.btn_list], spacing=4, vertical_alignment=ft.CrossAxisAlignment.CENTER)
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

    def _filter_pill(self, label: str, val: str, active=False):
        warna = self.theme["primary"] if active else self.theme["text_muted"]
        def _on_hover(e):
            is_active_now = (self.current_filter == val)
            current_warna = self.theme["primary"] if is_active_now else self.theme["text_muted"]
            if e.data == "true":
                e.control.scale = 1.05
                e.control.bgcolor = f"{current_warna},0.15"
                e.control.border = ft.border.all(1.5, current_warna)
            else:
                e.control.scale = 1.0
                e.control.bgcolor = f"{current_warna},0.1" if is_active_now else ft.Colors.TRANSPARENT
                e.control.border = ft.border.all(1, f"{current_warna},0.4")
            try: e.control.update()
            except: pass

        return ft.Container(
            content=ft.Text(label, size=11, weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400, color=warna),
            bgcolor=f"{warna},0.1" if active else ft.Colors.TRANSPARENT,
            border=ft.border.all(1, f"{warna},0.4"),
            border_radius=ft.border_radius.only(top_left=12, bottom_right=12, top_right=3, bottom_left=3),
            padding=ft.padding.symmetric(horizontal=12, vertical=5),
            on_click=lambda _: self._handle_filter(val), on_hover=_on_hover, scale=1.0,
            animate=ft.Animation(200, ft.AnimationCurve.DECELERATE),
        )

    def _handle_filter(self, val):
        self.current_filter = val
        for btn, btn_val in [(self.btn_all, "all"), (self.btn_rated, "rated"), (self.btn_unrated, "unrated")]:
            active = (val == btn_val)
            warna = self.theme["primary"] if active else self.theme["text_muted"]
            btn.bgcolor = f"{warna},0.1" if active else ft.Colors.TRANSPARENT
            btn.border = ft.border.all(1, f"{warna},0.4")
            btn.content.color = warna
            btn.content.weight = ft.FontWeight.W_600 if active else ft.FontWeight.W_400
            try: btn.update()
            except: pass
        if self.on_filter_pill: self.on_filter_pill(val)

    def _handle_sort(self, e):
        self.sort_label.value = f"Sort: {e.control.content.value}"
        try: self.sort_label.update()
        except: pass
        if self.on_sort_click: self.on_sort_click(e.control.data)

    def update_view_buttons(self, mode):
        self.btn_grid.icon_color = self.theme["primary"] if mode == "grid" else self.theme["text_muted"]
        self.btn_list.icon_color = self.theme["primary"] if mode == "list" else self.theme["text_muted"]
        try:
            self.btn_grid.update()
            self.btn_list.update()
        except: pass

    def update_genre_button_state(self, selected_genre):
        if selected_genre == "All Genres":
            self.btn_filter_genre.icon_color = self.theme["text_secondary"]
            self.btn_filter_genre.tooltip = "Filter Genre"
        else:
            self.btn_filter_genre.icon_color = self.theme["primary"]
            self.btn_filter_genre.tooltip = f"Filtered: {selected_genre}"
        try: self.btn_filter_genre.update()
        except: pass