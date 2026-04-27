import flet as ft
import math
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

C_BG        = "#FCF8FA"
C_BG2       = "#F5EEF2"
C_SAKURA    = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_TEXT      = "#3D2535"
C_TEXT2     = "#8B6A7A"
C_TEXT3     = "#B0909A"
C_BORDER    = "#EDE0E8"
C_GOLD      = "#C08030"
C_PURPLE    = "#9060A0"
C_WHITE     = "#FFFFFF"

CARDS_PER_PAGE = 24

class AnimeCard(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, on_click_callback):
        super().__init__()
        self.anime        = anime
        self._on_click_cb = on_click_callback

        self.width         = 140
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(0, -1),
            end=ft.Alignment(0, 1),
            colors=["#FFFFFF", "#FDF5F8"]
        )
        self.border        = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.on_click      = lambda _: self._on_click_cb(anime.get("anime_id", ""))
        self.on_hover      = self._on_hover
        self.scale         = 1.0
        self.shadow        = None
        self.animate       = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated = skor_personal is not None

        badge = ft.Container(
            content=ft.Text(
                "★ rated" if is_rated else "not rated",
                size=8, color=C_WHITE if is_rated else C_TEXT2,
                weight=ft.FontWeight.BOLD,
            ),
            bgcolor=C_SAKURA if is_rated else C_BG2,
            border=None if is_rated else ft.border.all(1, C_BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )

        thumb = anime.get("thumbnail_path", "")
        if thumb:
            thumb = os.path.join(BASE_DIR, thumb)

        if thumb and os.path.exists(thumb):
            poster = ft.Image(
                src=thumb, width=140, height=162,
                fit=ft.BoxFit.COVER,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )
        else:
            poster = ft.Container(
                width=140, height=162, bgcolor=C_BG2,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
                content=ft.Text(anime.get("title", "")[:14], size=9, color=C_TEXT3,
                                text_align=ft.TextAlign.CENTER),
                alignment=ft.Alignment(0, 0),
            )

        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {skor_global:.1f}  ·  {anime.get('episodes','?')} eps"
                  if skor_global else f"{anime.get('episodes','?')} eps")

        self._overlay = ft.Container(
            width=140, height=162,
            bgcolor=ft.Colors.with_opacity(0.85, "#000000"),
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=10, color=C_WHITE,
                            weight=ft.FontWeight.BOLD, max_lines=2),
                    ft.Text(sg_str, size=9, color="#D4A8BC"),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=ft.Text(g, size=8, color="#F5D0E0"),
                                bgcolor="#C07090", border_radius=8,
                                padding=ft.padding.symmetric(horizontal=6, vertical=1),
                                opacity=0.75,
                            )
                            for g in genres
                        ],
                        spacing=3,
                        run_spacing=2,
                        wrap=True,
                    ),
                ],
                spacing=4,
            ),
            visible=False,
        )

        sp_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"
        sp_col = C_PURPLE if is_rated else C_TEXT3

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            content=ft.Column(
                controls=[
                    ft.Text(anime.get("title", "—"), size=10, color=C_TEXT,
                            weight=ft.FontWeight.BOLD, max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(controls=[
                        ft.Text(f"★ {skor_global:.1f}" if skor_global else "★ —",
                                size=9, color=C_GOLD, weight=ft.FontWeight.BOLD),
                        ft.Text("·", size=9, color=C_BORDER),
                        ft.Text(sp_txt, size=9, color=sp_col, weight=ft.FontWeight.BOLD),
                    ], spacing=3),
                ],
                spacing=2, tight=True,
            ),
        )

        self.content = ft.Column(
            controls=[
                ft.Stack(
                    controls=[
                        ft.Stack(controls=[poster, self._overlay], width=140, height=162),
                        ft.Container(content=badge, top=6, right=6),
                    ],
                    width=140, height=162,
                ),
                info,
            ],
            spacing=0,
        )

    def _on_hover(self, e):
        is_hovered        = str(e.data).lower() == "true"
        self._overlay.visible = is_hovered
        self.border       = ft.border.all(1.5 if is_hovered else 1,
                                          C_SAKURA if is_hovered else C_BORDER)
        self.scale        = 1.03 if is_hovered else 1.0
        self.shadow       = ft.BoxShadow(
            spread_radius=1, blur_radius=10,
            color=ft.Colors.BLACK12, offset=ft.Offset(0, 4),
        ) if is_hovered else None
        self.update()

class AnimeListItem(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, on_click_callback):
        super().__init__()
        self._on_click_cb = on_click_callback

        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, 0),
            end=ft.Alignment(1, 0),
            colors=["#FFFFFF", "#FDF5F8"]
        )
        self.border        = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.padding       = ft.padding.symmetric(horizontal=14, vertical=10)
        self.on_click      = lambda _: on_click_callback(anime.get("anime_id", ""))
        self.on_hover      = self._on_hover
        self.animate       = ft.Animation(duration=120, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated  = skor_personal is not None

        thumb = anime.get("thumbnail_path", "")
        if thumb:
            thumb = os.path.join(BASE_DIR, thumb)

        genres    = anime.get("genre", [])[:3]

        if thumb and os.path.exists(thumb):
            poster = ft.Image(
                src=thumb, width=48, height=64,
                fit=ft.BoxFit.COVER,
                border_radius=6,
            )
        else:
            poster = ft.Container(
                width=48, height=64, bgcolor=C_BG2,
                border_radius=6,
                content=ft.Text("IMG", size=8, color=C_TEXT3),
                alignment=ft.Alignment(0, 0),
            )

        genre_chips = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(g, size=9, color=C_TEXT2),
                    bgcolor=C_BG2,
                    border=ft.border.all(1, C_BORDER),
                    border_radius=10,
                    padding=ft.padding.symmetric(horizontal=8, vertical=2),
                )
                for g in genres
            ],
            spacing=4,
        )

        sp_txt = f"you: {skor_personal:.1f}" if is_rated else "you: N/A"
        sp_col = C_PURPLE if is_rated else C_TEXT3

        rated_badge = ft.Container(
            content=ft.Text("★ rated" if is_rated else "not rated",
                            size=8, color=C_WHITE if is_rated else C_TEXT2,
                            weight=ft.FontWeight.BOLD),
            bgcolor=C_SAKURA if is_rated else C_BG2,
            border=None if is_rated else ft.border.all(1, C_BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )

        self.content = ft.Row(
            controls=[
                poster,
                ft.Column(
                    controls=[
                        ft.Row(controls=[
                            ft.Text(anime.get("title", "—"), size=13, color=C_TEXT,
                                    weight=ft.FontWeight.BOLD, expand=True,
                                    max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                            rated_badge,
                        ]),
                        genre_chips,
                        ft.Row(controls=[
                            ft.Text(f"★ {skor_global:.1f}" if skor_global else "★ —",
                                    size=11, color=C_GOLD, weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=11, color=C_TEXT3),
                            ft.Text(sp_txt, size=11, color=sp_col,
                                    weight=ft.FontWeight.BOLD),
                            ft.Text("·", size=11, color=C_TEXT3),
                            ft.Text(f"{anime.get('episodes','?')} eps",
                                    size=11, color=C_TEXT3),
                        ], spacing=5),
                    ],
                    spacing=5, tight=True, expand=True,
                ),
                ft.Icon(ft.Icons.CHEVRON_RIGHT, color=C_TEXT3, size=18),
            ],
            spacing=12,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )

    def _on_hover(self, e):
        is_hovered  = str(e.data).lower() == "true"
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment(-1, 0),
            end=ft.Alignment(1, 0),
            colors=["#FDF5F8", "#F5EEF2"] if is_hovered else ["#FFFFFF", "#FDF5F8"]
        )
        self.border  = ft.border.all(1 if not is_hovered else 1.5,
                                     C_BORDER if not is_hovered else C_SAKURA)
        self.update()

class UIKatalog(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager, filter_kategori=None):
        super().__init__()
        self.my_page        = page
        self.data_manager   = data_manager
        self.auth_manager   = auth_manager
        self.screen_manager = screen_manager

        self._filter       = filter_kategori if filter_kategori else "all"
        self._sort         = "title"
        self._keyword      = ""
        self._halaman      = 1
        self._total_pg     = 1
        self._view_mode    = "grid"
        self._sidebar_open = False

        self.expand  = True
        self.spacing = 0

        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="katalog"
        )

        self._search = ft.TextField(
            hint_text="Search anime...",
            hint_style=ft.TextStyle(color=C_TEXT3, size=12),
            prefix_icon=ft.Icons.SEARCH,
            border_color=C_BORDER,
            focused_border_color=C_SAKURA,
            border_radius=20,
            text_size=12,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=0),
            bgcolor=C_WHITE,
            color=C_TEXT,
            width=240,
            on_change=self._on_search,
        )

        is_sub_page = filter_kategori in ["rated", "unrated", "trending"]

        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,

            gradient=ft.LinearGradient(
                begin=ft.Alignment(0.0, -1.0),
                end=ft.Alignment(0.0, 1.0),
                colors=["#A1C4FD", "#E0F2FE"],
            ),
            shadow=ft.BoxShadow(
                blur_radius=15,
                color="#15000000",
                offset=ft.Offset(0, 4)
            ),

            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK if is_sub_page else ft.Icons.MENU,
                        icon_color=C_SAKURA,
                        tooltip="Back to Home" if is_sub_page else "Menu",
                        on_click=lambda
                            e: self.screen_manager.tampilkan_home() if is_sub_page else self._toggle_sidebar(e),
                    ),
                    ft.Column([
                        ft.Text("RadarAni", size=13, color=C_SAKURA,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("レーダアニ", size=8, color=C_TEXT3),
                    ], spacing=0, tight=True),
                    ft.Container(expand=True),
                    self._search,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._btn_all = self._filter_btn("All", "all", active=(self._filter == "all"))
        self._btn_rated = self._filter_btn("Rated", "rated", active=(self._filter == "rated"))
        self._btn_unrated = self._filter_btn("Unrated", "unrated", active=(self._filter == "unrated"))

        self._sort_dd = ft.Dropdown(
            options=[
                ft.DropdownOption(key="title", text="Title"),
                ft.DropdownOption(key="global", text="Global Score"),
                ft.DropdownOption(key="personal", text="Your Score"),
            ],
            value="title",
            width=130,
            text_style=ft.TextStyle(size=11, color=C_TEXT),
            dense=True,
            border_color=C_BORDER,
            focused_border_color=C_SAKURA,
            border_radius=8,
            bgcolor=C_BG2,
            content_padding=ft.padding.only(left=10, right=10, top=2, bottom=2),
            on_select=self._on_sort,
        )

        self._btn_grid = ft.IconButton(
            ft.Icons.GRID_VIEW,
            icon_color=C_SAKURA,
            icon_size=20,
            tooltip="Grid view",
            style=ft.ButtonStyle(bgcolor={ft.ControlState.DEFAULT: C_BG2}),
            on_click=lambda _: self._set_view("grid"),
        )
        self._btn_list = ft.IconButton(
            ft.Icons.LIST,
            icon_color=C_TEXT3,
            icon_size=20,
            tooltip="List view",
            on_click=lambda _: self._set_view("list"),
        )

        if filter_kategori == "rated":
            kiri_toolbar = [
                ft.Text("   Your Recent Ratings", size=12, color=C_SAKURA, weight=ft.FontWeight.BOLD)]
        elif filter_kategori == "unrated":
            kiri_toolbar = [ft.Text("   Top Unrated", size=12, color=C_SAKURA, weight=ft.FontWeight.BOLD)]
        elif filter_kategori == "trending":
            kiri_toolbar = [
                ft.Text("   Global Trending", size=12, color=C_SAKURA, weight=ft.FontWeight.BOLD)]
        else:
            kiri_toolbar = [self._btn_all, self._btn_rated, self._btn_unrated]

        toolbar = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
            padding=ft.padding.symmetric(horizontal=20, vertical=8),
            content=ft.Row(
                controls=kiri_toolbar + [
                    ft.Container(expand=True),
                    ft.Text("Sort:", size=11, color=C_TEXT2),
                    self._sort_dd,
                    ft.Container(width=8),
                    self._btn_grid,
                    self._btn_list,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
        )

        self._content_area = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            expand=True,
            spacing=0,
        )

        self._prev_btn = ft.ElevatedButton(
            "< Prev",
            bgcolor=C_BG2, color=C_TEXT2,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            on_click=lambda _: self._ganti_halaman(self._halaman - 1),
            disabled=True,
        )
        self._pg_label = ft.Text(
            "Page 1 of 1",
            size=13, color=C_TEXT2, weight=ft.FontWeight.W_500,
        )
        self._next_btn = ft.ElevatedButton(
            "Next >",
            bgcolor=C_SAKURA, color=C_WHITE,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=20, vertical=10),
            ),
            on_click=lambda _: self._ganti_halaman(self._halaman + 1),
        )

        pagination = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(top=ft.BorderSide(1, C_BORDER)),
            height=56,
            content=ft.Row(
                controls=[self._prev_btn, self._pg_label, self._next_btn],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._main_col = ft.Column(
            controls=[topbar, toolbar, self._content_area, pagination],
            spacing=0, expand=True,
        )

        self.controls = [self._sidebar_widget, self._main_col]
        self.muat_tabel_anime()

    def muat_tabel_anime(self):
        self._content_area.controls.clear()

        data    = self.data_manager.cari_anime(self._keyword) \
                  if self._keyword else self.data_manager.get_semua_anime()
        user_id = self.auth_manager.get_user_aktif()

        if self._filter == "rated":
            data = [a for a in data
                    if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is not None]
        elif self._filter == "unrated":
            data = [a for a in data
                    if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is None]
        elif self._filter == "trending":
            data.sort(key=lambda a: a.get("global_score", 0) or 0, reverse=True)

        if self._sort == "title":
            data.sort(key=lambda a: a.get("title", "").lower())
        elif self._sort == "global":
            data.sort(key=lambda a: a.get("global_score", 0) or 0, reverse=True)
        elif self._sort == "personal":
            data.sort(key=lambda a: self.data_manager.hitung_skor_personal(
                user_id, a["anime_id"]) or 0, reverse=True)

        self._total_pg = max(1, math.ceil(len(data) / CARDS_PER_PAGE))
        self._halaman  = min(self._halaman, self._total_pg)

        start        = (self._halaman - 1) * CARDS_PER_PAGE
        halaman_data = data[start: start + CARDS_PER_PAGE]

        if not halaman_data:
            self._content_area.controls.append(
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Icon(ft.Icons.SEARCH_OFF, size=40, color=C_TEXT3),
                            ft.Text("No anime found.", color=C_TEXT3, size=13),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=5
                    ),
                    alignment=ft.Alignment(0, 0),
                    height=300,
                )
            )
        else:
            if self._view_mode == "grid":
                self._render_grid(halaman_data, user_id)
            else:
                self._render_list(halaman_data, user_id)

        self._render_pagination()

        try:
            self.my_page.update()
        except Exception:
            pass

    def _render_grid(self, data, user_id):
        grid = ft.Row(
            wrap=True,
            spacing=16, run_spacing=16,
            alignment=ft.MainAxisAlignment.START,
        )
        for anime in data:
            sg   = anime.get("global_score", 0)
            sp   = self.data_manager.hitung_skor_personal(user_id, anime["anime_id"])
            grid.controls.append(
                AnimeCard(anime, sg, sp,
                          on_click_callback=self.screen_manager.tampilkan_detail)
            )

        self._content_area.controls.append(
            ft.Container(content=grid, padding=ft.padding.only(left=26, right=26, top=16, bottom=16), expand=True)
        )

    def _render_list(self, data, user_id):
        list_col = ft.Column(spacing=8)
        for anime in data:
            sg   = anime.get("global_score", 0)
            sp   = self.data_manager.hitung_skor_personal(user_id, anime["anime_id"])
            list_col.controls.append(
                AnimeListItem(anime, sg, sp,
                              on_click_callback=self.screen_manager.tampilkan_detail)
            )

        self._content_area.controls.append(
            ft.Container(content=list_col, padding=ft.padding.all(16), expand=True)
        )

    def _render_pagination(self):
        self._prev_btn.disabled = self._halaman <= 1
        self._next_btn.disabled = self._halaman >= self._total_pg
        self._pg_label.value    = f"Page {self._halaman} of {self._total_pg}"

        self._next_btn.bgcolor = C_SAKURA if not self._next_btn.disabled else C_BG2
        self._next_btn.color   = C_WHITE  if not self._next_btn.disabled else C_TEXT3

    def _on_search(self, e):
        self._keyword = e.control.value.strip()
        self._halaman = 1
        self.muat_tabel_anime()

    def _on_sort(self, e):
        self._sort    = e.control.value
        self._halaman = 1
        self.muat_tabel_anime()

    def _set_filter(self, val: str):
        self._filter  = val
        self._halaman = 1

        active_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_WHITE},
            bgcolor={ft.ControlState.DEFAULT: C_SAKURA},
            shape=ft.RoundedRectangleBorder(radius=16),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )
        normal_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_TEXT2,
                   ft.ControlState.HOVERED: C_TEXT},
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT,
                     ft.ControlState.HOVERED: C_BG2},
            shape=ft.RoundedRectangleBorder(radius=16),
            side=ft.BorderSide(1, C_BORDER),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )
        self._btn_all.style     = active_s if val == "all"     else normal_s
        self._btn_rated.style   = active_s if val == "rated"   else normal_s
        self._btn_unrated.style = active_s if val == "unrated" else normal_s
        self._btn_all.update()
        self._btn_rated.update()
        self._btn_unrated.update()
        self.muat_tabel_anime()

    def _set_view(self, mode: str):
        self._view_mode = mode
        self._btn_grid.icon_color = C_SAKURA if mode == "grid" else C_TEXT3
        self._btn_list.icon_color = C_SAKURA if mode == "list" else C_TEXT3
        self._btn_grid.style = ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: C_BG2 if mode == "grid" else ft.Colors.TRANSPARENT}
        )
        self._btn_list.style = ft.ButtonStyle(
            bgcolor={ft.ControlState.DEFAULT: C_BG2 if mode == "list" else ft.Colors.TRANSPARENT}
        )
        self._btn_grid.update()
        self._btn_list.update()
        self.muat_tabel_anime()

    def _ganti_halaman(self, n: int):
        if 1 <= n <= self._total_pg:
            self._halaman = n
            self.muat_tabel_anime()

    def _toggle_sidebar(self, e=None):
        self._sidebar_open            = not self._sidebar_open
        self._sidebar_widget.width    = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _filter_btn(self, label: str, val: str, active=False) -> ft.TextButton:
        return ft.TextButton(
            label,
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: C_WHITE if active else C_TEXT2},
                bgcolor={ft.ControlState.DEFAULT: C_SAKURA if active else ft.Colors.TRANSPARENT,
                         ft.ControlState.HOVERED: C_BG2 if not active else C_SAKURA},
                shape=ft.RoundedRectangleBorder(radius=16),
                side=ft.BorderSide(1, C_SAKURA if active else C_BORDER),
                padding=ft.padding.symmetric(horizontal=16, vertical=4),
            ),
            on_click=lambda _, v=val: self._set_filter(v),
        )