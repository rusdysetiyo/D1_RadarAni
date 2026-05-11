import flet as ft
import math
import os
from src.ui.icons import _sakura_icon_svg

# ── Section: Konfigurasi Dasar & Tema ────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

C_BG = "#FCF8FA"
C_BG2 = "#F5EEF2"
C_SAKURA = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_TEXT = "#3D2535"
C_TEXT2 = "#8B6A7A"
C_TEXT3 = "#B0909A"
C_BORDER = "#EDE0E8"
C_GOLD = "#C08030"
C_PURPLE = "#9060A0"
C_WHITE = "#FFFFFF"

CARDS_PER_PAGE = 24


# ── Section: Komponen AnimeCard ──────────────────────────────────────────────
class AnimeCard(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, is_favorite=False, on_click_callback=None):
        super().__init__()
        self.anime = anime
        self.is_favorite = is_favorite
        self._on_click_cb = on_click_callback

        self.width = 140
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.TOP_CENTER,
            end=ft.Alignment.BOTTOM_CENTER,
            colors=[ft.Colors.WHITE, "#FDF5F8"]
        )
        self.border = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.on_click = lambda _: self._on_click_cb(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.scale = 1.0
        self.shadow = None
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)
        self.animate_scale = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated = skor_personal is not None

        if is_rated:
            pill_bg = "#EC407A"
            pill_txt = "★ rated"
            pill_color = ft.Colors.WHITE
        else:
            pill_bg = ft.Colors.with_opacity(0.9, C_BG2)
            pill_txt = "not rated"
            pill_color = C_TEXT2

        self._status_pill = ft.Container(
            content=ft.Text(pill_txt, size=8, color=pill_color, weight=ft.FontWeight.BOLD),
            bgcolor=pill_bg,
            border_radius=12,
            padding=ft.padding.symmetric(horizontal=6, vertical=3),
            top=8, right=8,
            opacity=1.0,
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        self._fav_icon = ft.Container(
            content=ft.Image(src=_sakura_icon_svg(), width=24, height=24),
            top=8, right=8,
            opacity=0,
            offset=ft.Offset(0, -1),
            rotate=ft.Rotate(angle=-1, alignment=ft.Alignment(0, 0)),
            animate_offset=ft.Animation(300, ft.AnimationCurve.BOUNCE_OUT),
            animate_opacity=ft.Animation(200, ft.AnimationCurve.EASE_IN_OUT),
            animate_rotation=ft.Animation(300, ft.AnimationCurve.EASE_OUT),
        )

        thumb = anime.get("cover_path", "")
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
                alignment=ft.Alignment.CENTER,
            )

        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {skor_global:.1f}  ·  {anime.get('episodes', '?')} eps"
                  if skor_global else f"{anime.get('episodes', '?')} eps")

        self._overlay = ft.Container(
            width=140, height=162,
            bgcolor=ft.Colors.with_opacity(0.85, ft.Colors.BLACK),
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=10, color=ft.Colors.WHITE,
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
                        poster, self._overlay, self._status_pill, self._fav_icon
                    ],
                    width=140, height=162,
                ),
                info,
            ],
            spacing=0,
        )

    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"
        self._overlay.visible = is_hovered

        if is_hovered:
            self._status_pill.opacity = 0
            self._fav_icon.opacity = 1.0 if self.is_favorite else 0.4
            self._fav_icon.offset = ft.Offset(0, 0)
            self._fav_icon.rotate = ft.Rotate(angle=0, alignment=ft.Alignment(0, 0))
        else:
            self._status_pill.opacity = 1.0
            self._fav_icon.opacity = 0
            self._fav_icon.offset = ft.Offset(0, -1)
            self._fav_icon.rotate = ft.Rotate(angle=-1, alignment=ft.Alignment(0, 0))

        self.border = ft.border.all(
            1.5 if is_hovered else 1,
            "#EC407A" if is_hovered else C_BORDER,
        )
        self.scale = 1.03 if is_hovered else 1.0
        self.shadow = ft.BoxShadow(
            spread_radius=1, blur_radius=12,
            color=ft.Colors.with_opacity(0.3, "#EC407A"),
            offset=ft.Offset(0, 4),
        ) if is_hovered else None

        self._status_pill.update()
        self._fav_icon.update()
        self.update()


# ── Section: Komponen AnimeListItem ──────────────────────────────────────────
class AnimeListItem(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, is_favorite=False, on_click_callback=None):
        super().__init__()
        self._on_click_cb = on_click_callback

        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=[ft.Colors.WHITE, "#FDF5F8"]
        )
        self.border = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.padding = ft.padding.symmetric(horizontal=14, vertical=10)
        self.on_click = lambda _: on_click_callback(anime.get("anime_id", "")) if on_click_callback else None
        self.on_hover = self._on_hover
        self.animate = ft.Animation(duration=120, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated = skor_personal is not None

        thumb = anime.get("cover_path", "")
        if thumb:
            thumb = os.path.join(BASE_DIR, thumb)

        genres = anime.get("genre", [])[:3]

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
                alignment=ft.Alignment.CENTER,
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

        if is_favorite:
            rated_badge = ft.Container(
                content=ft.Row([
                    ft.Image(src=_sakura_icon_svg(), width=10, height=10, color=ft.Colors.WHITE),
                    ft.Text("FAVORITE", size=8, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)
                ], spacing=4),
                bgcolor="#EC407A",
                border_radius=8,
                padding=ft.padding.symmetric(horizontal=6, vertical=2),
            )
        else:
            rated_badge = ft.Container(
                content=ft.Text("★ rated" if is_rated else "not rated",
                                size=8, color=ft.Colors.WHITE if is_rated else C_TEXT2,
                                weight=ft.FontWeight.BOLD),
                bgcolor="#EC407A" if is_rated else C_BG2,
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
                            ft.Text(f"{anime.get('episodes', '?')} eps",
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
        is_hovered = str(e.data).lower() == "true"
        self.gradient = ft.LinearGradient(
            begin=ft.Alignment.CENTER_LEFT,
            end=ft.Alignment.CENTER_RIGHT,
            colors=["#FDF5F8", "#F5EEF2"] if is_hovered else [ft.Colors.WHITE, "#FDF5F8"]
        )
        self.border = ft.border.all(1.5 if is_hovered else 1, "#EC407A" if is_hovered else C_BORDER)
        self.update()


# ── Section: Halaman Utama Katalog ───────────────────────────────────────────
class UIKatalog(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager, filter_kategori=None):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager

        self._filter = filter_kategori if filter_kategori else "all"
        self._sort = "global" if filter_kategori == "trending" else "title"
        self._keyword = ""
        self._halaman = 1
        self._selected_genre = "All Genres"
        self._total_pg = 1
        self._view_mode = "grid"
        self._sidebar_open = False
        self._is_expanded = False
        self.is_sub_page_awal = filter_kategori in ["rated", "unrated", "trending"]

        self.expand = True
        self.spacing = 0

        # ── Sidebar ──
        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(
            screen_manager, auth_manager,
            self._toggle_sidebar, halaman_aktif="katalog"
        )

        # ── Topbar & Search ──
        search_input = ft.TextField(
            hint_text="Search anime...", hint_style=ft.TextStyle(color=C_TEXT3, size=12),
            border=ft.InputBorder.NONE, bgcolor=ft.Colors.TRANSPARENT, hover_color=ft.Colors.TRANSPARENT, color=C_TEXT,
            text_size=12, content_padding=ft.padding.all(0), dense=True, on_change=self._on_search,
        )
        self._search = ft.Container(
            content=ft.Row(
                [ft.Icon(ft.Icons.SEARCH, color=C_TEXT3, size=16), ft.Container(content=search_input, expand=True)],
                spacing=8),
            width=240, height=36, padding=ft.padding.symmetric(horizontal=12), border_radius=20,
            bgcolor="#40FFFFFF", border=ft.border.all(1, "#40C07090"),
        )

        is_sub_page = filter_kategori in ["rated", "unrated", "trending"]
        topbar = ft.Container(
            padding=ft.padding.symmetric(horizontal=16),
            height=55,
            bgcolor="#95FFFFFF",
            blur=ft.Blur(20, 20),
            border=ft.border.only(bottom=ft.BorderSide(1, "#15C07090")),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK if is_sub_page else ft.Icons.MENU,
                        icon_color=C_SAKURA,
                        on_click=lambda
                            e: self.screen_manager.tampilkan_home() if is_sub_page else self._toggle_sidebar(e),
                    ),
                    ft.Column(
                        [
                            ft.Row(
                                spacing=0,
                                controls=[
                                    ft.Text("R", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("a", font_family="Hitchcut", size=24, color="#D48CA8"),
                                    ft.Text("d", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("a", font_family="Hitchcut", size=24, color="#D48CA8"),
                                    ft.Text("r", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("A", font_family="Hitchcut", size=24, color="#D48CA8"),
                                    ft.Text("n", font_family="Hitchcut", size=24, color="#C07090"),
                                    ft.Text("i", font_family="Hitchcut", size=24, color="#D48CA8"),
                                ]
                            ),
                            ft.Text(
                                "レーダアニ",
                                font_family="Mofuji04",
                                size=10,
                                color=C_TEXT3,
                            ),
                        ],
                        spacing=0,
                        tight=True,
                    ),
                    ft.Container(expand=True),
                    self._search,
                ]
            )
        )

        # ── Filter & Toolbar Elemen ──
        self._section_title = ft.Text(
            "Your Recent Ratings" if filter_kategori == "rated" else "Top Unrated" if filter_kategori == "unrated"
            else "Global Trending" if filter_kategori == "trending" else "Anime List",
            size=28, color=C_TEXT, font_family="Clayful",
        )

        self._btn_all = self._filter_pill("All", "all", active=(self._filter == "all"))
        self._btn_rated = self._filter_pill("Rated", "rated", active=(self._filter == "rated"))
        self._btn_unrated = self._filter_pill("Unrated", "unrated", active=(self._filter == "unrated"))

        semua_anime_awal = self.data_manager.get_semua_anime()
        list_genre_unik = sorted(list({g for a in semua_anime_awal for g in a.get("genre", [])}))

        def _buat_chip(label, data, aktif=False):
            return ft.Container(
                content=ft.Text(
                    label, size=12, color=C_WHITE if aktif else C_TEXT,
                    weight=ft.FontWeight.W_600 if aktif else ft.FontWeight.W_500,
                ),
                data=data,
                bgcolor=C_SAKURA if aktif else C_SAKURA_LT,
                border=ft.border.all(1.5 if aktif else 1, C_SAKURA if aktif else "#E5C8D4"),
                border_radius=25,
                padding=ft.padding.symmetric(horizontal=16, vertical=8),
                on_click=self._pilih_genre_dari_dialog,
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                ink=True
            )

        self._chip_refs = {}
        genre_chips = []

        chip_all = _buat_chip("All Genres", "All Genres", aktif=True)
        self._chip_refs["All Genres"] = chip_all
        genre_chips.append(chip_all)

        for g in list_genre_unik:
            chip = _buat_chip(g, g, aktif=False)
            self._chip_refs[g] = chip
            genre_chips.append(chip)

        self.genre_dialog = ft.AlertDialog(
            title=ft.Row(
                controls=[
                    ft.Row([
                         ft.Icon(ft.Icons.STYLE, color=C_SAKURA, size=24), # Tambah icon
                         ft.Text("Select Genre", size=20, weight=ft.FontWeight.BOLD, color=C_TEXT),
                    ], spacing=8),
                    ft.Container(expand=True),
                    ft.Container(
                        content=ft.IconButton(
                            ft.Icons.CLOSE, icon_size=18, icon_color=C_TEXT3, on_click=self._tutup_dialog_genre,
                        ),
                        bgcolor=C_BG2,
                        border_radius=20,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            title_padding=ft.padding.only(left=24, right=16, top=16, bottom=8),
            content=ft.Container(
                width=550, height=400,
                padding=ft.padding.all(8),
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=genre_chips, wrap=True, spacing=10, run_spacing=10,
                            alignment=ft.MainAxisAlignment.CENTER
                        ),
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            content_padding=ft.padding.only(left=16, right=16, bottom=24, top=8),
            bgcolor=C_WHITE,
            shape=ft.RoundedRectangleBorder(radius=20),
            elevation=10,
        )

        self._btn_filter = ft.IconButton(
            icon=ft.Icons.FILTER_ALT,
            icon_color=C_TEXT2,
            icon_size=20,
            tooltip="Filter Genre",
            on_click=self._buka_dialog_genre
        )

        self._sort_label = ft.Text("Sort: Title", size=11, color=C_TEXT)
        self._sort_btn = ft.PopupMenuButton(
            items=[
                ft.PopupMenuItem(content=ft.Text("Title"), data="title", on_click=self._on_sort),
                ft.PopupMenuItem(content=ft.Text("Global Score"), data="global", on_click=self._on_sort),
                ft.PopupMenuItem(content=ft.Text("Your Score"), data="personal", on_click=self._on_sort),
            ],
            content=ft.Container(
                content=ft.Row([self._sort_label, ft.Icon(ft.Icons.ARROW_DROP_DOWN, size=14, color=C_TEXT2)],
                               spacing=2),
                padding=ft.padding.symmetric(horizontal=10, vertical=4), border=ft.border.all(1, C_BORDER),
                border_radius=8, bgcolor=C_BG2
            )
        )

        self._btn_grid = ft.IconButton(ft.Icons.GRID_VIEW,
                                       icon_color=C_SAKURA if self._view_mode == "grid" else C_TEXT3, icon_size=20,
                                       on_click=lambda _: self._set_view("grid"))
        self._btn_list = ft.IconButton(ft.Icons.LIST, icon_color=C_SAKURA if self._view_mode == "list" else C_TEXT3,
                                       icon_size=20, on_click=lambda _: self._set_view("list"))

        # ── Pagination Setup ──
        self._pagination_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=5)
        self._pill_container = ft.Container(
            content=self._pagination_row, bgcolor=ft.Colors.WHITE,
            padding=ft.padding.symmetric(horizontal=8, vertical=6),
            border_radius=30, shadow=ft.BoxShadow(blur_radius=15, color="#15000000", offset=ft.Offset(0, 5)),
            opacity=0, offset=ft.Offset(0, 0.4), disabled=True,
            animate_opacity=250, animate_offset=ft.Animation(250, ft.AnimationCurve.DECELERATE),
        )

        self._dropdown_text = ft.Text(f"{self._halaman:02d}", size=13, weight=ft.FontWeight.BOLD, color=C_TEXT)
        self._dropdown_icon = ft.Icon(ft.Icons.KEYBOARD_ARROW_DOWN, size=16, color=C_TEXT, rotate=0,
                                      animate_rotation=ft.Animation(250, ft.AnimationCurve.DECELERATE))

        self._select_page_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            controls=[
                ft.Text("Page:", size=12, weight=ft.FontWeight.W_500, color=C_TEXT2),
                ft.Container(
                    content=ft.Row([self._dropdown_text, self._dropdown_icon], spacing=2,
                                   alignment=ft.MainAxisAlignment.CENTER),
                    bgcolor=C_SAKURA_LT, padding=ft.padding.symmetric(horizontal=12, vertical=4),
                    border=ft.border.all(1, C_BORDER), border_radius=16, ink=True, on_click=self._toggle_expand
                )
            ]
        )

        self._pagination_wrapper = ft.Container(
            content=ft.Stack(
                width=400, height=100,
                controls=[
                    ft.Container(content=self._select_page_row, alignment=ft.Alignment.BOTTOM_CENTER, bottom=0, left=0,
                                 right=0),
                    ft.Container(content=ft.Row([self._pill_container], alignment=ft.MainAxisAlignment.CENTER),
                                 alignment=ft.Alignment.BOTTOM_CENTER, bottom=40, left=0, right=0)
                ]
            ), padding=ft.Padding.only(top=10, bottom=40), alignment=ft.Alignment.CENTER
        )

        # ── Setup Layout  ──
        self._content_area = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        self._main_col = ft.Container(
            expand=True,
            bgcolor=C_BG,
            content=ft.Column(
                controls=[
                    topbar,
                    self._content_area,
                ],
                spacing=0, expand=True,
            )
        )

        self.controls = [self._sidebar_widget, self._main_col]
        self._list_favorit_user = []
        user_id = self.auth_manager.get_user_aktif()
        if user_id:
            user_data = self.data_manager.get_user_by_id(user_id) or {}
            self._list_favorit_user = user_data.get("favorit", [])

        self.muat_tabel_anime()

    def _filter_pill(self, label: str, val: str, active=False):
        warna = C_SAKURA if active else C_TEXT3

        def _on_hover(e):
            is_active_now = (self._filter == val)
            current_warna = C_SAKURA if is_active_now else C_TEXT3

            if e.data == "true":
                e.control.scale = 1.05
                e.control.bgcolor = ft.Colors.with_opacity(0.15, current_warna)
                e.control.border = ft.border.all(1.5, current_warna)  # Border lebih tegas
                e.control.shadow = ft.BoxShadow(
                    blur_radius=12,
                    spread_radius=1,
                    color=ft.Colors.with_opacity(0.3, current_warna),
                    offset=ft.Offset(0, 3)
                )
            else:
                e.control.scale = 1.0
                e.control.bgcolor = ft.Colors.with_opacity(0.1,
                                                           current_warna) if is_active_now else ft.Colors.TRANSPARENT
                e.control.border = ft.border.all(1, ft.Colors.with_opacity(0.4, current_warna))
                e.control.shadow = None

            e.control.update()

        return ft.Container(
            content=ft.Text(
                label,
                size=11,
                weight=ft.FontWeight.W_600 if active else ft.FontWeight.W_400,
                color=warna
            ),
            bgcolor=ft.Colors.with_opacity(0.1, warna) if active else ft.Colors.TRANSPARENT,
            border=ft.border.all(1, ft.Colors.with_opacity(0.4, warna)),
            border_radius=ft.border_radius.only(top_left=12, bottom_right=12, top_right=3, bottom_left=3),
            padding=ft.padding.symmetric(horizontal=12, vertical=5),
            on_click=lambda _, v=val: self._set_filter(v),
            on_hover=_on_hover,

            shadow=None,
            scale=1.0,
            animate=ft.Animation(200, ft.AnimationCurve.DECELERATE),
        )

    def _toggle_expand(self, e=None):
        self._is_expanded = not self._is_expanded
        self._pill_container.opacity = 1 if self._is_expanded else 0
        self._pill_container.offset = ft.Offset(0, 0) if self._is_expanded else ft.Offset(0, 0.4)
        self._pill_container.disabled = not self._is_expanded
        self._dropdown_icon.rotate = math.pi if self._is_expanded else 0
        self._dropdown_icon.update()
        self._pill_container.update()

    def muat_tabel_anime(self):
        self._content_area.controls.clear()

        is_sub_page = self.is_sub_page_awal
        header_scrollable = ft.Container(
            padding=ft.padding.only(left=26, right=26, top=20, bottom=10),
            content=ft.Row(
                controls=[
                    self._section_title,
                    ft.Container(width=16) if not is_sub_page else ft.Container(),
                    ft.Row(controls=[self._btn_all, self._btn_rated, self._btn_unrated] if not is_sub_page else [],
                           spacing=10),
                    ft.Container(expand=True),

                    ft.Row(
                        controls=[
                            self._btn_filter,
                            ft.Container(width=4),
                            self._sort_btn,
                            ft.Container(width=4),
                            self._btn_grid,
                            self._btn_list
                        ],
                        spacing=4,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER
                    )

                ], vertical_alignment=ft.CrossAxisAlignment.CENTER,
            )
        )
        self._content_area.controls.append(header_scrollable)

        # ── Load Data ──
        semua_anime = self.data_manager.cari_anime(
            self._keyword) if self._keyword else self.data_manager.get_semua_anime()
        user_id = self.auth_manager.get_user_aktif()

        rating_user_ini = {}
        if user_id:
            semua_rating = self.data_manager._read_json(self.data_manager.ratings_file) or {}
            rating_user_ini = semua_rating.get(user_id, {})

        data_dengan_skor = []
        for anime in semua_anime:
            if self._selected_genre != "All Genres":
                if self._selected_genre not in anime.get("genre", []):
                    continue

            aid = anime.get("anime_id", "")
            sp = None
            if aid in rating_user_ini:
                skor_dict = rating_user_ini[aid]
                sp = round(sum(skor_dict.values()) / len(skor_dict), 2) if skor_dict else 0
            data_dengan_skor.append((anime, sp))

        if self._filter == "rated":
            data_dengan_skor = [i for i in data_dengan_skor if i[1] is not None]
        elif self._filter == "unrated":
            data_dengan_skor = [i for i in data_dengan_skor if i[1] is None]

        if self._sort == "title":
            data_dengan_skor.sort(key=lambda i: i[0].get("title", "").lower())
        elif self._sort == "global":
            data_dengan_skor.sort(key=lambda i: i[0].get("global_score", 0) or 0, reverse=True)
        elif self._sort == "personal":
            data_dengan_skor.sort(key=lambda i: i[1] or -1, reverse=True)

        self._total_pg = max(1, math.ceil(len(data_dengan_skor) / CARDS_PER_PAGE))
        self._halaman = min(self._halaman, self._total_pg)

        start = (self._halaman - 1) * CARDS_PER_PAGE
        halaman_data = data_dengan_skor[start: start + CARDS_PER_PAGE]

        if not halaman_data:
            self._content_area.controls.append(
                ft.Container(
                    content=ft.Column([ft.Icon(ft.Icons.SEARCH_OFF, size=40, color=C_TEXT3),
                                       ft.Text("No anime found.", color=C_TEXT3, size=13)],
                                      horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                      alignment=ft.MainAxisAlignment.CENTER),
                    height=300, alignment=ft.Alignment.CENTER
                )
            )
        else:
            if self._view_mode == "grid":
                self._render_grid(halaman_data)
            else:
                self._render_list(halaman_data)

        self._render_pagination()
        self._content_area.controls.append(self._pagination_wrapper)

        try:
            self.my_page.update()
        except Exception:
            pass

    def _render_grid(self, data):
        grid = ft.Row(wrap=True, spacing=16, run_spacing=16, alignment=ft.MainAxisAlignment.START)
        for item in data:
            anime = item[0]
            grid.controls.append(AnimeCard(anime=anime, skor_global=anime.get("global_score", 0), skor_personal=item[1],
                                           is_favorite=(anime.get("anime_id", "") in self._list_favorit_user),
                                           on_click_callback=self.screen_manager.tampilkan_detail))
        self._content_area.controls.append(
            ft.Container(content=grid, padding=ft.padding.only(left=26, right=26, top=0, bottom=16)))

    def _render_list(self, data):
        list_col = ft.Column(spacing=8)
        for item in data:
            anime = item[0]
            list_col.controls.append(
                AnimeListItem(anime=anime, skor_global=anime.get("global_score", 0), skor_personal=item[1],
                              is_favorite=(anime.get("anime_id", "") in self._list_favorit_user),
                              on_click_callback=self.screen_manager.tampilkan_detail))
        self._content_area.controls.append(
            ft.Container(content=list_col, padding=ft.padding.only(left=26, right=26, top=0, bottom=16)))

    def _render_pagination(self):
        self._pagination_row.controls.clear()
        self._pagination_row.controls.append(
            ft.Container(
                content=ft.Icon(ft.Icons.CHEVRON_LEFT, size=20, color=C_TEXT if self._halaman > 1 else C_BORDER),
                ink=self._halaman > 1, padding=10, border_radius=20,
                on_click=lambda e: self._ganti_halaman(self._halaman - 1) if self._halaman > 1 else None)
        )

        start_page = max(1, self._halaman - 2)
        end_page = min(self._total_pg, start_page + 4)
        if end_page - start_page < 4 and self._total_pg >= 5: start_page = max(1, end_page - 4)

        for i in range(start_page, end_page + 1):
            is_active = (i == self._halaman)
            self._pagination_row.controls.append(
                ft.Container(
                    content=ft.Text(f"{i:02d}", size=13,
                                    weight=ft.FontWeight.BOLD if is_active else ft.FontWeight.W_500,
                                    color=ft.Colors.WHITE if is_active else C_TEXT2),
                    gradient=ft.LinearGradient(begin=ft.Alignment.TOP_LEFT, end=ft.Alignment.BOTTOM_RIGHT,
                                               colors=["#FF9A9E", "#A1C4FD"]) if is_active else None,
                    bgcolor=None if is_active else ft.Colors.TRANSPARENT, width=36, height=36, border_radius=18,
                    alignment=ft.Alignment.CENTER,
                    shadow=ft.BoxShadow(spread_radius=1, blur_radius=3, color="#FF9A9E") if is_active else None,
                    ink=True, on_click=lambda e, num=i: self._ganti_halaman(num)
                )
            )

        self._pagination_row.controls.append(
            ft.Container(content=ft.Icon(ft.Icons.CHEVRON_RIGHT, size=20,
                                         color=C_TEXT if self._halaman < self._total_pg else C_BORDER),
                         ink=self._halaman < self._total_pg, padding=10, border_radius=20,
                         on_click=lambda e: self._ganti_halaman(
                             self._halaman + 1) if self._halaman < self._total_pg else None)
        )
        self._dropdown_text.value = f"{self._halaman:02d}"
        try:
            self._pagination_row.update()
            self._dropdown_text.update()
        except Exception:
            pass

    def _ganti_halaman(self, n: int):
        if 1 <= n <= self._total_pg:
            self._halaman = n
            if self._is_expanded: self._toggle_expand(None)
            self.muat_tabel_anime()
            try:
                self.my_page.run_task(self._content_area.scroll_to, offset=0, duration=300)
            except Exception:
                pass

    def _set_filter(self, val: str):
        self._filter = val
        self._halaman = 1

        for btn, btn_val in [
            (self._btn_all, "all"),
            (self._btn_rated, "rated"),
            (self._btn_unrated, "unrated")
        ]:
            active = (val == btn_val)
            warna = C_SAKURA if active else C_TEXT3

            btn.bgcolor = ft.Colors.with_opacity(0.1, warna) if active else ft.Colors.TRANSPARENT
            btn.border = ft.border.all(1, ft.Colors.with_opacity(0.4, warna))
            btn.content.color = warna
            btn.content.weight = ft.FontWeight.W_600 if active else ft.FontWeight.W_400
            btn.shadow = None
            btn.update()

        self.muat_tabel_anime()

    def _on_search(self, e):
        self._keyword = e.control.value.strip()
        self._halaman = 1
        self.muat_tabel_anime()

    def _on_sort(self, e):
        self._sort = e.control.data
        self._sort_label.value = f"Sort: {e.control.content.value}"
        self.muat_tabel_anime()

    def _on_genre_select(self, e):
        self._selected_genre = e.control.data
        self._halaman = 1
        self.muat_tabel_anime()

    def _set_view(self, mode: str):
        self._view_mode = mode
        self._btn_grid.icon_color = C_SAKURA if mode == "grid" else C_TEXT3
        self._btn_list.icon_color = C_SAKURA if mode == "list" else C_TEXT3
        self.muat_tabel_anime()

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._sidebar_widget.update()

    def _pilih_genre_dari_dialog(self, e):
        self._selected_genre = e.control.data
        for key, chip in self._chip_refs.items():
            aktif = (key == self._selected_genre)
            chip.bgcolor = C_SAKURA if aktif else C_WHITE
            chip.border = ft.border.all(1.5 if aktif else 1, C_SAKURA if aktif else C_BORDER)
            chip.content.color = C_WHITE if aktif else C_TEXT2
            chip.content.weight = ft.FontWeight.W_600 if aktif else ft.FontWeight.W_400
            chip.update()

        if self._selected_genre == "All Genres":
            self._btn_filter.icon_color = C_TEXT2
            self._btn_filter.tooltip = "Filter Genre"
        else:
            self._btn_filter.icon_color = C_SAKURA
            self._btn_filter.tooltip = f"Filtered: {self._selected_genre}"
        self._btn_filter.update()

        self._tutup_dialog_genre()
        self._halaman = 1
        self.muat_tabel_anime()

    def _buka_dialog_genre(self, e):
        if self.genre_dialog not in self.my_page.overlay:
            self.my_page.overlay.append(self.genre_dialog)
        self.genre_dialog.open = True
        self.my_page.update()

    def _tutup_dialog_genre(self, e=None):
        self.genre_dialog.open = False
        self.my_page.update()