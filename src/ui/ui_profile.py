# -*- coding: utf-8 -*-
import flet as ft
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import io
import base64


class UIProfile(ft.Container):
    def __init__(self, page: ft.Page, data_manager, auth_manager, screen_manager, theme):
        super().__init__(expand=True)
        self._page        = page
        self.data_manager = data_manager
        self.auth_manager = auth_manager
        self.screen_manager = screen_manager
        self.theme        = theme

        # ── Warna dari theme ────────────────────────────────────────────────
        self._PRIMARY     = theme["primary"]
        self._PRIMARY_MID = ft.Colors.with_opacity(0.70, theme["primary"])
        self._LIGHT       = theme.get("bg_secondary", theme["bg"])
        self._BORDER      = theme["border_color"]
        self._TEXT_DARK   = theme["text_main"]
        self._TEXT_MUTED  = theme.get("text_secondary", theme.get("text_muted", "#999"))
        self._BG          = theme["bg"]
        self._CARD        = theme["card"]

        # Genre colors: turunan dari primary (hue tetap, lightness bervariasi)
        self._GENRE_COLORS = [
            theme["primary"],
            ft.Colors.with_opacity(0.75, theme["primary"]),
            ft.Colors.with_opacity(0.55, theme["primary"]),
            ft.Colors.with_opacity(0.38, theme["primary"]),
            theme.get("text_secondary", "#999"),
        ]

        self._DIM_ICONS = {
            "Plot":             ft.Icons.BAR_CHART_ROUNDED,
            "Story / Plot":     ft.Icons.BAR_CHART_ROUNDED,
            "Visual":           ft.Icons.REMOVE_RED_EYE_OUTLINED,
            "Audio":            ft.Icons.MUSIC_NOTE_OUTLINED,
            "Characterization": ft.Icons.PERSON_OUTLINE_ROUNDED,
            "Direction":        ft.Icons.MOVIE_FILTER_OUTLINED,
            "Overall Avg":      ft.Icons.STAR_BORDER_ROUNDED,
            "Overall":          ft.Icons.STAR_BORDER_ROUNDED,
        }

        self.content = self.bangun_ui()

    # ── Chart generators ────────────────────────────────────────────────────
    def gambar_bar_chart(self, rata_rata: dict) -> str:
        dimensi = list(rata_rata.keys())
        nilai   = list(rata_rata.values())

        # Konversi hex primary ke RGB untuk matplotlib
        hex_p = self._PRIMARY.lstrip("#")
        r, g, b = tuple(int(hex_p[i:i+2], 16) / 255 for i in (0, 2, 4))
        bar_color  = (r, g, b)
        bg_color   = (r, g, b, 0.15)

        fig, ax = plt.subplots(figsize=(7.0, 3.2))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")

        for i, (dim, val) in enumerate(zip(dimensi, nilai)):
            ax.barh(i, 10,  color=bg_color, height=0.40, zorder=1, linewidth=0)
            ax.barh(i, val, color=bar_color, height=0.40, zorder=2, linewidth=0)
            ax.text(val + 0.15, i, str(val), va="center", ha="left",
                    fontsize=10, fontweight="bold", color="#2d1a2e")

        ax.set_yticks(range(len(dimensi)))
        ax.set_yticklabels(dimensi, fontsize=10, fontweight="600")
        ax.set_xlim(0, 10.9)
        ax.set_ylim(-0.7, len(dimensi) - 0.3)
        ax.invert_yaxis()
        ax.xaxis.set_visible(True)
        ax.set_xticks([0, 2, 4, 6, 8, 10])
        ax.xaxis.set_tick_params(labelsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(left=False)
        ax.grid(axis="x", linewidth=0.7, linestyle="--", alpha=0.3)
        plt.tight_layout(pad=0.8)

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=150, facecolor="#ffffff")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    def gambar_pie_chart(self, proporsi_genre: dict) -> str:
        sizes  = list(proporsi_genre.values())
        hex_p  = self._PRIMARY.lstrip("#")
        r, g, b = tuple(int(hex_p[i:i+2], 16) / 255 for i in (0, 2, 4))
        # 5 shade dari primary
        colors = [
            (r, g, b),
            (r, g, b, 0.75),
            (r, g, b, 0.55),
            (r, g, b, 0.38),
            (r, g, b, 0.22),
        ][:len(sizes)]

        fig, ax = plt.subplots(figsize=(3.2, 3.2))
        fig.patch.set_facecolor("#ffffff")
        ax.set_facecolor("#ffffff")
        ax.pie(sizes, colors=colors, startangle=90,
               wedgeprops={"linewidth": 2, "edgecolor": "white"}, radius=1.0)
        plt.tight_layout(pad=0.1)
        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, facecolor="#ffffff")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    # ── Aksi ────────────────────────────────────────────────────────────────
    def aksi_tombol_kembali(self, e):
        self.screen_manager.tampilkan_home()

    def aksi_tombol_hapus_akun(self, e):
        def _konfirmasi_hapus(ev):
            dlg.open = False
            self._page.update()
            self.auth_manager.hapus_akun_aktif()
            self.screen_manager.tampilkan_login()

        def _batal(ev):
            dlg.open = False
            self._page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color="#d94040", size=20),
                ft.Text("Hapus Akun", weight=ft.FontWeight.W_800,
                        color="#d94040", size=14),
            ], spacing=8),
            content=ft.Text(
                "Akun dan semua data ratingmu akan dihapus permanen.\n"
                "Tindakan ini tidak dapat dibatalkan.",
                size=12, color=self._TEXT_MUTED,
            ),
            actions=[
                ft.OutlinedButton(
                    "Batal", on_click=_batal,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1.5, self._BORDER),
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=self._TEXT_MUTED,
                    ),
                ),
                ft.ElevatedButton(
                    "Ya, Hapus Akun", on_click=_konfirmasi_hapus,
                    style=ft.ButtonStyle(
                        bgcolor="#d94040", color="#ffffff",
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=self._CARD,
        )
        self._page.overlay.append(dlg)
        dlg.open = True
        self._page.update()

    def aksi_tombol_logout(self, e):
        def _konfirmasi_logout(ev):
            dlg.open = False
            self._page.update()
            self.auth_manager.logout()
            self.screen_manager.tampilkan_login()

        def _batal(ev):
            dlg.open = False
            self._page.update()

        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Row([
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=self._PRIMARY, size=20),
                ft.Text("Logout", weight=ft.FontWeight.W_800,
                        color=self._PRIMARY, size=14),
            ], spacing=8),
            content=ft.Text(
                "Kamu akan keluar dari akun ini.",
                size=12, color=self._TEXT_MUTED,
            ),
            actions=[
                ft.OutlinedButton(
                    "Batal", on_click=_batal,
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1.5, self._BORDER),
                        shape=ft.RoundedRectangleBorder(radius=8),
                        color=self._TEXT_MUTED,
                    ),
                ),
                ft.ElevatedButton(
                    "Ya, Logout", on_click=_konfirmasi_logout,
                    style=ft.ButtonStyle(
                        bgcolor=self._PRIMARY, color=self._CARD,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
            bgcolor=self._CARD,
        )
        self._page.overlay.append(dlg)
        dlg.open = True
        self._page.update()

    # ── Data ────────────────────────────────────────────────────────────────
    def muat_data_profil(self) -> dict:
        _FB = {"user": {"username": "-", "user_id": "-",
                        "created_at": "-", "last_login": "-"},
               "statistik": {}, "anime": [], "genre": {}}
        user_id = self.auth_manager.get_user_aktif()
        if user_id is None:
            self.screen_manager.tampilkan_login()
            return _FB
        user = self.data_manager.get_user_by_id(user_id)
        if user is None:
            self.auth_manager.logout()
            self.screen_manager.tampilkan_login()
            return _FB
        return {
            "user":      user,
            "statistik": self.data_manager.get_avg_dimensi_user(user_id),
            "anime":     self.data_manager.get_anime_favorit(user_id),
            "genre":     self.data_manager.get_top_genre_user(user_id),
        }

    # ── Sub-widgets ──────────────────────────────────────────────────────────
    def _info_row(self, icon, label: str, value: str,
                  is_last: bool = False) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Row([
                    ft.Icon(icon, size=13, color=self._TEXT_MUTED),
                    ft.Text(label, size=11, color=self._TEXT_MUTED,
                            weight=ft.FontWeight.W_500),
                ], spacing=5),
                ft.Text(value, size=11, color=self._TEXT_DARK,
                        weight=ft.FontWeight.BOLD),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=14, vertical=8),
            border=ft.border.only(
                bottom=ft.BorderSide(1, self._BORDER) if not is_last else None),
        )

    def _anime_item(self, rank: int, judul: str,
                    genre_initial: str) -> ft.Container:
        return ft.Container(
            content=ft.Row([
                ft.Text(f"#{rank}", size=11, color=self._PRIMARY,
                        weight=ft.FontWeight.W_800, width=24),
                ft.Text(judul, size=11, color=self._TEXT_DARK,
                        weight=ft.FontWeight.BOLD, expand=True),
                ft.Container(
                    content=ft.Text(genre_initial, size=10, color=self._CARD,
                                    weight=ft.FontWeight.W_800),
                    bgcolor=self._PRIMARY, border_radius=6,
                    width=24, height=24, alignment=ft.Alignment(0, 0),
                ),
            ], spacing=6, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            bgcolor=self._CARD,
            border=ft.border.all(1, self._BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=10, vertical=7),
        )

    def _empty_state(self, pesan: str) -> ft.Container:
        return ft.Container(
            content=ft.Column([
                ft.Icon(ft.Icons.INBOX_OUTLINED, color=self._BORDER, size=24),
                ft.Text(pesan, size=10, color=self._TEXT_MUTED,
                        text_align=ft.TextAlign.CENTER),
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               spacing=4, tight=True),
            bgcolor=self._LIGHT,
            border=ft.border.all(1, self._BORDER),
            border_radius=8,
            padding=ft.padding.symmetric(horizontal=10, vertical=12),
            alignment=ft.Alignment(0, 0),
            width=float("inf"),
        )

    def _section_title(self, teks: str) -> ft.Text:
        return ft.Text(teks.upper(), size=10, color=self._TEXT_MUTED,
                       weight=ft.FontWeight.W_800,
                       style=ft.TextStyle(letter_spacing=1.2))

    def _card(self, content: ft.Control, padding=16,
              expand=None, height=None) -> ft.Container:
        return ft.Container(
            content=content,
            bgcolor=self._CARD,
            border=ft.border.all(1, self._BORDER),
            border_radius=12,
            padding=padding,
            expand=expand,
            height=height,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )

    # ── BANGUN UI ────────────────────────────────────────────────────────────
    def bangun_ui(self) -> ft.Control:

        data           = self.muat_data_profil()
        user           = data["user"]
        statistik      = data["statistik"]
        anime_list     = data["anime"]
        genre_proporsi = data["genre"]

        ada_statistik = bool(statistik)
        ada_genre     = bool(genre_proporsi)

        _all_ratings = self.data_manager._read_json(self.data_manager.ratings_file) or {}
        total_rated  = len(_all_ratings.get(user.get("user_id", ""), {}))
        avg_overall  = (round(sum(statistik.values()) / len(statistik), 1)
                        if statistik else 0.0)
        total_genres = len(genre_proporsi)

        # ── TOPBAR ──────────────────────────────────────────────────────────
        top_bar = ft.Container(
            content=ft.Row([
                ft.OutlinedButton(
                    content=ft.Row([
                        ft.Icon(ft.Icons.CHEVRON_LEFT, color=self._PRIMARY, size=14),
                        ft.Text("Back to Dashboard", color=self._PRIMARY, size=11,
                                weight=ft.FontWeight.W_600),
                    ], alignment=ft.MainAxisAlignment.CENTER, spacing=2),
                    on_click=lambda e: self.aksi_tombol_kembali(e),
                    style=ft.ButtonStyle(
                        side=ft.BorderSide(1.5, self._BORDER),
                        shape=ft.RoundedRectangleBorder(radius=20),
                        padding=ft.padding.symmetric(horizontal=14, vertical=6),
                    ),
                ),
                ft.Text("RadarAni — プロフィール", size=13,
                        weight=ft.FontWeight.BOLD, color=self._PRIMARY),
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            padding=ft.padding.symmetric(horizontal=24, vertical=12),
            border=ft.border.only(bottom=ft.BorderSide(1, self._BORDER)),
            bgcolor=self._CARD,
        )

        # ── SIDEBAR ──────────────────────────────────────────────────────────
        avatar = ft.Container(
            content=ft.Icon(ft.Icons.PERSON_ROUNDED, size=46, color=self._PRIMARY),
            width=80, height=80, border_radius=40,
            border=ft.border.all(2, self._PRIMARY),
            bgcolor=self._LIGHT,
            alignment=ft.Alignment(0, 0),
        )

        def _stat_cell(angka, label):
            return ft.Container(
                content=ft.Column([
                    ft.Text(str(angka), size=16, weight=ft.FontWeight.W_800,
                            color=self._TEXT_DARK, text_align=ft.TextAlign.CENTER),
                    ft.Text(label, size=9, color=self._TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                ], spacing=0, tight=True,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                expand=1, padding=ft.padding.symmetric(vertical=8),
            )

        stat_strip = ft.Container(
            content=ft.Row([
                _stat_cell(total_rated, "Rated"),
                ft.VerticalDivider(width=1, color=self._BORDER),
                _stat_cell(avg_overall, "Avg"),
                ft.VerticalDivider(width=1, color=self._BORDER),
                _stat_cell(total_genres, "Genres"),
            ], spacing=0, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            border=ft.border.all(1, self._BORDER),
            border_radius=8,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            bgcolor=self._LIGHT,
        )

        info_rows = [
            self._info_row(ft.Icons.PERSON_OUTLINE,          "Username",
                           user.get("username", "-")),
            self._info_row(ft.Icons.TAG,                     "User ID",
                           user.get("user_id", "-")),
            self._info_row(ft.Icons.CALENDAR_TODAY_OUTLINED, "Created At",
                           str(user.get("created_at", "-"))[:10]),
            self._info_row(ft.Icons.LOGIN_OUTLINED,          "Last Login",
                           str(user.get("last_login", "-"))[:10]),
            self._info_row(ft.Icons.FAVORITE_BORDER,         "Total Ratings",
                           f"{total_rated} anime", is_last=True),
        ]
        account_info_card = ft.Container(
            content=ft.Column(info_rows, spacing=0, tight=True),
            border=ft.border.all(1, self._BORDER),
            border_radius=10,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
            bgcolor=self._CARD,
        )

        anime_controls = [
            self._anime_item(
                rank=i + 1,
                judul=a.get("title", "Unknown"),
                genre_initial=(", ".join(a.get("genre", [])[:1]) or "-")[0].upper(),
            )
            for i, a in enumerate(anime_list[:4])
        ] if anime_list else [self._empty_state("Belum ada anime favorit.")]

        tombol_logout = ft.OutlinedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.LOGOUT_ROUNDED, color=self._PRIMARY, size=15),
                ft.Text("Logout", color=self._PRIMARY, size=12,
                        weight=ft.FontWeight.W_700),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            on_click=lambda e: self.aksi_tombol_logout(e),
            style=ft.ButtonStyle(
                bgcolor=self._CARD,
                side=ft.BorderSide(1.5, self._BORDER),
                shape=ft.RoundedRectangleBorder(radius=10),
                overlay_color=ft.Colors.with_opacity(0.06, self._PRIMARY),
                padding=ft.padding.symmetric(horizontal=0, vertical=10),
            ),
            width=float("inf"),
        )

        tombol_hapus = ft.ElevatedButton(
            content=ft.Row([
                ft.Icon(ft.Icons.DELETE_OUTLINE_ROUNDED, color=self._CARD, size=15),
                ft.Text("Hapus Akun", color=self._CARD, size=12,
                        weight=ft.FontWeight.W_800,
                        style=ft.TextStyle(letter_spacing=0.3)),
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=6),
            on_click=lambda e: self.aksi_tombol_hapus_akun(e),
            style=ft.ButtonStyle(
                bgcolor="#d94040",
                overlay_color=ft.Colors.with_opacity(0.12, "#ffffff"),
                shape=ft.RoundedRectangleBorder(radius=10),
                padding=ft.padding.symmetric(horizontal=0, vertical=10),
            ),
            width=float("inf"),
        )

        sidebar = ft.Container(
            width=300,
            content=ft.Column([
                ft.Column([
                    avatar,
                    ft.Text(user.get("username", "-"), size=14,
                            weight=ft.FontWeight.W_800, color=self._TEXT_DARK,
                            text_align=ft.TextAlign.CENTER),
                    ft.Text(f"Member since {str(user.get('created_at',''))[:10]}",
                            size=9, color=self._TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                ], spacing=5, tight=True,
                   horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                stat_strip,
                self._section_title("Account Info"),
                account_info_card,
                self._section_title("Anime Favorit"),
                ft.Column(anime_controls, spacing=6, tight=True),
                tombol_logout,
                tombol_hapus,
            ], spacing=12, tight=True,
               horizontal_alignment=ft.CrossAxisAlignment.CENTER,
               scroll=ft.ScrollMode.AUTO),
            padding=ft.padding.symmetric(horizontal=18, vertical=18),
            border=ft.border.only(right=ft.BorderSide(1, self._BORDER)),
            bgcolor=self._BG,
        )

        # ── MAIN AREA ────────────────────────────────────────────────────────
        if not ada_statistik and not ada_genre:
            main_area = ft.Container(
                content=ft.Column([
                    ft.Icon(ft.Icons.STAR_BORDER_ROUNDED, color=self._BORDER, size=52),
                    ft.Text("Belum Ada Rating", size=16, weight=ft.FontWeight.W_800,
                            color=self._TEXT_DARK, text_align=ft.TextAlign.CENTER),
                    ft.Text("Mulai beri rating anime dari katalog!",
                            size=12, color=self._TEXT_MUTED,
                            text_align=ft.TextAlign.CENTER),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                   alignment=ft.MainAxisAlignment.CENTER, spacing=10),
                expand=True, alignment=ft.Alignment(0, 0),
            )
        else:
            all_dims    = list(statistik.items()) if ada_statistik else []
            overall_val = (round(sum(v for _, v in all_dims) / len(all_dims), 1)
                           if all_dims else 0.0)

            def _dim_card(label, val, highlight=False):
                icon = self._DIM_ICONS.get(label, ft.Icons.ANALYTICS_OUTLINED)
                return ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Icon(icon, size=15, color=self._PRIMARY),
                            ft.Text(label, size=11, color=self._TEXT_DARK,
                                    weight=ft.FontWeight.W_600),
                        ], spacing=5),
                        ft.Text(str(val), size=26, weight=ft.FontWeight.W_800,
                                color=self._PRIMARY),
                        ft.Text("/ 10", size=10, color=self._TEXT_MUTED),
                        ft.ProgressBar(value=val / 10, bgcolor=self._BORDER,
                                       color=self._PRIMARY, height=4),
                    ], spacing=3, tight=True),
                    bgcolor=self._LIGHT,
                    border=ft.border.all(1.5 if highlight else 1, self._BORDER),
                    border_radius=12,
                    padding=ft.padding.symmetric(horizontal=14, vertical=12),
                    expand=True,
                    height=110,
                    clip_behavior=ft.ClipBehavior.HARD_EDGE,
                )

            dim_row = ft.Row(
                controls=[_dim_card(l, v) for l, v in all_dims]
                         + [_dim_card("Overall Avg", overall_val, highlight=True)],
                spacing=12,
            )

            bar_b64  = self.gambar_bar_chart(statistik) if ada_statistik else None
            bar_card = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text("RATA-RATA DIMENSI", size=10,
                                        weight=ft.FontWeight.W_800,
                                        color=self._PRIMARY,
                                        style=ft.TextStyle(letter_spacing=1.1)),
                        bgcolor=self._LIGHT,
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        border=ft.border.only(bottom=ft.BorderSide(1, self._BORDER)),
                        width=float("inf"),
                    ),
                    ft.Container(
                        content=ft.Column([
                            ft.Text("(dari semua ratingmu)", size=10,
                                    color=self._TEXT_MUTED),
                            ft.Image(src=f"data:image/png;base64,{bar_b64}",
                                     fit="contain", expand=True)
                            if bar_b64 else self._empty_state("Belum ada data."),
                        ], spacing=4, expand=True),
                        padding=ft.padding.symmetric(horizontal=16, vertical=12),
                        expand=True,
                    ),
                ], spacing=0, expand=True),
                bgcolor=self._CARD,
                border=ft.border.all(1, self._BORDER),
                border_radius=12,
                expand=3, height=340,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )

            if ada_genre:
                pie_b64      = self.gambar_pie_chart(genre_proporsi)
                legend_items = [
                    ft.Row([
                        ft.Container(width=10, height=10,
                                     bgcolor=self._GENRE_COLORS[i % 5],
                                     border_radius=5),
                        ft.Text(label, size=11, color=self._TEXT_DARK,
                                weight=ft.FontWeight.W_600, expand=True),
                        ft.Text(f"{pct}%", size=11, color=self._TEXT_MUTED,
                                weight=ft.FontWeight.BOLD),
                    ], spacing=8)
                    for i, (label, pct) in enumerate(genre_proporsi.items())
                ]
                pie_body = ft.Container(
                    content=ft.Row([
                        ft.Image(src=f"data:image/png;base64,{pie_b64}",
                                 width=200, height=200, fit="contain"),
                        ft.Column(legend_items, spacing=8, tight=True, expand=True),
                    ], spacing=12,
                       vertical_alignment=ft.CrossAxisAlignment.CENTER,
                       expand=True),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    expand=True,
                )
            else:
                pie_body = ft.Container(
                    content=self._empty_state("Data genre belum tersedia."),
                    padding=ft.padding.symmetric(horizontal=16, vertical=12),
                    expand=True,
                )

            pie_card = ft.Container(
                content=ft.Column([
                    ft.Container(
                        content=ft.Text("PIE CHART — PROPORSI GENRE FAVORIT", size=10,
                                        weight=ft.FontWeight.W_800,
                                        color=self._PRIMARY,
                                        style=ft.TextStyle(letter_spacing=1.1)),
                        bgcolor=self._LIGHT,
                        padding=ft.padding.symmetric(horizontal=16, vertical=10),
                        border=ft.border.only(bottom=ft.BorderSide(1, self._BORDER)),
                        width=float("inf"),
                    ),
                    pie_body,
                ], spacing=0, expand=True),
                bgcolor=self._CARD,
                border=ft.border.all(1, self._BORDER),
                border_radius=12,
                expand=2, height=340,
                clip_behavior=ft.ClipBehavior.HARD_EDGE,
            )

            charts_row = ft.Row(
                controls=[bar_card, pie_card],
                spacing=12,
                vertical_alignment=ft.CrossAxisAlignment.START,
            )

            bintang_penuh    = int(avg_overall)
            bintang_setengah = 1 if (avg_overall - bintang_penuh) >= 0.5 else 0
            bintang_kosong   = 10 - bintang_penuh - bintang_setengah
            stars = (
                [ft.Icon(ft.Icons.STAR_ROUNDED, color="#f59e0b", size=20)]
                * bintang_penuh
                + ([ft.Icon(ft.Icons.STAR_HALF_ROUNDED, color="#f59e0b", size=20)]
                   if bintang_setengah else [])
                + [ft.Icon(ft.Icons.STAR_BORDER_ROUNDED, color="#f59e0b", size=20)]
                * bintang_kosong
            )

            avg_card = self._card(
                content=ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.BAR_CHART_ROUNDED, color="#f59e0b", size=18),
                            ft.Text("Rata-rata dari Semua Rating", size=11,
                                    weight=ft.FontWeight.W_700, color=self._TEXT_DARK),
                        ], spacing=6),
                        ft.Row([
                            ft.Text(str(avg_overall), size=26,
                                    weight=ft.FontWeight.W_800, color=self._PRIMARY),
                            ft.Text("/ 10", size=11, color=self._TEXT_MUTED),
                            ft.Row(stars, spacing=1),
                        ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                    ], spacing=5, tight=True),
                    ft.Text(f"Berdasarkan {total_rated} anime",
                            size=11, color=self._TEXT_MUTED),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                expand=True, height=90,
            )

            top_label = list(genre_proporsi.keys())[0] if ada_genre else "-"
            top_pct   = list(genre_proporsi.values())[0] if ada_genre else 0

            top_card = self._card(
                content=ft.Row([
                    ft.Column([
                        ft.Row([
                            ft.Icon(ft.Icons.EMOJI_EVENTS_OUTLINED,
                                    color="#f59e0b", size=18),
                            ft.Text("Top Genre Dominan", size=11,
                                    weight=ft.FontWeight.W_700, color=self._TEXT_DARK),
                        ], spacing=6),
                        ft.Text(top_label, size=20, weight=ft.FontWeight.W_800,
                                color=self._PRIMARY),
                        ft.Text(f"{top_pct}% dari total rating",
                                size=10, color=self._TEXT_MUTED),
                    ], spacing=3, tight=True),
                    ft.Container(
                        content=ft.Text("Genre favoritmu", size=10,
                                        color=self._PRIMARY,
                                        weight=ft.FontWeight.W_600),
                        bgcolor=self._LIGHT,
                        border=ft.border.all(1, self._BORDER),
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=12, vertical=5),
                    ),
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.symmetric(horizontal=20, vertical=14),
                expand=True, height=90,
            )

            bottom_row = ft.Row(controls=[avg_card, top_card], spacing=12)

            main_area = ft.Container(
                content=ft.Column([
                    ft.Text("Statistik Penilaian", size=16,
                            weight=ft.FontWeight.W_800, color=self._TEXT_DARK),
                    dim_row,
                    charts_row,
                    bottom_row,
                ], spacing=14, tight=True, scroll=ft.ScrollMode.AUTO),
                expand=True,
                padding=ft.padding.symmetric(horizontal=22, vertical=18),
            )

        # ── LAYOUT UTAMA ─────────────────────────────────────────────────────
        return ft.Container(
            content=ft.Column([
                top_bar,
                ft.Row([sidebar, main_area], spacing=0, expand=True,
                       vertical_alignment=ft.CrossAxisAlignment.START),
            ], spacing=0, expand=True),
            bgcolor=self._CARD,
            border_radius=16,
            shadow=ft.BoxShadow(spread_radius=0, blur_radius=28,
                                color=ft.Colors.with_opacity(0.10, self._PRIMARY)),
            expand=True,
            clip_behavior=ft.ClipBehavior.HARD_EDGE,
        )