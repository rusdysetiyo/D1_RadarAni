import flet as ft
import math

# ── Warna Tema ────────────────────────────────────────
C_BG = "#FCF8FA"
C_BG2 = "#F5EEF2"
C_SAKURA = "#C07090"
C_SAKURA_LT = "#F9F0F5"
C_BLUE_LT = "#D4EBF8"
C_TEXT = "#3D2535"
C_TEXT2 = "#8B6A7A"
C_TEXT3 = "#B0909A"
C_BORDER = "#EDE0E8"
C_GOLD = "#C08030"
C_PURPLE = "#9060A0"
C_WHITE = "#FFFFFF"


def build_pill(text: str, icon: str = "") -> ft.Container:
    return ft.Container(
        content=ft.Text(f"{icon}  {text}" if icon else text,
                        size=11, color=C_TEXT2),
        bgcolor=C_BG2,
        border=ft.border.all(1, C_BORDER),
        border_radius=20,
        padding=ft.padding.symmetric(horizontal=12, vertical=4),
    )


class AnimeCard(ft.Container):
    def __init__(self, anime: dict, skor_global, skor_personal, on_click_callback):
        super().__init__()
        self.anime = anime
        self.sg = skor_global
        self.sp = skor_personal
        self._on_click_cb = on_click_callback
        self._hovered = False

        self.width = 140
        self.bgcolor = C_WHITE
        self.border = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.clip_behavior = ft.ClipBehavior.ANTI_ALIAS
        self.on_hover = self._on_hover
        self.on_click = lambda _: self._on_click_cb(self.anime.get("anime_id", ""))
        self.animate = ft.Animation(150, ft.AnimationCurve.EASE_IN_OUT)

        is_rated = self.sp is not None

        badge = ft.Container(
            content=ft.Text("★ rated" if is_rated else "not rated",
                            size=8, color=C_WHITE if is_rated else C_TEXT2,
                            weight=ft.FontWeight.BOLD),
            bgcolor=C_SAKURA if is_rated else C_BG2,
            border=None if is_rated else ft.border.all(1, C_BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=6, vertical=2),
        )

        thumb = anime.get("thumbnail_path", "")
        if thumb:
            poster_content = ft.Image(
                src=thumb,
                width=140, height=162,
                fit="cover",
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )
        else:
            poster_content = ft.Container(
                width=140, height=162,
                bgcolor=C_BG2,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
                content=ft.Text(anime.get("title", "")[:14],
                                size=9, color=C_TEXT3,
                                text_align=ft.TextAlign.CENTER),
                alignment=ft.Alignment(0, 0),
            )

        genres = anime.get("genre", [])[:3]
        genre_row = ft.Row(
            controls=[
                ft.Container(
                    content=ft.Text(g, size=8, color="#F5D0E0"),
                    bgcolor="#C07090",
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=6, vertical=1),
                    opacity=0.75,
                )
                for g in genres
            ],
            spacing=3,
        )

        sg_str = f"★ {self.sg:.1f}  ·  {anime.get('episodes', '?')} eps  ·  {anime.get('broadcast_type', 'TV')}" \
            if self.sg else f"{anime.get('episodes', '?')} eps"

        self._overlay = ft.Container(
            width=140, height=162,
            bgcolor="#1C0C16CC",
            border_radius=ft.border_radius.only(top_left=10, top_right=10),
            padding=8,
            content=ft.Column(
                controls=[
                    ft.Container(expand=True),
                    ft.Text(anime.get("title", ""), size=10,
                            color=C_WHITE, weight=ft.FontWeight.BOLD,
                            max_lines=2),
                    ft.Text(sg_str, size=9, color="#D4A8BC"),
                    genre_row,
                ],
                spacing=4,
            ),
            visible=False,
        )

        sp_txt = f"you: {self.sp:.1f}" if is_rated else "you: N/A"
        sp_col = C_PURPLE if is_rated else C_TEXT3

        info = ft.Container(
            padding=ft.padding.only(left=7, right=7, top=4, bottom=5),
            bgcolor=C_WHITE,
            border_radius=ft.border_radius.only(bottom_left=10, bottom_right=10),
            content=ft.Column(
                controls=[
                    ft.Text(anime.get("title", "—"), size=10,
                            color=C_TEXT, weight=ft.FontWeight.BOLD,
                            max_lines=1, overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(controls=[
                        ft.Text(f"★ {self.sg:.1f}" if self.sg else "★ —",
                                size=9, color=C_GOLD, weight=ft.FontWeight.BOLD),
                        ft.Text("·", size=9, color=C_BORDER),
                        ft.Text(sp_txt, size=9, color=sp_col,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=3),
                ],
                spacing=2,
                tight=True,
            ),
        )

        card_stack = ft.Stack(
            controls=[poster_content, self._overlay],
            width=140, height=162,
        )

        self.content = ft.Column(
            controls=[
                ft.Stack(
                    controls=[
                        card_stack,
                        ft.Container(content=badge, top=6, right=6),
                    ],
                    width=140, height=162,
                ),
                info,
            ],
            spacing=0,
            tight=True,
        )

    def _on_hover(self, e):
        # Flet terbaru mengirim e.data sebagai string "true"/"false" atau bool True/False
        is_hovered = str(e.data).lower() == "true"

        # Munculkan overlay sinopsis/genre
        self._overlay.visible = is_hovered

        # Ganti border (Gunakan string 'sakura' atau variabel warna)
        self.border = ft.border.all(1.5 if is_hovered else 1, C_SAKURA if is_hovered else C_BORDER)

        # Update komponen
        self.update()


class UIDashboard(ft.Row):
    CARDS_PER_PAGE = 12

    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()

        self.my_page = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager

        self._filter = "all"
        self._sort = "title"
        self._keyword = ""
        self._halaman = 1
        self._total_pg = 1
        self._sidebar_open = False

        self.expand = True
        self.spacing = 0

        # ── Sidebar ──────────────────────────────
        nav_btn_style = dict(
            style=ft.ButtonStyle(
                color={ft.ControlState.DEFAULT: C_TEXT},
                bgcolor={ft.ControlState.HOVERED: C_BG2, ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=16, vertical=12),
            )
        )

        self._sidebar = ft.Container(
            width=0,
            height=self.my_page.height,
            bgcolor=None,
            content=ft.Container(
                width=200,
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=["#FDEEF4", "#EAF3FC"],
                ),
                border=ft.border.only(right=ft.BorderSide(1, C_BORDER)),
                padding=ft.padding.only(left=16, right=16, top=32, bottom=32),
                content=ft.Column(
                    controls=[
                        ft.Row([
                            ft.IconButton(
                                ft.Icons.CHEVRON_LEFT,
                                icon_color=C_SAKURA,
                                on_click=self._toggle_sidebar,
                            )
                        ], alignment=ft.MainAxisAlignment.END),
                        ft.Container(height=8),
                        ft.TextButton(
                            "🏠   Dashboard",
                            **nav_btn_style,
                            expand=True,
                        ),
                        ft.TextButton(
                            "👤   Profile",
                            **nav_btn_style,
                            expand=True,
                            on_click=lambda _: self.screen_manager.tampilkan_profil(),
                        ),
                        ft.Container(expand=True),
                        ft.Divider(color=C_BORDER, height=1),
                        ft.TextButton(
                            "↪   Log Out",
                            style=ft.ButtonStyle(
                                color={ft.ControlState.DEFAULT: C_TEXT2},
                                bgcolor={ft.ControlState.HOVERED: C_BG2, ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                            ),
                            expand=True,
                            on_click=lambda _: self._aksi_logout(),
                        ),
                        ft.TextButton(
                            "✖   Delete Account",
                            style=ft.ButtonStyle(
                                color={ft.ControlState.DEFAULT: "#C04040"},
                                bgcolor={ft.ControlState.HOVERED: "#FCE8E8", ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
                                shape=ft.RoundedRectangleBorder(radius=8),
                                padding=ft.padding.symmetric(horizontal=14, vertical=10),
                            ),
                            expand=True,
                            on_click=lambda _: self._aksi_hapus_akun(),
                        ),
                    ],
                    spacing=4,
                    expand=True,
                ),
            ),
            animate_size=ft.Animation(280, ft.AnimationCurve.EASE_OUT),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        # ── Top Bar ───────────────────────────────
        self._search = ft.TextField(
            hint_text="🔍  Search anime...",
            hint_style=ft.TextStyle(color=C_TEXT3, size=12),
            border_color=C_BORDER,
            focused_border_color=C_SAKURA,
            border_radius=20,
            height=36,
            text_size=12,
            content_padding=ft.padding.symmetric(horizontal=16, vertical=0),
            bgcolor=C_WHITE,
            color=C_TEXT,
            width=240,
            on_change=self._on_search,
        )

        topbar = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
            padding=ft.padding.symmetric(horizontal=16),
            height=48,
            content=ft.Row(
                controls=[
                    ft.IconButton(
                        ft.Icons.MENU,
                        icon_color=C_SAKURA,
                        on_click=self._toggle_sidebar,
                        tooltip="Menu",
                    ),
                    ft.Column([
                        ft.Text("RadarAni", size=15, color=C_SAKURA,
                                weight=ft.FontWeight.BOLD),
                        ft.Text("レーダアニ", size=9, color=C_TEXT3),
                    ], spacing=0, tight=True),
                    ft.Container(expand=True),
                    self._search,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        # ── Header ────────────────────────────────
        user_id = self.auth_manager.get_user_aktif()
        username = "User"
        if user_id and hasattr(self.data_manager, "get_profil_user"):
            username = self.data_manager.get_profil_user(user_id).get("username", "User")

        self._stat_rated = build_pill("— rated", "📊")
        self._stat_unrated = build_pill("— unrated", "🎌")
        self._stat_avg = build_pill("avg —", "⭐")
        self._stat_dim = build_pill("top: —", "✨")
        self._perbarui_stats()

        self._rec_title = ft.Text("—", size=13, color=C_TEXT,
                                weight=ft.FontWeight.BOLD, max_lines=1,
                                overflow=ft.TextOverflow.ELLIPSIS)
        self._rec_reason = ft.Text("Based on your top dimension",
                                size=10, color="#A07888")
        self._rec_anime_id = None

        rec_banner = ft.Container(
            bgcolor=C_SAKURA_LT,
            border=ft.border.all(1, "#E8D0DE"),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row(
                controls=[
                    ft.Container(
                        width=32, height=44,
                        bgcolor="#D4A8C0",
                        border_radius=4,
                    ),
                    ft.Column(
                        controls=[
                            ft.Text("✦  RECOMMENDED FOR YOU",
                                    size=9, color="#9B6080",
                                    weight=ft.FontWeight.BOLD),
                            self._rec_title,
                            self._rec_reason,
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                    ft.ElevatedButton(
                        "View",
                        bgcolor=C_SAKURA, color=C_WHITE,
                        style=ft.ButtonStyle(
                            shape=ft.RoundedRectangleBorder(radius=8),
                            padding=ft.padding.symmetric(horizontal=14, vertical=6),
                        ),
                        on_click=lambda _: self._klik_rekomendasi(),
                    ),
                ],
                spacing=10,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        header = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
            padding=ft.padding.only(left=20, right=20, top=12, bottom=10),
            content=ft.Column(
                controls=[
                    ft.Text(f"🌸  Konnichiwa, {username}!",
                            size=18, color="#5C3D52",
                            weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[self._stat_rated, self._stat_unrated,
                                self._stat_avg, self._stat_dim],
                        spacing=6,
                    ),
                    rec_banner,
                ],
                spacing=8,
            ),
        )

        # ── Toolbar ───────────────────────────────
        self._btn_all = self._filter_btn("All", "all", active=True)
        self._btn_rated = self._filter_btn("Rated", "rated")
        self._btn_unrated = self._filter_btn("Unrated", "unrated")

        self._sort_dd = ft.Dropdown(
            options=[
                ft.DropdownOption(key="title", text="Title"),
                ft.DropdownOption(key="global", text="Global Score"),
                ft.DropdownOption(key="personal", text="Your Score"),
            ],
            value="title",
            width=150,
            height=34,
            text_size=11,
            border_color=C_BORDER,
            focused_border_color=C_SAKURA,
            border_radius=8,
            bgcolor=C_BG2,
            color=C_TEXT2,
            content_padding=ft.padding.symmetric(horizontal=10, vertical=0),
            on_select=self._on_sort,
        )

        toolbar = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(bottom=ft.BorderSide(1, C_BORDER)),
            height=42,
            padding=ft.padding.symmetric(horizontal=20),
            content=ft.Row(
                controls=[
                    self._btn_all,
                    self._btn_rated,
                    self._btn_unrated,
                    ft.Container(expand=True),
                    ft.Text("Sort:", size=11, color=C_TEXT2),
                    self._sort_dd,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
        )

        # ── Grid Area ─────────────────────────────
        self._grid = ft.GridView(
            expand=True,
            runs_count=6,
            max_extent=150,
            child_aspect_ratio=0.64,
            spacing=10,
            run_spacing=10,
            padding=ft.padding.all(16),
        )

        # ── Pagination ────────────────────────────
        self._pg_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=4,
        )

        pagination = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(top=ft.BorderSide(1, C_BORDER)),
            height=44,
            content=ft.Row(
                [self._pg_row],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
        )

        # ── Konten utama ──────────────────────────
        self._main_col = ft.Column(
            controls=[topbar, header, toolbar,
                    ft.Container(content=self._grid, expand=True),
                    pagination],
            spacing=0,
            expand=True,
        )

        self.controls = [self._sidebar, self._main_col]
        self.muat_tabel_anime()

    # ── PUBLIC ────────────────────────────────────

    def muat_tabel_anime(self):
        self._grid.controls.clear()

        keyword = self._keyword
        if keyword:
            data = self.data_manager.cari_anime(keyword)
        else:
            data = self.data_manager.get_semua_anime()

        user_id = self.auth_manager.get_user_aktif()

        if self._filter == "rated":
            data = [a for a in data
                    if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is not None]
        elif self._filter == "unrated":
            data = [a for a in data
                    if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is None]

        if self._sort == "title":
            data.sort(key=lambda a: a.get("title", "").lower())
        elif self._sort == "global":
            data.sort(key=lambda a: self.data_manager.hitung_skor_global(a["anime_id"]) or 0, reverse=True)
        elif self._sort == "personal":
            data.sort(key=lambda a: self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) or 0, reverse=True)

        self._total_pg = max(1, math.ceil(len(data) / self.CARDS_PER_PAGE))
        self._halaman = min(self._halaman, self._total_pg)

        start = (self._halaman - 1) * self.CARDS_PER_PAGE
        halaman_data = data[start: start + self.CARDS_PER_PAGE]

        if not halaman_data:
            self._grid.controls.append(
                ft.Container(
                    content=ft.Text("Tidak ada anime ditemukan.",
                                    color=C_TEXT3, size=13),
                    alignment=ft.Alignment(0, 0),
                    expand=True,
                )
            )
        else:
            for anime in halaman_data:
                sg = self.data_manager.hitung_skor_global(anime["anime_id"])
                sp = self.data_manager.hitung_skor_personal(user_id, anime["anime_id"])
                card = AnimeCard(anime, sg, sp,
                                on_click_callback=self.screen_manager.tampilkan_detail)
                self._grid.controls.append(card)

        self._render_pagination()

        if self.my_page:
            try:
                self.my_page.update()
            except Exception:
                pass

    # ── EVENT HANDLERS ────────────────────────────

    def _on_search(self, e):
        self._keyword = e.control.value.strip()
        self._halaman = 1
        self.muat_tabel_anime()

    def _on_sort(self, e):
        self._sort = e.control.value
        self._halaman = 1
        self.muat_tabel_anime()

    def _set_filter(self, val: str):
        self._filter = val
        self._halaman = 1
        active_style = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_WHITE},
            bgcolor={ft.ControlState.DEFAULT: C_SAKURA},
            shape=ft.RoundedRectangleBorder(radius=16),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )
        normal_style = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_TEXT2, ft.ControlState.HOVERED: C_TEXT},
            bgcolor={ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT, ft.ControlState.HOVERED: C_BG2},
            shape=ft.RoundedRectangleBorder(radius=16),
            side=ft.BorderSide(1, C_BORDER),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )
        self._btn_all.style = active_style if val == "all" else normal_style
        self._btn_rated.style = active_style if val == "rated" else normal_style
        self._btn_unrated.style = active_style if val == "unrated" else normal_style
        self._btn_all.update()
        self._btn_rated.update()
        self._btn_unrated.update()
        self.muat_tabel_anime()

    def _toggle_sidebar(self, e=None):
        self._sidebar_open = not self._sidebar_open
        self._sidebar.width = 240 if self._sidebar_open else 0
        self._sidebar.update()

    def _aksi_logout(self):
        self.auth_manager.logout()
        self.screen_manager.tampilkan_login()

    def _aksi_hapus_akun(self):
        def confirm(e):
            if e.control.text == "Hapus":
                self.auth_manager.hapus_akun_aktif()
                self.my_page.close(dlg)
                self.screen_manager.tampilkan_login()
            else:
                self.my_page.close(dlg)

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus Akun?"),
            content=ft.Text("Semua data rating kamu akan ikut terhapus."),
            actions=[
                ft.TextButton("Batal", on_click=confirm),
                ft.TextButton("Hapus",
                            style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: "#C04040"}),
                            on_click=confirm),
            ],
        )
        self.my_page.open(dlg)

    def _klik_rekomendasi(self):
        if self._rec_anime_id:
            self.screen_manager.tampilkan_detail(self._rec_anime_id)

    # ── HELPERS ───────────────────────────────────

    def _filter_btn(self, label: str, val: str, active=False) -> ft.TextButton:
        style = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_WHITE if active else C_TEXT2},
            bgcolor={ft.ControlState.DEFAULT: C_SAKURA if active else ft.Colors.TRANSPARENT,
                    ft.ControlState.HOVERED: C_BG2 if not active else C_SAKURA},
            shape=ft.RoundedRectangleBorder(radius=16),
            side=ft.BorderSide(1, C_SAKURA if active else C_BORDER),
            padding=ft.padding.symmetric(horizontal=16, vertical=4),
        )
        return ft.TextButton(
            label,
            style=style,
            on_click=lambda _, v=val: self._set_filter(v),
        )

    def _render_pagination(self):
        self._pg_row.controls.clear()
        total = self._total_pg
        cur = self._halaman

        def pg_btn(n, active=False):
            return ft.TextButton(
                str(n),
                style=ft.ButtonStyle(
                    color={ft.ControlState.DEFAULT: C_WHITE if active else C_TEXT2},
                    bgcolor={ft.ControlState.DEFAULT: C_SAKURA if active else ft.Colors.TRANSPARENT,
                            ft.ControlState.HOVERED: C_BG2},
                    shape=ft.RoundedRectangleBorder(radius=6),
                    side=ft.BorderSide(1, C_SAKURA if active else C_BORDER),
                    padding=ft.padding.symmetric(horizontal=12, vertical=4),
                ),
                on_click=lambda _, pg=n: self._ganti_halaman(pg),
            )

        pages = list(range(1, min(4, total + 1)))
        if total > 4:
            pages += [None, total]

        for p in pages:
            if p is None:
                self._pg_row.controls.append(
                    ft.Text("…", color=C_TEXT3, size=11)
                )
            else:
                self._pg_row.controls.append(pg_btn(p, active=(p == cur)))

        self._pg_row.controls.append(
            ft.Text(f"of {total} pages", color=C_TEXT3, size=11)
        )

    def _ganti_halaman(self, n: int):
        self._halaman = n
        self.muat_tabel_anime()

    def _perbarui_stats(self):
        user_id = self.auth_manager.get_user_aktif()
        semua = self.data_manager.get_semua_anime()
        rated = sum(
            1 for a in semua
            if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is not None
        )
        unrated = len(semua) - rated

        avg_dim = {}
        if hasattr(self.data_manager, "get_avg_dimensi_user"):
            avg_dim = self.data_manager.get_avg_dimensi_user(user_id) or {}
        top_dim = max(avg_dim, key=avg_dim.get).capitalize() if avg_dim else "—"

        scores = [
            self.data_manager.hitung_skor_personal(user_id, a["anime_id"])
            for a in semua
        ]
        scores = [s for s in scores if s is not None]
        avg_val = f"{sum(scores) / len(scores):.1f}" if scores else "—"

        self._stat_rated.content = ft.Text(f"📊  {rated} rated", size=11, color=C_TEXT2)
        self._stat_unrated.content = ft.Text(f"🎌  {unrated} unrated", size=11, color=C_TEXT2)
        self._stat_avg.content = ft.Text(f"⭐  avg {avg_val}", size=11, color=C_TEXT2)
        self._stat_dim.content = ft.Text(f"✨  top: {top_dim}", size=11, color=C_TEXT2)

