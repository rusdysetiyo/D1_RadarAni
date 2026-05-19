import flet as ft
import math
import os
from src.ui.components.anime_cards import AnimeCardKatalog, AnimeListItem
from src.ui.components.genre_dialog import GenreDialog
from src.ui.components.action_bar import CatalogActionBar
from src.ui.components.pagination import PaginationBar

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CARDS_PER_PAGE = 24


class UIKatalog(ft.Row):
    def __init__(self, page, data_manager, auth_manager, screen_manager, theme, filter_kategori=None, search_query=""):
        super().__init__()
        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self.theme = theme

        self._filter = filter_kategori if filter_kategori else "all"
        self._sort = "global" if filter_kategori == "trending" else "title"
        self._keyword = search_query.lower()
        self._halaman = 1
        self._selected_genre = "All Genres"
        self._total_pg = 1
        self._view_mode = "grid"
        self._sidebar_open = False
        self.is_sub_page_awal = filter_kategori in ["rated", "unrated", "trending"]

        self.expand = True
        self.spacing = 0

        # ── Sidebar ──
        from src.ui.ui_home import _sidebar
        self._sidebar_widget = _sidebar(screen_manager, auth_manager, self._toggle_sidebar, theme=self.theme,
                                        halaman_aktif="katalog")

        # ── Topbar Search ──
        self.search_input = ft.TextField(
            value=self._keyword, hint_text="Search anime...",
            hint_style=ft.TextStyle(color=self.theme["text_muted"], size=12),
            border=ft.InputBorder.NONE, bgcolor=ft.Colors.TRANSPARENT, hover_color=ft.Colors.TRANSPARENT,
            color=self.theme["text_main"], text_size=12, content_padding=ft.padding.all(0), dense=True,
            on_change=self._on_search,
        )
        self._search = ft.Container(
            content=ft.Row([ft.Icon(ft.Icons.SEARCH, color=self.theme["text_muted"], size=16),
                            ft.Container(content=self.search_input, expand=True)], spacing=8),
            width=240, height=36, padding=ft.padding.symmetric(horizontal=12), border_radius=20,
            bgcolor=f"{self.theme['text_main']},0.1", border=ft.border.all(1, self.theme["border_color"]),
        )
        topbar = self._build_topbar(self.is_sub_page_awal)

        # ── Modular Components Injection ──
        semua_anime_awal = self.data_manager.get_semua_anime()
        list_genre_unik = sorted(list({g for a in semua_anime_awal for g in a.get("genre", [])}))

        # 1. Dialog Genre
        self.genre_dialog = GenreDialog(self.my_page, self.theme, list_genre_unik,
                                        on_genre_selected=self._on_genre_pilih)

        # 2. Action Bar
        judul_section = "Your Recent Ratings" if filter_kategori == "rated" else "Top Unrated" if filter_kategori == "unrated" else "Global Trending" if filter_kategori == "trending" else "Anime List"
        self.action_bar = CatalogActionBar(
            theme=self.theme, title=judul_section, is_sub_page=self.is_sub_page_awal, initial_filter=self._filter,
            view_mode=self._view_mode,
            on_filter_pill=self._on_filter_ubah, on_genre_click=lambda _: self.genre_dialog.buka(),
            on_sort_click=self._on_sort_ubah, on_view_click=self._on_view_ubah
        )

        # 3. Pagination Bar
        self.pagination_bar = PaginationBar(theme=self.theme, on_page_change=self._ganti_halaman)

        # ── Setup Layout Layout ──
        self._content_area = ft.Column(scroll=ft.ScrollMode.AUTO, expand=True, spacing=0)
        self.main_scroll = self._content_area
        self._main_col = ft.Container(
            expand=True, bgcolor=self.theme["bg"],
            content=ft.Column(controls=[topbar, self._content_area], spacing=0, expand=True)
        )

        self.controls = [self._sidebar_widget, self._main_col]
        self._list_favorit_user = []
        user_id = self.auth_manager.get_user_aktif()
        if user_id:
            user_data = self.data_manager.get_user_by_id(user_id) or {}
            self._list_favorit_user = user_data.get("favorit", [])

        self.muat_tabel_anime()

    def _safe_update(self, control):
        try:
            if control and control.page: control.update()
        except:
            pass

    def _build_topbar(self, is_sub_page):
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=16), height=55,
            bgcolor=f"{self.theme['bg']},0.8", blur=ft.Blur(20, 20),
            border=ft.border.only(bottom=ft.BorderSide(1, self.theme["border_color"])),
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        icon=ft.Icons.ARROW_BACK if is_sub_page else ft.Icons.MENU,
                        on_click=lambda
                            e: self.screen_manager.tampilkan_home() if is_sub_page else self._toggle_sidebar(e),
                        style=ft.ButtonStyle(overlay_color=ft.Colors.TRANSPARENT,
                                             icon_color={ft.ControlState.HOVERED: f"{self.theme['primary']},0.8",
                                                         ft.ControlState.DEFAULT: self.theme["primary"]})
                    ),
                    ft.Column([
                        ft.Row(spacing=0, controls=[ft.Text(huruf, font_family="Hitchcut", size=24,
                                                            color=self.theme["logo_1" if i % 2 == 0 else "logo_2"]) for
                                                    i, huruf in enumerate("RadarAni")]),
                        ft.Text("レーダアニ", font_family="Mofuji04", size=10, color=self.theme["text_muted"]),
                    ], spacing=0, tight=True),
                    ft.Container(expand=True),
                    self._search,
                ]
            )
        )

    def muat_tabel_anime(self):
        self._content_area.controls.clear()
        self._content_area.controls.append(self.action_bar)

        # ── Load Data ──
        semua_anime = self.data_manager.cari_anime(
            self._keyword) if self._keyword else self.data_manager.get_semua_anime()
        user_id = self.auth_manager.get_user_aktif()

        rating_user_ini = {}
        if user_id:
            rating_user_ini = self.data_manager.get_semua_rating().get(user_id, {})

        data_dengan_skor = []
        for anime in semua_anime:
            if self._selected_genre != "All Genres" and self._selected_genre not in anime.get("genre", []):
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
                    content=ft.Column([ft.Icon(ft.Icons.SEARCH_OFF, size=40, color=self.theme["text_muted"]),
                                       ft.Text("No anime found.", color=self.theme["text_muted"], size=13)],
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

        self.pagination_bar.render_pages(self._halaman, self._total_pg)
        self._content_area.controls.append(self.pagination_bar)
        self._safe_update(self.my_page)

    def _render_grid(self, data):
        grid = ft.Row(wrap=True, spacing=16, run_spacing=16, alignment=ft.MainAxisAlignment.START)
        for item in data:
            anime = item[0]
            grid.controls.append(
                AnimeCardKatalog(anime=anime, skor_global=anime.get("global_score", 0), skor_personal=item[1],
                                 theme=self.theme, is_favorite=(anime.get("anime_id", "") in self._list_favorit_user),
                                 on_click_callback=self.screen_manager.tampilkan_detail))
        self._content_area.controls.append(
            ft.Container(content=grid, padding=ft.padding.only(left=26, right=26, top=0, bottom=16)))

    def _render_list(self, data):
        list_col = ft.Column(spacing=8)
        for item in data:
            anime = item[0]
            list_col.controls.append(
                AnimeListItem(anime=anime, skor_global=anime.get("global_score", 0), skor_personal=item[1],
                              theme=self.theme, is_favorite=(anime.get("anime_id", "") in self._list_favorit_user),
                              on_click_callback=self.screen_manager.tampilkan_detail))
        self._content_area.controls.append(
            ft.Container(content=list_col, padding=ft.padding.only(left=26, right=26, top=0, bottom=16)))

    def _ganti_halaman(self, n: int):
        if 1 <= n <= self._total_pg:
            self._halaman = n
            self.pagination_bar.tutup_expand()
            self.muat_tabel_anime()
            try:
                self.my_page.run_task(self._content_area.scroll_to, offset=0, duration=300)
            except:
                pass

    def _on_filter_ubah(self, val: str):
        self._filter = val
        self._halaman = 1
        self.muat_tabel_anime()

    def _on_search(self, e):
        self._keyword = self.search_input.value.lower()
        self._halaman = 1
        self.muat_tabel_anime()

    def _on_sort_ubah(self, sort_val: str):
        self._sort = sort_val
        self.muat_tabel_anime()

    def _on_view_ubah(self, mode: str):
        self._view_mode = mode
        self.action_bar.update_view_buttons(mode)
        self.muat_tabel_anime()

    def _on_genre_pilih(self, genre: str):
        self._selected_genre = genre
        self.action_bar.update_genre_button_state(genre)
        self._halaman = 1
        self.muat_tabel_anime()

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar_widget.width = 240 if self._sidebar_open else 0
        self._safe_update(self._sidebar_widget)