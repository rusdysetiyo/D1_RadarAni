import flet as ft
import math

C_BG         = "#FCF8FA"
C_BG2        = "#F5EEF2"
C_SAKURA     = "#C07090"
C_SAKURA_LT  = "#F9F0F5"
C_BLUE_LT    = "#D4EBF8"
C_TEXT       = "#3D2535"
C_TEXT2      = "#8B6A7A"
C_TEXT3      = "#B0909A"
C_BORDER     = "#EDE0E8"
C_GOLD       = "#C08030"
C_PURPLE     = "#9060A0"
C_WHITE      = "#FFFFFF"


def build_pill(text: str, icon: str = "") -> ft.Container:
    return ft.Container(
        content=ft.Text(f"{icon}  {text}" if icon else text, size=11, color=C_TEXT2),
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

        # --- KONFIGURASI CARD AWAL ---
        self.width = 140
        self.bgcolor = C_WHITE
        self.border = ft.border.all(1, C_BORDER)
        self.border_radius = 10
        self.clip_behavior = ft.ClipBehavior.HARD_EDGE
        self.on_hover = self._on_hover
        self.on_click = lambda _: self._on_click_cb(self.anime.get("anime_id", ""))

        # FIX POP OUT: Inisialisasi Scale awal (normal) dan Bayangan (polos)
        self.scale = 1.0
        self.shadow = None

        # Animasi digeneralisasi (akan mengcover border, scale, dan shadow sekaligus)
        self.animate = ft.Animation(duration=150, curve=ft.AnimationCurve.EASE_IN_OUT)

        is_rated = self.sp is not None

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
            poster_content = ft.Image(
                src=thumb, width=140, height=162,
                fit=ft.BoxFit.COVER,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
            )
        else:
            poster_content = ft.Container(
                width=140, height=162,
                bgcolor=C_BG2,
                border_radius=ft.border_radius.only(top_left=10, top_right=10),
                content=ft.Text(anime.get("title", "")[:14], size=9, color=C_TEXT3,
                                text_align=ft.TextAlign.CENTER),
                alignment=ft.alignment.center,
            )

        genres = anime.get("genre", [])[:3]
        sg_str = (f"★ {self.sg:.1f}  ·  {anime.get('episodes', '?')} eps  ·  {anime.get('broadcast_type', 'TV')}"
                  if self.sg else f"{anime.get('episodes', '?')} eps")

        self._overlay = ft.Container(
            width=140, height=162,
            bgcolor="#1C0C16CC",
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
                    ),
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
                    ft.Text(anime.get("title", "—"), size=10, color=C_TEXT,
                            weight=ft.FontWeight.BOLD, max_lines=1,
                            overflow=ft.TextOverflow.ELLIPSIS),
                    ft.Row(controls=[
                        ft.Text(f"★ {self.sg:.1f}" if self.sg else "★ —",
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
                        ft.Stack(controls=[poster_content, self._overlay], width=140, height=162),
                        ft.Container(content=badge, top=6, right=6),
                    ],
                    width=140, height=162,
                ),
                info,
            ],
            spacing=0, tight=True,
        )

    # --- LOGIKA POP OUT SAAT HOVER ---
    def _on_hover(self, e):
        is_hovered = str(e.data).lower() == "true"

        # 1. Overlay Detail tetap muncul
        self._overlay.visible = is_hovered

        # 2. FIX POP OUT: Border, Scale, dan Shadow berubah mulus
        if is_hovered:
            self.border = ft.border.all(1.5, C_SAKURA)
            self.scale = 1.03  # Naik 3% biar pop out (kerasa lifting)
            self.shadow = ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLACK12,  # Bayangan tipis abu-abu
                offset=ft.Offset(0, 4),  # Jatuh sedikit ke bawah biar kerasa melayang
            )
        else:
            # Kembalikan ke normal
            self.border = ft.border.all(1, C_BORDER)
            self.scale = 1.0
            self.shadow = None

        self.update()


class UIDashboard(ft.Row):
    CARDS_PER_PAGE = 12

    def __init__(self, page, data_manager, auth_manager, screen_manager):
        super().__init__()
        self.my_page        = page
        self.data_manager   = data_manager
        self.auth_manager   = auth_manager
        self.screen_manager = screen_manager

        self._filter       = "all"
        self._sort         = "title"
        self._keyword      = ""
        self._halaman      = 1
        self._total_pg     = 1
        self._sidebar_open = False

        self.expand  = True
        self.spacing = 0

        # ── Sidebar ───────────────────────────────────────────
        nav_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_TEXT},
            bgcolor={ft.ControlState.HOVERED: C_BG2,
                     ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
            shape=ft.RoundedRectangleBorder(radius=10),
            padding=ft.padding.symmetric(horizontal=16, vertical=10),
            alignment=ft.Alignment(-1, 0),
        )
        danger_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: C_TEXT2},
            bgcolor={ft.ControlState.HOVERED: C_BG2,
                     ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            alignment=ft.Alignment(-1, 0),
        )
        delete_s = ft.ButtonStyle(
            color={ft.ControlState.DEFAULT: "#C04040"},
            bgcolor={ft.ControlState.HOVERED: "#FCE8E8",
                     ft.ControlState.DEFAULT: ft.Colors.TRANSPARENT},
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            alignment=ft.Alignment(-1, 0),
        )

        self._sidebar = ft.Container(
            width=0,
            bgcolor=None,
            content=ft.Container(
                width=240,
                expand=True,
                gradient=ft.LinearGradient(
                    begin=ft.Alignment(0, -1),
                    end=ft.Alignment(0, 1),
                    colors=["#FDEEF4", "#EAF3FC"],
                ),
                border=ft.border.only(right=ft.BorderSide(1, C_BORDER)),
                padding=ft.padding.only(left=12, right=12, top=24, bottom=24),
                content=ft.Column(
                    controls=[
                        # Close button
                        ft.Row(
                            [ft.IconButton(
                                ft.Icons.CHEVRON_LEFT,
                                icon_color=C_SAKURA,
                                icon_size=20,
                                on_click=self._toggle_sidebar,
                            )],
                            alignment=ft.MainAxisAlignment.END,
                        ),
                        ft.Container(height=8),

                        # Nav items (FIX: hapus expand=True, ganti jadi width=216)
                        ft.TextButton("🏠   Dashboard", style=nav_s, width=216),
                        ft.TextButton(
                            "👤   Profile", style=nav_s, width=216,
                            on_click=lambda _: self.screen_manager.tampilkan_profil(),
                        ),

                        # Push to bottom (Yang ini biarin expand=True biar dia jadi pendorong ke bawah)
                        ft.Container(expand=True),
                        ft.Divider(color=C_BORDER, height=1, thickness=1),
                        ft.Container(height=4),

                        # Bottom Actions (FIX: hapus expand=True, ganti jadi width=216)
                        ft.TextButton(
                            "↪   Log Out", style=danger_s, width=216,
                            on_click=lambda _: self._aksi_logout(),
                        ),
                        ft.TextButton(
                            "✖   Delete Account", style=delete_s, width=216,
                            on_click=lambda _: self._aksi_hapus_akun(),
                        ),
                    ],
                    spacing=2,
                    expand=True,
                ),
            ),
            animate_size=ft.Animation(duration=280, curve=ft.AnimationCurve.EASE_OUT),
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

        # ── Top Bar ───────────────────────────────────────────
        self._search = ft.TextField(
            hint_text="Search anime...",
            hint_style=ft.TextStyle(color=C_TEXT3, size=12),
            prefix_icon=ft.Icons.SEARCH,
            border_color=C_BORDER,
            focused_border_color=C_SAKURA,
            border_radius=20,
            height=36,
            text_size=12,
            content_padding=ft.padding.symmetric(horizontal=12, vertical=0),
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
                        ft.Icons.MENU, icon_color=C_SAKURA,
                        on_click=self._toggle_sidebar, tooltip="Menu",
                    ),
                    # ← Title lebih kecil & compact
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

        # ── Header ────────────────────────────────────────────
        user_id  = self.auth_manager.get_user_aktif()
        username = "User"
        if user_id and hasattr(self.data_manager, "get_profil_user"):
            username = self.data_manager.get_profil_user(user_id).get("username", "User")

        self._stat_rated   = build_pill("— rated",   "📊")
        self._stat_unrated = build_pill("— unrated", "🎌")
        self._stat_avg     = build_pill("avg —",     "⭐")
        self._stat_dim     = build_pill("top: —",    "✨")
        self._perbarui_stats()

        self._rec_title    = ft.Text("—", size=13, color=C_TEXT,
                                     weight=ft.FontWeight.BOLD, max_lines=1,
                                     overflow=ft.TextOverflow.ELLIPSIS)
        self._rec_reason   = ft.Text("Based on your top dimension", size=10, color="#A07888")
        self._rec_anime_id = None

        rec_banner = ft.Container(
            bgcolor=C_SAKURA_LT,
            border=ft.border.all(1, "#E8D0DE"),
            border_radius=10,
            padding=ft.padding.symmetric(horizontal=12, vertical=8),
            content=ft.Row(
                controls=[
                    ft.Container(width=32, height=44, bgcolor="#D4A8C0", border_radius=4),
                    ft.Column(
                        controls=[
                            ft.Text("✦  RECOMMENDED FOR YOU", size=9, color="#9B6080",
                                    weight=ft.FontWeight.BOLD),
                            self._rec_title,
                            self._rec_reason,
                        ],
                        spacing=2, tight=True, expand=True,
                    ),
                    ft.ElevatedButton(
                        "View", bgcolor=C_SAKURA, color=C_WHITE,
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
                    ft.Text(f"🌸  Konnichiwa, {username}!", size=18, color="#5C3D52",
                            weight=ft.FontWeight.BOLD),
                    ft.Row(controls=[self._stat_rated, self._stat_unrated,
                                     self._stat_avg, self._stat_dim], spacing=6),
                    rec_banner,
                ],
                spacing=8,
            ),
        )

        # ── Toolbar ───────────────────────────────────────────
        self._btn_all     = self._filter_btn("All",     "all",     active=True)
        self._btn_rated   = self._filter_btn("Rated",   "rated")
        self._btn_unrated = self._filter_btn("Unrated", "unrated")

        # INI DROPDOWN LU, KEMBALI SEPERTI ASLINYA TANPA DIUBAH
        self._sort_dd = ft.Dropdown(
            options=[
                ft.DropdownOption(key="title", text="Title"),
                ft.DropdownOption(key="global", text="Global Score"),
                ft.DropdownOption(key="personal", text="Your Score"),
            ],
            value="title",
            width=130, height=36, text_size=11,  # FIX: height dilegakan, width ditambah
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
                    self._btn_all, self._btn_rated, self._btn_unrated,
                    ft.Container(expand=True),
                    ft.Text("Sort:", size=11, color=C_TEXT2),
                    self._sort_dd,
                ],
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=6,
            ),
        )

        # ── Grid ──────────────────────────────────────────────
        # INI FIX GAP-NYA, pakai ft.Row dan wrap
        self._grid = ft.Row(
            wrap=True,
            spacing=16,
            run_spacing=16,
            alignment=ft.MainAxisAlignment.START,
        )

        grid_container = ft.Container(
            content=ft.Column([self._grid], scroll="auto", expand=True),
            expand=True,
            padding=ft.padding.all(16)
        )

        # ── Pagination ────────────────────────────────────────
        self._pg_row = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=4)

        pagination = ft.Container(
            bgcolor=C_WHITE,
            border=ft.border.only(top=ft.BorderSide(1, C_BORDER)),
            height=44,
            content=ft.Row([self._pg_row], alignment=ft.MainAxisAlignment.CENTER),
        )

        self._main_col = ft.Column(
            controls=[
                topbar, header, toolbar,
                grid_container,
                pagination,
            ],
            spacing=0, expand=True,
        )

        self.controls = [self._sidebar, self._main_col]
        self.muat_tabel_anime()

    # ── PUBLIC ────────────────────────────────────────────────

    def muat_tabel_anime(self):
        self._grid.controls.clear()

        data    = self.data_manager.cari_anime(self._keyword) \
                  if self._keyword else self.data_manager.get_semua_anime()
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
        self._halaman  = min(self._halaman, self._total_pg)

        start        = (self._halaman - 1) * self.CARDS_PER_PAGE
        halaman_data = data[start: start + self.CARDS_PER_PAGE]

        if not halaman_data:
            self._grid.controls.append(
                ft.Container(
                    content=ft.Text("Tidak ada anime ditemukan.", color=C_TEXT3, size=13),
                    alignment=ft.alignment.center, expand=True,
                )
            )
        else:
            for anime in halaman_data:
                sg   = self.data_manager.hitung_skor_global(anime["anime_id"])
                sp   = self.data_manager.hitung_skor_personal(user_id, anime["anime_id"])
                card = AnimeCard(anime, sg, sp,
                                 on_click_callback=self.screen_manager.tampilkan_detail)
                self._grid.controls.append(card)

        self._render_pagination()
        try:
            self.my_page.update()
        except Exception:
            pass

    # ── EVENT HANDLERS ────────────────────────────────────────

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
            color={ft.ControlState.DEFAULT: C_TEXT2, ft.ControlState.HOVERED: C_TEXT},
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

    def _toggle_sidebar(self, e=None):
        self._sidebar_open    = not self._sidebar_open
        self._sidebar.width   = 240 if self._sidebar_open else 0
        self._sidebar.update()

    def _aksi_logout(self):
        self.auth_manager.logout()
        self.screen_manager.tampilkan_login()

    def _aksi_hapus_akun(self):
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Hapus Akun?"),
            content=ft.Text("Semua data rating kamu akan ikut terhapus."),
        )

        def confirm(e):
            dlg.open = False
            self.my_page.update()
            if e.control.text == "Hapus":
                self.auth_manager.hapus_akun_aktif()
                self.screen_manager.tampilkan_login()

        dlg.actions = [
            ft.TextButton("Batal", on_click=confirm),
            ft.TextButton("Hapus",
                          style=ft.ButtonStyle(color={ft.ControlState.DEFAULT: "#C04040"}),
                          on_click=confirm),
        ]
        self.my_page.overlay.append(dlg)
        dlg.open = True
        self.my_page.update()

    def _klik_rekomendasi(self):
        if self._rec_anime_id:
            self.screen_manager.tampilkan_detail(self._rec_anime_id)

    # ── HELPERS ───────────────────────────────────────────────

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

    def _render_pagination(self):
        self._pg_row.controls.clear()
        total = self._total_pg
        cur   = self._halaman

        if total <= 1:
            return

        pages = set()
        pages.add(1)
        pages.add(total)
        for i in range(max(1, cur - 2), min(total, cur + 2) + 1):
            pages.add(i)
        pages_sorted = sorted(pages)

        def pg_btn(n):
            active = (n == cur)
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

        prev = None
        for p in pages_sorted:
            if prev is not None and p - prev > 1:
                self._pg_row.controls.append(
                    ft.Text("…", color=C_TEXT3, size=11)
                )
            self._pg_row.controls.append(pg_btn(p))
            prev = p

        self._pg_row.controls.append(
            ft.Text(f"of {total} pages", color=C_TEXT3, size=11)
        )

    def _ganti_halaman(self, n: int):
        self._halaman = n
        self.muat_tabel_anime()

    def _perbarui_stats(self):
        user_id = self.auth_manager.get_user_aktif()
        semua   = self.data_manager.get_semua_anime()
        rated   = sum(
            1 for a in semua
            if self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) is not None
        )
        unrated = len(semua) - rated

        avg_dim = {}
        if hasattr(self.data_manager, "get_avg_dimensi_user"):
            avg_dim = self.data_manager.get_avg_dimensi_user(user_id) or {}
        top_dim = max(avg_dim, key=avg_dim.get).capitalize() if avg_dim else "—"

        scores  = [self.data_manager.hitung_skor_personal(user_id, a["anime_id"]) for a in semua]
        scores  = [s for s in scores if s is not None]
        avg_val = f"{sum(scores)/len(scores):.1f}" if scores else "—"

        self._stat_rated.content   = ft.Text(f"📊  {rated} rated",    size=11, color=C_TEXT2)
        self._stat_unrated.content = ft.Text(f"🎌  {unrated} unrated", size=11, color=C_TEXT2)
        self._stat_avg.content     = ft.Text(f"⭐  avg {avg_val}",    size=11, color=C_TEXT2)
        self._stat_dim.content     = ft.Text(f"✨  top: {top_dim}",   size=11, color=C_TEXT2)